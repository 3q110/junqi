"""棋盘模块 - 7x11 网格，管理棋子位置"""

from typing import Optional, List, Tuple
from jiqi.piece import Piece, PieceType


class Board:
    """军旗棋盘"""

    WIDTH = 7
    HEIGHT = 11

    # 铁路线位置（简化版：第2行和第9行为横贯铁路线）
    RAILWAY_ROWS = {2, 9}

    @property
    def width(self):
        return self.WIDTH

    @property
    def height(self):
        return self.HEIGHT
    # 竖直线铁路：第0列和第6列的第1-3行和第7-9行
    VERTICAL_RAILWAY = set()
    for r in range(1, 4):
        VERTICAL_RAILWAY.add((r, 0))
        VERTICAL_RAILWAY.add((r, 6))
    for r in range(7, 10):
        VERTICAL_RAILWAY.add((r, 0))
        VERTICAL_RAILWAY.add((r, 6))
    # 大本营
    HEADQUARTERS = {
        (0, 2), (0, 4),   # 黑方大本营
        (10, 2), (10, 4),  # 红方大本营
    }
    # 军旗位置
    FLAG_POSITIONS = {
        (0, 3),   # 黑方军旗
        (10, 3),  # 红方军旗
    }

    def __init__(self):
        self.grid: List[List[Optional[Piece]]] = [[None] * self.WIDTH for _ in range(self.HEIGHT)]

    def in_bounds(self, row: int, col: int) -> bool:
        """检查坐标是否在棋盘内"""
        return 0 <= row < self.HEIGHT and 0 <= col < self.WIDTH

    def get(self, row: int, col: int) -> Optional[Piece]:
        """获取指定位置的棋子"""
        if not self.in_bounds(row, col):
            return None
        piece = self.grid[row][col]
        if piece and not piece.is_alive:
            return None
        return piece

    def place(self, piece: Piece, row: int, col: int) -> bool:
        """放置棋子。如果位置已有活棋则失败。"""
        if not self.in_bounds(row, col):
            return False
        if self.grid[row][col] and self.grid[row][col].is_alive:
            return False
        self.grid[row][col] = piece
        piece.is_alive = True
        return True

    def remove(self, row: int, col: int) -> Optional[Piece]:
        """移除指定位置的棋子"""
        if not self.in_bounds(row, col):
            return None
        piece = self.grid[row][col]
        if piece:
            piece.is_alive = False
        self.grid[row][col] = None
        return piece

    def move(self, piece: Piece, from_row: int, from_col: int, to_row: int, to_col: int) -> Optional[Piece]:
        """
        移动棋子。返回被吃掉的棋子（如果有），None 表示空位移动。
        """
        captured = self.grid[to_row][to_col]
        if captured and captured.is_alive:
            captured.is_alive = False
        self.grid[from_row][from_col] = None
        self.grid[to_row][to_col] = piece
        return captured

    def get_side_pieces(self, side: str) -> List[Tuple[int, int, Piece]]:
        """获取某方所有活棋"""
        result = []
        for r in range(self.HEIGHT):
            for c in range(self.WIDTH):
                p = self.grid[r][c]
                if p and p.is_alive and p.side == side:
                    result.append((r, c, p))
        return result

    def is_on_railway(self, row: int, col: int) -> bool:
        """检查位置是否在铁路线上"""
        if row in self.RAILWAY_ROWS:
            return True
        if (row, col) in self.VERTICAL_RAILWAY:
            return True
        return False

    def __repr__(self):
        lines = []
        for r in range(self.HEIGHT):
            row_str = []
            for c in range(self.WIDTH):
                p = self.grid[r][c]
                if p and p.is_alive:
                    row_str.append(f"[{p.name[:2]}]")
                else:
                    row_str.append("[  ]")
            lines.append(f"{r:2d}| {' '.join(row_str)}")
        return "\n".join(lines)
