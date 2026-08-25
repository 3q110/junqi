"""规则引擎测试"""
import unittest
from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.rules import Rules


class TestRules(unittest.TestCase):
    def test_normal_piece_moves(self):
        board = Board()
        p = Piece(PieceType.COMMANDER, "red")
        board.place(p, 5, 3)

        moves = Rules.get_valid_moves(board, 5, 3)
        # Should have moves to adjacent empty cells
        self.assertTrue((4, 2) in moves or (6, 3) in moves)

    def test_mine_cannot_move(self):
        board = Board()
        mine = Piece(PieceType.MINE, "red")
        board.place(mine, 5, 3)
        moves = Rules.get_valid_moves(board, 5, 3)
        self.assertEqual(len(moves), 0)

    def test_flag_cannot_move(self):
        board = Board()
        flag = Piece(PieceType.FLAG, "red")
        board.place(flag, 10, 3)
        moves = Rules.get_valid_moves(board, 10, 3)
        self.assertEqual(len(moves), 0)

    def test_sapper_railway_moves(self):
        board = Board()
        sapper = Piece(PieceType.SAPPER, "red")
        board.place(sapper, 2, 0)

        moves = Rules.get_valid_moves(board, 2, 0)
        # Sapper on railway can move along the railway
        self.assertIn((2, 1), moves)
        self.assertIn((2, 2), moves)

    def test_combat_attack_wins(self):
        attacker = Piece(PieceType.COMMANDER, "red")
        defender = Piece(PieceType.SAPPER, "black")
        result = Rules.resolve_combat(attacker, defender)
        self.assertEqual(result, "attack_wins")

    def test_combat_mutual(self):
        attacker = Piece(PieceType.BOMB, "red")
        defender = Piece(PieceType.COMMANDER, "black")
        result = Rules.resolve_combat(attacker, defender)
        self.assertEqual(result, "mutual")

    def test_combat_equal_rank_mutual(self):
        # 同级棋子相撞 → 同归于尽
        attacker = Piece(PieceType.COMMANDER, "red")
        defender = Piece(PieceType.COMMANDER, "black")
        result = Rules.resolve_combat(attacker, defender)
        self.assertEqual(result, "mutual")

    def test_combat_lower_rank_defend_wins(self):
        attacker = Piece(PieceType.SAPPER, "red")
        defender = Piece(PieceType.COMMANDER, "black")
        result = Rules.resolve_combat(attacker, defender)
        self.assertEqual(result, "defend_wins")

    def test_combat_no_combat(self):
        attacker = Piece(PieceType.COMMANDER, "red")
        result = Rules.resolve_combat(attacker, None)
        self.assertEqual(result, "no_combat")

    def test_game_over_flag_captured(self):
        board = Board()
        # Only red flag (black flag captured)
        red_flag = Piece(PieceType.FLAG, "red")
        board.place(red_flag, 10, 3)
        result = Rules.check_game_over(board)
        self.assertEqual(result, "red_wins")

    def test_game_over_both_flags(self):
        # 双方军旗都在且有可动棋子 → 游戏继续
        board = Board()
        red_flag = Piece(PieceType.FLAG, "red")
        black_flag = Piece(PieceType.FLAG, "black")
        board.place(red_flag, 10, 3)
        board.place(black_flag, 0, 3)
        board.place(Piece(PieceType.COMMANDER, "red"), 9, 3)
        board.place(Piece(PieceType.COMMANDER, "black"), 1, 3)
        result = Rules.check_game_over(board)
        self.assertIsNone(result)

    def test_game_over_draw(self):
        # 双方军旗都在，但都只剩不可移动的棋子 → 和棋
        board = Board()
        board.place(Piece(PieceType.FLAG, "red"), 10, 3)
        board.place(Piece(PieceType.MINE, "red"), 10, 0)
        board.place(Piece(PieceType.FLAG, "black"), 0, 3)
        board.place(Piece(PieceType.MINE, "black"), 0, 0)
        result = Rules.check_game_over(board)
        self.assertEqual(result, "draw")

    def test_has_movable_pieces(self):
        board = Board()
        board.place(Piece(PieceType.FLAG, "red"), 10, 3)
        self.assertFalse(Rules.has_movable_pieces(board, "red"))
        board.place(Piece(PieceType.COMMANDER, "red"), 9, 3)
        self.assertTrue(Rules.has_movable_pieces(board, "red"))

    def test_can_capture_flag_in_hq(self):
        # 军旗在大本营内，敌方棋子应能走进大本营吃掉军旗（获胜途径）
        board = Board()
        flag = Piece(PieceType.FLAG, "black")
        board.place(flag, 0, 2)
        commander = Piece(PieceType.COMMANDER, "red")
        board.place(commander, 1, 2)
        self.assertTrue(Rules.is_valid_move(board, 1, 2, 0, 2))

    def test_cannot_enter_empty_hq_while_flag_alive(self):
        # 敌方军旗仍在时，不能进入空的敌方大本营
        board = Board()
        board.place(Piece(PieceType.FLAG, "black"), 0, 4)
        commander = Piece(PieceType.COMMANDER, "red")
        board.place(commander, 1, 2)
        self.assertFalse(Rules.is_valid_move(board, 1, 2, 0, 2))

    def test_one_sided_stalemate_loses(self):
        # 红方无棋可走 → 黑方获胜
        board = Board()
        board.place(Piece(PieceType.FLAG, "red"), 10, 3)
        board.place(Piece(PieceType.MINE, "red"), 10, 0)
        board.place(Piece(PieceType.FLAG, "black"), 0, 3)
        board.place(Piece(PieceType.COMMANDER, "black"), 1, 3)
        result = Rules.check_game_over(board)
        self.assertEqual(result, "black_wins")


if __name__ == "__main__":
    unittest.main()
