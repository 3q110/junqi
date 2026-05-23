# execute_code Sandbox Limitations

## Sandbox path issue

The `execute_code` tool runs scripts in `/tmp/hermes_sandbox_*/` — a clean temp directory with NO project modules in `sys.path`.

**This means:**

```python
# FAILS — jiqi not in sys.path
from jiqi.board import Board  # ModuleNotFoundError: No module named 'jiqi'
```

**Workaround — use terminal instead:**

```bash
# DO THIS:
cd /home/loveback1987 && python -c "
from jiqi.board import Board
from jiqi.piece import Piece, PieceType
board = Board()
..."
```

## When to use which

| Tool | Use when |
|------|----------|
| `execute_code` | Multi-step logic with Python stdlib processing, conditional branching, filtering tool outputs |
| `terminal` | Any project code that needs imports, running tests, git commands, or anything in the project's working directory |

**Rule of thumb:** If you need `from jiqi...` or `import jiqi...`, use `terminal` with `cd` to the project root. Use `execute_code` only for pure stdlib processing (json parsing, string manipulation, math, etc.).
