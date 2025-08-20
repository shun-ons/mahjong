from .helpers import Tile, Call


def calculate_call_fu(call: Call) -> int:
    """
    鳴き面子（副露）の符を計算する。
    暗刻の符はここでは計算しない。

    Args:
        meld (Call): 符を計算したい鳴き面子のCallオブジェクト。

    Returns:
        int: 計算された符。
    """
    # チーの符は0
    if call.is_shuntsu():
        return 0

    base_fu = 0
    is_yaochu = Tile.is_yaochu(call.tiles[0])

    # 明刻（ポン）
    if call.call_type == "pon":
        base_fu = 2
        if is_yaochu:
            base_fu *= 2 # ヤオ九牌の明刻は符が2倍
    
    # 明槓・加槓
    elif call.call_type in ["minkan", "kakan"]:
        base_fu = 8
        if is_yaochu:
            base_fu *= 2 # ヤオ九牌の明槓は符が2倍
            
    return base_fu


def calculate_fu(analysis: dict, melds: list[Call], found_yaku: dict, game_state: dict) -> int:
    """
    手牌の符を計算するメイン関数.

    Args:
        analysis (dict)   : HandAnalysisによる手牌の解析結果.
        melds (list[Call]): 鳴いた面子のリスト.
        found_yaku (dict) : 成立した役の辞書.
        game_state (dict) : ゲームの状況設定.

    Returns:
        int: 最終的な符（10の倍数に切り上げ済み）.
    """
    # --- ステップ1：例外役の処理 ---
    if "七対子" in found_yaku:
        return 25
    if "平和" in found_yaku:
        # 平和ツモは20符、平和ロンは30符
        return 20 if game_state.get("is_tsumo", False) else 30
    # --- ステップ2：副底 ---
    fu = 20
    # --- ステップ3：アガリ方の符 ---
    is_menzen = len(melds) == 0
    is_tsumo = game_state.get("is_tsumo", False)
    if is_menzen and not is_tsumo:
        fu += 10  # 門前ロン加符
    if is_tsumo:
        fu += 2   # ツモ符
    # --- ステップ4, 5, 6：各要素の符を加算 ---
    fu += _get_mentsu_fu(analysis, melds, game_state)
    fu += _get_janto_fu(analysis.get("janto"), game_state)
    machi = analysis.get("machi")
    if machi in ['kanchan', 'penchan', 'tanki']:
        fu += 2
    # --- ステップ7：切り上げと例外処理 ---
    # 喰い平和形（鳴いていて、他に符がない状態）は30符に
    if not is_menzen and fu == 20:
        return 30
    return _round_up_fu(fu)


def _get_mentsu_fu(analysis: dict, melds: list[Call], game_state: dict) -> int:
    """
    面子（メンツ）に付く符を計算する.
    
    Args:
        analysis (dict)   : HandAnalysisによる手牌の解析結果.
        melds (list[Call]): 鳴いた面子のリスト.
        game_state (dict) : ゲームの状況設定.
        
    Returns:
        int: 面子に付く符の合計値.
    """
    mentsu_fu = 0
    agari_hai = game_state.get("agari_hai")
    is_tsumo = game_state.get("is_tsumo", False)
    # 門前の面子（暗刻）の符
    for m in analysis.get("mentsu", []):
        if len(set(Tile.to_normal(t) for t in m)) == 1: # 刻子である
            # ロンアガリで完成した刻子は明刻扱い
            is_ankou = is_tsumo or (agari_hai not in m)
            base = 4 if is_ankou else 2
            if Tile.is_yaochu(m[0]):
                base *= 2
            mentsu_fu += base
    # 鳴いた面子（副露面子）の符
    for m in melds:
        # Callクラスのget_fuメソッドを呼び出す
        mentsu_fu += m.get_fu()
    return mentsu_fu


def _get_janto_fu(janto_pair: list[str], game_state: dict) -> int:
    """
    雀頭（ジャントウ）に付く符を計算する.
    
    Args:
        janto_pair (list[str]): 雀頭の牌のリスト（2枚の同じ牌）.
        game_state (dict)     : ゲームの状況設定.  
        
    Returns:
        int: 雀頭に付く符の値.
    """
    if not janto_pair:
        return 0
    janto_tile = Tile.to_normal(janto_pair[0])
    bakaze = game_state.get("bakaze")
    jikaze = game_state.get("jikaze")
    fu = 0
    # 三元牌
    if Tile.is_sangenpai(janto_tile):
        fu += 2
    # 場風・自風
    if janto_tile == bakaze:
        fu += 2
    if janto_tile == jikaze:
        fu += 2
        
    # 連風牌（ダブ東など）の場合、場風と自風で重複して+2されるので合計4符になる
    return fu


def _round_up_fu(fu: int) -> int:
    """
    符の1の位を切り上げる.
    
    Args:
        fu (int): 符の値.
        
    Returns:
        int: 切り上げた符の値（10の倍数）.
    """
    return -(-fu // 10) * 10


from .helpers import Tile, Call # Callクラスをインポート

# ▼▼▼ 新しい関数を作成 ▼▼▼
def calculate_meld_fu(meld: Call) -> int:
    """
    鳴き面子（副露）の符を計算する。
    暗刻の符はここでは計算しない。

    Args:
        meld (Call): 符を計算したい鳴き面子のCallオブジェクト。

    Returns:
        int: 計算された符。
    """
    # チーの符は0
    if meld.is_shuntsu():
        return 0

    base_fu = 0
    is_yaochu = Tile.is_yaochu(meld.tiles[0])

    # 明刻（ポン）
    if meld.call_type == "pon":
        base_fu = 2
        if is_yaochu:
            base_fu *= 2 # ヤオ九牌の明刻は符が2倍
    
    # 明槓・加槓
    elif meld.call_type in ["minkan", "kakan"]:
        base_fu = 8
        if is_yaochu:
            base_fu *= 2 # ヤオ九牌の明槓は符が2倍
            
    return base_fu
