"""游戏主模块 - 初始化棋盘、游戏循环、入口点"""

import random
import sys
from typing import Optional, Tuple

from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.rules import Rules
from jiqi.ai import RandomAI
from jiqi.ui import UI


class GameSetup:
    """游戏初始化 - 设置初始棋盘布局"""

    # 每方24枚棋子配置（标准军旗）
    # 司令×2 军长×2 师长×2 旅长×2 团长×2 营长×2 连长×2
    # 工兵×3 炸弹×3 地雷×3 军旗×1
    PIECE_CONFIG = [
        (PieceType.COMMANDER, 2),
        (PieceType.ARMY_COMMANDER, 2),
        (PieceType.DIVISION_COMMANDER, 2),
        (PieceType.BRIGADE_COMMANDER, 2),
        (PieceType.REGIMENT_COMMANDER, 2),
        (PieceType.BATTALION_COMMANDER, 2),
        (PieceType.COMPANY_COMMANDER, 2),
        (PieceType.SAPPER, 3),
        (PieceType.BOMB, 3),
        (PieceType.MINE, 3),
        (PieceType.FLAG, 1),
    ]

    @classmethod
    def setup_board(cls) -> Board:
        """创建并初始化棋盘"""
        board = Board()

        # 黑方（上方，行 0-3 放置棋子）
        cls._place_side(board, "black", rows=[0, 1, 2, 3], flag_positions=[(0, 2), (0, 4)])

        # 红方（下方，行 7-10 放置棋子）
        cls._place_side(board, "red", rows=[7, 8, 9, 10], flag_positions=[(10, 2), (10, 4)])

        return board

    @classmethod
    def _place_side(cls, board: Board, side: str, rows: list, flag_positions: list):
        """放置一方的棋子（25枚）

        标准布局规则：
        - 军旗放在大本营（随机从两个大本营选一个）
        - 地雷放在己方后两行
        - 炸弹不能放在第一排（己方底线）
        - 其余棋子随机分布
        """
        # 生成棋子列表
        pieces = []
        for piece_type, count in cls.PIECE_CONFIG:
            pieces.extend([piece_type] * count)

        # 移除军旗（单独放置）
        pieces.remove(PieceType.FLAG)

        # 分离地雷、炸弹和其余棋子
        mines = [pt for pt in pieces if pt == PieceType.MINE]
        bombs = [pt for pt in pieces if pt == PieceType.BOMB]
        remaining = [pt for pt in pieces if pt not in (PieceType.MINE, PieceType.BOMB)]

        # 随机打乱
        random.shuffle(mines)
        random.shuffle(bombs)
        random.shuffle(remaining)

        # 1. 军旗放在随机一个大本营
        random.shuffle(flag_positions)
        flag_r, flag_c = flag_positions[0]
        board.place(Piece(PieceType.FLAG, side), flag_r, flag_c)

        # 2. 地雷放在己方后两行（最靠近己方底线的两行）
        if side == "black":
            back_rows = [rows[0], rows[1]]  # 行 0, 1
            forbidden_bomb_row = rows[0]    # 炸弹不能放在行 0
        else:
            back_rows = [rows[-1], rows[-2]]  # 行 10, 9
            forbidden_bomb_row = rows[-1]     # 炸弹不能放在行 10

        back_positions = [(r, c) for r in back_rows for c in range(7)
                          if board.get(r, c) is None]
        random.shuffle(back_positions)
        for i, pt in enumerate(mines):
            r, c = back_positions[i]
            board.place(Piece(pt, side), r, c)

        # 3. 炸弹不能放在第一排（己方底线）
        bomb_positions = [(r, c) for r in rows if r != forbidden_bomb_row
                          for c in range(7) if board.get(r, c) is None]
        random.shuffle(bomb_positions)
        for i, pt in enumerate(bombs):
            r, c = bomb_positions[i]
            board.place(Piece(pt, side), r, c)

        # 4. 其余棋子随机放置到剩余空位
        remaining_positions = [(r, c) for r in rows for c in range(7)
                               if board.get(r, c) is None]
        random.shuffle(remaining_positions)
        for i, pt in enumerate(remaining):
            r, c = remaining_positions[i]
            board.place(Piece(pt, side), r, c)


class Game:
    """游戏主循环"""

    def __init__(self):
        self.board = GameSetup.setup_board()
        self.human_player = None  # 红方人类玩家
        self.ai_player = RandomAI(side="black", name="AI")
        self.current_side = "black"  # 黑方先手
        self.last_move = None
        self.move_count = 0

    def run(self):
        """运行游戏"""
        UI.print_setup_board(self.board)
        input("  按 Enter 开始游戏...")

        while True:
            self._play_turn()
            self.move_count += 1

            result = Rules.check_game_over(self.board)
            if result:
                UI.print_game_over(result, self.board)
                break

    def _play_turn(self):
        """执行一个回合"""
        if self.current_side == "black":
            self._ai_turn()
        else:
            self._human_turn()

        # 切换回合
        self.current_side = "red" if self.current_side == "black" else "black"

    def _human_turn(self):
        """人类玩家回合"""
        try:
            fr, fc, tr, tc = UI.get_human_move(self.board)
            self._execute_move(fr, fc, tr, tc, "红方")
        except SystemExit:
            raise

    def _ai_turn(self):
        """AI 回合"""
        print(f"\n  {UI.BLACK}AI 思考中...{UI.RESET}")
        import time
        time.sleep(1)

        try:
            fr, fc, tr, tc = self.ai_player.make_move(self.board)
            self._execute_move(fr, fc, tr, tc, "AI")
        except ValueError as e:
            print(f"  {UI.YELLOW}{e}{UI.RESET}")
            print("  AI 无法移动，跳过回合。")

    def _execute_move(self, fr: int, fc: int, tr: int, tc: int, player_name: str):
        """执行移动并显示结果"""
        piece = self.board.get(fr, fc)
        target = self.board.get(tr, tc)

        result = Rules.resolve_combat(piece, target)

        # 执行移动
        captured = self.board.move(piece, fr, fc, tr, tc)
        self.last_move = (fr, fc, tr, tc)

        # 显示移动信息
        move_str = f"{player_name}: {piece.name} ({fr},{fc}) -> ({tr},{tc})"

        if result == "no_combat":
            print(f"  {move_str}")
        elif result == "attack_wins":
            print(f"  {move_str} 吃掉 {target.name}")
        elif result == "defend_wins":
            print(f"  {move_str} 被 {target.name} 吃掉!")
            # 攻击方被吃，移除攻击方
            self.board.remove(tr, tc)
            # 恢复防守方
            self.board.grid[tr][tc] = target
            target.is_alive = True
        elif result == "mutual":
            print(f"  {move_str} 与 {target.name} 同归于尽!")
            # 同归于尽，移除双方
            self.board.remove(tr, tc)

        # 重新显示棋盘
        UI.display_board(self.board, self.last_move)

        # 等待用户确认
        if self.current_side == "black":
            # AI 走完后等用户确认
            input("  按 Enter 继续...")


def main():
    """主入口"""
    print("欢迎游玩军旗人机对战！")
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        print("\n游戏退出。")
        sys.exit(0)


if __name__ == "__main__":
    main()
