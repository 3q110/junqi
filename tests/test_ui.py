from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.ui import TerminalUI


def test_board_display_no_crash():
    ui = TerminalUI()
    board = Board()
    # Should not raise
    ui.display_board(board)


def test_board_display_shows_pieces():
    ui = TerminalUI()
    board = Board()
    p = Piece(PieceType.COMMANDER, side="human")
    board.place(p, 0, 0)
    # Should not raise
    ui.display_board(board)


def test_board_display_7x11():
    ui = TerminalUI()
    board = Board()
    for r in range(11):
        for c in range(7):
            p = Piece(PieceType.COMMANDER, side="human")
            board.place(p, c, r)
    # Should not raise
    ui.display_board(board)


def test_display_message():
    ui = TerminalUI()
    # Should not raise
    ui.display_message("test message")


def test_display_error():
    ui = TerminalUI()
    # Should not raise
    ui.display_error("test error")


def test_display_success():
    ui = TerminalUI()
    # Should not raise
    ui.display_success("test success")
