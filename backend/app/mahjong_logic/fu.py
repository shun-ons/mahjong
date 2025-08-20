from .helpers import Tile, Call

# SANGENPAIはヘルパー側にあるかもしれませんが、念のためここに定義
SANGENPAI = {"5z", "6z", "7z"}
YAKUMAN_LIST = ["国士無双", "四暗刻", "大三元", "緑一色", "字一色", "清老頭", "九蓮宝燈", "四槓子", "天和", "地和"]

class FuCalculator:
    """
    手牌の符計算を責務に持つクラス。
    """
    def __init__(self, analysis: dict, melds: list[Call], found_yaku: dict, game_state: dict):
        """
        符計算に必要な情報を初期化する。

        Args:
            analysis (dict)   : HandAnalysisによる手牌の解析結果。
            melds (list[Call]): 鳴いた面子のリスト。
            found_yaku (dict) : 成立した役の辞書。
            game_state (dict) : ゲームの状況設定。
        """
        self.analysis = analysis
        self.melds = melds
        self.found_yaku = found_yaku
        self.game_state = game_state

    def calculate(self) -> int:
        """
        手牌の符を計算するメインメソッド。

        Returns:
            int: 最終的な符（10の倍数に切り上げ済み）。
        """
        # --- ステップ1：例外役の処理 ---
        if any(yaku in self.found_yaku for yaku in YAKUMAN_LIST):
            return 0
        if "七対子" in self.found_yaku:
            return 25
        if "平和" in self.found_yaku:
            return 20 if self.game_state.get("is_tsumo", False) else 30

        # --- ステップ2：副底 ---
        fu = 20

        # --- ステップ3：アガリ方の符 ---
        is_menzen = not self.melds
        is_tsumo = self.game_state.get("is_tsumo", False)
        
        if is_menzen and not is_tsumo:
            fu += 10  # 門前ロン加符
        if is_tsumo:
            fu += 2   # ツモ符

        # --- ステップ4, 5, 6：各要素の符を加算 ---
        fu += self._get_mentsu_fu()
        fu += self._get_janto_fu()
        fu += self._get_machi_fu()

        # --- ステップ7：切り上げと例外処理 ---
        if not is_menzen and fu == 20: # 喰い平和形
            return 30
            
        return self._round_up_fu(fu)

    def _get_mentsu_fu(self) -> int:
        """面子（メンツ）に付く符を計算する。"""
        mentsu_fu = 0
        agari_hai = self.game_state.get("agari_hai")
        is_tsumo = self.game_state.get("is_tsumo", False)
        
        # 鳴き面子の情報を比較しやすいようにタプルのセットに変換
        open_melds_tuples = {tuple(m.tiles) for m in self.melds}

        for meld in self.analysis.get("mentsu", []):
            # 順子の符は0
            if len(set(meld)) == 3:
                continue

            base = 0
            is_yaochu = Tile.is_yaochu(meld[0])
            
            # 槓子か刻子かを判定
            is_kantsu = len(meld) == 4
            
            # 鳴いているか（明刻/明槓）どうかを判定
            is_open = tuple(sorted(meld, key=Tile.sort_key)) in open_melds_tuples
            
            # ロンで完成した刻子は明刻扱い
            is_ron_kotsu = not is_tsumo and (agari_hai in meld)
            
            if is_kantsu:
                base = 8 if is_open else 16 # 明槓:8, 暗槓:16
            else: # 刻子
                base = 2 if (is_open or is_ron_kotsu) else 4 # 明刻:2, 暗刻:4

            if is_yaochu:
                base *= 2
            
            mentsu_fu += base
            
        return mentsu_fu

    def _get_janto_fu(self) -> int:
        """雀頭（ジャントウ）に付く符を計算する。"""
        janto_tile = self.analysis.get("janto")
        if not janto_tile:
            return 0
            
        bakaze = self.game_state.get("bakaze")
        jikaze = self.game_state.get("jikaze")
        fu = 0
        
        # 三元牌
        if janto_tile in SANGENPAI:
            fu += 2
        # 場風・自風
        if janto_tile == bakaze:
            fu += 2
        if janto_tile == jikaze:
            fu += 2
            
        return fu

    def _get_machi_fu(self) -> int:
        """待ちの形に付く符を計算する。"""
        machi = self.analysis.get("machi")
        fu = 0
        if machi in ['kanchan', 'penchan', 'tanki']:
            fu += 2
        return 0

    def _round_up_fu(self, fu: int) -> int:
        """符の1の位を切り上げる。"""
        return -(-fu // 10) * 10