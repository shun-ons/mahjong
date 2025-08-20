import pytest

# --- Pythonのimportパスを通すための設定 ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -----------------------------------------

from app.mahjong_logic.helpers import Tile, Call

# ===================================
# Tileクラスのテスト
# ===================================
class TestTile:
    def test_sort_key(self):
        """牌のソートキーが正しい順序を返すかテスト"""
        assert Tile.sort_key('1m') < Tile.sort_key('9m')
        assert Tile.sort_key('9m') < Tile.sort_key('1p')
        assert Tile.sort_key('1p') < Tile.sort_key('9p')
        assert Tile.sort_key('9p') < Tile.sort_key('1s')
        assert Tile.sort_key('1s') < Tile.sort_key('9s')
        assert Tile.sort_key('9s') < Tile.sort_key('1z')
        assert Tile.sort_key('1z') < Tile.sort_key('7z')

        # 赤ドラも考慮
        assert Tile.sort_key('5m') == Tile.sort_key('5mr')

    def test_to_normal(self):
        """赤ドラが通常牌に正しく変換されるかテスト"""
        assert Tile.to_normal('5mr') == '5m'
        assert Tile.to_normal('5pr') == '5p'
        assert Tile.to_normal('5sr') == '5s'
        assert Tile.to_normal('3m') == '3m'

    @pytest.mark.parametrize("tile, expected", [
        ("1m", True), ("9p", True), ("1z", True), ("7z", True), # ヤオ九牌
        ("2m", False), ("5s", False), ("5pr", False)           # 中張牌
    ])
    def test_is_yaochu(self, tile, expected):
        """牌がヤオ九牌かどうかを正しく判定できるかテスト"""
        assert Tile.is_yaochu(tile) == expected

    @pytest.mark.parametrize("tile, expected", [
        ("1z", True), ("7z", True),  # 字牌
        ("1m", False), ("9s", False) # 数牌
    ])
    def test_is_jihai(self, tile, expected):
        """牌が字牌かどうかを正しく判定できるかテスト"""
        assert Tile.is_jihai(tile) == expected

    @pytest.mark.parametrize("dora_indicator, expected_dora", [
        ("1m", "2m"), ("8p", "9p"), ("9s", "1s"), # 数牌
        ("3z", "4z"), ("4z", "1z"), # 風牌
        ("6z", "7z"), ("7z", "5z"), # 三元牌
        ("5mr", "6m") # 赤ドラ表示牌
    ])
    def test_next_tile(self, dora_indicator, expected_dora):
        """ドラ表示牌から次の牌（ドラ）を正しく計算できるかテスト"""
        assert Tile.next_tile(dora_indicator) == expected_dora
        
    @pytest.mark.parametrize("invalid_tile", [
        "10m",    # 存在しない数字
        "0p",     # 存在しない数字
        "az",     # 不正な種類
        "5q",     # 不正な種類
        ""        # 空文字
    ])
    def test_next_tile_with_invalid_input(self, invalid_tile):
        """next_tile関数が不正な入力に対してNoneを返すかテスト"""
        assert Tile.next_tile(invalid_tile) is None

# ===================================
# Callクラスのテスト
# ===================================
class TestCall:
    def test_call_type_checking(self):
        """鳴きの種類を判定するis_*メソッドが正しく動作するかテスト"""
        pon = Call('pon', ['1m', '1m', '1m'])
        chi = Call('chi', ['2p', '3p', '4p'])
        minkan = Call('minkan', ['5s', '5s', '5s', '5s'])
        
        assert pon.is_kotsu() == True
        assert pon.is_shuntsu() == False
        
        assert chi.is_kotsu() == False
        assert chi.is_shuntsu() == True
        
        assert minkan.is_minkan() == True
        assert minkan.is_kotsu() == True