import collections
from itertools import combinations

# 牌の定義
# 萬子: 1m-9m, 筒子: 1p-9p, 索子: 1s-9s, 字牌: 1z-7z (東南西北白發中)
# 赤ドラ: 5mr, 5pr, 5sr
TILES = {
    'm': [f'{i}m' for i in range(1, 10)],
    'p': [f'{i}p' for i in range(1, 10)],
    's': [f'{i}s' for i in range(1, 10)],
    'z': [f'{i}z' for i in range(1, 8)],
}
ALL_TILES = sum(TILES.values(), [])
YAOCHUHAI = {"1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"}

class Tile:
    """牌の情報を扱うヘルパークラス"""
    @staticmethod
    def sort_key(tile):
        _tile = tile.replace('r', '')
        suit = 'mpsz'.index(_tile[-1])
        num = int(_tile[:-1])
        return suit * 10 + num

    @staticmethod
    def to_normal(tile):
        return tile.replace('r', '')

    @staticmethod
    def is_yaochu(tile):
        return Tile.to_normal(tile) in YAOCHUHAI

    @staticmethod
    def is_jihai(tile):
        return tile[-1] == 'z'

    @staticmethod
    def next_tile(tile):
        """ドラ表示牌からドラを計算するための関数"""
        tile = Tile.to_normal(tile)
        if not tile in ALL_TILES: return None
        
        suit = tile[-1]
        num = int(tile[:-1])
        
        if suit in 'mps':
            return f"{num % 9 + 1}{suit}"
        if suit == 'z':
            if 1 <= num <= 3: return f"{num + 1}z"
            if num == 4: return "1z"
            if 5 <= num <= 6: return f"{num + 1}z"
            if num == 7: return "5z"
        return None

class Meld:
    """鳴き（面子）の情報を扱うクラス"""
    def __init__(self, meld_type, tiles):
        self.meld_type = meld_type  # "pon", "chi", "minkan", "ankan", "kakan"
        self.tiles = sorted(tiles, key=Tile.sort_key)
        self.is_open = meld_type != "ankan"

    def is_kotsu(self):
        return self.meld_type in ["pon", "minkan", "ankan", "kakan"]

    def is_shuntsu(self):
        return self.meld_type == "chi"

    def get_fu(self):
        base_fu = 0
        is_yaochu = Tile.is_yaochu(self.tiles[0])
        if self.meld_type in ["pon", "chi"]:
            base_fu = 2 if self.is_kotsu() else 0
            if not self.is_open: base_fu *= 2 # 暗刻の場合
            if is_yaochu: base_fu *= 2
        elif self.meld_type in ["minkan", "ankan", "kakan"]:
            base_fu = 8
            if not self.is_open: base_fu *= 2 # 暗槓の場合
            if is_yaochu: base_fu *= 2
        return base_fu

class HandAnalysis:
    """手牌の解析（面子分解、待ちの形特定）を行うクラス"""
    def __init__(self, hand, melds, agari_hai):
        self.hand = sorted(hand, key=Tile.sort_key)
        self.melds = melds
        self.agari_hai = agari_hai
        self.agari_combinations = self._analyze()

    def _find_combinations(self, hand_counter):
        if not hand_counter:
            return [[]]
        
        tile = next(iter(hand_counter))
        count = hand_counter[tile]
        
        results = []
        
        # 刻子として取り出す
        if count >= 3:
            hand_counter[tile] -= 3
            if not hand_counter[tile]: del hand_counter[tile]
            
            sub_results = self._find_combinations(hand_counter.copy())
            for res in sub_results:
                results.append([[tile, tile, tile]] + res)

            hand_counter[tile] += 3

        # 順子として取り出す
        suit = tile[-1]
        if suit != 'z' and count > 0:
            num = int(tile[:-1])
            t1, t2, t3 = f"{num}{suit}", f"{num+1}{suit}", f"{num+2}{suit}"
            if t2 in hand_counter and t3 in hand_counter:
                hand_counter[t1] -= 1
                hand_counter[t2] -= 1
                hand_counter[t3] -= 1

                for t in [t1, t2, t3]:
                    if not hand_counter[t]: del hand_counter[t]

                sub_results = self._find_combinations(hand_counter.copy())
                for res in sub_results:
                    results.append([[t1, t2, t3]] + res)
                
                for t in [t1, t2, t3]:
                    hand_counter[t] = hand_counter.get(t, 0) + 1

        return results
    
    def _analyze(self):
        # 国士無双と七対子のチェック
        counts = collections.Counter(self.hand)
        if len(self.melds) == 0:
            if all(t in counts for t in YAOCHUHAI) and len(counts) == 14:
                return [{"type": "kokushi", "janto": self.agari_hai, "mentsu": []}]
            if len(counts) == 7 and all(c == 2 for c in counts.values()):
                machi_type = "tanki" # 七対子は単騎待ち
                return [{"type": "chitoi", "janto": None, "mentsu": list(counts.keys()), "machi": machi_type}]

        # 4面子1雀頭の解析
        open_mentsu = [m.tiles for m in self.melds]
        closed_hand = [t for t in self.hand if t not in sum(open_mentsu, [])]
        
        results = []
        
        # 雀頭の候補を探す
        unique_tiles = sorted(list(set(closed_hand)), key=Tile.sort_key)
        for janto_candidate in unique_tiles:
            if closed_hand.count(janto_candidate) >= 2:
                temp_hand = closed_hand[:]
                temp_hand.remove(janto_candidate)
                temp_hand.remove(janto_candidate)
                
                combinations = self._find_combinations(collections.Counter(temp_hand))
                
                for combo in combinations:
                    # 待ちの形を判定
                    agari_mentsu = []
                    is_agari_in_janto = self.agari_hai == janto_candidate
                    for m in combo:
                        if self.agari_hai in m:
                            agari_mentsu.append(m)

                    if not agari_mentsu and not is_agari_in_janto:
                        continue # アガリ牌が手牌にないのはおかしい

                    machi = self._get_machi_type(agari_mentsu[0] if agari_mentsu else [], janto_candidate, is_agari_in_janto)
                    
                    results.append({
                        "type": "normal",
                        "janto": janto_candidate,
                        "mentsu": combo + open_mentsu,
                        "machi": machi
                    })
        return results

    def _get_machi_type(self, mentsu, janto, is_agari_in_janto):
        if is_agari_in_janto:
            return "tanki" # 雀頭待ち

        is_shuntsu = len(set(mentsu)) > 1
        agari_normal = Tile.to_normal(self.agari_hai)
        
        if is_shuntsu:
            sorted_mentsu = sorted([Tile.to_normal(t) for t in mentsu], key=Tile.sort_key)
            if sorted_mentsu[1] == agari_normal: return "kanchan"
            if (int(sorted_mentsu[0][:-1]) == 1 and agari_normal == sorted_mentsu[2]) or \
               (int(sorted_mentsu[0][:-1]) == 7 and agari_normal == sorted_mentsu[0]):
                return "penchan"
            return "ryanmen"
        else: # 刻子
            return "shanpon"

class MahjongScorer:
    def __init__(self, hand, melds, agari_hai, is_tsumo, is_oya,
                 dora_indicators, ura_dora_indicators=[],
                 bakaze="1z", jikaze="1z",
                 is_reach=False, is_daburi=False, is_ippatsu=False,
                 is_rinshan=False, is_haitei=False):
        
        # 手牌情報
        self.hand = hand
        self.melds = melds
        self.agari_hai = agari_hai
        self.is_tsumo = is_tsumo
        self.is_menzen = len(melds) == 0
        
        # 状況
        self.is_oya = is_oya
        self.bakaze = bakaze
        self.jikaze = jikaze
        
        # 役フラグ
        self.is_reach = is_reach
        self.is_daburi = is_daburi
        self.is_ippatsu = is_ippatsu
        self.is_rinshan = is_rinshan
        self.is_haitei = is_haitei
        
        # ドラ
        self.dora_indicators = dora_indicators
        self.ura_dora_indicators = ura_dora_indicators
        
        self.analysis_results = HandAnalysis(hand, melds, agari_hai).agari_combinations
        
    def calculate(self):
        best_score = {"score": 0, "han": 0, "fu": 0}
        
        if not self.analysis_results:
            return {"error": "アガリ形ではありません。"}
            
        for analysis in self.analysis_results:
            yaku, han, fu = self._calculate_yaku_fu_han(analysis)
            
            dora_count = self._count_dora()
            han += dora_count['total']
            
            if dora_count['dora'] > 0: yaku['ドラ'] = dora_count['dora']
            if dora_count['akadora'] > 0: yaku['赤ドラ'] = dora_count['akadora']
            if dora_count['uradora'] > 0: yaku['裏ドラ'] = dora_count['uradora']
            
            final_score, score_name = self._get_final_score(han, fu)
            
            if final_score['total'] > best_score['score']:
                best_score = {
                    "yaku": yaku,
                    "han": han,
                    "fu": fu,
                    "score_name": score_name,
                    "score": final_score['total'],
                    "payment": final_score
                }
        
        return best_score

    def _calculate_yaku_fu_han(self, analysis):
        yaku, han = {}, 0
        
        # 役満判定
        yaku, han = self._check_yakuman(analysis)
        if han > 0:
            return yaku, han * (han // 13), 0 # 複合役満

        # 通常役判定
        yaku, han = self._check_normal_yaku(analysis)
        if han == 0: return {}, 0, 0
        
        # 符計算
        fu = self._calculate_fu(analysis, yaku)
        
        return yaku, han, fu

    def _check_yakuman(self, analysis):
        yaku, han = {}, 0
        
        # 国士無双
        if analysis['type'] == 'kokushi':
            # 13面待ちの場合はダブル役満とするルールもあるが、ここではシングル
            yaku['国士無双'] = 13
            han += 13
        
        # 四暗刻
        if self.is_menzen and analysis['type'] == 'normal':
            ankou_count = sum(1 for m in analysis['mentsu'] if len(set(m)) == 1)
            if ankou_count == 4:
                # 単騎待ちならダブル役満
                han_val = 26 if analysis['machi'] == 'tanki' else 13
                yaku['四暗刻'] = han_val
                han += han_val
        
        # 大三元
        sangenpai_kotsu = 0
        for m in analysis['mentsu'] + [m.tiles for m in self.melds]:
            if m[0] in ["5z", "6z", "7z"] and len(set(m)) == 1:
                sangenpai_kotsu += 1
        if sangenpai_kotsu == 3:
            yaku['大三元'] = 13
            han += 13

        # ... 他の役満（緑一色、字一色、清老頭など）の判定ロジック ...
        
        return yaku, han

    def _check_normal_yaku(self, analysis):
        yaku, han = {}, 0
        
        # リーチ系
        if self.is_reach: yaku['リーチ'] = 1
        if self.is_daburi: yaku['ダブルリーチ'] = 2; yaku.pop('リーチ', None) # ダブルリーチはリーチと複合しない
        if self.is_ippatsu: yaku['一発'] = 1
        
        # 偶然役
        if self.is_rinshan: yaku['嶺上開花'] = 1
        if self.is_haitei: yaku['海底撈月' if self.is_tsumo else '河底撈魚'] = 1
        
        if self.is_menzen and self.is_tsumo: yaku['門前清自摸和'] = 1

        # 手牌構成による役
        if analysis['type'] == 'chitoi':
            yaku['七対子'] = 2
        elif analysis['type'] == 'normal':
            # 平和 (Pinfu)
            if self.is_menzen and not self._get_mentsu_fu(analysis) and \
               not self._get_janto_fu(analysis['janto']) and analysis['machi'] == 'ryanmen':
                yaku['平和'] = 1
            
            # 断么九 (Tanyao)
            is_tanyao = all(not Tile.is_yaochu(t) for t in self.hand)
            if is_tanyao: yaku['断么九'] = 1
            
            # 役牌 (Yakuhai)
            for m in analysis['mentsu'] + [m.tiles for m in self.melds]:
                if len(set(m)) > 1: continue
                tile = m[0]
                if tile == self.bakaze: yaku['役牌(場風)'] = yaku.get('役牌(場風)', 0) + 1
                if tile == self.jikaze: yaku['役牌(自風)'] = yaku.get('役牌(自風)', 0) + 1
                if tile in ['5z', '6z', '7z']: yaku[f'役牌({ { "5z":"白", "6z":"發", "7z":"中"}[tile] })'] = 1
            
            # ... 他の役（一盃口、三色同順、混一色など）の判定 ...
        
        # 喰い下がりを考慮しつつ翻数を計算
        final_han = 0
        for name, h in yaku.items():
            final_han += h
        
        return yaku, final_han
    
    def _calculate_fu(self, analysis, yaku):
        if '七対子' in yaku:
            return 25

        # 平和ツモは20符, 平和ロンは30符
        if '平和' in yaku:
            return 20 if self.is_tsumo else 30
        
        # 副底
        fu = 20
        
        # アガリ方
        if self.is_menzen and not self.is_tsumo: fu += 10 # 門前ロン
        if self.is_tsumo: fu += 2 # ツモ符
            
        # 雀頭
        fu += self._get_janto_fu(analysis['janto'])
        
        # 面子
        fu += self._get_mentsu_fu(analysis)
        
        # 待ち
        if analysis['machi'] in ['kanchan', 'penchan', 'tanki']:
            fu += 2
            
        # 喰い平和形の例外
        if not self.is_menzen and fu == 20:
            return 30
        
        # 切り上げ
        return -(-fu // 10) * 10
    
    def _get_janto_fu(self, janto_tile):
        fu = 0
        if janto_tile == self.bakaze: fu += 2
        if janto_tile == self.jikaze: fu += 2
        # 連風牌
        if self.bakaze == self.jikaze and janto_tile == self.bakaze: fu = 4
        if janto_tile in ["5z", "6z", "7z"]: fu = 2
        return fu

    def _get_mentsu_fu(self, analysis):
        fu = 0
        # 手牌中の面子
        for m in analysis['mentsu']:
            is_shuntsu = len(set(m)) > 1
            if is_shuntsu: continue
            
            kotsu_fu = 4 # 暗刻
            if Tile.is_yaochu(m[0]): kotsu_fu *= 2
            fu += kotsu_fu

        # 副露面子
        for m in self.melds:
            fu += m.get_fu()
            
        return fu

    def _count_dora(self):
        dora = [Tile.next_tile(t) for t in self.dora_indicators]
        uradora = [Tile.next_tile(t) for t in self.ura_dora_indicators] if self.is_reach else []
        
        all_hand_tiles = self.hand + sum([m.tiles for m in self.melds], [])
        
        dora_count = 0
        akadora_count = 0
        uradora_count = 0

        for tile in all_hand_tiles:
            if Tile.to_normal(tile) in dora:
                dora_count += 1
            if tile in ['5mr', '5pr', '5sr']:
                akadora_count += 1
            if self.is_menzen and Tile.to_normal(tile) in uradora: # 裏ドラは面前リーチのみ
                uradora_count += 1
        
        return {
            "dora": dora_count, "akadora": akadora_count, "uradora": uradora_count,
            "total": dora_count + akadora_count + uradora_count
        }

    def _get_final_score(self, han, fu):
        if han == 0: return {"total": 0, "oya": 0, "ko": 0}, ""

        if han >= 13: score_name, base_p = "数え役満", 8000
        elif han >= 11: score_name, base_p = "三倍満", 6000
        elif han >= 8: score_name, base_p = "倍満", 4000
        elif han >= 6: score_name, base_p = "跳満", 3000
        elif han >= 5: score_name, base_p = "満貫", 2000
        else:
            score_name = f"{han}翻{fu}符"
            base_p = fu * (2 ** (han + 2))
            if base_p > 2000: base_p = 2000

        if self.is_oya:
            if self.is_tsumo:
                ko_pay = -(-base_p * 2 // 100) * 100
                return {"total": ko_pay * 3, "payment_per_ko": ko_pay}, score_name
            else: # ロン
                ron_pay = -(-base_p * 6 // 100) * 100
                return {"total": ron_pay, "payment_from_ron": ron_pay}, score_name
        else: # 子
            if self.is_tsumo:
                oya_pay = -(-base_p * 2 // 100) * 100
                ko_pay = -(-base_p * 1 // 100) * 100
                return {"total": oya_pay + ko_pay * 2, "payment_from_oya": oya_pay, "payment_per_ko": ko_pay}, score_name
            else: # ロン
                ron_pay = -(-base_p * 4 // 100) * 100
                return {"total": ron_pay, "payment_from_ron": ron_pay}, score_name