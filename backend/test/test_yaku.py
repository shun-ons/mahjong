import pytest

# --- Pythonのimportパスを通すための設定 ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -----------------------------------------

from app.mahjong_logic.yaku import YakuJudge
from app.mahjong_logic.helpers import Call

class TestYakuJudge:
    """YakuJudgeクラスの包括的なテスト"""

    # --- 1飜役のテスト ---
    def test_riichi(self):
        analysis = {"type": "normal", "mentsu": [["1m","2m","3m"],["2p","3p","4p"],["5s","6s","7s"],["1z","1z","1z"]], "janto": "5z", "machi": "kanchan"}
        context = {"is_riichi": True, "is_menzen": True}
        judge = YakuJudge(analysis, [], context)
        assert judge.check_all_yaku() == {"立直": 1}

    def test_tanyao_open(self):
        analysis = {"type": "normal", "mentsu": [["2m","3m","4m"],["3p","4p","5p"],["6s","7s","8s"],["2s","2s","2s"]], "janto": "5m", "machi": "ryanmen"}
        melds = [Call("pon", ["2s", "2s", "2s"])]
        context = {"is_menzen": False}
        judge = YakuJudge(analysis, melds, context)
        assert judge.check_all_yaku() == {"断么九": 1}

    @pytest.mark.parametrize("context_flag, expected_yaku_name", [
        ("is_ippatsu", "一発"),
        ("is_rinshan", "嶺上開花"),
        ("is_haitei", "海底摸月"),
        ("is_houtei", "河底撈魚"),
    ])
    def test_context_1han_yaku(self, context_flag, expected_yaku_name):
        """一発・嶺上開花・海底・河底のテスト"""
        # セットアップ：シンプルな手牌を用意
        analysis = {"type": "normal", "mentsu": [["1m","2m","3m"],["2p","3p","4p"],["5s","6s","7s"],["1z","1z","1z"]], "janto": "9p"}
        # contextの特定のフラグだけをTrueにする
        context = {context_flag: True, "is_menzen": True, "machi": "kanchan"}
        judge = YakuJudge(analysis, [], context)
        result = judge.check_all_yaku()
        
        assert result == {expected_yaku_name: 1}

    @pytest.mark.parametrize("kotsu_tile, bakaze, jikaze, expected_yaku_name", [
        ("5z", "1z", "2z", "白"),
        ("6z", "1z", "2z", "發"),
        ("7z", "1z", "2z", "中"),
        ("1z", "1z", "2z", "場風"), # 場風が東の場合
        ("2z", "1z", "2z", "自風"), # 自風が南の場合
    ])
    def test_yakuhai(self, kotsu_tile, bakaze, jikaze, expected_yaku_name):
        """各種役牌のテスト"""
        # セットアップ：指定された牌の刻子を含む手牌
        analysis = {"type": "normal", "mentsu": [[kotsu_tile,kotsu_tile,kotsu_tile],["1m","2m","3m"],["4p","5p","6p"],["7s","8s","9s"]], "janto": "9p"}
        context = {"bakaze": bakaze, "jikaze": jikaze}
        
        judge = YakuJudge(analysis, [], context)
        result = judge.check_all_yaku()
        
        assert result == {expected_yaku_name: 1}

    def test_pinfu(self):
        """平和（ピンフ）のテスト"""
        # セットアップ：平和の条件をすべて満たす手牌
        # 1. 門前である
        # 2. 4面子がすべて順子
        # 3. 雀頭が役牌ではない
        # 4. 両面待ちである
        analysis = {"type": "normal", "mentsu": [["1m","2m","3m"],["4m","5m","6m"],["2p","3p","4p"],["5s","6s","7s"]], "janto": "8p", "machi": "ryanmen"}
        context = {"is_menzen": True, "agari_hai": "3p"} # 仮の和了牌
        
        judge = YakuJudge(analysis, [], context)
        result = judge.check_all_yaku()
        
        assert result == {"平和": 1}
        
    def test_chankan(self):
        """槍槓（チャンカン）のテスト"""
        analysis = {"type": "normal", "mentsu": [["1m","2m","3m"],["2p","3p","4p"],["5s","6s","7s"],["1z","1z","1z"]], "janto": "9p", "machi": "kanchan"}
        context = {"is_chankan": True, "is_menzen": True}
        judge = YakuJudge(analysis, [], context)
        assert judge.check_all_yaku() == {"槍槓": 1}

    # --- 2飜役のテスト ---
    def test_toitoi(self):
        analysis = {"type": "normal", "mentsu": [["2m","2m","2m"],["4p","4p","4p"],["6s","6s","6s"],["8s","8s","8s"]], "janto": "1z", "machi": "shanpon"}
        melds = [Call("pon", ["2m","2m","2m"]), Call("pon", ["6s","6s","6s"])]
        context = {"is_menzen": False}
        judge = YakuJudge(analysis, melds, context)
        assert judge.check_all_yaku() == {"対々和": 2}

    def test_sanankou(self):
        analysis = {"type": "normal", "mentsu": [["2m","3m","4m"],["4p","4p","4p"],["6s","6s","6s"],["8s","8s","8s"]], "janto": "1z", "machi": "shanpon"}
        context = {"is_menzen": True, "is_tsumo": False, "agari_hai": "3m"}
        judge = YakuJudge(analysis, [], context)
        assert judge.check_all_yaku() == {"三暗刻": 2}

    def test_sanshoku_doujun_open(self):
        analysis = {"type": "normal", "mentsu": [["2m","3m","4m"],["2p","3p","4p"],["2s","3s","4s"],["9m","9m","9m"]], "janto": "1p", "machi": "kanchan"}
        melds = [Call("chi", ["2m", "3m", "4m"])]
        context = {"is_menzen": False}
        judge = YakuJudge(analysis, melds, context)
        assert judge.check_all_yaku() == {"三色同順": 1}

    def test_sanshoku_doukou(self):
        """三色同刻のテスト"""
        analysis = {"type": "normal", "mentsu": [["2m","2m","2m"],["2p","2p","2p"],["2s","2s","2s"],["5m","6m","7m"]], "janto": "1z", "machi": "kanchan"}
        melds = [Call("pon", ["2m","2m","2m"])]
        context = {"is_menzen": False}
        judge = YakuJudge(analysis, melds, context)
        assert judge.check_all_yaku() == {"三色同刻": 2}

    def test_sankantsu(self):
        """三槓子のテスト"""
        analysis = {"type": "normal", "mentsu": [["2m","2m","2m","2m"],["3p","3p","3p","3p"],["4s","4s","4s","4s"],["5m","6m","7m"]], "janto": "1z", "machi": "kanchan"}
        melds = [Call("minkan", ["2m","2m","2m","2m"]), Call("kakan", ["3p","3p","3p","3p"])]
        context = {"is_menzen": False}
        judge = YakuJudge(analysis, melds, context)
        assert judge.check_all_yaku() == {"三槓子": 2}

    def test_shousangen(self):
        """小三元のテスト"""
        analysis = {"type": "normal", "mentsu": [["5z","5z","5z"],["6z","6z","6z"],["1m","2m","3m"],["2p","3p","4p"]], "janto": "7z", "machi": "kanchan"}
        melds = [Call("pon", ["5z","5z","5z"])]
        context = {"is_menzen": False}
        judge = YakuJudge(analysis, melds, context)
        # 小三元(2) + 白(1) + 發(1) = 4飜
        expected = {"小三元": 2, "白": 1, "發": 1}
        assert judge.check_all_yaku() == expected

    def test_double_riichi(self):
        """ダブル立直のテスト"""
        analysis = {"type": "normal", "mentsu": [["1m","2m","3m"],["2p","3p","4p"],["5s","6s","7s"],["1z","1z","1z"]], "janto": "9p", "machi": "kanchan"}
        context = {"is_double_riichi": True, "is_menzen": True}
        judge = YakuJudge(analysis, [], context)
        assert judge.check_all_yaku() == {"ダブル立直": 2}

    def test_honroutou(self):
        """混老頭のテスト"""
        # 混老頭は必ず対々和か七対子と複合する
        analysis = {"type": "normal", "mentsu": [["1m","1m","1m"],["9p","9p","9p"],["1z","1z","1z"],["7z","7z","7z"]], "janto": "9s", "machi": "shanpon"}
        melds = [Call("pon", ["1z","1z","1z"])]
        context = {"is_menzen": False, "bakaze": "2z", "jikaze": "3z"}
        judge = YakuJudge(analysis, melds, context)
        expected = {"混老頭": 2, "対々和": 2, "役牌(東)": 1, "役牌(中)": 1}
        # 役牌の名前はyaku.pyの実装に依存するため、キーの存在と飜数でチェック
        result = judge.check_all_yaku()
        assert "混老頭" in result and result["混老頭"] == 2
        assert "対々和" in result and result["対々和"] == 2
        # 役牌のチェック（実装によって役牌名が異なる可能性があるため）
        yakuhai_count = sum(1 for yaku in result if yaku in ["白", "發", "中", "場風", "自風"])
        assert yakuhai_count == 1
        
    def test_ikkitsuukan_open(self):
        """一気通貫（鳴きあり）のテスト"""
        analysis = {"type": "normal", "mentsu": [["1m","2m","3m"],["4m","5m","6m"],["7m","8m","9m"],["5z","5z","5z"]], "janto": "1p", "machi": "kanchan"}
        melds = [Call("chi", ["4m","5m","6m"])]
        context = {"is_menzen": False}
        judge = YakuJudge(analysis, melds, context)
        assert judge.check_all_yaku() == {"一気通貫": 1, "白": 1}
    
    def test_chanta_open(self):
        """混全帯么九（鳴きあり）のテスト"""
        analysis = {"type": "normal", "mentsu": [["1m","2m","3m"],["7s","8s","9s"],["1z","1z","1z"],["9p","9p","9p"]], "janto": "1p", "machi": "kanchan"}
        melds = [Call("chi", ["1m","2m","3m"])]
        context = {"is_menzen": False, "bakaze": "1z"} # 場風と自風は役牌ではない設定
        judge = YakuJudge(analysis, melds, context)
        assert judge.check_all_yaku() == {"混全帯么九": 1, "場風": 1}

    # --- 3飜役のテスト ---
    def test_ryanpeiko(self):
        """二盃口のテスト"""
        analysis = {"type": "normal", "mentsu": [["2m","3m","4m"],["2m","3m","4m"],["5s","6s","7s"],["5s","6s","7s"]], "janto": "9p", "machi": "tanki"}
        context = {"is_menzen": True, "agari_hai": "9p"}
        judge = YakuJudge(analysis, [], context)
        result = judge.check_all_yaku()
        assert "二盃口" in result and result["二盃口"] == 3

    def test_honitsu_with_yakuhai(self):
        """混一色（鳴きあり）のテスト"""
        analysis = {"type": "normal", "mentsu": [["1m","2m","3m"],["4m","5m","6m"],["5z","5z","5z"],["1z","1z","1z"]], "janto": "7m", "machi": "kanchan"}
        melds = [Call("pon", ["5z","5z","5z"])]
        context = {"is_menzen": False, "bakaze": "1z", "jikaze": "2z"}
        judge = YakuJudge(analysis, melds, context)
        result = judge.check_all_yaku()
        assert "混一色" in result and result["混一色"] == 2
        assert "白" in result and result["白"] == 1
        assert "場風" in result and result["場風"] == 1
        
    @pytest.mark.parametrize("is_menzen, expected_han", [
        (True, 3),  # 門前ケース
        (False, 2)  # 鳴きケース（食い下がり）
    ])
    def test_junchan(self, is_menzen, expected_han):
        """純全帯幺九（ジュンチャン）のテスト（門前・鳴き）"""
        # セットアップ：全ての面子・雀頭に1か9が含まれ、字牌は含まない
        analysis = {
            "type": "normal",
            "mentsu": [
                ["1m", "2m", "3m"],
                ["7p", "8p", "9p"],
                ["1s", "1s", "1s"],
                ["9s", "9s", "9s"]
            ],
            "janto": "1p",
            "machi": "kanchan" # 仮
        }
        
        # 鳴きの有無に応じて設定を分ける
        if is_menzen:
            melds = []
            context = {"is_menzen": True}
        else:
            melds = [Call("chi", ["1m", "2m", "3m"])]
            context = {"is_menzen": False}
        
        judge = YakuJudge(analysis, melds, context)
        result = judge.check_all_yaku()
        
        # ジュンチャンが成立し、飜数が正しいことを確認
        assert "純全帯么九" in result
        assert result["純全帯么九"] == expected_han
    
    # --- 6飜役のテスト ---
    def test_chinitsu(self):
        """清一色のテスト"""
        analysis = {"type": "normal", "mentsu": [["1m","2m","3m"],["2m","3m","4m"],["5m","6m","7m"],["8m","8m","8m"]], "janto": "9m", "machi": "kanchan"}
        context = {"is_menzen": True}
        judge = YakuJudge(analysis, [], context)
        assert judge.check_all_yaku() == {"清一色": 6}

    # --- 役満のテスト ---
    def test_daisangen(self):
        """大三元のテスト"""
        analysis = {"type": "normal", "mentsu": [["5z","5z","5z"],["6z","6z","6z"],["7z","7z","7z"],["1m","2m","3m"]], "janto": "9p", "machi": "kanchan"}
        context = {}
        judge = YakuJudge(analysis, [], context)
        assert judge.check_all_yaku() == {"大三元": 13}

    def test_suuankou(self):
        """四暗刻のテスト"""
        analysis = {"type": "normal", "mentsu": [["2m","2m","2m"],["4p","4p","4p"],["6s","6s","6s"],["8s","8s","8s"]], "janto": "1z", "machi": "shanpon"}
        context = {"is_menzen": True, "is_tsumo": True, "agari_hai": "8s"}
        judge = YakuJudge(analysis, [], context)
        assert judge.check_all_yaku() == {"四暗刻": 13}
        
    def test_suukantsu(self):
        """四槓子（スーカンツ）のテスト"""
        analysis = {
            "type": "normal",
            "mentsu": [
                ["1m", "1m", "1m", "1m"],
                ["2p", "2p", "2p", "2p"],
                ["3s", "3s", "3s", "3s"],
                ["4z", "4z", "4z", "4z"]
            ],
            "janto": "5z"
        }
        # 4つの鳴き槓子を設定
        melds = [
            Call("minkan", ["1m", "1m", "1m", "1m"]),
            Call("minkan", ["2p", "2p", "2p", "2p"]),
            Call("kakan", ["4z", "4z", "4z", "4z"])
        ]
        judge = YakuJudge(analysis, melds, {})
        assert judge.check_all_yaku() == {"四槓子": 13}

    def test_ryuuiisou(self):
        """緑一色（リューイーソー）のテスト"""
        # 緑一色を構成する牌のみで作成
        analysis = {
            "type": "normal",
            "mentsu": [
                ["2s", "3s", "4s"],
                ["2s", "3s", "4s"],
                ["6s", "6s", "6s"],
                ["6z", "6z", "6z"] # 發
            ],
            "janto": "8s"
        }
        judge = YakuJudge(analysis, [], {"is_menzen": True})
        # 役満なので役牌(發)は複合しない
        assert judge.check_all_yaku() == {"緑一色": 13}
        
    def test_tsuuiisou(self):
        """字一色（ツーイーソー）のテスト"""
        # 字牌のみで構成
        analysis = {
            "type": "normal",
            "mentsu": [
                ["1z", "1z", "1z"],
                ["2z", "2z", "2z"],
                ["3z", "3z", "3z"],
                ["6z", "6z", "6z"]
            ],
            "janto": "5z"
        }
        context = {"is_menzen": True, "agari_hai": "6z", "is_tsumo": False}
        judge = YakuJudge(analysis, [], context)
        # 役満なので役牌や対々和は複合しない
        assert judge.check_all_yaku() == {"字一色": 13}

    def test_chinroutou(self):
        """清老頭（チンロウトウ）のテスト"""
        # 1,9牌のみで構成
        analysis = {
            "type": "normal",
            "mentsu": [
                ["1m", "1m", "1m"],
                ["9m", "9m", "9m"],
                ["1p", "1p", "1p"],
                ["9s", "9s", "9s"]
            ],
            "janto": "1s"
        }
        judge = YakuJudge(analysis, [], {"is_menzen": False})
        assert judge.check_all_yaku() == {"清老頭": 13}

    def test_shousuushii(self):
        """小四喜（ショウスーシー）のテスト"""
        # 3種類の風牌が刻子、1種類が雀頭
        analysis = {
            "type": "normal",
            "mentsu": [
                ["1z", "1z", "1z"], # 東
                ["2z", "2z", "2z"], # 南
                ["3z", "3z", "3z"], # 西
                ["1m", "2m", "3m"]
            ],
            "janto": "4z" # 北
        }
        judge = YakuJudge(analysis, [], {"is_menzen": True})
        assert judge.check_all_yaku() == {"小四喜": 13}

    def test_kyuuren_poutou_normal(self):
        """九蓮宝燈（通常）のテスト"""
        # 1112345678999の形
        hand = ["1m","1m","1m","2m","3m","4m","5m","6m","7m","8m","9m","9m","9m","2m"]
        agari_hai = "2m" # 9面待ちではない和了牌
        # analyzerの解析結果を模倣
        analysis = {"type": "normal", "mentsu": [["1m","1m","1m"],["2m","3m","4m"],["5m","6m","7m"],["9m","9m","9m"]], "janto": "8m"} # 仮の分解
        
        # YakuJudgeのコンストラクタはhandを直接使うので、handを渡す
        judge = YakuJudge(analysis, [], {"is_menzen": True, "agari_hai": agari_hai})
        judge.hand = hand # YakuJudgeの内部handをテスト用に上書き
        
        result = judge.check_all_yaku()
        assert "九蓮宝燈" in result and result["九蓮宝燈"] == 13

    def test_kokushi_musou_normal(self):
        """国士無双（通常）のテスト"""
        # ヤオ九牌13種のうち1つが対子
        hand = ["1m","1m","9m","1p","9p","1s","9s","1z","2z","3z","4z","5z","6z","7z"]
        agari_hai = "9m"
        analysis = {"type": "kokushi", "janto": "1m", "mentsu": [hand]}
        context = {"is_menzen": True, "agari_hai": agari_hai}
        
        judge = YakuJudge(analysis, [], context)
        judge.hand = hand
        
        assert judge.check_all_yaku() == {"国士無双": 13}
        
    # --- ダブル役満のテスト ---
    # test/test_yaku.py に追記

    # --- ダブル役満級のテスト ---

    def test_suuankou_tanki(self):
        """四暗刻単騎待ちのテスト"""
        # セットアップ：4つの暗刻が完成しており、雀頭の単騎待ちで和了
        analysis = {
            "type": "normal",
            "mentsu": [
                ["2m", "2m", "2m"],
                ["4p", "4p", "4p"],
                ["6s", "6s", "6s"],
                ["8s", "8s", "8s"]
            ],
            "janto": "1z",
            "machi": "tanki" # 待ちの形が単騎
        }
        # 和了牌が雀頭を完成させている
        context = {"is_menzen": True, "is_tsumo": True, "agari_hai": "1z"}
        
        judge = YakuJudge(analysis, [], context)
        result = judge.check_all_yaku()
        assert result == {"四暗刻単騎": 26}

    def test_kokushi_musou_13_sided_wait(self):
        """国士無双13面待ちのテスト"""
        # セットアップ：ヤオ九牌13種が1枚ずつあり、13面待ち
        hand = ["1m","9m","1p","9p","1s","9s","1z","2z","3z","4z","5z","6z","7z"]
        agari_hai = "1z" # 13面のいずれかで和了
        full_hand = hand + [agari_hai]
        
        # analyzerの解析結果を模倣
        analysis = {"type": "kokushi", "janto": agari_hai}
        context = {"is_menzen": True, "agari_hai": agari_hai}
        
        judge = YakuJudge(analysis, [], context)
        judge.hand = full_hand # YakuJudgeの内部handをテスト用に上書き
        
        result = judge.check_all_yaku()
        assert result == {"国士無双13面待ち": 26}

    def test_junsei_kyuuren_poutou(self):
        """純正九蓮宝燈（9面待ち）のテスト"""
        # セットアップ：九蓮宝燈の聴牌形で、9面待ちのいずれかで和了
        # 最終形は「1112345678999」になる
        hand_before_win = ["1m","1m","1m","2m","3m","4m","5m","6m","7m","9m","9m","9m","9m"]
        agari_hai = "8m"
        full_hand = hand_before_win + [agari_hai]
        
        # analyzerの解析結果を模倣
        analysis = {"type": "normal", "mentsu": [], "janto": ""} # ダミー
        context = {"is_menzen": True, "agari_hai": agari_hai}
        
        judge = YakuJudge(analysis, [], context)
        judge.hand = full_hand # YakuJudgeの内部handをテスト用に上書き
        
        result = judge.check_all_yaku()
        assert result == {"純正九蓮宝燈": 26}