"""终端 UI 模块 - 显示棋盘和交互"""

import sys
from typing import Optional, Tuple
from jiqi.board import Board
from jiqi.piece import Piece, PieceType


class UI:
    """终端界面"""

    # ANSI 颜色
    RED = "\033[91m"
    BLACK = "\033[90m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"

    @classmethod
    def clear_screen(cls):
        """清屏"""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    @classmethod
    def display_board(cls, board: Board, last_move: Optional[Tuple[int, int, int, int]] = None):
        """
        显示棋盘。

        棋盘布局（标准军旗 11x7）：
        行 0-4: 黑方区域
        行 5:   楚河汉界
        行 6-10: 红方区域
        """
        cls.clear_screen()

        # 标题
        print(f"\n  {cls.BOLD}{'='*50}{cls.RESET}")
        print(f"  {cls.BOLD}            军 棋 人 机 对 战{cls.RESET}")
        print(f"  {cls.BOLD}{'='*50}{cls.RESET}\n")

        # 列号
        print("     " + "".join(f" {i} " for i in range(7)))
        print("     " + "+".join("---" for _ in range(7)))

        for r in range(board.HEIGHT):
            if r == 5:
                # 楚河汉界
                print(f"{r:2d} | {'~~~~~'*1 + '~'*3}")
                print("     " + "+".join("---" for _ in range(7)))
                continue

            row_cells = []
            for c in range(7):
                piece = board.get(r, c)
                cell = cls._render_cell(piece, r, c, board)

                # 标记最后一步
                if last_move and (r, c) in [(last_move[0], last_move[1]), (last_move[2], last_move[3])]:
                    cell = f"{cls.YELLOW}{cell}{cls.RESET}"

                row_cells.append(cell)

            # 行号
            row_str = f"{r:2d} | " + " ".join(row_cells)

            # 标记铁路
            if r in board.RAILWAY_ROWS or (r, 0) in board.VERTICAL_RAILWAY or (r, 6) in board.VERTICAL_RAILWAY:
                row_str = f"  {row_str}"
            else:
                row_str = f"  {row_str}"

            print(row_str)
            print("     " + "+".join("---" for _ in range(7)))

        # 最后移动提示
        if last_move:
            fr, fc, tr, tc = last_move
            print(f"\n  {cls.YELLOW}最后一步: ({fr},{fc}) -> ({tr},{tc}){cls.RESET}")

        print()

    @classmethod
    def _render_cell(cls, piece: Optional[Piece], row: int, col: int, board: Board) -> str:
        """渲染单个格子"""
        if piece is None:
            # 特殊位置标记
            if (row, col) in board.FLAG_POSITIONS:
                return "[★]"
            elif (row, col) in board.HEADQUARTERS:
                return "[营]"
            else:
                return "[·]"

        # 根据颜色着色
        color = cls.RED if piece.side == "red" else cls.BLACK
        name = piece.name[:2] if len(piece.name) > 2 else piece.name
        return f"{color}[{name}]{cls.RESET}"

    @classmethod
    def get_human_move(cls, board: Board) -> Tuple[int, int, int, int]:
        """
        获取人类玩家的移动输入。

        Returns:
            (from_row, from_col, to_row, to_col)
        """
        from jiqi.rules import Rules

        while True:
            print(f"\n  {cls.GREEN}红方回合 - 请输入移动指令{cls.RESET}")
            print("  格式: 行,列 行,列  (例如: 6,3 7,3)")
            print("  输入 'q' 退出, 'h' 查看帮助")
            print()

            try:
                user_input = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  游戏退出。")
                sys.exit(0)

            if user_input.lower() == 'q':
                print("  游戏退出。")
                sys.exit(0)
            if user_input.lower() == 'h':
                cls.print_help()
                continue

            try:
                parts = user_input.split()
                if len(parts) != 2:
                    print("  {0}错误: 请输入两个坐标，用空格分隔{1}".format(cls.YELLOW, cls.RESET))
                    continue

                fr_str, fc_str = parts[0].split(',')
                tr_str, tc_str = parts[1].split(',')

                fr, fc = int(fr_str), int(fc_str)
                tr, tc = int(tr_str), int(tc_str)

                if not board.in_bounds(fr, fc) or not board.in_bounds(tr, tc):
                    print("  {0}错误: 坐标超出范围{1}".format(cls.YELLOW, cls.RESET))
                    continue

                piece = board.get(fr, fc)
                if not piece:
                    print("  {0}错误: 起始位置没有棋子{1}".format(cls.YELLOW, cls.RESET))
                    continue
                if piece.side != "red":
                    print("  {0}错误: 这不是你的棋子{1}".format(cls.YELLOW, cls.RESET))
                    continue
                if not piece.is_movable:
                    print("  {0}错误: {1} 不能移动{1}".format(cls.YELLOW, piece.name, cls.RESET))
                    continue

                if not Rules.is_valid_move(board, fr, fc, tr, tc):
                    print("  {0}错误: 非法移动{1}".format(cls.YELLOW, cls.RESET))
                    continue

                return (fr, fc, tr, tc)

            except ValueError:
                print("  {0}错误: 格式不正确，请使用 行,列 行,列{1}".format(cls.YELLOW, cls.RESET))
                continue

    @classmethod
    def print_help(cls):
        """打印帮助信息"""
        print(f"\n  {cls.BOLD}{'─'*40}{cls.RESET}")
        print(f"  {cls.BOLD}军棋规则{cls.RESET}")
        print(f"  {'─'*40}")
        print("  棋子等级: 司令 > 军长 > 师长 > 旅长 > 团长")
        print("            > 营长 > 连长 > 排长 > 工兵")
        print("  炸弹: 与任何棋子同归于尽")
        print("  地雷: 只能被工兵或炸弹消灭")
        print("  军旗: 被捉即输")
        print("  工兵: 可在铁路线上任意行走")
        print("  移动: 输入 起始行,起始列 目标行,目标列")
        print(f"  {'─'*40}\n")

    @classmethod
    def print_game_over(cls, result: str, board: Board):
        """打印游戏结束信息"""
        cls.clear_screen()
        print(f"\n  {cls.BOLD}{'='*50}{cls.RESET}")
        if result == "red_wins":
            print(f"  {cls.RED}{cls.BOLD}        🎉 红方获胜！🎉{cls.RESET}")
        else:
            print(f"  {cls.BLACK}{cls.BOLD}        🤖 黑方(AI)获胜！{cls.RESET}")
        print(f"  {cls.BOLD}{'='*50}{cls.RESET}\n")
        cls.display_board(board)

    @classmethod
    def print_setup_board(cls, board: Board):
        """显示初始布局"""
        cls.clear_screen()
        print(f"\n  {cls.BOLD}{'='*50}{cls.RESET}")
        print(f"  {cls.BOLD}            军 棋 人 机 对 战{cls.RESET}")
        print(f"  {cls.BOLD}{'='*50}{cls.RESET}")
        print(f"\n  {cls.GREEN}你控制红方（下方），AI 控制黑方（上方）{cls.RESET}\n")
        cls.display_board(board)
