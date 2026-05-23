from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.player import GameSetup, AIPlayer, HumanPlayer


# --- GameSetup tests ---

def test_setup_pieces_count():
    board = Board()
    GameSetup.setup_pieces(board)
    human_count = sum(1 for c in range(7) for r in range(5) if board.get(c, r) is not None)
    ai_count = sum(1 for c in range(7) for r in range(6, 11) if board.get(c, r) is not None)
    assert human_count == 24
    assert ai_count == 24


def test_no_pieces_on_river():
    board = Board()
    GameSetup.setup_pieces(board)
    row5 = sum(1 for c in range(7) if board.get(c, 5) is not None)
    assert row5 == 0


def test_flag_placed():
    board = Board()
    GameSetup.setup_pieces(board)
    flag_found = False
    for r in range(5):
        for c in range(7):
            p = board.get(c, r)
            if p and p.piece_type == PieceType.FLAG and p.side == "human":
                flag_found = True
    assert flag_found


def test_ai_flag_on_last_row():
    board = Board()
    GameSetup.setup_pieces(board)
    ai_flag_found = False
    for c in range(7):
        p = board.get(c, 10)
        if p and p.piece_type == PieceType.FLAG and p.side == "ai":
            ai_flag_found = True
    assert ai_flag_found


def test_no_duplicates():
    """Each board cell should have at most one piece."""
    board = Board()
    GameSetup.setup_pieces(board)
    cells = []
    for c in range(7):
        for r in range(11):
            p = board.get(c, r)
            if p is not None:
                cells.append((c, r))
    assert len(cells) == len(set(cells)), "Duplicate cells found"
    # Total pieces should be 24 per side
    assert len(cells) == 48, f"Expected 48 pieces total, got {len(cells)}"


def test_human_pieces_on_top_half():
    board = Board()
    GameSetup.setup_pieces(board)
    for c in range(7):
        for r in range(5, 11):
            p = board.get(c, r)
            assert p is None or p.side != "human", f"Human piece found at ({c},{r})"


def test_ai_pieces_on_bottom_half():
    board = Board()
    GameSetup.setup_pieces(board)
    for c in range(7):
        for r in range(5):
            p = board.get(c, r)
            assert p is None or p.side != "ai", f"AI piece found at ({c},{r})"


def test_piece_type_counts():
    board = Board()
    GameSetup.setup_pieces(board)
    human_types: dict = {}
    ai_types: dict = {}
    for c in range(7):
        for r in range(11):
            p = board.get(c, r)
            if p is None:
                continue
            key = (p.piece_type, p.side)
            counts = human_types if p.side == "human" else ai_types
            counts[key] = counts.get(key, 0) + 1

    # Check expected counts
    expected = {
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
    for side in ("human", "ai"):
        counts = human_types if side == "human" else ai_types
        for ptype, count in expected.items():
            assert counts.get((ptype, side), 0) == count, \
                f"Expected {count} {ptype.name} for {side}, got {counts.get((ptype, side), 0)}"


def test_commander_not_on_flag_row():
    """COMMANDER, ARMY_COMMANDER, DIVISION_COMMANDER cannot be on row 0 for human."""
    board = Board()
    GameSetup.setup_pieces(board)
    for c in range(7):
        p = board.get(c, 0)
        if p and p.side == "human":
            assert p.piece_type not in (
                PieceType.COMMANDER,
                PieceType.ARMY_COMMANDER,
                PieceType.DIVISION_COMMANDER,
            ), f"High-rank piece {p.piece_type} found on flag row at ({c},0)"


# --- AIPlayer tests ---

def test_ai_random_move():
    board = Board()
    GameSetup.setup_pieces(board)
    ai = AIPlayer(board, "电脑")
    move = ai.get_move()
    assert move is not None
    assert len(move) == 4


def test_ai_move_valid():
    board = Board()
    GameSetup.setup_pieces(board)
    ai = AIPlayer(board, "电脑")
    for _ in range(100):
        move = ai.get_move()
        assert move is not None
        assert 0 <= move[0] < 7
        assert 0 <= move[1] < 11
        assert 0 <= move[2] < 7
        assert 0 <= move[3] < 11


def test_ai_move_source_has_piece():
    board = Board()
    GameSetup.setup_pieces(board)
    ai = AIPlayer(board, "电脑")
    for _ in range(100):
        move = ai.get_move()
        src_col, src_row, dst_col, dst_row = move
        src_piece = board.get(src_col, src_row)
        assert src_piece is not None, f"Move source ({src_col},{src_row}) is empty"


def test_ai_move_dest_not_own_piece():
    board = Board()
    GameSetup.setup_pieces(board)
    ai = AIPlayer(board, "电脑")
    for _ in range(100):
        move = ai.get_move()
        src_col, src_row, dst_col, dst_row = move
        dst_piece = board.get(dst_col, dst_row)
        if dst_piece is not None:
            assert dst_piece.side != "ai", \
                f"AI moved onto own piece at ({dst_col},{dst_row})"


# --- HumanPlayer tests ---

def test_human_player_creation():
    board = Board()
    hp = HumanPlayer(board)
    assert hp.name == "玩家"


def test_human_player_custom_name():
    board = Board()
    hp = HumanPlayer(board, "小明")
    assert hp.name == "小明"


def test_human_player_get_move_raises():
    board = Board()
    hp = HumanPlayer(board)
    try:
        hp.get_move()
        assert False, "Expected NotImplementedError"
    except NotImplementedError:
        pass
