from .helpers import Tile, Call
import collections

# 牌の定義
# 萬子: 1m-9m, 筒子: 1p-9p, 索子: 1s-9s, 字牌: 1z-7z (東南西北白發中)
# 赤ドラ: 5mr, 5pr, 5sr
TILES = {
    'm': [f'{i}m' for i in range(1, 10)],  # 萬子.
    'p': [f'{i}p' for i in range(1, 10)],  # 筒子.
    's': [f'{i}s' for i in range(1, 10)],  # 索子.
    'z': [f'{i}z' for i in range(1, 8)],   # 字牌 (1z-7z).
}
ALL_TILES = sum(TILES.values(), [])
YAOCHUHAI = {"1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"}
SANGENPAI = {"5z", "6z", "7z"}

class HandAnalysis:
    """手牌の解析（面子分解、待ちの形特定）を行うクラス"""
    def __init__(self, hand: list[str], called_mentsu: list[Call], agari_hai: str):
        """
        手牌の解析を初期化する.
        
        Args:
            hand (list[str])  : 手牌のリスト (例: ["1m", "2m", "3m", "4m", "5m", "6m", "7m"])
            called_mentsu (list[Call]): 鳴きの情報 (例: [Call("pon", [1m,2m,3m]), Call("chi", [4m,5m,6m]) )
            agari_hai (str)   : アガリ牌の文字列 (例: "5m")
        """
        self.hand = sorted(hand, key=Tile.sort_key)
        self.called_mentsu = called_mentsu
        self.agari_hai = agari_hai
        self.agari_combinations = self._analyze()
    
    def _find_combinations(self, hand_counter: collections.Counter) -> list[list[str]]:
        """
        手牌のカウンターから面子の組み合わせを再帰的に探す関数.
        
        Args:
            hand_counter (collections.Counter): 手牌のカウンター.
        
        Returns:
            list[list[str]]: 面子の組み合わせのリスト.
        """
        # 手牌が空なら空の組み合わせを返す.
        if not hand_counter:
            return [[]]
        
        # 最初の牌を取り出す.
        tile = next(iter(hand_counter))
        count = hand_counter[tile]
        results = []
        
        # 刻子として取り出す.
        if count >= 3:
            hand_counter[tile] -= 3
            if not hand_counter[tile]:
                del hand_counter[tile]
            sub_results = self._find_combinations(hand_counter.copy())
            # 刻子の組み合わせを結果に追加.
            for res in sub_results:
                results.append([[tile, tile, tile]] + res)
            hand_counter[tile] += 3
        
        # 順子として取り出す.
        # 牌の種類を取得 (m, p, s, z)
        suit = tile[-1]  
        if suit != 'z' and count > 0:
            normal_tile = Tile.to_normal(tile)
            num = int(normal_tile[:-1])
            t1, t2, t3 = f"{num}{suit}", f"{num+1}{suit}", f"{num+2}{suit}"
            if t2 in hand_counter and t3 in hand_counter:
                hand_counter[t1] -= 1
                hand_counter[t2] -= 1
                hand_counter[t3] -= 1
                for t in [t1, t2, t3]:
                    if not hand_counter[t]:
                        del hand_counter[t]
                sub_results = self._find_combinations(hand_counter.copy())
                for res in sub_results:
                    results.append([[t1, t2, t3]] + res)
                for t in [t1, t2, t3]:
                    hand_counter[t] = hand_counter.get(t, 0) + 1
        return results
    
    def _analyze(self) -> list[dict]:
        """
        手牌の解析を行い、面子分解と待ちの形を特定する関数.

        Returns:
            list[dict]: 解析結果のリスト.各辞書は面子の情報を含む.
        """
        # 国士無双と七対子のチェック.
        counts = collections.Counter(self.hand)
        if len(self.called_mentsu) == 0:
            # 国士無双の判定.
            if all(t in counts for t in YAOCHUHAI) and len(counts) == 14:
                return [{"type": "kokushi", "janto": self.agari_hai, "mentsu": []}]
            # 七対子の判定.
            if len(counts) == 7 and all(c == 2 for c in counts.values()):
                machi_type = "tanki" # 七対子は単騎待ち.
                return [{"type": "chitoi", "janto": None, "mentsu": list(counts.keys()), "machi": machi_type}]
        
        # 4面子1雀頭の解析.
        hand_counter = collections.Counter(self.hand)
        open_mentsu = []
        for m in self.called_mentsu:
            open_mentsu.append(m.tiles)
            for tile in m.tiles:
                hand_counter[tile] -= 1
        # Counterから枚数が1以上の牌だけをリストに戻す
        closed_hand = list(hand_counter.elements())
        results = []
        
        # 雀頭の候補を探す.
        closed_hand_counter = collections.Counter(closed_hand)
        unique_tiles = sorted(list(closed_hand_counter), key=Tile.sort_key)
        for janto_candidate in unique_tiles:
            normal_janto_candidate = Tile.to_normal(janto_candidate)
            # 雀頭候補が手牌に2枚以上ある場合のみ処理.
            if closed_hand.count(normal_janto_candidate) >= 2:
                # 雀頭を除いた手牌から面子の組み合わせを探す.
                temp_hand = closed_hand[:]
                temp_hand.remove(normal_janto_candidate)
                temp_hand.remove(normal_janto_candidate)
                combinations = self._find_combinations(collections.Counter(temp_hand))
                # 各面子の組み合わせに対して待ちの形を判定.
                for combo in combinations:
                    # 待ちの形を判定.
                    agari_mentsu = []
                    is_agari_in_janto = self.agari_hai == normal_janto_candidate
                    # アガリ牌が手牌に含まれているか確認.
                    for m in combo:
                        if self.agari_hai in m:
                            agari_mentsu.append(m)
                    # アガリ牌が面子に含まれていない場合は雀頭待ちかどうかを確認.
                    if not agari_mentsu and not is_agari_in_janto:
                        continue
                    machi = self._get_machi_type(agari_mentsu[0] if agari_mentsu else [], normal_janto_candidate, is_agari_in_janto)                    
                    results.append({
                        "type": "normal",
                        "janto": normal_janto_candidate,
                        "mentsu": combo + open_mentsu,
                        "machi": machi
                    })
        return results

    def _get_machi_type(self, mentsu: list[str], janto: list[str], is_agari_in_janto: bool) -> str:
        """
        待ちの形を判定する関数.

        Args:
            mentsu (list[str]): アガリ牌を含む1つの面子.
            janto (list[str]): 雀頭の牌.
            is_agari_in_janto (bool): アガリ牌が雀頭に含まれているかどうか.

        Returns:
            str: 待ちの形 ("tanki", "ryanmen", "penchan", "kanchan", "shanpon").
        """
        # 単騎待ちの判定.
        if is_agari_in_janto:
            return "tanki"
        # 面子が順子か刻子かを判定.
        is_shuntsu = len(set(mentsu)) > 1
        agari_normal = Tile.to_normal(self.agari_hai)
        # 面子が順子の場合、待ちの形を判定.
        if is_shuntsu:
            sorted_mentsu = sorted([Tile.to_normal(t) for t in mentsu], key=Tile.sort_key)
            # 嵌張待ち(順子の真ん中待ち)の判定.
            if sorted_mentsu[1] == agari_normal: return "kanchan"
            # 辺張待ち(1,2を持っているときの3,または8,9を持っているときの7待ち)の判定.
            if (int(sorted_mentsu[0][:-1]) == 1 and agari_normal == sorted_mentsu[2]) or (int(sorted_mentsu[0][:-1]) == 7 and agari_normal == sorted_mentsu[0]):
                return "penchan"
            # 両面待ち(順子の両端待ち)の判定.
            return "ryanmen"
        else: # 刻子
            return "shanpon"