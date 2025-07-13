# 牌の定義
# 萬子: 1m-9m, 筒子: 1p-9p, 索子: 1s-9s, 字牌: 1z-7z (東南西北白發中)
# 赤ドラ: 5mr, 5pr, 5sr
TILES = {
    'm': [f'{i}m' for i in range(1, 10)],  # 萬子.
    'p': [f'{i}p' for i in range(1, 10)],  # 筒子.
    's': [f'{i}s' for i in range(1, 10)],  # 索子.
    'z': [f'{i}z' for i in range(1, 8)],   # 字牌 (1z-7z).
}
ALL_TILES = sum(TILES.values(), [])
YAOCHUHAI = {"1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"}
SANGENPAI = {"5z", "6z", "7z"}

class Tile:
    """牌の情報を扱うヘルパークラス"""
    @staticmethod
    def sort_key(tile: str) -> int:
        """
        牌をソートするためのキーを返す関数.
        
        Args:
            tile (str): 牌の文字列 (例: "1m", "5pr", "7z")
        
        Returns:
            int: ソート用の整数値.
        """
        _tile = tile.replace('r', '')
        suit = 'mpsz'.index(_tile[-1])
        num = int(_tile[:-1])
        return suit * 10 + num
    
    @staticmethod
    def to_normal(tile: str) -> str:
        """
        牌を通常の形式に変換する関数.
        
        Args:
            tile (str): 牌の文字列 (例: "5mr", "1p")

        Returns:
            str: 通常の形式の牌 (例: "5m", "1p")
        """
        return tile.replace('r', '')
    
    @staticmethod
    def is_yaochu(tile: str) -> bool:
        """
        牌が幺九牌（ヤオチュウハイ）かどうかを判定する関数.
        幺九牌は、1m, 9m, 1p, 9p, 1s, 9s, 1z, 2z, 3z, 4z, 5z, 6z, 7z のいずれかです.
        
        Args:
            tile (str): 牌の文字列 (例: "1m", "9p", "5z")
        
        Returns:
            bool: 牌が幺九牌ならTrue、そうでなければFalse.
        """
        return Tile.to_normal(tile) in YAOCHUHAI
    
    @staticmethod
    def is_jihai(tile: str) -> bool:
        """
        牌が字牌（じはい）かどうかを判定する関数.
        
        Args:
            tile (str): 牌の文字列 (例: "1z", "5z", "7z")
        
        Returns:
            bool: 牌が字牌ならTrue、そうでなければFalse.
        """
        return tile[-1] == 'z'
    
    @staticmethod
    def next_tile(tile: str) -> str:
        """
        ドラ表示牌からドラを計算するための関数.
        
        Args:
            tile (str): ドラ表示牌の文字列 (例: "5m", "5pr", "5sr")
            
        Returns:
            str: ドラ牌の文字列 (例: "6m", "6pr", "6sr")
        """
        tile = Tile.to_normal(tile)
        if not tile in ALL_TILES:
            return None
        # 牌の種類と数字を分解
        suit = tile[-1]       # 最後の文字が牌の種類 (m, p, s, z)
        num = int(tile[:-1])  # 数字部分を整数に変換
        
        # 萬子、筒子、索子の処理.
        if suit in 'mps':
            return f"{num % 9 + 1}{suit}"
        # 字牌の処理.
        if suit == 'z':
            if 1 <= num <= 3: return f"{num + 1}z"
            if num == 4: return "1z"
            if 5 <= num <= 6: return f"{num + 1}z"
            if num == 7: return "5z"
        return None


class Meld:
    """鳴き（面子）の情報を扱うクラス"""
    def __init__(self, meld_type: str, tiles: list[str]):
        """
        鳴き（面子）の初期化.
        
        Args:
            meld_type (str)  : 鳴きの種類 ("pon", "chi", "minkan", "ankan", "kakan")
            tiles (list[str]): 鳴きに含まれる牌のリスト (例: ["1m", "2m", "3m"])
        """
        self.meld_type = meld_type  # "pon", "chi", "minkan", "ankan", "kakan"
        self.tiles = sorted(tiles, key=Tile.sort_key)
        self.is_open = meld_type != "ankan"
    
    def is_kotsu(self) -> bool:
        """
        鳴きが刻子（コーツ）かどうかを判定する関数.
        
        Returns:
            bool: 鳴きが刻子ならTrue、そうでなければFalse.
        """
        return self.meld_type in ["pon", "minkan", "ankan", "kakan"]
    
    def is_shuntsu(self) -> bool:
        """
        鳴きが順子（シュンツ）かどうかを判定する関数.
        
        Returns:
            bool: 鳴きが順子ならTrue、そうでなければFalse.
        """
        return self.meld_type == "chi"
    
    def get_fu(self) -> int:
        """
        鳴きの符を計算する関数.
        
        Returns:
            int: 鳴きの符の値.
        """
        base_fu = 0
        is_yaochu = Tile.is_yaochu(self.tiles[0])
        # 鳴きの種類に応じて符を計算.
        # ポン、チーの符計算.
        if self.meld_type in ["pon", "chi"]:
            base_fu = 2 if self.is_kotsu() else 0
            if not self.is_open: base_fu *= 2 # 暗刻の場合.
            if is_yaochu: base_fu *= 2
        # 明槓、暗槓、加槓の符計算.
        elif self.meld_type in ["minkan", "ankan", "kakan"]:
            base_fu = 8
            if not self.is_open: base_fu *= 2 # 暗槓の場合.
            if is_yaochu: base_fu *= 2
        return base_fu