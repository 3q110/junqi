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

    def prompt_move(self, board, selected=None):
        """Two-step move selection: first select piece, then select destination.

        Parameters
        ----------
        board:
            Current board state.
        selected:
            Currently selected (col, row) or None.

        Returns
        -------
        (src_col, src_row, dst_col, dst_row) or None.
        """
        width = board.width
        height = board.height

        if selected is None:
            # Step 1: select a piece
            while True:
                print(f"\n选择棋子 (格式: col,row, 输入 q 退出): ", end="")
                raw = input().strip()
                if raw.lower() in ("q", "quit", "exit"):
                    return None
                try:
                    parts = raw.split(",")
                    if len(parts) != 2:
                        print("格式错误，请使用 col,row (例如 0,0)")
                        continue
                    col, row = int(parts[0]), int(parts[1])
                    if col < 0 or col >= width or row < 0 or row >= height:
                        print(f"坐标超出范围 (0-{width-1}, 0-{height-1})")
                        continue
                    piece = board.get(col, row)
                    if piece is None:
                        print("该位置没有棋子")
                        continue
                    if piece.side != "human":
                        print("这不是你的棋子")
                        continue
                    selected = (col, row)
                    print(f"已选择: ({col},{row}) — 请选择目标位置 (格式: col,row, 输入 c 取消)")
                except ValueError:
                    print("格式错误，请使用 col,row (例如 0,0)")
                else:
                    break

            # Step 2: select destination
            src_col, src_row = selected
            piece = board.get(src_col, src_row)
            symbols = {
                "司": "军长", "军": "司令", "师": "师长", "旅": "旅长",
                "团": "团长", "营": "营长", "连": "连长", "排": "排长",
                "工": "工兵", "炸": "炸弹", "地雷": "地雷", "旗": "军旗"
            }
            sym = _PIECE_SYMBOLS.get(piece.piece_type, "?")
            name = symbols.get(sym, piece.piece_type.name)
            print(f"棋子: {name} at ({src_col},{src_row})")
            print("可移动方向: ↑(0,-1) ↓(0,1) ←(-1,0) →(1,0)")

            while True:
                print(f"选择目标 (格式: col,row, 输入 c 取消): ", end="")
                raw = input().strip()
                if raw.lower() in ("c", "cancel"):
                    selected = None
                    return self.prompt_move(board, selected)
                try:
                    parts = raw.split(",")
                    if len(parts) != 2:
                        print("格式错误，请使用 col,row (例如 1,0)")
                        continue
                    dst_col, dst_row = int(parts[0]), int(parts[1])
                    if dst_col < 0 or dst_col >= width or dst_row < 0 or dst_row >= height:
                        print(f"坐标超出范围 (0-{width-1}, 0-{height-1})")
                        continue
                    return (src_col, src_row, dst_col, dst_row)
                except ValueError:
                    print("格式错误，请使用 col,row (例如 1,0)")
        else:
            # Should not reach here, but handle gracefully
            return self.prompt_move(board, None)
