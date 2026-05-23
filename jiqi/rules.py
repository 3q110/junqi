"""规则引擎 - 验证走棋合法性"""

from typing import List, Tuple, Optional
from jiqi.board import Board
from jiqi.piece import Piece, PieceType


class Rules:
    """走棋规则验证器"""

    @staticmethod
    def get_valid_moves(board: Board, row: int, col: int) -> List[Tuple[int, int]]:
        """
        获取指定位置棋子的所有合法移动目标。

        Returns:
            合法目标位置列表 [(row, col), ...]
        """
        piece = board.get(row, col)
        if not piece or not piece.is_alive:
            return []
        if not piece.is_movable:
            return []

        if piece.piece_type == PieceType.SAPPER:
            return Rules._sapper_moves(board, row, col)
        else:
            return Rules._normal_moves(board, row, col)

    @staticmethod
    def _normal_moves(board: Board, row: int, col: int) -> List[Tuple[int, int]]:
        """普通棋子的移动（只能走到相邻格）"""
        piece = board.get(row, col)
        if not piece:
            return []

        # 8 个方向
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]

        moves = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if not board.in_bounds(nr, nc):
                continue
            target = board.get(nr, nc)
            if target is None:
                moves.append((nr, nc))
            elif target.side != piece.side and piece.can_eat(target):
                moves.append((nr, nc))
        return moves

    @staticmethod
    def _sapper_moves(board: Board, row: int, col: int) -> List[Tuple[int, int]]:
        """
        工兵的移动：
        - 普通相邻移动（同普通棋子）
        - 如果在铁路线上，可以沿铁路线直走（可拐弯）
        """
        piece = board.get(row, col)
        if not piece:
            return []

        # 基本相邻移动
        moves = Rules._normal_moves(board, row, col)

        # 铁路线特殊移动
        if board.is_on_railway(row, col):
            rail_moves = Rules._railway_moves(board, row, col, piece)
            # 合并去重
            seen = set(moves)
            for m in rail_moves:
                if m not in seen:
                    moves.append(m)
                    seen.add(m)

        return moves

    @staticmethod
    def _railway_moves(board: Board, row: int, col: int, piece: Piece) -> List[Tuple[int, int]]:
        """工兵在铁路线上的移动：可以沿铁路线走到任意远"""
        moves = []
        # 4 个直线方向
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.in_bounds(r, c) and board.is_on_railway(r, c):
                target = board.get(r, c)
                if target is None:
                    moves.append((r, c))
                elif target.side != piece.side and piece.can_eat(target):
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return moves

    @staticmethod
    def is_valid_move(board: Board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """检查从 (from_row, from_col) 到 (to_row, to_col) 是否是合法移动"""
        valid_moves = Rules.get_valid_moves(board, from_row, from_col)
        return (to_row, to_col) in valid_moves

    @staticmethod
    def resolve_combat(attacker: Piece, defender: Piece) -> str:
        """
        解决战斗，返回结果：
        - "attack_wins": 攻击方赢，防守方被吃
        - "defend_wins": 防守方赢，攻击方被吃
        - "mutual": 同归于尽
        - "no_combat": 无战斗（移动至空位）
        """
        if defender is None:
            return "no_combat"

        if attacker.piece_type == PieceType.BOMB and defender.piece_type != PieceType.FLAG:
            return "mutual"
        if defender.piece_type == PieceType.BOMB and attacker.piece_type != PieceType.FLAG:
            return "mutual"

        if attacker.can_eat(defender):
            return "attack_wins"
        else:
            return "defend_wins"

    @staticmethod
    def check_game_over(board: Board) -> Optional[str]:
        """
        检查游戏是否结束。
        Returns:
            - None: 游戏继续
            - "red_wins": 红方获胜
            - "black_wins": 黑方获胜
        """
        red_flag = False
        black_flag = False
        for r in range(board.HEIGHT):
            for c in range(board.WIDTH):
                p = board.get(r, c)
                if p and p.piece_type == PieceType.FLAG:
                    if p.side == "red":
                        red_flag = True
                    else:
                        black_flag = True

        if not red_flag:
            return "black_wins"
        if not black_flag:
            return "red_wins"
        return None
