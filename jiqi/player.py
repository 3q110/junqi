"""玩家模块 - 人类玩家和AI基类"""

from abc import ABC, abstractmethod
from typing import Tuple
from jiqi.board import Board


class Player(ABC):
    """玩家基类"""

    def __init__(self, side: str, name: str):
        self.side = side
        self.name = name

    @abstractmethod
    def make_move(self, board: Board) -> Tuple[int, int, int, int]:
        """
        执行一步棋。

        Returns:
            (from_row, from_col, to_row, to_col)
        """
        pass
