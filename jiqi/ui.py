"""Terminal UI for the Chinese Army Chess (军旗) game."""

from __future__ import annotations

from jiqi.piece import PieceType


# Piece display symbols
_PIECE_SYMBOLS: dict[PieceType, str] = {
    PieceType.COMMANDER: "司",
    PieceType.ARMY_COMMANDER: "军",
    PieceType.DIVISION_COMMANDER: "师",
    PieceType.BRIGADE_COMMANDER: "旅",
    PieceType.REGIMENT_COMMANDER: "团",
    PieceType.BATTALION_COMMANDER: "营",
    PieceType.COMPANY_COMMANDER: "连",
    PieceType.PLATOON_LEADER: "排",
    PieceType.SAPPER: "工",
    PieceType.BOMB: "炸",
    PieceType.MINE: "地雷",
    PieceType.FLAG: "旗",
}

# ANSI colour codes
_RED = "\033[91m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RESET = "\033[0m"


class TerminalUI:
    """Handles all terminal-based display and input for the game."""

    # -- initialisation --

    def __init__(self) -> None:
        pass

    # -- board display --

    def display_board(self, board, show_enemy: bool = False) -> None:
        """Print the board to the terminal.

        Parameters
        ----------
        board:
            A ``jiqi.board.Board`` instance.
        show_enemy:
            If ``True`` the AI (human-side) pieces are revealed.
            Otherwise they are shown as ``?``.
        """
        width = board.width
        height = board.height

        # Column header
        header = "   " + " ".join(f"{c}" for c in range(width))
        print(header)

        # Separator line
        sep = "  +" + "---+" * width
        print(sep)

        # Row by row
        for row in range(height):
            row_label = f"{row} |"
            cells = ""
            for col in range(width):
                piece = board.get(col, row)
                if piece is None:
                    cell = " . "
                elif piece.side == "human":
                    symbol = _PIECE_SYMBOLS.get(piece.piece_type, "?")
                    cell = f" {symbol} "
                else:
                    # AI side (enemy)
                    if show_enemy:
                        symbol = _PIECE_SYMBOLS.get(piece.piece_type, "?")
                        cell = f" {symbol} "
                    else:
                        cell = " ? "
                cells += cell
            print(f"{row_label}{cells}")

        # Bottom separator
        print(sep)

    # -- messages --

    def display_message(self, message: str) -> None:
        """Print a normal message."""
        print(message)

    def display_error(self, error_msg: str) -> None:
        """Print an error message in red."""
        print(f"{_RED}{error_msg}{_RESET}")

    def display_success(self, success_msg: str) -> None:
        """Print a success message in green."""
        print(f"{_GREEN}{success_msg}{_RESET}")

    # -- piece info --

    def show_piece_info(self, piece) -> None:
        """Print information about a single piece."""
        if piece is None:
            print("No piece at this position.")
            return
        type_name = piece.piece_type.name
        side_name = piece.side
        alive = "alive" if piece.is_alive else "dead"
        print(f"  Type: {type_name}  |  Side: {side_name}  |  Status: {alive}")

    # -- input --

    def get_coordinates(self, prompt: str = "请输入坐标") -> tuple[int, int, int, int] | None:
        """Prompt the user for move coordinates.

        Expects input in the form ``col1,row1 col2,row2`` (e.g. ``0,0 1,0``).

        Returns
        -------
        A tuple ``(src_col, src_row, dst_col, dst_row)`` on success,
        or ``None`` if the input is invalid.
        """
        try:
            raw = input(prompt).strip()
            parts = raw.split()
            if len(parts) != 2:
                raise ValueError("Expected two coordinates, e.g. '0,0 1,0'")

            src_col, src_row = map(int, parts[0].split(","))
            dst_col, dst_row = map(int, parts[1].split(","))
            return (src_col, src_row, dst_col, dst_row)

        except (ValueError, IndexError):
            print(f"{_RED}Invalid input. Please use format: 'col1,row1 col2,row2'{_RESET}")
            return None
