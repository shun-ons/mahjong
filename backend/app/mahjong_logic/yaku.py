import collections
from .helpers import Tile, Call

KAZEHAI = ['1z', '2z', '3z', '4z']
SANGENPAI = ['5z', '6z', '7z']
YAOCHUHAI = ['1m', '9m', '1p', '9p', '1s', '9s'] + KAZEHAI + SANGENPAI

class YakuJudge:
    """
    手牌と状況を受け取り, 成立する役を判定するクラス.
    """
    def __init__(self, analysis: dict, called_mentsu_list: list, context: dict):
        """
        役判定に必要な情報を初期化する.

        Args:
            analysis (dict)          : 手牌の分析結果.
            called_mentsu_list (list): 鳴き牌のリスト.
            context (dict)           : 役判定に必要なコンテキスト情報.
                                        (例: is_tsumo, is_riichi, is_ippatsu, etc.)
        """
        self.mentsu_list = analysis["mentsu"]
        self.janto = analysis["janto"]
        self.hand = [self.janto, self.janto] + sum(self.mentsu_list, [])
        self.type = analysis["type"]
        self.machi = analysis.get("machi", "ryanmen")
        self.called_mentsu_list = called_mentsu_list
        self.context = context
        
    def check_all_yaku(self) -> dict:
        """
        成立するすべての役を判定する.

        役の判定は、手牌、鳴き牌、和了牌、コンテキスト情報を基に行われる.
        判定された役は辞書形式で返される.

        Returns:
            dict: 役名と飜数の辞書.
        """
        yaku_dict = {}
        is_menzen = self.context.get('is_menzen', False)
        
        # 国士無双の判定.
        if self.type == 'kokushi':
            if self._is_kokushi_13men_machi():
                yaku_dict['国士無双13面待ち'] = 26
            else:
                yaku_dict['国士無双'] = 13
        
        # 七対子の判定.
        elif self.type == 'chitoitsu':
            # 字一色七対子は役満.
            if self._is_tuuiisou():
                yaku_dict['字一色'] = 13
            # 通常の七対子.
            yaku_dict['七対子'] = 2
            if self._is_riiti():
            # 複合役の判定.
                yaku_dict['立直'] = 1
            if self._is_ippatsu():
                yaku_dict['一発'] = 1
            if self._is_menzen_tsumo():
                yaku_dict['門前清自摸和'] = 1
            if self._is_tanyao():
                yaku_dict['断么九'] = 1
            if self._is_honroutou():
                yaku_dict['混老頭'] = 2
            if self._is_chinitsu():
                yaku_dict['清一色'] = 6
                
                
        # 通常の役の判定.
        else:
            # 役満の判定.
            if self._is_daisuushi():
                yaku_dict['大四喜'] = 26
                return yaku_dict
            normal, junsei = self._is_churenpoutou()
            if normal:
                if junsei:
                    yaku_dict['純正九蓮宝燈'] = 26
                    return yaku_dict
                yaku_dict['九蓮宝燈'] = 13
            normal, tanki = self._is_suuankou()
            if normal:
                if tanki:
                    yaku_dict['四暗刻単騎'] = 26
                    return yaku_dict
                yaku_dict['四暗刻'] = 13
            if self._is_daisangen():
                yaku_dict['大三元'] = 13
            if self._is_suukantsu():
                yaku_dict['四槓子'] = 13
            if self._is_ryuuiisou():
                yaku_dict['緑一色'] = 13
            if self._is_tuuiisou():
                yaku_dict['字一色'] = 13
            if self._is_chinroutou():
                yaku_dict['清老頭'] = 13
            if self._is_shousuushi():
                yaku_dict['小四喜'] = 13
            if self.context.get('is_tenhou', False):
                yaku_dict['天和'] = 13
                return yaku_dict
            if self.context.get('is_chiihou', False):
                yaku_dict['地和'] = 13
                return yaku_dict
            # 役満は役満以外の役と複合しないため、ここで終了.
            if len(yaku_dict) > 0:
                return yaku_dict
            
            #  通常の役の判定.
            if self._is_chinitsu():
                if is_menzen:
                    yaku_dict['清一色'] = 6
                else:
                    yaku_dict['清一色'] = 5
            elif self._is_honitsu():
                if is_menzen:
                    yaku_dict['混一色'] = 3
                else:
                    yaku_dict['混一色'] = 2
            if self._is_ryanpeiko():
                yaku_dict['二盃口'] = 3
            elif self._is_iipeko():
                yaku_dict['一盃口'] = 1
            if self._is_junchan():
                if is_menzen:
                    yaku_dict['純全帯么九'] = 3
                else:
                    yaku_dict['純全帯么九'] = 2
            elif self._is_chanta():
                if is_menzen:
                    yaku_dict['混全帯么九'] = 2
                else:
                    yaku_dict['混全帯么九'] = 1
            if self._is_ikkitsukan():
                if is_menzen:
                    yaku_dict['一気通貫'] = 2
                else:
                    yaku_dict['一気通貫'] = 1
            if self._is_sanshoku_doujun():
                if is_menzen:
                    yaku_dict['三色同順'] = 2
                else:
                    yaku_dict['三色同順'] = 1
            if self._is_honroutou():
                yaku_dict['混老頭'] = 2
            if self._is_shousangen():
                yaku_dict['小三元'] = 2
            if self._is_sankantsu():
                yaku_dict['三槓子'] = 2
            if self._is_toitoi():
                yaku_dict['対々和'] = 2
            if self._is_sanankou():
                yaku_dict['三暗刻'] = 2
            if self._is_sanshoku_doukou():
                yaku_dict['三色同刻'] = 2
            if self._is_double_riichi():
                yaku_dict['ダブル立直'] = 2
            if self._is_chankan():
                yaku_dict['槍槓'] = 1
            if self._is_rinshan():
                yaku_dict['嶺上開花'] = 1
            if self._is_haitei():
                yaku_dict['海底摸月'] = 1
            if self._is_houtei():
                yaku_dict['河底撈魚'] = 1
            if self._is_tanyao():
                yaku_dict['断么九'] = 1
            if self._is_jikaze():
                yaku_dict['自風'] = 1
            if self._is_bakaze():
                yaku_dict['場風'] = 1
            if self._is_haku():
                yaku_dict['白'] = 1
            if self._is_hatsu():
                yaku_dict['發'] = 1
            if self._is_chun():
                yaku_dict['中'] = 1

            if self._is_pinfu():
                yaku_dict['平和'] = 1
            if self._is_menzen_tsumo():
                yaku_dict['門前清自摸和'] = 1
            if self._is_ippatsu():
                yaku_dict['一発'] = 1
            if self._is_riiti():
                yaku_dict['立直'] = 1
            dora_count = self._is_dora()
            if dora_count > 0:
                yaku_dict['ドラ'] = dora_count
        return yaku_dict
            
        
    #-- 共通メソッド ---
    def _get_shuntsu_counts(self) -> collections.Counter:
        """
        面子の順子の枚数をカウントする関数.

        Returns:
            collections.Counter: 順子の牌の枚数をカウントしたCounterオブジェクト.
        """
        shuntsu_list = [mentsu for mentsu in self.mentsu_list if len(set(mentsu)) ==3]
        if len(shuntsu_list) <2:
            return collections.Counter()
        shuntsu_tuple = [tuple(sorted(shunstu)) for shunstu in shuntsu_list]
        return collections.Counter(shuntsu_tuple)
    
    def _get_shuntsu(self) -> list[str]:
        """
        面子の順子の牌のリストを取得する関数.
        
        Returns:
            list[str]: 順子の牌のリスト.
        """
        shuntsu_list = [mentsu for mentsu in self.mentsu_list if len(set(mentsu)) == 3]
        return shuntsu_list
    
    def _get_kotsu(self) -> list[str]:
        """
        面子の刻子の枚数をカウントする関数.
        
        Returns:
            list[str]: 刻子の牌のリスト.
        """
        kotsu_list = [mentsu[0] for mentsu in self.mentsu_list if len(set(mentsu)) == 1]
        return kotsu_list
    
    def _get_kantsu(self) -> list[str]:
        """
        面子の槓子の枚数をカウントする関数.
        
        Returns:
            list[str]: 槓子の牌のリスト.
        """
        kantsu_list = [mentsu[0] for mentsu in self.mentsu_list if len(set(mentsu)) == 4]
        return kantsu_list
    
    # --- 1飜役の判定メソッド ---
    def _is_riiti(self) -> bool:
        """
        立直の判定を行う.

        Returns:
            bool: 立直が成立する場合はTrue, それ以外はFalse.
        """
        return self.context.get('is_riichi', False)
    
    def _is_ippatsu(self) -> bool:
        """
        一発の判定を行う.
        
        Returns:
            bool: 一発が成立する場合はTrue, それ以外はFalse.
        """
        return self.context.get('is_ippatsu', False)
    
    def _is_dora(self) -> int:
        """
        ドラの枚数をカウントする関数.
        ドラ、赤ドラ、裏ドラの合計を返す.
        
        Returns:
            int: ドラ、赤ドラ、裏ドラの合計枚数.
        """
        dora = [d.strip() for d in self.context.get('dora_indicators', '').split(',') if not d.strip().isspace()]
        ura_dora = [u_d.strip() for u_d in self.context.get('ura_dora_indicators', '').split(',') if not u_d.strip().isspace()]
        akadora = ['5mr', '5pr', '5sr']  # 赤ドラの牌
        dora_list = dora + ura_dora + akadora
        dora_count = 0
        
        for tile in self.hand:
            if tile in dora_list:
                dora_count += 1
        return dora_count
    
    def _is_menzen_tsumo(self) -> bool:
        """
        門前清自摸和の判定を行う.
        
        Returns:
            bool: 門前清自摸和が成立する場合はTrue, それ以外はFalse.
        """
        return self.context.get('is_menzen', False) and self.context.get('is_tsumo', False)
    
    def _is_pinfu(self) -> bool:
        """
        平和の判定を行う.
        
        Returns:
            bool: 平和が成立する場合はTrue, それ以外はFalse.
        """
        # 平和は門前で、両面待ちで、雀頭が役牌でないことが条件
        if self.context.get('is_menzen', False) and \
            (self.machi == 'ryanmen') and\
            (self.janto not in YAOCHUHAI):
            return True
        return False
    
    def _is_iipeko(self) -> bool:
        """
        一盃口の判定を行う.
        
        Returns:
            bool: 一盃口が成立する場合はTrue, それ以外はFalse.
        """
        # 面前の確認.
        if not self.context.get('is_menzen', False):
            return False
        # 面子の順子の枚数をカウント.
        shuntsu_counts = self._get_shuntsu_counts()
        # 同じ順子が2つあるかを確認.
        return list(shuntsu_counts.values()).count(2) == 1
    
    def _is_jikaze(self) -> bool:
        """
        自風の判定を行う.
        
        Returns:
            bool: 自風が成立する場合はTrue, それ以外はFalse.
        """
        kotsu_list = self._get_kotsu()
        jikaze = self.context.get('jikaze', '')
        if jikaze in kotsu_list:
            return True
        return False
        
    def _is_bakaze(self) -> bool:
        """
        場風の判定を行う.
        
        Returns:
            bool: 場風が成立する場合はTrue, それ以外はFalse.
        """
        kotsu_list = self._get_kotsu()
        bakaze = self.context.get('bakaze', '')
        if bakaze in kotsu_list:
            return True
        return False
    
    def _is_haku(self) -> bool:
        """
        白の判定を行う.
        
        Returns:
            bool: 白が成立する場合はTrue, それ以外はFalse.
        """
        kotsu_list = self._get_kotsu()
        if '5z' in kotsu_list:  # 白は5zとして扱う
            return True
        return False
    
    def _is_hatsu(self) -> bool:
        """
        發の判定を行う.
        
        Returns:
            bool: 發が成立する場合はTrue, それ以外はFalse.
        """
        kotsu_list = self._get_kotsu()
        if '6z' in kotsu_list:  # 發は6zとして扱う
            return True
        return False
    
    def _is_chun(self) -> bool:
        """
        中の判定を行う.
        
        Returns:
            bool: 中が成立する場合はTrue, それ以外はFalse.
        """
        kotsu_list = self._get_kotsu()
        if '7z' in kotsu_list:  # 中は7zとして扱う
            return True
        return False
    
    def _is_tanyao(self) -> bool:
        """
        断么九の判定を行う.

        Returns:
            bool: 断么九が成立する場合はTrue, それ以外はFalse.
        """
        # 么九中牌が含まれていないかをチェック
        for tile in self.hand:
            if tile in YAOCHUHAI:
                return False
        return True
    
    def _is_haitei(self) -> bool:
        """
        海底摸月の判定を行う.
        
        Returns:
            bool: 海底摸月が成立する場合はTrue, それ以外はFalse.
        """
        return self.context.get('is_haitei', False)
    
    def _is_houtei(self) -> bool:
        """
        河底撈魚の判定を行う.
        
        Returns:
            bool: 河底撈魚が成立する場合はTrue, それ以外はFalse.
        """
        return self.context.get('is_houtei', False)
    
    def _is_rinshan(self) -> bool:
        """
        嶺上開花の判定を行う.
        
        Returns:
            bool: 嶺上開花が成立する場合はTrue, それ以外はFalse.
        """
        return self.context.get('is_rinshan', False)
    
    def _is_chankan(self) -> bool:
        """
        槍槓の判定を行う.
        
        Returns:
            bool: 槍槓が成立する場合はTrue, それ以外はFalse.
        """
        return self.context.get('is_chankan', False)
    
    # -- 2飜役の判定メソッド ---
    def _is_double_riichi(self) -> bool:
        """
        ダブル立直の判定を行う.

        Returns:
            bool: ダブル立直が成立する場合はTrue, それ以外はFalse.
        """
        return self.context.get('is_double_riichi', False)
    
    def _is_sanshoku_doukou(self) -> bool:
        """
        三色同刻の判定を行う.
        
        Returns:
            bool: 三色同刻が成立する場合はTrue, それ以外はFalse.
        """
        # 面子の刻子の枚数をカウント.
        kotsu_list = self._get_kotsu()
        # 3種類の刻子がそれぞれ1枚ずつあるかを確認.
        if len(kotsu_list) < 3:
            return False
        # 三色同刻の条件を満たすかを確認.
        number_kotsu = collections.defaultdict(set)
        for tile in kotsu_list:
            number = tile[0]
            suit = tile[1]
            if suit != 'z':  # 字牌は除外
                number_kotsu[number].add(suit)
        # 3種類の牌がそれぞれ1枚ずつあるかを確認.
        for suits in number_kotsu.values():
            if len(suits) == 3:
                return True
        return False
    
    def _is_sanankou(self) -> bool:
        """
        三暗刻の判定を行う.
        
        Returns:
            bool: 三暗刻が成立する場合はTrue, それ以外はFalse.
        """
        ankou_count = 0
        called_mentsu_tuples = [tuple(sorted(called_mentsu.tiles)) for called_mentsu in self.called_mentsu_list]
        
        # 面子の刻子をチェック.
        for mentsu in self.mentsu_list:
            # 刻子でなければスキップ
            if len(set(mentsu)) != 1:
                continue
            is_ankou = True
            # 鳴いた面子（ポンなど）は暗刻ではない
            if tuple(sorted(mentsu)) in called_mentsu_tuples:
                is_ankou = False
            # ロン和了りで、和了牌がこの刻子を完成させた場合も暗刻ではない
            is_ron = not self.context.get('is_tsumo', False)
            if is_ron and self.context.get('agari_hai') in mentsu:
                is_ankou = False
            if is_ankou:
                ankou_count += 1
        return ankou_count == 3
    
    def _is_toitoi(self) -> bool:
        """
        対々和の判定を行う.
        
        Returns:
            bool: 対々和が成立する場合はTrue, それ以外はFalse.
        """
        # 面子の刻子の枚数をカウント.
        kotsu_list = self._get_kotsu()
        # 面子の順子の枚数をカウント.
        kantsu_list = self._get_kantsu()
        # 刻子が4つ以上、順子が0つであれば対々和
        return (len(kotsu_list) + len(kantsu_list)) == 4
    
    def _is_sankantsu(self) -> bool:
        """
        三槓子の判定を行う.
        
        Returns:
            bool: 三槓子が成立する場合はTrue, それ以外はFalse.
        """
        kantsu_count = 0
        for mentsu in self.mentsu_list:
            if len(mentsu) == 4:
                kantsu_count += 1
        return kantsu_count == 3
    
    def _is_shousangen(self) -> bool:
        """
        小三元の判定を行う.
        
        Returns:
            bool: 小三元が成立する場合はTrue, それ以外はFalse.
        """
        # 雀頭が三元牌であることを確認.
        if  not self.janto or self.janto not in SANGENPAI:
            return False
        # 三元牌の刻子の枚数をカウント.
        kotsu_list = self._get_kotsu()
        sangenpai_list = [tile for tile in kotsu_list if tile in SANGENPAI]
        sangenpai_list.append(self.janto)  # 雀頭も含める
        # 小三元は、3種類の三元牌のうち2種類が刻子であることを確認.
        return len(set(sangenpai_list)) == 3
    
    def _is_honroutou(self) -> bool:
        """
        混老頭の判定を行う.
        
        Returns:
            bool: 混老頭が成立する場合はTrue, それ以外はFalse.
        """
        # 么九中牌が含まれているかをチェック
        for tile in self.hand:
            if tile not in YAOCHUHAI:
                return False
        # 刻子の枚数をカウント.
        return True
    
    def _is_sanshoku_doujun(self) -> bool:
        """
        三色同順の判定を行う.
        
        Returns:
            bool: 三色同順が成立する場合はTrue, それ以外はFalse.
        """
        shuntsu_list = self._get_shuntsu()
        if len(shuntsu_list) < 3:
            return False
        
        shuntsu_groups = collections.defaultdict(set)
        for shuntsu in shuntsu_list:
            # 順子をソートして、開始牌を特定 (例: '1m')
            start_tile = sorted(shuntsu, key=Tile.sort_key)[0]
            number = start_tile[0] # 数字部分 (例: '1')
            suit = start_tile[1]   # 種類部分 (例: 'm')
            shuntsu_groups[number].add(suit)
            
        # 3種類の面子が揃っているグループがあるか確認
        for suits in shuntsu_groups.values():
            # グループにマンズ('m'), ピンズ('p'), ソーズ('s')の3種類が揃っていれば成立
            if len(suits) == 3:
                return True
        # どのグループも条件を満たさなければ不成立
        return False
    
    def _is_ikkitsukan(self) -> bool:
        """
        一気通貫の判定を行う.
        
        Returns:
            bool: 一気通貫が成立する場合はTrue, それ以外はFalse.
        """
        shuntsu_list = self._get_shuntsu()
        if len(shuntsu_list) < 3:
            return False
        
        # 面子の順子の数字部分を抽出
        shuntsu_groups = collections.defaultdict(set)
        for shuntsu in shuntsu_list:
            suit = shuntsu[0][1]  # 種類部分 (例: 'm')
            shuntsu_groups[suit].add(tuple(sorted(shuntsu, key=Tile.sort_key)))
            
        for suit, shuntsu_in_suit in shuntsu_groups.items():
            if suit == 'z':
                continue  # 字牌は除外
            
            # その種類の順子のセットを作成.
            shuntsu_set = set(shuntsu_in_suit)
            # 一気通貫の順子のセットを定義.
            target_shuntsu = {
                (f"1{suit}", f"2{suit}", f"3{suit}"),
                (f"4{suit}", f"5{suit}", f"6{suit}"),
                (f"7{suit}", f"8{suit}", f"9{suit}"),
            }
            # 一気通貫の順子が存在するか確認.
            if target_shuntsu.issubset(shuntsu_set):
                return True
        return False
            
    def _is_chanta(self) -> bool:
        """
        混全帯么九の判定を行う.
        
        Returns:
            bool: 混全帯么九が成立する場合はTrue, それ以外はFalse.
        """
        # 么九中牌が含まれているかをチェック
        if self.janto not in YAOCHUHAI:
            return False
        for mentsu in self.mentsu_list:
            yaochuhai_count = 0
            for tile in mentsu:
                if tile in YAOCHUHAI:
                    yaochuhai_count += 1
            # 面子に么九中牌が1枚以上含まれているかを確認
            if yaochuhai_count == 0:
                return False
        return True
    
    # -- 3飜役の判定メソッド ---
    def _is_ryanpeiko(self) -> bool:
        """
        二盃口の判定を行う.
        
        Returns:
            bool: 二盃口が成立する場合はTrue, それ以外はFalse.
        """
        if not self.context.get('is_menzen', False):
            return False
        # 面子の順子の枚数をカウント.
        shuntsu_counts = self._get_shuntsu_counts()
        # 同じ順子が4つあるかを確認.
        counts_value = list(shuntsu_counts.values())
        return counts_value.count(2) == 2 or 4 in counts_value
    
    def _is_junchan(self) -> bool:
        """
        純全帯么九の判定を行う.
        
        Returns:
            bool: 純全帯么九が成立する場合はTrue, それ以外はFalse.
        """
        if not self._is_chanta():
            return False
        for tile in self.hand:
            if tile[1] == 'z':
                return False
        return True
    
    def _is_honitsu(self) -> bool:
        """
        混一色の判定を行う.
        
        Returns:
            bool: 混一色が成立する場合はTrue, それ以外はFalse.
        """
        suit = ''
        for tile in self.hand:
            if tile[1] == 'z':
                continue
            if len(suit) == 0:
                suit = tile[1]
            elif suit != tile[1]:
                return False
        return True
    
    # --6飜役の判定メソッド ---
    def _is_chinitsu(self) -> bool:
        """
        清一色の判定を行う.
        
        Returns:
            bool: 清一色が成立する場合はTrue, それ以外はFalse.
        """
        suit = ''
        for tile in self.hand:
            if tile[1] == 'z':
                False
            if len(suit) == 0:
                suit = tile[1]
            elif suit != tile[1]:
                return False
        return True
    
    # --役満の判定メソッド ---
    def _is_daisangen(self) -> bool:
        """
        大三元の判定を行う.
        
        Returns:
            bool: 大三元が成立する場合はTrue, それ以外はFalse.
        """
        # 三元牌の刻子の枚数をカウント.
        kotsu_list = self._get_kotsu()
        kantsu_list = self._get_kantsu()
        # 三元牌の刻子と槓子を合わせてカウント.
        sangenpai_count = sum(1 for tile in kotsu_list + kantsu_list if tile in SANGENPAI)
        # 大三元は、3種類の三元牌がすべて刻子であることを確認.
        return sangenpai_count == 3
    
    def _is_suuankou(self) -> tuple[bool, bool]:
        """
        四暗刻の判定を行う.
        
        Returns:
            tuple[bool, bool]: (四暗刻が成立するか、四暗刻単騎が成立するか).
        """
        if not self.context.get('is_menzen', False):
            return False, False
        ankou_count = 0
        called_mentsu_tuples = [tuple(sorted(called_mentsu.tiles)) for called_mentsu in self.called_mentsu_list]
        
        # 面子の刻子をチェック.
        for mentsu in self.mentsu_list:
            # 刻子でなければスキップ
            if len(set(mentsu)) != 1:
                continue
            is_ankou = True
            # 鳴いた面子（ポンなど）は暗刻ではない
            if tuple(sorted(mentsu)) in called_mentsu_tuples:
                is_ankou = False
            # ロン和了りで、和了牌がこの刻子を完成させた場合も暗刻ではない
            is_ron = not self.context.get('is_tsumo', False)
            if is_ron and self.context.get('agari_hai') in mentsu:
                is_ankou = False
            if is_ankou:
                ankou_count += 1
        # 四暗刻は、暗刻が4つあることを確認.
        return ankou_count == 4, self.machi == 'tankii'
    
    def _is_suukantsu(self) -> bool:
        """
        四槓子の判定を行う.
        
        Returns:
            bool: 四槓子が成立する場合はTrue, それ以外はFalse.
        """
        kantsu_count = 0
        for mentsu in self.mentsu_list:
            if len(mentsu) == 4:
                kantsu_count += 1
        # 四槓子は、槓子が4つあることを確認.
        return kantsu_count == 4

    def _is_ryuuiisou(self) -> bool:
        """
        緑一色の判定を行う.
        
        Returns:
            bool: 緑一色が成立する場合はTrue, それ以外はFalse.
        """
        green_tiles = ['2s', '3s', '4s', '6s', '8s', '9s', '6z']
        for tile in self.hand:
            if tile not in green_tiles:
                return False
        return True
    
    def _is_tuuiisou(self) -> bool:
        """
        字一色の判定を行う.
        
        Returns:
            bool: 字一色が成立する場合はTrue, それ以外はFalse.
        """
        for tile in self.hand:
            if tile[1] != 'z':
                return False
        return True
    
    def _is_chinroutou(self) -> bool:
        """
        清老頭の判定を行う.
        
        Returns:
            bool: 清老頭が成立する場合はTrue, それ以外はFalse.
        """
        # 么九中牌が含まれているかをチェック
        chinroutou_tiles = {"1m", "9m", "1p", "9p", "1s", "9s"}
        for tile in self.hand:
            if tile not in chinroutou_tiles:
                return False
        return True
    
    def _is_shousuushi(self) -> bool:
        """
        小四喜の判定を行う.
        
        Returns:
            bool: 小四喜が成立する場合はTrue, それ以外はFalse.
        """
        # 雀頭が風牌であることを確認.
        if not self.janto or self.janto not in KAZEHAI:
            return False
        # 風牌の刻子の枚数をカウント.
        kotsu_list = self._get_kotsu()
        kantsu_list = self._get_kantsu()
        kazehai_count = sum(1 for tile in kotsu_list + kantsu_list if tile in KAZEHAI)
        # 小四喜は、4種類の風牌のうち3種類が刻子であることを確認.
        return kazehai_count == 3
    
    def _is_churenpoutou(self) -> tuple[bool, bool]:
        """
        九蓮宝燈の判定を行う.
        
        Returns:
            tuple[bool, bool]: (九蓮宝燈が成立するか、純正九蓮宝燈が成立するか).
        """
        if not self.context.get('is_menzen', False):
            return False, False
        # 面子の順子の枚数をカウント.
        suit = self.hand[0][1]  # 全ての牌が同じ種類であることを確認
        if suit == 'z':
            return False, False
        if not all(tile[1] == suit for tile in self.hand):
            return False, False
        # 基本形の確認(1,1,1,2,3,4,5,6,7,8,9,9,9)
        number_counts = collections.Counter(tile[0] for tile in self.hand)
        is_kyuuren_shape = True
        if number_counts.get('1', 0) < 3 or number_counts.get('9', 0) < 3:
            is_kyuuren_shape = False
        for i in range(2, 9):
            if number_counts.get(str(i), 0) < 1:
                is_kyuuren_shape = False
        if not is_kyuuren_shape:
            return False, False
        
        # 九蓮宝燈の基本形が成立している場合、純正九蓮宝燈を確認
        hand_before_win =self.hand[:]
        hand_before_win.remove(self.context.get('agari_hai'))  # 雀頭を除外
        is_junsei = True
        tenpai_counts = collections.Counter(tile[0] for tile in hand_before_win)
        # 純正九蓮宝燈は、1と9が2枚ずつ必要
        if tenpai_counts.get('1', 0) != 2 or tenpai_counts.get('9', 0) != 2:
            is_junsei = False
        # 2から8までの牌が1枚ずつ必要
        for i in range(2, 9):
            if tenpai_counts.get(str(i), 0) != 1:
                is_junsei = False
        
        return True, is_junsei
    
    def _is_daisuushi(self) -> bool:
        """
        大四喜の判定を行う.
        
        Returns:
            bool: 大四喜が成立する場合はTrue, それ以外はFalse.
        """
        kotsu_list = self._get_kotsu()
        kantsu_list = self._get_kantsu()
        kazehai_count = sum(1 for tile in kotsu_list + kantsu_list if tile in KAZEHAI)
        # 大四喜は、4種類の風牌がすべて刻子であることを確認.
        return kazehai_count == 4
    
    def _is_kokushi_13men_machi(self) -> bool:
        """
        国士無双の13面待ちの判定を行う.
        
        Returns:
            bool: 国士無双の13面待ちが成立する場合はTrue, それ以外はFalse.
        """
        hand_before_win = self.hand[:]
        hand_before_win.remove(self.context.get('agari_hai'))
        # 国士無双の13面待ちは、13種類の么九中牌がすべて含まれていることを確認
        for tile in YAOCHUHAI:
            if tile not in hand_before_win:
                return False
        # 13種類の牌がすべて含まれていることを確認
        return len(set(hand_before_win)) == 13