import collections
from helpers import Tile, Call

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
        self.machi = analysis["machi"]
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
        # ここに役判定のロジックを実装する
        # 例: yaku_dict['役名'] = 飜数.
        
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
        if (not self.context.get('is_menzen', False)) and \
            (self.machi == 'ryanmen') and\
            (self.janto not in self.yaochu_hai):
            return True
        return False
    
    def _is_iipeko(self) -> bool:
        """
        一盃口の判定を行う.
        
        Returns:
            bool: 一盃口が成立する場合はTrue, それ以外はFalse.
        """
        # 面前の確認.
        if self.context.get('is_menzen', False):
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
            if tile[0] in YAOCHUHAI:
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
    
    def _is_san_ankou(self) -> bool:
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
    
    def _is_san_kantsu(self) -> bool:
        """
        三槓子の判定を行う.
        
        Returns:
            bool: 三槓子が成立する場合はTrue, それ以外はFalse.
        """
        kantsu_list = self._get_kantsu()
        return len(kantsu_list) == 3
    
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
            shuntsu_groups[suit].append(tuple(sorted(shuntsu, key=Tile.sort_key)))
            
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
        for tile in self.hand:
            if tile not in YAOCHUHAI:
                return False
        return True