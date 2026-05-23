from __future__ import annotations

from typing import Optional

from jiqi.piece import Piece


class Board:
    """7 columns x 11 rows grid for a Chinese Army Chess (军旗) game."""

    WIDTH = 7
    HEIGHT = 11

    def __init__(self) -> None:
        self.width = self.WIDTH
        self.height = self.HEIGHT
        # grid[col][row] — indexed by column first, then row
        self.grid: list[list[Optional[Piece]]] = [
            [None] * self.height for _ in range(self.width)
        ]

    # -- accessors --

    def get(self, col: int, row: int) -> Optional[Piece]:
        """Return the piece at (col, row), or None if empty."""
        return self.grid[col][row]

    def get_piece_at(self, col: int, row: int) -> Optional[Piece]:
        """Alias for :meth:`get`."""
        return self.get(col, row)

    # -- mutation --

    def place(self, piece: Piece, col: int, row: int) -> bool:
        """Place *piece* on the board at (col, row).

        Returns ``True`` on success, ``False`` if the cell is already occupied.
        """
        if self.grid[col][row] is not None:
            return False
        self.grid[col][row] = piece
        return True

    def remove(self, col: int, row: int) -> Optional[Piece]:
        """Remove and return the piece at (col, row), or ``None`` if empty."""
        piece = self.grid[col][row]
        self.grid[col][row] = None
        return piece

    def move(self, src_col: int, src_row: int, dst_col: int, dst_row: int) -> bool:
        """Move the piece at (src_col, src_row) to (dst_col, dst_row).

        Returns ``True`` on success, ``False`` if source is empty or
        destination is already occupied.
        """
        piece = self.grid[src_col][src_row]
        if piece is None:
            return False
        if self.grid[dst_col][dst_row] is not None:
            return False
        self.grid[src_col][src_row] = None
        self.grid[dst_col][dst_row] = piece
        return True
