import pytest

# --- Pythonのimportパスを通すための設定 ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -----------------------------------------

from app.mahjong_logic.scorer import MahjongScorer
from app.mahjong_logic.helpers import Call

class TestMahjongScorer:
    def test_riichi_tsumo_pinfu_dora1(self):
        """リーチ・ツモ・平和・ドラ1 (子) のケース"""
        # 手牌: 123m 456p 567s 22s + 4s(ツモ)
        hand = ["1m","2m","3m","4p","5p","6p","5s","6s","7s","2s","2s","2s","3s"]
        agari_hai = "4s"
        full_hand = hand + [agari_hai]
        
        game_state = {
            "is_tsumo": True,
            "is_menzen": True,
            "is_oya": False,
            "is_riichi": True,
            "dora_indicators": "3s",
            "bakaze": "1z",
            "jikaze": "2z",
        }
        
        scorer = MahjongScorer(full_hand, [], agari_hai, **game_state)
        result = scorer.calculate()
        
        # リーチ(1) + ツモ(1) + 平和(1) + ドラ1(4s) = 4飜
        # 4飜20符 -> 子のツモ和了は 1300/2600
        assert result["han"] == 4
        assert result["fu"] == 20
        assert "立直" in result["yaku"]
        assert "門前清自摸和" in result["yaku"]
        assert "平和" in result["yaku"]
        assert "ドラ" in result["yaku"]
        assert result["score"]["total"] == 5200 # 1300*2 + 2600
        assert result["score"]["payment_from_oya"] == 2600
        assert result["score"]["payment_per_ko"] == 1300

    def test_yakuhai_only_open_hand(self):
        """役牌のみ（鳴きあり・親）のケース"""
        # 手牌: 5z(白)ポン, 234m, 567p, 88s + 666s
        hand = ["2m","3m","4m","5p","6p","7p","8s","8s","6s","6s", "5z", "5z", "5z"]
        agari_hai = "6s"
        full_hand = hand + [agari_hai]
        
        called_mentsu = [Call("pon", ["5z", "5z", "5z"])]
        game_state = {
            "is_tsumo": False, # ロン
            "is_oya": True,    # 親
        }
        
        scorer = MahjongScorer(full_hand, called_mentsu, agari_hai, **game_state)
        result = scorer.calculate()
        
        # 白(1飜)のみ
        # 1飜30符 -> 親のロン和了は 1500点
        assert result["han"] == 1
        assert result["fu"] == 30
        assert result["yaku"] == {"白": 1}
        assert result["score"]["total"] == 1500

    def test_mangan(self):
        """満貫のケース"""
        # 混一色(2) + 役牌(1) + ドラ1 = 4飜
        hand = ["1m","2m","3m","4m","5m","6m","1z","1z","1z","5z","5z", "9m", "9m"]
        agari_hai = "5z"
        full_hand = hand + [agari_hai]
        
        called_mentsu = [Call("pon", ["1z", "1z", "1z"])]
        game_state = {
            "is_tsumo": True,
            "is_oya": False, # 子
            "dora_indicators": "1m", # ドラは1m
            "bakaze": "2z",
            "jikaze": "2z",
        }

        scorer = MahjongScorer(full_hand, called_mentsu, agari_hai, **game_state)
        result = scorer.calculate()

        # 混一色(2) + 役牌:東(1) + ドラ:白(1) = 4飜40符 -> 満貫切り上げ
        assert result["han"] == 4
        assert result["fu"] == 40 # 満貫なので符は実質無関係
        assert result["score_name"] == "満貫"
        assert result["score"]["total"] == 8000