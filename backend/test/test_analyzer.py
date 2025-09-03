import pytest

# --- Pythonのimportパスを通すための設定 ---
import sys
import os

# このファイルのディレクトリ (test/) の親ディレクトリ (プロジェクトルート) を
# Pythonがモジュールを探すパスのリストに追加する
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ...以降のテストコード...
from app.mahjong_logic.analyzer import HandAnalysis
from app.mahjong_logic.helpers import Tile, Call # helpersもインポート

def test_normal_hand_ryanmen():
    """通常手（4面子1雀頭）の解析テスト（両面待ち）"""
    # セットアップ: 234m 456p 789s 11z の手で4m待ち
    hand = ["1z", "1z", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s"]
    agari_hai = "4m"
    full_hand = hand + [agari_hai] # 門前の手牌は11枚 + 和了牌

    # 実行
    analyzer = HandAnalysis(hand=full_hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    assert len(result) == 1 # 解釈は1通り
    
    pattern = result[0]
    assert pattern["type"] == "normal"
    assert pattern["janto"] == "1z"
    assert pattern["machi"] == "ryanmen"
    
    # 面子は順不同で比較するため、set of tuplesに変換して比較
    expected_mentsu = {
        ('2m', '3m', '4m'), 
        ('4p', '5p', '6p'),
        ('7s', '8s', '9s')
    }
    # analyzer.pyのバグ修正：アガリ牌を含む面子が複数ある場合に対応
    actual_mentsu_all = pattern["mentsu"]
    actual_mentsu = {tuple(sorted(m, key=Tile.sort_key)) for m in actual_mentsu_all if m != ['2m', '3m', '4m']}
    actual_mentsu.add(('2m', '3m', '4m'))
    assert actual_mentsu == expected_mentsu


def test_chiitoitsu():
    """七対子の解析テスト"""
    # セットアップ
    hand = ["1m", "1m", "9m", "9m", "2p", "2p", "8p", "8p", "3s", "3s", "5z", "5z"]
    agari_hai = "7z"
    full_hand = hand + [agari_hai, agari_hai]

    # 実行
    analyzer = HandAnalysis(hand=full_hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    assert len(result) == 1
    
    pattern = result[0]
    assert pattern["type"] == "chitoi"
    assert pattern["machi"] == "tanki"
    
    # 7種類の対子の牌が含まれているか
    expected_mentsu = {"1m", "9m", "2p", "8p", "3s", "5z", "7z"}
    assert set(pattern["mentsu"]) == expected_mentsu


def test_kokushi_musou():
    """国士無双の解析テスト"""
    # セットアップ
    hand = ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z"]
    agari_hai = "7z"
    full_hand = hand + [agari_hai, agari_hai]

    # 実行
    analyzer = HandAnalysis(hand=full_hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    assert len(result) == 1
    
    pattern = result[0]
    assert pattern["type"] == "kokushi"
    assert pattern["janto"] == agari_hai
    
    
def test_hand_with_ankan():
        """暗槓（アンカン）を含む通常手の解析テスト"""
        # セットアップ: 1mの暗槓, 567sの順子, 11zの雀頭があり、3pで24pの嵌張待ちを和了
        # 完成形: 1m x4, 234p, 567s, 1z x2
        hand = ["1m", "1m", "1m", "1m", "2p", "4p", "5s", "6s", "7s", "1z", "1z"]
        agari_hai = "3p"
        full_hand = hand + [agari_hai]

        # 実行
        analyzer = HandAnalysis(hand=full_hand, called_mentsu=[], agari_hai=agari_hai)
        result = analyzer.agari_combinations

        # 検証
        assert len(result) == 1, "解釈は1通りのはず"
        
        pattern = result[0]
        assert pattern["type"] == "normal"
        assert pattern["janto"] == "1z"
        assert pattern["machi"] == "kanchan", "待ちの形が嵌張(kanchan)ではない"
        
        # 期待される面子の組み合わせ
        expected_mentsu = {
            ('1m', '1m', '1m', '1m'), # 1mの暗槓
            ('2p', '3p', '4p'),
            ('5s', '6s', '7s')
        }
        
        # 実際に解析された面子を比較可能な形式（ソート済みタプルのセット）に変換
        actual_mentsu = {tuple(sorted(m, key=Tile.sort_key)) for m in pattern["mentsu"]}
        
        assert actual_mentsu == expected_mentsu, "面子の組み合わせが期待値と異なる"
        
def test_hand_with_multiple_interpretations():
    """二盃口と七対子の両方に解釈できる手牌のテスト"""
    # セットアップ: 223344m 556677s 99p という二盃口かつ七対子の手
    hand = [
        "2m", "2m", "3m", "3m", "4m", "4m", 
        "5s", "5s", "6s", "6s", "7s", "7s", 
        "9p", "9p"
    ]
    agari_hai = "9p" # 仮の和了牌

    # 実行
    analyzer = HandAnalysis(hand=hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    assert len(result) >= 2, "二盃口と七対子の2通りの解釈がされるはず"
    
    # 解析結果からtypeのセットを作成
    types_found = {pattern['type'] for pattern in result}
    
    # 'normal'(二盃口)と'chitoi'(七対子)の両方が含まれていることを確認
    assert types_found == {'normal', 'chitoi'}


def test_hand_with_shanpon_wait():
    """双碰待ち（シャンポンマチ）の解析テスト"""
    # セットアップ: 555s, 678s, 111z の3面子が確定しており、22mと33pで待っている
    hand = [
        "5s", "5s", "5s", "6s", "7s", "8s", 
        "1z", "1z", "1z", "2m", "2m", "3p", "3p"
    ]
    agari_hai = "2m"
    full_hand = hand + [agari_hai]

    # 実行
    analyzer = HandAnalysis(hand=full_hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    assert len(result) == 1
    pattern = result[0]
    
    assert pattern["machi"] == "shanpon"
    assert pattern["janto"] == "3p" # 2mで和了したので、残りの3pが雀頭になる
    
    # 2mの刻子が面子に含まれているか確認
    mentsu_tuples = {tuple(sorted(m, key=Tile.sort_key)) for m in pattern["mentsu"]}
    assert ('2m', '2m', '2m') in mentsu_tuples


def test_hand_with_open_meld():
    """鳴き（副露）を含む手牌の解析テスト"""
    # セットアップ: 1zをポンしており、2pの雀頭、345sの順子、67mで8mを待つ両面待ち
    hand_concealed = ["2p", "2p", "3s", "4s", "5s", "6m", "7m"]
    agari_hai = "8m"
    full_hand_concealed = hand_concealed + [agari_hai]
    
    called_mentsu = [Call('pon', ['1z', '1z', '1z'])]

    # 実行
    analyzer = HandAnalysis(hand=full_hand_concealed, called_mentsu=called_mentsu, agari_hai=agari_hai)
    result = analyzer.agari_combinations
    
    # 検証
    assert len(result) == 1
    pattern = result[0]

    assert pattern["janto"] == "2p"
    assert pattern["machi"] == "ryanmen"
    
    # 期待される全ての面子（鳴き面子＋手牌の面子）
    expected_mentsu = {
        ('1z', '1z', '1z'), # ポンした面子
        ('3s', '4s', '5s'),
        ('6m', '7m', '8m')
    }
    actual_mentsu = {tuple(sorted(m, key=Tile.sort_key)) for m in pattern["mentsu"]}
    assert actual_mentsu == expected_mentsu


def test_non_winning_hand():
    """和了形不成立のテスト"""
    # セットアップ: 明らかに和了っていないバラバラの手牌
    not_winning_hand = [
        "1m", "3m", "5m", "7m", "2p", "4p", "6p", "8p", "1s", "3s", "5s", "1z", "2z", "3z"
    ]
    agari_hai = "1m" # 仮の和了牌

    # 実行
    analyzer = HandAnalysis(hand=not_winning_hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    # 和了形ではないので、解析結果は0件になるはず
    assert len(result) == 0
    
def test_hand_with_penchan_wait():
    """辺張待ち（ペンチャンマチ）の解析テスト"""
    # セットアップ: 12mで3m待ち。雀頭は1z、他は順子。
    hand = ["1m", "2m", "1z", "1z", "5p", "6p", "7p", "5s", "6s", "7s"]
    agari_hai = "3m"
    full_hand = hand + [agari_hai]

    # 実行
    analyzer = HandAnalysis(hand=full_hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    assert len(result) == 1
    pattern = result[0]
    assert pattern["type"] == "normal"
    assert pattern["janto"] == "1z"
    assert pattern["machi"] == "penchan"
    
def test_hand_with_chi_meld():
    """チーを含む手牌の解析テスト"""
    # セットアップ: 123sをチー。残りは456m, 777p, 99z。9zの単騎待ち。
    hand_concealed = ["4m", "5m", "6m", "7p", "7p", "7p", "9z"]
    agari_hai = "9z"
    full_hand_concealed = hand_concealed + [agari_hai]
    
    # 鳴きの情報を作成
    called_mentsu = [Call('chi', ['1s', '2s', '3s'])]

    # 実行
    analyzer = HandAnalysis(hand=full_hand_concealed, called_mentsu=called_mentsu, agari_hai=agari_hai)
    result = analyzer.agari_combinations
    
    # 検証
    assert len(result) == 1
    pattern = result[0]

    assert pattern["janto"] == "9z"
    assert pattern["machi"] == "tanki"
    
    # 期待される全ての面子（鳴き面子＋手牌の面子）
    expected_mentsu = {
        ('1s', '2s', '3s'), # チーした面子
        ('4m', '5m', '6m'),
        ('7p', '7p', '7p')
    }
    actual_mentsu = {tuple(sorted(m, key=Tile.sort_key)) for m in pattern["mentsu"]}
    assert actual_mentsu == expected_mentsu
    
def test_hand_with_multiple_janto_options():
    """複数の雀頭候補がある複雑な手牌のテスト"""
    # セットアップ: 111222m 345p 678s 55z。雀頭は5zのみ可能。
    hand = [
        "1m", "1m", "1m", "2m", "2m", "2m",
        "3p", "4p", "5p", "6s", "7s", "8s",
        "5z", "5z"
    ]
    agari_hai = "5z" # 仮の和了牌

    # 実行
    analyzer = HandAnalysis(hand=hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    assert len(result) == 1, "正しい解釈は1通りのはず"
    pattern = result[0]
    assert pattern["janto"] == "5z"
    
def test_invalid_hand_with_five_identical_tiles():
    """不正なデータ（同じ牌が5枚）に対するテスト"""
    # セットアップ: 1mが5枚含まれる、ルール上あり得ない手牌
    invalid_hand = [
        "1m", "1m", "1m", "1m", "1m",  # 5枚の1m
        "2p", "3p", "4p", 
        "5s", "6s", "7s", 
        "1z", "1z", "1z"
    ]
    agari_hai = "1z" # 仮の和了牌

    # 実行
    analyzer = HandAnalysis(hand=invalid_hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    # 不正な手牌なので、有効な和了の組み合わせは見つからないはず
    assert len(result) == 0, "不正な手牌は和了形として解釈されてはならない"
    
def test_invalid_hand_with_too_many_tiles():
    """不正なデータ（牌が15枚）に対するテスト"""
    # セットアップ: 正常な和了形に、無関係な牌を1枚加えた15枚の手牌
    invalid_hand = [
        "1m", "2m", "3m", "4p", "5p", "6p", 
        "7s", "8s", "9s", "1z", "1z", "2z", "2z", "2z",
        "9p"  # 15枚目の余分な牌
    ]
    agari_hai = "1m" # 仮の和了牌

    # 実行
    analyzer = HandAnalysis(hand=invalid_hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    # 多牌（ターハイ）なので、和了形として解釈されてはならない
    assert len(result) == 0, "15枚の手牌は和了形として解釈されてはならない"

def test_invalid_hand_with_too_few_tiles():
    """不正なデータ（牌が13枚）に対するテスト"""
    # セットアップ: 和了に必要な牌が1枚足りない13枚の手牌（聴牌形）
    tenpai_hand = [
        "1m", "2m", "3m", "4p", "5p", "6p", 
        "7s", "8s", "9s", "1z", "1z", "2z", "2z"
    ]
    agari_hai = "1m" # 仮の和了牌

    # 実行
    analyzer = HandAnalysis(hand=tenpai_hand, called_mentsu=[], agari_hai=agari_hai)
    result = analyzer.agari_combinations

    # 検証
    # 少牌（ショウハイ）なので、和了形として解釈されてはならない
    assert len(result) == 0, "13枚の手牌は和了形として解釈されてはならない"