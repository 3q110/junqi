from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.rules import RuleEngine


# -- movement tests --

def test_can_move_adjacent():
    board = Board()
    p = Piece(PieceType.COMMANDER, side="human")
    board.place(p, 0, 0)
    assert RuleEngine.can_move(board, 0, 0, 1, 0)  # right
    assert RuleEngine.can_move(board, 0, 0, 0, 1)  # down


def test_can_move_diagonal_fails():
    board = Board()
    p = Piece(PieceType.COMMANDER, side="human")
    board.place(p, 0, 0)
    assert not RuleEngine.can_move(board, 0, 0, 1, 1)  # diagonal


def test_cannot_move_off_board():
    board = Board()
    p = Piece(PieceType.COMMANDER, side="human")
    board.place(p, 0, 0)
    assert not RuleEngine.can_move(board, 0, 0, -1, 0)
    assert not RuleEngine.can_move(board, 0, 0, 0, -1)


def test_cannot_move_to_own_piece():
    board = Board()
    p1 = Piece(PieceType.COMMANDER, side="human")
    p2 = Piece(PieceType.ARMY_COMMANDER, side="human")
    board.place(p1, 0, 0)
    board.place(p2, 1, 0)
    assert not RuleEngine.can_move(board, 0, 0, 1, 0)


def test_can_move_to_enemy_piece():
    board = Board()
    p1 = Piece(PieceType.COMMANDER, side="human")
    p2 = Piece(PieceType.COMMANDER, side="ai")
    board.place(p1, 0, 0)
    board.place(p2, 1, 0)
    assert RuleEngine.can_move(board, 0, 0, 1, 0)


# -- battle resolution tests --

def test_battle_normal():
    assert RuleEngine.resolve_battle(
        Piece(PieceType.COMMANDER, "human"),
        Piece(PieceType.ARMY_COMMANDER, "ai")
    ) == "attacker_wins"


def test_battle_equal_rank():
    assert RuleEngine.resolve_battle(
        Piece(PieceType.COMMANDER, "human"),
        Piece(PieceType.COMMANDER, "ai")
    ) == "both_die"


def test_battle_bomb():
    result = RuleEngine.resolve_battle(
        Piece(PieceType.COMMANDER, "human"),
        Piece(PieceType.BOMB, "ai")
    )
    assert result == "both_die"


def test_battle_sapper_vs_mine():
    assert RuleEngine.resolve_battle(
        Piece(PieceType.SAPPER, "human"),
        Piece(PieceType.MINE, "ai")
    ) == "attacker_wins"


def test_battle_commander_vs_mine():
    assert RuleEngine.resolve_battle(
        Piece(PieceType.COMMANDER, "human"),
        Piece(PieceType.MINE, "ai")
    ) == "attacker_loses"


def test_battle_capture_flag():
    assert RuleEngine.resolve_battle(
        Piece(PieceType.COMMANDER, "human"),
        Piece(PieceType.FLAG, "ai")
    ) == "attacker_wins"


def test_battle_flag_vs_flag():
    assert RuleEngine.resolve_battle(
        Piece(PieceType.FLAG, "human"),
        Piece(PieceType.FLAG, "ai")
    ) == "invalid"


def test_battle_flag_cannot_eat():
    assert RuleEngine.resolve_battle(
        Piece(PieceType.FLAG, "human"),
        Piece(PieceType.COMMANDER, "ai")
    ) == "invalid"
