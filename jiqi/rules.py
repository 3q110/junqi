from __future__ import annotations

from jiqi.board import Board
from jiqi.piece import Piece, PieceType


class RuleEngine:
    """Static rule engine for movement validation and battle resolution."""

    @staticmethod
    def can_move(board: Board, src_col: int, src_row: int,
                 dst_col: int, dst_row: int) -> bool:
        """Check if a move from (src_col, src_row) to (dst_col, dst_row) is valid."""
        # --- bounds check ---
        if not (0 <= dst_col < board.width and 0 <= dst_row < board.height):
            return False

        # --- must be adjacent (up/down/left/right only, no diagonals) ---
        dc = abs(dst_col - src_col)
        dr = abs(dst_row - src_row)
        if not ((dc == 1 and dr == 0) or (dc == 0 and dr == 1)):
            return False

        src_piece = board.get(src_col, src_row)
        if src_piece is None:
            return False

        dst_piece = board.get(dst_col, dst_row)

        # --- cannot move to own flag ---
        if dst_piece is not None and dst_piece.piece_type == PieceType.FLAG:
            if dst_piece.side == src_piece.side:
                return False

        # --- cannot move to own piece ---
        if dst_piece is not None and dst_piece.side == src_piece.side:
            return False

        return True

    @staticmethod
    def resolve_battle(attacker: Piece, defender: Piece) -> str:
        """Resolve a battle between attacker and defender.

        Returns one of:
            "attacker_wins"  – attacker defeats defender
            "defender_wins"  – defender defeats attacker
            "both_die"       – both pieces are destroyed
            "invalid"        – the battle cannot happen
        """
        # --- FLAG attacks are invalid ---
        if attacker.piece_type == PieceType.FLAG:
            return "invalid"

        # --- defender is MINE ---
        if defender.piece_type == PieceType.MINE:
            if attacker.piece_type in (PieceType.SAPPER, PieceType.BOMB):
                return "attacker_wins"
            return "attacker_loses"

        # --- defender is BOMB ---
        if defender.piece_type == PieceType.BOMB:
            return "both_die"

        # --- defender is FLAG ---
        if defender.piece_type == PieceType.FLAG:
            if attacker.piece_type == PieceType.FLAG:
                return "invalid"
            return "attacker_wins"

        # --- normal battle: lower rank number = higher rank ---
        if attacker.rank < defender.rank:
            return "attacker_wins"
        if attacker.rank > defender.rank:
            return "defender_wins"

        # equal rank – mutual destruction
        return "both_die"
