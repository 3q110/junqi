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

        规则概要：
        - 8 方向相邻移动（所有可行走棋子）
        - 铁路线直线移动（任何在铁路线上的棋子）
        - 工兵可在铁路线拐弯（BFS 遍历整个铁路网）
        - 行营保护：不能吃掉行营里的棋子
        - 大本营限制：敌方只能在我军旗被吃后进入大本营

        Returns:
            合法目标位置列表 [(row, col), ...]
        """
        piece = board.get(row, col)
        if not piece or not piece.is_alive:
            return []
        if not piece.is_movable:
            return []

        moves = Rules._normal_moves(board, row, col, piece)

        # 任何在铁路线上的棋子均可沿铁路直线移动
        if board.is_on_railway(row, col):
            rail_straight = Rules._railway_straight_moves(board, row, col, piece)
            seen = set(moves)
            for m in rail_straight:
                if m not in seen:
                    moves.append(m)
                    seen.add(m)

        # 工兵特权：可在铁路线拐弯（BFS）
        if piece.piece_type == PieceType.SAPPER:
            sapper_turns = Rules._railway_sapper_moves(board, row, col, piece)
            seen = set(moves)
            for m in sapper_turns:
                if m not in seen:
                    moves.append(m)
                    seen.add(m)

        return moves

    @staticmethod
    def _is_target_valid(board: Board, piece: Piece, nr: int, nc: int) -> bool:
        """
        统一的目标位置合法性检查。

        检查项：
        1. 不能走到己方棋子位置
        2. 行营保护：不能攻击行营中的棋子
        3. 大本营限制：敌方棋子只能在军旗被吃后进入大本营
        4. 空位可走
        5. 敌方棋子按吃子规则判断
        """
        if not board.in_bounds(nr, nc):
            return False

        target = board.get(nr, nc)

        # 不能走到己方棋子位置
        if target and target.side == piece.side:
            return False

        # 行营保护：不能攻击行营里的棋子
        if target and target.side != piece.side and board.is_camp(nr, nc):
            return False

        # 大本营限制：敌方棋子只能在军旗被吃后进入大本营
        if board.is_headquarter(nr, nc):
            hq_side = Board.get_side_of_headquarter(nr, nc)
            if hq_side and hq_side != piece.side:
                if board.is_flag_alive(hq_side):
                    return False

        # 空位 → 可走
        if target is None:
            return True

        # 敌方棋子 → 按吃子规则判断
        return piece.can_eat(target)

    @staticmethod
    def _normal_moves(board: Board, row: int, col: int, piece: Piece) -> List[Tuple[int, int]]:
        """普通棋子的移动：只能走到 8 方向相邻格"""
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]

        moves = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if Rules._is_target_valid(board, piece, nr, nc):
                moves.append((nr, nc))
        return moves

    @staticmethod
    def _railway_straight_moves(board: Board, row: int, col: int, piece: Piece) -> List[Tuple[int, int]]:
        """
        所有棋子在铁路线上的直线移动（非工兵专用）。
        - 只能沿 4 个正方向（上/下/左/右）直走
        - 不能拐弯
        """
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.in_bounds(r, c) and board.is_on_railway(r, c):
                if Rules._is_target_valid(board, piece, r, c):
                    moves.append((r, c))
                    # 如果目标有棋子，吃掉后停止在这个方向
                    if board.get(r, c) is not None:
                        break
                else:
                    # 被友方棋子阻挡或违规则停止
                    break
                r += dr
                c += dc

        return moves

    @staticmethod
    def _railway_sapper_moves(board: Board, row: int, col: int, piece: Piece) -> List[Tuple[int, int]]:
        """
        工兵铁路线特权移动：BFS 遍历整个铁路网，可拐弯。
        这是工兵对比其他棋子的核心优势。
        """
        moves = []
        visited = {(row, col)}
        queue = [(row, col)]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            cr, cc = queue.pop(0)
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if (nr, nc) in visited:
                    continue
                visited.add((nr, nc))

                if not board.in_bounds(nr, nc):
                    continue
                if not board.is_on_railway(nr, nc):
                    continue

                if Rules._is_target_valid(board, piece, nr, nc):
                    moves.append((nr, nc))
                    # 空位可继续 BFS 扩展
                    if board.get(nr, nc) is None:
                        queue.append((nr, nc))
                # 有棋子（友方或无法吃掉的敌方）→ 阻塞，不继续扩展

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
        red_flag = board.is_flag_alive("red")
        black_flag = board.is_flag_alive("black")

        if not red_flag:
            return "black_wins"
        if not black_flag:
            return "red_wins"
        return None
