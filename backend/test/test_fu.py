import pytest

# --- Pythonのimportパスを通すための設定 ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -----------------------------------------

# テスト対象のクラスと、そのクラスが使うヘルパーをインポート
from app.mahjong_logic.fu import FuCalculator
from app.mahjong_logic.helpers import Call, Tile

class TestFuCalculator:
    """FuCalculatorクラスのテストをまとめたクラス"""

    def test_pinfu_tsumo(self):
        """平和ツモは20符になることをテスト"""
        calculator = FuCalculator(
            analysis={},
            melds=[],
            found_yaku={"平和": 1},
            game_state={"is_tsumo": True}
        )
        assert calculator.calculate() == 20

    def test_pinfu_ron(self):
        """平和ロンは30符になることをテスト"""
        calculator = FuCalculator(
            analysis={},
            melds=[],
            found_yaku={"平和": 1},
            game_state={"is_tsumo": False}
        )
        assert calculator.calculate() == 30

    def test_chiitoitsu(self):
        """七対子は25符になることをテスト"""
        calculator = FuCalculator(
            analysis={},
            melds=[],
            found_yaku={"七対子": 1},
            game_state={}
        )
        assert calculator.calculate() == 25

    def test_complex_menzen_ron_hand(self):
        """複雑な手の符計算をテスト (門前ロン)"""
        # 手牌: 234m, 555p(暗刻), 678s, 99z(雀頭), 嵌張3m待ちロン
        analysis = {
            "mentsu": [["2m", "3m", "4m"], ["5p", "5p", "5p"], ["6s", "7s", "8s"]],
            "janto": "9z",
            "machi": "kanchan"
        }
        game_state = {
            "agari_hai": "3m",
            "is_tsumo": False
        }
        
        calculator = FuCalculator(analysis, [], {}, game_state)
        # 計算: 副底20 +
        
    def test_calculate_fu_with_penchan_wait(self):
        """辺張待ちの符計算をテスト"""
        # 手牌: 12sで3s待ちロン。他は暗刻2つと雀頭。
        analysis = {
            "mentsu": [["1s", "2s", "3s"], ["2p", "2p", "2p"], ["3p", "3p", "3p"]],
            "janto": "1z",
            "machi": "penchan"
        }
        game_state = {"is_tsumo": False, "agari_hai": "3s"}
        
        calculator = FuCalculator(analysis, [], {}, game_state)
        # 計算: 副底20 + 門前ロン10 + 中張牌暗刻4x2 + 辺張待ち2 = 40符
        assert calculator.calculate() == 40

    def test_calculate_fu_with_tanki_wait(self):
        """単騎待ちの符計算をテスト"""
        # 手牌: 4面子が完成しており、雀頭の片割れで待つ。
        analysis = {
            "mentsu": [["1s", "2s", "3s"], ["2p", "3p", "4p"], ["5m", "6m", "7m"], ["1z", "1z", "1z"]],
            "janto": "5z",
            "machi": "tanki"
        }
        game_state = {"is_tsumo": True, "agari_hai": "5z"} # ツモ和了り
        
        calculator = FuCalculator(analysis, [], {}, game_state)
        # 計算: 副底20 + ツモ2 + ヤオ九牌暗刻8 + 単騎待ち2 = 32符 -> 切り上げて40符
        assert calculator.calculate() == 40
        
    def test_calculate_fu_with_ankan(self):
        """暗槓を含む手の符計算をテスト"""
        # 手牌: 2mの暗槓、1sのポン、東の雀頭、嵌張待ちツモ
        analysis = {
            "mentsu": [["2m", "2m", "2m", "2m"], ["1s", "1s", "1s"], ["4p", "5p", "6p"]],
            "janto": "1z",
            "machi": "kanchan"
        }
        melds = [Call("pon", ["1s", "1s", "1s"])]
        game_state = {
            "is_tsumo": True, 
            "bakaze": "1z", 
            "jikaze": "1z" # 連風牌
        }
        
        calculator = FuCalculator(analysis, melds, {}, game_state)
        # 計算: 副底20 + ツモ2 + 中張牌暗槓16 + ヤオ九牌明刻4 + 連風牌雀頭4 + 嵌張待ち2 = 48符 -> 切り上げて50符
        assert calculator.calculate() == 50

    def test_calculate_fu_for_kokushi_musou(self):
        """役満（国士無双）の符は0になることをテスト"""
        analysis = {
            "type": "kokushi",
            "janto": "1m"
        }
        found_yaku = {"国士無双": 13}
        
        calculator = FuCalculator(analysis, [], found_yaku, {})
        # 役満の場合、符は計算されず0になる
        assert calculator.calculate() == 0

    def test_calculate_fu_for_multiple_open_melds(self):
        """複数の鳴きと単騎待ちのテスト"""
        # 手牌: 234m(チー), 567p(チー), 2z(ポン), 1s(単騎待ち)ツモ
        analysis = {
            "mentsu": [], # analyzerは門前面子のみ返す想定
            "janto": "1s",
            "machi": "tanki"
        }
        melds = [
            Call("chi", ["2m", "3m", "4m"]),
            Call("chi", ["5p", "6p", "7p"]),
            Call("pon", ["2z", "2z", "2z"]),
        ]
        game_state = {
            "is_tsumo": True,
            "bakaze": "1z", # 場風:東
            "jikaze": "2z"  # 自風:南 (役牌)
        }
        
        calculator = FuCalculator(analysis, melds, {}, game_state)
        # 計算: 副底20 + ツモ2 + 単騎待ち2 + 役牌(自風)の明刻4 = 28符 -> 切り上げて30符
        assert calculator.calculate() == 30