from __future__ import annotations

import random
from typing import Optional, Tuple

from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.rules import RuleEngine


class GameSetup:
    """Static class for setting up pieces on the board."""

    PIECE_COUNTS = {
        PieceType.FLAG: 1,
        PieceType.COMMANDER: 1,
        PieceType.ARMY_COMMANDER: 1,
        PieceType.DIVISION_COMMANDER: 2,
        PieceType.BRIGADE_COMMANDER: 2,
        PieceType.REGIMENT_COMMANDER: 2,
        PieceType.BATTALION_COMMANDER: 2,
        PieceType.COMPANY_COMMANDER: 2,
        PieceType.PLATOON_LEADER: 2,
        PieceType.SAPPER: 3,
        PieceType.MINE: 3,
        PieceType.BOMB: 3,
    }

    HIGH_RANK_PIECES = (
        PieceType.COMMANDER,
        PieceType.ARMY_COMMANDER,
        PieceType.DIVISION_COMMANDER,
    )

    @staticmethod
    def setup_pieces(board: Board) -> None:
        """Place all pieces on the board in a standard setup pattern.

        Human pieces go on rows 0-4, AI pieces on rows 6-10.
        Row 5 (the river) remains empty.
        Total per side: 24 pieces (1+1+1+2+2+2+2+2+2+3+3+3).
        """
        for c in range(board.width):
            for r in range(board.height):
                board.remove(c, r)

        GameSetup._place_side(board, "human", human_flag=True)
        GameSetup._place_side(board, "ai", human_flag=False)

    @staticmethod
    def _place_side(board: Board, side: str, human_flag: bool) -> None:
        """Place all 24 pieces for one side using a deterministic layout.

        Pieces are distributed evenly across the 7 columns and 5 available rows
        (35 cells for 24 pieces). Each row gets at most 7 pieces.

        Layout:
          Row 0: FLAG (1 piece, center)
          Row 1: COMMANDER, ARMY_COMMANDER, DIVISION_COMMANDER x2, BRIGADE_COMMANDER x2 (7 pieces)
          Row 2: REGIMENT_COMMANDER x2, BATTALION_COMMANDER x2, MINE x2 (6 pieces)
          Row 3: COMPANY_COMMANDER x2, PLATOON_LEADER x2, BOMB x2 (6 pieces)
          Row 4: SAPPER x3, MINE x1, BOMB x1 (5 pieces)
        """
        if human_flag:
            flag_row = 0
            hr_rows = (1, 2, 3, 4)
            row1 = 1
            row2 = 2
            row3 = 3
            row4 = 4
        else:
            flag_row = 10
            hr_rows = (6, 7, 8, 9)
            row1 = 6
            row2 = 7
            row3 = 8
            row4 = 9

        # Row 0: FLAG at center column (3)
        board.place(Piece(PieceType.FLAG, side=side), 3, flag_row)

        # Row 1 (cols 0-6): COMMANDER, ARMY_COMMANDER, DIVISION_COMMANDER x2, BRIGADE_COMMANDER x2
        row1_pieces = [
            PieceType.COMMANDER,
            PieceType.ARMY_COMMANDER,
            PieceType.DIVISION_COMMANDER,
            PieceType.DIVISION_COMMANDER,
            PieceType.BRIGADE_COMMANDER,
            PieceType.BRIGADE_COMMANDER,
        ]
        for i, pt in enumerate(row1_pieces):
            board.place(Piece(pt, side=side), i, row1)

        # Row 2 (cols 0-5): REGIMENT_COMMANDER x2, BATTALION_COMMANDER x2, MINE x2
        row2_pieces = [
            PieceType.REGIMENT_COMMANDER,
            PieceType.REGIMENT_COMMANDER,
            PieceType.BATTALION_COMMANDER,
            PieceType.BATTALION_COMMANDER,
            PieceType.MINE,
            PieceType.MINE,
        ]
        for i, pt in enumerate(row2_pieces):
            board.place(Piece(pt, side=side), i, row2)

        # Row 3 (cols 0-5): COMPANY_COMMANDER x2, PLATOON_LEADER x2, BOMB x2
        row3_pieces = [
            PieceType.COMPANY_COMMANDER,
            PieceType.COMPANY_COMMANDER,
            PieceType.PLATOON_LEADER,
            PieceType.PLATOON_LEADER,
            PieceType.BOMB,
            PieceType.BOMB,
        ]
        for i, pt in enumerate(row3_pieces):
            board.place(Piece(pt, side=side), i, row3)

        # Row 4 (cols 0-4): SAPPER x3, MINE x1, BOMB x1
        row4_pieces = [
            PieceType.SAPPER,
            PieceType.SAPPER,
            PieceType.SAPPER,
            PieceType.MINE,
            PieceType.BOMB,
        ]
        for i, pt in enumerate(row4_pieces):
            board.place(Piece(pt, side=side), i, row4)

        # Verify all cells are filled (no duplicates, no overwrites)
        placed = 0
        for r in (flag_row, row1, row2, row3, row4):
            for c in range(board.width):
                if board.get(c, r) is not None:
                    placed += 1
        assert placed == 24, f"Expected 24 pieces, placed {placed}"


class HumanPlayer:
    """Human player — move selection via UI."""

    def __init__(self, board: Board, name: str = "玩家", ui=None) -> None:
        self.board = board
        self.name = name
        self.ui = ui
        self._selected = None  # (col, row) of selected piece

    def get_move(self) -> Optional[Tuple[int, int, int, int]]:
        """Request a move from the human player via UI."""
        if self.ui is None:
            raise NotImplementedError("HumanPlayer.get_move() requires a UI")
        return self.ui.prompt_move(self.board, self._selected)


class AIPlayer:
    """AI player — currently uses simple random valid move selection."""

    def __init__(self, board: Board, name: str = "电脑") -> None:
        self.board = board
        self.name = name

    def get_move(self) -> Optional[Tuple[int, int, int, int]]:
        """Return a random valid move, or None if no moves are available."""
        valid_moves = self._get_all_valid_moves()
        if not valid_moves:
            return None
        return random.choice(valid_moves)

    def _get_all_valid_moves(self) -> list[tuple[int, int, int, int]]:
        """Find all valid moves for the AI's side."""
        moves = []
        for c in range(self.board.width):
            for r in range(self.board.height):
                piece = self.board.get(c, r)
                if piece is None or piece.side != "ai":
                    continue
                for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    dst_col = c + dc
                    dst_row = r + dr
                    if RuleEngine.can_move(self.board, c, r, dst_col, dst_row):
                        moves.append((c, r, dst_col, dst_row))
        return moves
