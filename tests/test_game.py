"""Tests for the Game class (jiqi/game.py)."""

from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.rules import RuleEngine
from jiqi.game import Game


# --- Game creation tests ---

def test_game_creation():
    game = Game()
    assert game.board is not None
    assert game.human_turn is True


def test_game_piece_count():
    game = Game()
    human_count = sum(1 for c in range(7) for r in range(11)
                      if game.board.get(c, r) and game.board.get(c, r).side == "human")
    ai_count = sum(1 for c in range(7) for r in range(11)
                   if game.board.get(c, r) and game.board.get(c, r).side == "ai")
    assert human_count == 24
    assert ai_count == 24


def test_game_flag_exists():
    game = Game()
    human_flag = None
    ai_flag = None
    for r in range(11):
        for c in range(7):
            p = game.board.get(c, r)
            if p and p.piece_type == PieceType.FLAG:
                if p.side == "human":
                    human_flag = p
                elif p.side == "ai":
                    ai_flag = p
    assert human_flag is not None
    assert ai_flag is not None


def test_game_turn_starts_with_human():
    game = Game()
    assert game.human_turn is True


def test_game_has_ui():
    game = Game()
    assert game.ui is not None


def test_game_has_human_player():
    game = Game()
    assert game.human_player is not None


def test_game_has_ai_player():
    game = Game()
    assert game.ai_player is not None


# --- Win/lose condition tests ---

def test_no_winner_at_start():
    game = Game()
    assert game.check_win() is False


def test_human_wins_when_ai_flag_captured():
    """Human wins when AI flag is captured."""
    game = Game()
    game.ai_flag_captured = True
    assert game.check_win() is True
    assert game.get_winner() == "human"


def test_ai_wins_when_human_flag_captured():
    """AI wins when human flag is captured."""
    game = Game()
    game.human_flag_captured = True
    assert game.check_win() is True
    assert game.get_winner() == "ai"


# --- process_move tests ---

def test_process_move_valid_empty_dest():
    """A valid move to an empty cell should succeed."""
    game = Game()
    board = game.board

    # Human SAPPER at (0,4) can move to (0,5) — empty river cell
    move = (0, 4, 0, 5)
    result = game.process_move(move)
    assert result is not None
    assert board.get(0, 4) is None
    assert board.get(0, 5) is not None
    assert board.get(0, 5).side == "human"


def test_process_move_invalid():
    """An invalid move should return None."""
    game = Game()
    # Move from empty cell
    move = (6, 1, 6, 2)  # (6,1) is empty
    result = game.process_move(move)
    assert result is None


def test_process_move_same_side_dest():
    """Moving to own piece should fail."""
    game = Game()
    board = game.board
    # Human FLAG at (3,0), human COMMANDER at (0,1) — not adjacent
    # Human COMMANDER at (0,1), human ARMY_COMMANDER at (1,1) — adjacent, same side
    move = (0, 1, 1, 1)
    result = game.process_move(move)
    assert result is None


def test_process_move_battle_attacker_wins():
    """When attacker wins a battle, defender is removed and attacker moves."""
    game = Game()
    board = game.board

    # Manually set up: human COMMANDER at (0,5), AI ARMY_COMMANDER at (0,6)
    board.remove(0, 5)
    board.remove(0, 6)
    attacker = Piece(PieceType.COMMANDER, side="human")
    defender = Piece(PieceType.ARMY_COMMANDER, side="ai")
    board.place(attacker, 0, 5)
    board.place(defender, 0, 6)

    move = (0, 5, 0, 6)
    result = game.process_move(move)
    assert result is not None
    assert "attacker_wins" in result
    assert board.get(0, 5) is None
    assert board.get(0, 6) is not None
    assert board.get(0, 6).side == "human"


def test_process_move_battle_both_die():
    """Equal rank pieces should both be removed."""
    game = Game()
    board = game.board

    # Place two COMMANDERs adjacent across the river
    board.remove(0, 5)
    board.remove(0, 6)
    attacker = Piece(PieceType.COMMANDER, side="human")
    defender = Piece(PieceType.COMMANDER, side="ai")
    board.place(attacker, 0, 5)
    board.place(defender, 0, 6)

    move = (0, 5, 0, 6)
    result = game.process_move(move)
    assert result is not None
    assert "both_die" in result
    assert board.get(0, 5) is None
    assert board.get(0, 6) is None


def test_process_move_battle_attacker_loses():
    """When attacker loses, attacker is removed and defender stays."""
    game = Game()
    board = game.board

    # Commander (rank 1) vs Mine — attacker loses
    board.remove(0, 5)
    board.remove(0, 6)
    attacker = Piece(PieceType.COMMANDER, side="human")
    defender = Piece(PieceType.MINE, side="ai")
    board.place(attacker, 0, 5)
    board.place(defender, 0, 6)

    move = (0, 5, 0, 6)
    result = game.process_move(move)
    assert result is not None
    assert "attacker_loses" in result
    assert board.get(0, 5) is None
    assert board.get(0, 6) is not None


def test_process_move_flag_capture():
    """Moving onto enemy flag captures it and wins the game."""
    game = Game()
    board = game.board

    # Place AI flag adjacent to a human piece across the river
    board.remove(0, 5)
    board.remove(0, 6)
    attacker = Piece(PieceType.COMMANDER, side="human")
    ai_flag = Piece(PieceType.FLAG, side="ai")
    board.place(attacker, 0, 5)
    board.place(ai_flag, 0, 6)

    move = (0, 5, 0, 6)
    result = game.process_move(move)
    assert result is not None
    assert "attacker_wins" in result
    assert board.get(0, 6) is not None  # attacker moved there
    assert board.get(0, 6).side == "human"
    assert game.ai_flag_captured is True


def test_process_move_on_empty_cell():
    """Moving to an empty cell should work (no battle)."""
    game = Game()
    board = game.board

    # Human piece at (0,4) can move to (0,5) — empty cell in river
    move = (0, 4, 0, 5)
    result = game.process_move(move)
    assert result is not None
    assert board.get(0, 4) is None
    assert board.get(0, 5) is not None
    assert board.get(0, 5).side == "human"


# --- Turn management tests ---

def test_turn_switches_after_human_move():
    """After processing a human move, turn should switch to AI."""
    game = Game()
    board = game.board

    # Human makes a valid move
    move = (0, 4, 0, 5)
    game.process_move(move)
    assert game.human_turn is False


def test_turn_switches_back_after_ai_move():
    """After processing an AI move, turn should switch back to human."""
    game = Game()
    board = game.board

    # First, human makes a move
    game.process_move((0, 4, 0, 5))
    assert game.human_turn is False

    # Now AI makes a move
    ai_move = game.ai_player.get_move()
    if ai_move:
        game.process_move(ai_move)
        assert game.human_turn is True


def test_turn_stays_human_after_invalid_move():
    """An invalid move should not switch turns."""
    game = Game()
    board = game.board

    # Try to move to own piece — invalid
    move = (0, 1, 1, 1)  # (1,1) has human ARMY_COMMANDER
    game.process_move(move)
    assert game.human_turn is True


# --- get_winner tests ---

def test_get_winner_returns_human_when_ai_flag_gone():
    game = Game()
    game.ai_flag_captured = True
    assert game.get_winner() == "human"


def test_get_winner_returns_ai_when_human_flag_gone():
    game = Game()
    game.human_flag_captured = True
    assert game.get_winner() == "ai"


def test_get_winner_returns_none_when_no_winner():
    game = Game()
    assert game.get_winner() is None


# --- check_win via board state ---

def test_check_win_detects_missing_ai_flag():
    """If AI flag is removed from board, human wins."""
    game = Game()
    # Find and remove AI flag
    for r in range(11):
        for c in range(7):
            p = game.board.get(c, r)
            if p and p.piece_type == PieceType.FLAG and p.side == "ai":
                game.board.remove(c, r)
                break
        else:
            continue
        break

    assert game.check_win() is True
    assert game.get_winner() == "human"


def test_check_win_detects_missing_human_flag():
    """If human flag is removed from board, AI wins."""
    game = Game()
    # Find and remove human flag
    for r in range(11):
        for c in range(7):
            p = game.board.get(c, r)
            if p and p.piece_type == PieceType.FLAG and p.side == "human":
                game.board.remove(c, r)
                break
        else:
            continue
        break

    assert game.check_win() is True
    assert game.get_winner() == "ai"
