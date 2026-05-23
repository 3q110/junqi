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
        board = Board()
        red_flag = Piece(PieceType.FLAG, "red")
        black_flag = Piece(PieceType.FLAG, "black")
        board.place(red_flag, 10, 3)
        board.place(black_flag, 0, 3)
        result = Rules.check_game_over(board)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
