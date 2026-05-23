# Board Game Testing Patterns

Patterns for testing "no valid moves" scenarios, battle resolution edge cases, common pitfalls when modifying board state, and CLI game interaction patterns.

## Testing "No Valid Moves"

**Problem:** You need to test that `AIPlayer.get_move()` returns `None` when no piece can legally move. But any piece you place on the board can potentially escape — mines can move in 4 directions, bombs can move, etc. Blocking one direction creates another escape route.

**Solution: Fill the entire board with same-side pieces.**

```python
def test_no_valid_moves():
    board = Board()
    for r in range(11):
        for c in range(7):
            if r == 0 and c == 3:
                board.place(Piece(PieceType.FLAG, side="ai"), c, r)
            else:
                board.place(Piece(PieceType.MINE, side="ai"), c, r)

    ai = AIPlayer(board)
    move = ai.get_move()
    assert move is None
```

**Why this works:** `can_move` rejects moving to own pieces. If every cell is occupied by same-side pieces, no move is possible. This is the only reliable way to guarantee "no valid moves" in a grid-based game where pieces can move to adjacent empty cells.

**Why partial blocking doesn't work:** Placing pieces to block one piece's moves means the blocking pieces themselves have escape routes. This creates an infinite regress — blocking escapes requires more pieces, which have more escapes.

## Testing Battle Resolution

**Problem:** Tests that modify board state (e.g., removing a piece to set up a scenario) can silently change the expected behavior.

**Pitfall:** If a test does `board.remove(flag_col, flag_row)` to clear a cell before placing a new piece, the removed piece is GONE. Later assertions that expect that piece to exist (e.g., "attacker captures flag") will fail because the flag is no longer on the board.

**Fix:** Don't remove pieces you need. Use `board.get()` to verify positions before modifying, and only remove pieces that are truly no longer needed.

```python
# BAD: removes the flag, then tries to test flag capture
board.remove(flag_col, flag_row)  # flag is gone!
board.place(commander, 3, 9)
# Now commander moving to (3,10) finds EMPTY cell, not a flag.

# GOOD: place commander adjacent without removing the flag
board.remove(3, 9)  # only clear the source cell
# Flag still at (3,10) — battle works as expected.
```

## Testing Bomb Rules

**Key rule:** A BOMB explodes with ANY piece it touches — both attacker and defender die.

**Common bug:** Only handling the case where the defender is a bomb, not the attacker.

```python
# BUG: only checks if defender is bomb
if defender.piece_type == PieceType.BOMB:
    return "both_die"
# Missing: attacker is also a bomb!

# FIX: check both
if attacker.piece_type == PieceType.BOMB or defender.piece_type == PieceType.BOMB:
    return "both_die"
```

## Testing Player-UI Wiring

**Problem:** Player classes need a UI object for interactive input, but it's often not passed during initialization.

**Pitfall:** `HumanPlayer.__init__()` accepts a `ui` parameter but the game loop creates `HumanPlayer(board)` without passing `ui`, causing `AttributeError: 'HumanPlayer' object has no attribute 'ui'` at runtime.

**Fix:** Always wire the UI at initialization time:

```python
# In Game.__init__:
self.ui = TerminalUI()
self.human_player = HumanPlayer(self.board, ui=self.ui)  # pass ui!
```

**Debugging tip:** If the game starts but crashes on the first player turn, check that all `Player` objects received their `ui` dependency.

## CLI Game: Two-Step Move Selection Pattern

**Problem:** In a CLI game, players need to select a piece first, then a destination. A single `input()` call that asks for "source destination" is error-prone — players often mistype or don't know valid destinations.

**Solution: Two-step recursive `prompt_move()` method.**

```python
def prompt_move(self, board, selected=None):
    """Two-step move selection: first select piece, then select destination.

    Returns (src_col, src_row, dst_col, dst_row) or None.
    """
    if selected is None:
        # Step 1: select a piece
        while True:
            print("选择棋子 (格式: col,row, 输入 q 退出): ", end="")
            raw = input().strip()
            if raw.lower() in ("q", "quit", "exit"):
                return None
            col, row = parse_coords(raw)
            piece = board.get(col, row)
            if not piece or piece.side != "human":
                print("这不是你的棋子")
                continue
            selected = (col, row)
            print(f"已选择: ({col},{row}) — 请选择目标位置 (输入 c 取消)")
            break

        # Step 2: select destination
        while True:
            print("选择目标 (格式: col,row, 输入 c 取消): ", end="")
            raw = input().strip()
            if raw.lower() in ("c", "cancel"):
                selected = None  # restart
                return self.prompt_move(board, selected)
            dst_col, dst_row = parse_coords(raw)
            return (selected[0], selected[1], dst_col, dst_row)
    else:
        return self.prompt_move(board, None)
```

**Key design decisions:**
- **Recursive restart on cancel:** When the player cancels in step 2, `selected` is reset to `None` and the method recurses back to step 1. This avoids nested state management.
- **Validation in step 1:** Only allow selecting own pieces. Invalid selections loop without advancing state.
- **`q` to quit, `c` to cancel:** Distinct escape hatches prevent accidental exits.
- **Return `None` on quit:** The game loop should check for `None` and exit gracefully.

**Integration with `HumanPlayer`:**

```python
class HumanPlayer:
    def __init__(self, board, name="玩家", ui=None):
        self.board = board
        self.name = name
        self.ui = ui
        self._selected = None

    def get_move(self):
        if self.ui is None:
            raise NotImplementedError("HumanPlayer.get_move() requires a UI")
        return self.ui.prompt_move(self.board, self._selected)
```

**EOFError handling:** In non-interactive contexts (piped input, CI), `input()` raises `EOFError`. Always catch it in the game loop:

```python
try:
    game.run()
except (KeyboardInterrupt, EOFError):
    print("\n游戏退出。")
    sys.exit(0)
```