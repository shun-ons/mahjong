import collections
from itertools import combinations
from helpers import Meld, Tile
from analyzer import HandAnalysis
import yaku as YakuChecker
import fu as FuCalculator

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
        self, hand: list[str], melds: list[Meld], agari_hai: str, **game_state
    ):
        """
        MahjongScorerの初期化.

        Args:
            hand (list[str]): 手牌のリスト (例: ["1m", "2m", "3m", "4m", "5m", "6m", "7m"])
            melds (list[Meld]): 鳴きの情報 (例: [Meld("pon", ["1m", "2m", "3m"]), Meld("chi", ["4m", "5m", "6m"])])
            agari_hai (str): アガリ牌の文字列 (例: "5m")
            game_state (dict): ゲームの状態（is_tsumo, is_oya など）を含む辞書.
                例: {
                    "is_tsumo": True,
                    "is_oya": False,
                    "is_reach": True,
                    "dora_indicators": ["5m", "5p"],
                    "ura_dora_indicators": ["6m", "6p"],
                    "bakaze": "1z",
                    "jikaze": "2z",
                    "is_ippatsu": False,
                    "is_rinshan": False,
                    "is_haitei": False}
        """
        self.hand = hand
        self.melds = melds
        self.agari_hai = agari_hai
        self.game_state = game_state

    def calculate(self) -> dict:
        """
        手牌のスコアを計算する関数.

        Returns:
            dict: スコア計算の結果を含む辞書.
                例: {
                    "yaku": {"リーチ": 1, "平和": 1},
                    "han": 2,
                    "fu": 30,
                    "score_name": "満貫",
                    "score": 2000,
                }
        """
        # 手牌の解析を行う.
        analysis = HandAnalysis(
            self.hand, self.melds, self.agari_hai
        ).agari_combinations
        if not analysis:
            return {"error": "アガリ形ではありません。"}
        # 高点法で最高点を選ぶ (簡単のため、最初の分析結果を使用)
        best_analysis = analysis[0]
        # 役を計算.
        found_yaku, han = YakuChecker.check_all_yaku(
            best_analysis, self.melds, self.game_state
        )
        if han == 0:
            return {"error": "役がありません。"}
        # 符を計算.
        fu = FuCalculator.calculate_fu(
            best_analysis, self.melds, found_yaku, self.game_state
        )
        # ドラを計算.
        dora_han = self._count_dora()
        total_han = han + dora_han
        # 最終的な点数を計算して報告.
        score, name = self._get_final_score(total_han, fu)
        return {
            "yaku": found_yaku,
            "han": total_han,
            "fu": fu,
            "score_name": name,
            "score": score,
        }

    def _count_dora(self) -> int:
        """
        ドラの枚数をカウントする関数.

        Returns:
            int : ドラの枚数.
        """
        # ゲーム状態からドラと裏ドラの情報を取得.
        dora_indicators = self.game_state.get("dora_indicators", [])
        ura_dora_indicators = self.game_state.get("ura_dora_indicators", [])
        is_reach = self.game_state.get("is_reach", False)
        # ドラと裏ドラのリストを準備する.
        dora = [Tile.next_tile(t) for t in dora_indicators if t]
        uradora = (
            [Tile.next_tile(t) for t in ura_dora_indicators if t] if is_reach else []
        )
        # 全ての手牌を一つのリストにまとめる.
        all_hand_tiles = self.hand + sum([m.tiles for m in self.melds], [])
        dora_count = 0
        akadora_count = 0
        uradora_count = 0
        # 各牌をチェックしてドラを数える.
        for tile in all_hand_tiles:
            # 表ドラのチェック.
            if Tile.to_normal(tile) in dora:
                dora_count += 1
            # 赤ドラのチェック.
            if tile in ["5mr", "5pr", "5sr"]:
                akadora_count += 1
            # 裏ドラのチェック(リーチしている時のみuradoraリストに中身がある)
            if Tile.to_normal(tile) in uradora:
                uradora_count += 1
        # ドラ、赤ドラ、裏ドラの合計を返す.
        total = dora_count + akadora_count + uradora_count
        return total

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
        elif han >= 5:
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
