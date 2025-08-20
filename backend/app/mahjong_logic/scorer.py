import collections
from itertools import combinations
from .helpers import Call, Tile
from .analyzer import HandAnalysis
from .yaku import YakuJudge
from .fu import FuCalculator

# 牌の定義
# 萬子: 1m-9m, 筒子: 1p-9p, 索子: 1s-9s, 字牌: 1z-7z (東南西北白發中)
# 赤ドラ: 5mr, 5pr, 5sr
TILES = {
    "m": [f"{i}m" for i in range(1, 10)],
    "p": [f"{i}p" for i in range(1, 10)],
    "s": [f"{i}s" for i in range(1, 10)],
    "z": [f"{i}z" for i in range(1, 8)],
}
ALL_TILES = sum(TILES.values(), [])
YAOCHUHAI = {
    "1m",
    "9m",
    "1p",
    "9p",
    "1s",
    "9s",
    "1z",
    "2z",
    "3z",
    "4z",
    "5z",
    "6z",
    "7z",
}

class MahjongScorer:
    def __init__(
        self, hand: list[str], called_mentsu: list[Call], agari_hai: str, **game_state
    ):
        self.hand = hand
        self.called_mentsu = called_mentsu
        self.agari_hai = agari_hai
        self.game_state = game_state

    def calculate(self) -> dict:
        """
        手牌のスコアを計算するメインの関数。
        高点法に基づき、最も点数が高くなる解釈を返す。
        """
        # 1. 手牌を解析し、考えられる全ての和了パターンを取得
        analysis_patterns = HandAnalysis(
            self.hand, self.called_mentsu, self.agari_hai
        ).agari_combinations
        
        if not analysis_patterns:
            return {"error": "和了形ではありません。"}

        # 2. 各パターンで点数を計算し、最も高いものを選ぶ（高点法）
        best_result = None
        highest_score = -1

        for pattern in analysis_patterns:
            # 2a. 役を判定
            yaku_judge = YakuJudge(pattern, self.called_mentsu, self.game_state)
            found_yaku = yaku_judge.check_all_yaku()
            print(f"Found Yaku: {found_yaku}")  # デバッグ用
            han = sum(found_yaku.values())
            print(f"Han Count: {han}")  # デバッグ用
            
            if han == 0:
                continue # 役なし

            # 2c. 符を計算
            fu_calculator = FuCalculator(pattern, self.called_mentsu, found_yaku, self.game_state)
            fu = fu_calculator.calculate()

            # 2d. 最終的な点数を計算
            score_details, score_name = self._get_final_score(han, fu)
            
            # 2e. 最高得点なら結果を更新
            if score_details["total"] > highest_score:
                highest_score = score_details["total"]
                best_result = {
                    "yaku": found_yaku,
                    "han": han,
                    "fu": fu,
                    "score_name": score_name,
                    "score": score_details, # totalだけでなく詳細も返す
                }
        
        if best_result is None:
            return {"error": "役がありません。"}
            
        return best_result

    def _count_dora(self) -> tuple[int, int, int]:
        """ドラ、赤ドラ、裏ドラの枚数をそれぞれカウントする。"""
        dora_indicators = self.game_state.get("dora_indicators", [])
        ura_dora_indicators = self.game_state.get("ura_dora_indicators", [])
        is_reach = self.game_state.get("is_riichi", False)

        dora_tiles = {Tile.next_tile(t) for t in dora_indicators if t}
        uradora_tiles = {Tile.next_tile(t) for t in ura_dora_indicators if t} if is_reach else set()
        
        all_hand_tiles = self.hand + sum([m.tiles for m in self.called_mentsu], [])
        
        dora_count = 0
        akadora_count = 0
        uradora_count = 0
        
        for tile in all_hand_tiles:
            # 赤ドラのチェック
            if 'r' in tile:
                akadora_count += 1
            
            normal_tile = Tile.to_normal(tile)
            dora_count += list(dora_tiles).count(normal_tile)
            uradora_count += list(uradora_tiles).count(normal_tile)
            
        return dora_count, akadora_count, uradora_count

    def _get_final_score(self, han: int, fu: int) -> tuple[dict, str]:
        """
        最終的な点数を計算する関数.

        Args:
            han (int): 翻数.
            fu (int) : 符数.

        Returns:
            tuple[dict, str]: 計算された点数とスコア名のタプル.
        """
        if han == 0:
            return {"total": 0, "oya": 0, "ko": 0}, ""
        if han >= 13:
            score_name, base_p = "数え役満", 8000
        elif han >= 11:
            score_name, base_p = "三倍満", 6000
        elif han >= 8:
            score_name, base_p = "倍満", 4000
        elif han >= 6:
            score_name, base_p = "跳満", 3000
        elif han >= 5 or (han == 4 and fu >= 40) or (han == 3 and fu >= 70):
            score_name, base_p = "満貫", 2000
        else:
            score_name = f"{han}翻{fu}符"
            base_p = fu * (2 ** (han + 2))
            if base_p > 2000:
                base_p = 2000

        # 親と子の支払いを計算.
        # 親の計算.
        if self.game_state.get("is_oya", False):
            # ツモ.
            if self.game_state.get("is_tsumo", False):
                ko_pay = -(-base_p * 2 // 100) * 100
                return {"total": ko_pay * 3, "payment_per_ko": ko_pay}, score_name
            # ロン.
            else:
                ron_pay = -(-base_p * 6 // 100) * 100
                return {"total": ron_pay, "payment_from_ron": ron_pay}, score_name
        # 子の計算.
        else:
            # ツモ.
            if self.game_state.get("is_tsumo", False):
                oya_pay = -(-base_p * 2 // 100) * 100
                ko_pay = -(-base_p * 1 // 100) * 100
                return {
                    "total": oya_pay + ko_pay * 2,
                    "payment_from_oya": oya_pay,
                    "payment_per_ko": ko_pay,
                }, score_name
            # ロン.
            else:
                ron_pay = -(-base_p * 4 // 100) * 100
                return {"total": ron_pay, "payment_from_ron": ron_pay}, score_name
