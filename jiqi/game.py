"""Game class with main loop, turn management, and win/lose conditions."""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.player import GameSetup, AIPlayer, HumanPlayer
from jiqi.rules import RuleEngine
from jiqi.ui import TerminalUI


class Game:
    """Manages the full game state, turn flow, and win/lose conditions."""

    def __init__(self) -> None:
        self.board = Board()
        GameSetup.setup_pieces(self.board)
        self.human_turn = True
        self.game_over = False
        self.human_flag_captured = False
        self.ai_flag_captured = False
        self.ui = TerminalUI()
        self.human_player = HumanPlayer(self.board, ui=self.ui)
        self.ai_player = AIPlayer(self.board)

    # -- win/lose checks --

    def check_win(self) -> bool:
        """Return True if the game has ended (someone's flag is gone)."""
        if self.human_flag_captured or self.ai_flag_captured:
            self.game_over = True
            return True

        # Also check if flags still exist on board
        human_flag_exists = False
        ai_flag_exists = False
        for r in range(self.board.height):
            for c in range(self.board.width):
                p = self.board.get(c, r)
                if p is None:
                    continue
                if p.piece_type == PieceType.FLAG:
                    if p.side == "human":
                        human_flag_exists = True
                    else:
                        ai_flag_exists = True

        if not ai_flag_exists:
            self.ai_flag_captured = True
            self.game_over = True
            return True
        if not human_flag_exists:
            self.human_flag_captured = True
            self.game_over = True
            return True

        return False

    def get_winner(self) -> str | None:
        """Return 'human', 'ai', or None if no winner yet."""
        if self.human_flag_captured:
            return "ai"
        if self.ai_flag_captured:
            return "human"
        return None

    # -- move processing --

    def process_move(self, move: tuple[int, int, int, int]) -> str | None:
        """Execute a move and return the battle result string, or None if invalid.

        Parameters
        ----------
        move : (src_col, src_row, dst_col, dst_row)

        Returns
        -------
        One of:
            "attacker_wins", "defender_wins", "both_die", "attacker_loses",
            "moved" (to empty cell), or None (invalid move).

        Side effect: switches turn on successful move.
        """
        src_col, src_row, dst_col, dst_row = move

        # Validate move
        if not RuleEngine.can_move(self.board, src_col, src_row, dst_col, dst_row):
            return None

        src_piece = self.board.get(src_col, src_row)
        dst_piece = self.board.get(dst_col, dst_row)

        if dst_piece is None:
            # Move to empty cell
            self.board.move(src_col, src_row, dst_col, dst_row)
            self._switch_turn()
            return "moved"

        # Battle — resolve
        result = RuleEngine.resolve_battle(src_piece, dst_piece)

        if result == "invalid":
            return None

        if result == "attacker_wins":
            # Remove defender, move attacker
            self.board.remove(dst_col, dst_row)
            self.board.move(src_col, src_row, dst_col, dst_row)
            # Check if flag was captured
            if dst_piece.piece_type == PieceType.FLAG:
                if dst_piece.side == "ai":
                    self.ai_flag_captured = True
                else:
                    self.human_flag_captured = True
            self._switch_turn()
            return result

        if result == "defender_wins":
            # Attacker is removed, defender stays
            self.board.remove(src_col, src_row)
            self._switch_turn()
            return result

        if result == "both_die":
            # Both pieces are removed
            self.board.remove(src_col, src_row)
            self.board.remove(dst_col, dst_row)
            self._switch_turn()
            return result

        if result == "attacker_loses":
            # Attacker is removed, defender stays
            self.board.remove(src_col, src_row)
            self._switch_turn()
            return result

        return None

    def _switch_turn(self) -> None:
        """Switch the turn if the game is still ongoing."""
        if not self.game_over:
            self.human_turn = not self.human_turn

    # -- main game loop --

    def run(self) -> None:
        """Run the full game loop until someone wins."""
        self.ui.display_message("=" * 40)
        self.ui.display_message(f"军旗人机对战 v{__import__('jiqi').__version__}")
        self.ui.display_message("开始!")
        self.ui.display_message("=" * 40)

        while not self.game_over:
            if self.human_turn:
                self._human_turn()
            else:
                self._ai_turn()

            # Turn switching is handled inside process_move

        # Game over — display result
        winner = self.get_winner()
        self.ui.display_message("=" * 40)
        if winner == "human":
            self.ui.display_success("恭喜你！你赢了！")
        elif winner == "ai":
            self.ui.display_error("电脑赢了！")
        self.ui.display_message("=" * 40)

    def _human_turn(self) -> None:
        """Handle a human player's turn."""
        self.ui.display_board(self.board, show_enemy=False)
        self.ui.display_message(f"--- {self.human_player.name} 的回合 ---")

        while True:
            move = self.human_player.get_move()
            if move is None:
                continue

            result = self.process_move(move)
            if result is None:
                self.ui.display_error("无效移动，请重新选择。")
                continue

            # Display result
            src_col, src_row, dst_col, dst_row = move
            moving_piece = self.board.get(dst_col, dst_row)
            if moving_piece is not None:
                self.ui.display_message(
                    f"移动: ({src_col},{src_row}) -> ({dst_col},{dst_row})"
                )
                if "attacker_wins" in result:
                    self.ui.display_success(
                        f"攻击成功! {moving_piece.piece_type.name} 吃掉敌人!"
                    )
                elif "both_die" in result:
                    self.ui.display_message("同归于尽!")
                elif "attacker_loses" in result:
                    self.ui.display_error("攻击失败! 你的棋子被消灭了!")
                elif "moved" in result:
                    self.ui.display_message("移动成功!")
            else:
                self.ui.display_message("移动成功!")

            # Check win
            self.check_win()
            if self.game_over:
                return

            break

    def _ai_turn(self) -> None:
        """Handle an AI player's turn."""
        self.ui.display_board(self.board, show_enemy=True)
        self.ui.display_message(f"--- {self.ai_player.name} 的回合 ---")

        move = self.ai_player.get_move()
        if move is None:
            self.ui.display_message("电脑没有可走的棋了!")
            self._switch_turn()
            return

        result = self.process_move(move)
        if result is None:
            self.ui.display_error("电脑无法移动!")
            return

        src_col, src_row, dst_col, dst_row = move
        dst_piece = self.board.get(dst_col, dst_row)
        if dst_piece is not None:
            self.ui.display_message(
                f"电脑移动: ({src_col},{src_row}) -> ({dst_col},{dst_row})"
            )
            if "attacker_wins" in result:
                self.ui.display_message(
                    f"电脑攻击成功! 吃掉了你的棋子!"
                )
            elif "both_die" in result:
                self.ui.display_message("同归于尽!")
            elif "attacker_loses" in result:
                self.ui.display_message("电脑攻击失败!")
            elif "defender_wins" in result:
                self.ui.display_message("电脑攻击失败!")
        else:
            self.ui.display_message("电脑移动成功!")

        # Check win
        self.check_win()


def main() -> None:
    """Entry point for the game."""
    try:
        game = Game()
        game.run()
        sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        print("\n游戏退出。")
        sys.exit(0)
    except Exception as exc:
        print(f"游戏出错: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
