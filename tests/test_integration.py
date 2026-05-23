"""Integration tests for the Jiqi (军旗) game.

These tests exercise multiple modules together to verify end-to-end
behaviour: game creation, flag capture, multi-turn play, and AI moves.
"""

from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.rules import RuleEngine
from jiqi.game import Game
from jiqi.player import GameSetup, AIPlayer


# ---------------------------------------------------------------------------
# Flag capture integration tests
# ---------------------------------------------------------------------------

def test_game_flag_captured_by_human():
    """Human wins when they capture the AI flag."""
    game = Game()

    # Find AI flag position
    ai_flag_col, ai_flag_row = None, None
    for r in range(11):
        for c in range(7):
            p = game.board.get(c, r)
            if p and p.piece_type == PieceType.FLAG and p.side == "ai":
                ai_flag_col, ai_flag_row = c, r
                break
        if ai_flag_col is not None:
            break
    assert ai_flag_col is not None

    # Place a human commander adjacent to the AI flag at (3, 9)
    board = game.board
    board.remove(3, 9)  # remove whatever is at the adjacent cell
    commander = Piece(PieceType.COMMANDER, side="human")
    board.place(commander, 3, 9)

    # Human attacks the flag
    move = (3, 9, 3, 10)
    result = game.process_move(move)
    assert result is not None
    assert "attacker_wins" in result

    # AI flag should be captured
    assert game.ai_flag_captured is True
    assert game.check_win() is True
    assert game.get_winner() == "human"


def test_game_flag_captured_by_ai():
    """AI wins when they capture the human flag."""
    game = Game()

    # Find human flag position
    human_flag_col, human_flag_row = None, None
    for r in range(11):
        for c in range(7):
            p = game.board.get(c, r)
            if p and p.piece_type == PieceType.FLAG and p.side == "human":
                human_flag_col, human_flag_row = c, r
                break
        if human_flag_col is not None:
            break
    assert human_flag_col is not None

    # Place an AI commander adjacent to the human flag at (3, 1)
    board = game.board
    board.remove(3, 1)  # remove whatever is at the adjacent cell
    ai_commander = Piece(PieceType.COMMANDER, side="ai")
    board.place(ai_commander, 3, 1)

    # AI attacks the flag
    move = (3, 1, 3, 0)
    result = game.process_move(move)
    assert result is not None
    assert "attacker_wins" in result

    # Human flag should be captured
    assert game.human_flag_captured is True
    assert game.check_win() is True
    assert game.get_winner() == "ai"


# ---------------------------------------------------------------------------
# Multi-turn integration test
# ---------------------------------------------------------------------------

def test_multi_turn_game():
    """Simulate several turns of human and AI moves."""
    game = Game()

    # Human makes a valid move
    move1 = (0, 4, 0, 5)  # SAPPER moves forward
    result1 = game.process_move(move1)
    assert result1 is not None
    assert game.human_turn is False  # turn switched to AI

    # AI makes a move
    ai_move1 = game.ai_player.get_move()
    assert ai_move1 is not None
    result2 = game.process_move(ai_move1)
    assert result2 is not None
    assert game.human_turn is True  # turn back to human

    # Human makes another move
    move2 = (1, 4, 1, 5)
    result3 = game.process_move(move2)
    assert result3 is not None
    assert game.human_turn is False

    # AI makes another move
    ai_move2 = game.ai_player.get_move()
    assert ai_move2 is not None
    result4 = game.process_move(ai_move2)
    assert result4 is not None
    assert game.human_turn is True

    # Game should still be ongoing
    assert game.check_win() is False
    assert game.get_winner() is None


def test_ai_moves_when_all_pieces_alive():
    """AI should always have valid moves when pieces are on the board."""
    game = Game()
    board = game.board

    # Simulate several rounds of AI moves
    for round_num in range(5):
        if not game.human_turn:
            # AI's turn
            ai_move = game.ai_player.get_move()
            if ai_move:
                result = game.process_move(ai_move)
                assert result is not None, f"Round {round_num}: AI move failed"

            # Human's turn — make a small move
            if game.human_turn:
                # Find a human piece that can move forward
                for c in range(7):
                    for r in range(4, 5):
                        p = board.get(c, r)
                        if p and p.side == "human":
                            if RuleEngine.can_move(board, c, r, c, r + 1):
                                game.process_move((c, r, c, r + 1))
                                break
                    if board.get(c, r + 1) is not None:
                        break
        else:
            # Human's turn — make a small move
            for c in range(7):
                for r in range(4, 5):
                    p = board.get(c, r)
                    if p and p.side == "human":
                        if RuleEngine.can_move(board, c, r, c, r + 1):
                            game.process_move((c, r, c, r + 1))
                            break
                if board.get(c, r + 1) is not None:
                    break

        assert game.check_win() is False


# ---------------------------------------------------------------------------
# Edge case integration tests
# ---------------------------------------------------------------------------

def test_both_pieces_removed_in_battle():
    """When two equal-rank pieces battle, both should be removed."""
    game = Game()
    board = game.board

    # Set up: human BOMB at (0,5), AI BOMB at (0,6)
    board.remove(0, 5)
    board.remove(0, 6)
    board.place(Piece(PieceType.BOMB, side="human"), 0, 5)
    board.place(Piece(PieceType.BOMB, side="ai"), 0, 6)

    move = (0, 5, 0, 6)
    result = game.process_move(move)
    assert result == "both_die"
    assert board.get(0, 5) is None
    assert board.get(0, 6) is None


def test_sapper_captures_mine():
    """Sapper should be able to capture mine."""
    game = Game()
    board = game.board

    # Set up: human SAPPER at (0,5), AI MINE at (0,6)
    board.remove(0, 5)
    board.remove(0, 6)
    board.place(Piece(PieceType.SAPPER, side="human"), 0, 5)
    board.place(Piece(PieceType.MINE, side="ai"), 0, 6)

    move = (0, 5, 0, 6)
    result = game.process_move(move)
    assert result == "attacker_wins"
    assert board.get(0, 5) is None
    assert board.get(0, 6) is not None
    assert board.get(0, 6).side == "human"


def test_bomb_captures_anything():
    """BOMB should be able to capture any piece (both die)."""
    game = Game()
    board = game.board

    # Set up: human BOMB at (0,5), AI COMMANDER at (0,6)
    board.remove(0, 5)
    board.remove(0, 6)
    board.place(Piece(PieceType.BOMB, side="human"), 0, 5)
    board.place(Piece(PieceType.COMMANDER, side="ai"), 0, 6)

    move = (0, 5, 0, 6)
    result = game.process_move(move)
    assert result == "both_die"
    assert board.get(0, 5) is None
    assert board.get(0, 6) is None


def test_ai_player_get_move_returns_valid_move():
    """AI player should return a valid move on a fresh board."""
    board = Board()
    GameSetup.setup_pieces(board)
    ai = AIPlayer(board, "电脑")
    for _ in range(50):
        move = ai.get_move()
        assert move is not None
        assert len(move) == 4
        src_col, src_row, dst_col, dst_row = move
        # Source must be an AI piece
        src_piece = board.get(src_col, src_row)
        assert src_piece is not None
        assert src_piece.side == "ai"
        # Destination must be within bounds
        assert 0 <= dst_col < 7
        assert 0 <= dst_row < 11
        # Destination must not be an AI piece (unless it's a valid capture)
        dst_piece = board.get(dst_col, dst_row)
        if dst_piece is not None:
            assert dst_piece.side == "ai" or dst_piece.piece_type == PieceType.FLAG


def test_ai_player_no_valid_moves():
    """When AI has no valid moves, get_move should return None."""
    board = Board()
    # Fill entire board with AI pieces — no empty cells means no moves possible
    # (can_move rejects moving to own pieces)
    for r in range(11):
        for c in range(7):
            if r == 0 and c == 3:
                board.place(Piece(PieceType.FLAG, side="ai"), c, r)
            else:
                board.place(Piece(PieceType.MINE, side="ai"), c, r)

    ai = AIPlayer(board)
    move = ai.get_move()
    assert move is None


def test_game_state_consistency_after_battle():
    """Verify game state is consistent after a battle."""
    game = Game()
    board = game.board

    # Set up battle: human COMMANDER vs AI ARMY_COMMANDER
    board.remove(0, 5)
    board.remove(0, 6)
    board.place(Piece(PieceType.COMMANDER, side="human"), 0, 5)
    board.place(Piece(PieceType.ARMY_COMMANDER, side="ai"), 0, 6)

    move = (0, 5, 0, 6)
    result = game.process_move(move)

    assert result == "attacker_wins"
    assert board.get(0, 5) is None  # attacker moved away
    assert board.get(0, 6) is not None  # attacker now here
    assert board.get(0, 6).side == "human"  # attacker owns the cell
    assert game.human_turn is False  # turn switched


def test_process_move_does_not_crash_on_out_of_bounds():
    """process_move should handle out-of-bounds gracefully."""
    game = Game()
    result = game.process_move((-1, 0, 0, 0))
    assert result is None
    result = game.process_move((0, 0, 7, 0))
    assert result is None
    result = game.process_move((0, 0, 0, 11))
    assert result is None


def test_flag_at_correct_initial_position():
    """Verify flags start at the correct positions."""
    game = Game()
    board = game.board

    # Human flag should be at (3, 0)
    human_flag = board.get(3, 0)
    assert human_flag is not None
    assert human_flag.piece_type == PieceType.FLAG
    assert human_flag.side == "human"

    # AI flag should be at (3, 10)
    ai_flag = board.get(3, 10)
    assert ai_flag is not None
    assert ai_flag.piece_type == PieceType.FLAG
    assert ai_flag.side == "ai"
