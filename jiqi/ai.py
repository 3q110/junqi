"""AI 模块 - 简单随机走棋"""

import random
from typing import Tuple
from jiqi.board import Board
from jiqi.rules import Rules
from jiqi.player import Player


class RandomAI(Player):
    """简单 AI：随机选择合法移动"""

    def __init__(self, side: str, name: str = "AI"):
        super().__init__(side, name)

    def make_move(self, board: Board) -> Tuple[int, int, int, int]:
        """随机选择一个合法移动"""
        all_moves = self._get_all_moves(board)
        if not all_moves:
            raise ValueError(f"{self.name} 没有合法移动")

        # 简单策略：优先吃子
        capture_moves = []
        other_moves = []
        for fr, fc, tr, tc in all_moves:
            target = board.get(tr, tc)
            if target:
                capture_moves.append((fr, fc, tr, tc))
            else:
                other_moves.append((fr, fc, tr, tc))

        if capture_moves:
            return random.choice(capture_moves)
        return random.choice(other_moves)

    def _get_all_moves(self, board: Board) -> list:
        """获取某方所有合法移动"""
        moves = []
        pieces = board.get_side_pieces(self.side)
        for r, c, piece in pieces:
            valid_targets = Rules.get_valid_moves(board, r, c)
            for tr, tc in valid_targets:
                moves.append((r, c, tr, tc))
        return moves
