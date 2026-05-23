# Board Game Testing Patterns

Patterns for testing board game logic, especially "no valid moves" scenarios.

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
