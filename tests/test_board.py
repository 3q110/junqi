from jiqi.board import Board
from jiqi.piece import Piece, PieceType


# --- Board creation ---

def test_board_creation():
    board = Board()
    assert board.width == 7
    assert board.height == 11
    assert board.grid[0][0] is None


# --- Place and get ---

def test_place_and_get():
    board = Board()
    p = Piece(PieceType.COMMANDER, side="human")
    board.place(p, 0, 0)
    assert board.get(0, 0) == p


def test_get_returns_none_for_empty_cell():
    board = Board()
    assert board.get(3, 5) is None


# --- Place on occupied cell ---

def test_place_on_occupied_fails():
    board = Board()
    p1 = Piece(PieceType.COMMANDER, side="human")
    p2 = Piece(PieceType.ARMY_COMMANDER, side="human")
    board.place(p1, 0, 0)
    assert not board.place(p2, 0, 0)


# --- Remove ---

def test_remove():
    board = Board()
    p = Piece(PieceType.COMMANDER, side="human")
    board.place(p, 0, 0)
    board.remove(0, 0)
    assert board.get(0, 0) is None


def test_remove_empty_cell_does_not_crash():
    board = Board()
    result = board.remove(3, 5)
    assert result is None


# --- Move ---

def test_move():
    board = Board()
    p = Piece(PieceType.COMMANDER, side="human")
    board.place(p, 0, 0)
    board.move(0, 0, 2, 3)
    assert board.get(0, 0) is None
    assert board.get(2, 3) == p


def test_get_piece_at_returns_correct_piece():
    board = Board()
    p = Piece(PieceType.BOMB, side="enemy")
    board.place(p, 6, 10)
    piece_at = board.get_piece_at(6, 10)
    assert piece_at == p
