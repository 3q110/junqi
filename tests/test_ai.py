"""AI 模块测试"""
import unittest
from jiqi.board import Board
from jiqi.piece import Piece, PieceType
from jiqi.ai import RandomAI, HeuristicAI


class TestRandomAI(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.ai = RandomAI(side='black', name='TestAI')

    def test_init(self):
        self.assertEqual(self.ai.side, 'black')
        self.assertEqual(self.ai.name, 'TestAI')

    def test_make_move_valid(self):
        # Place a black piece that can move
        p = Piece(PieceType.COMMANDER, 'black')
        self.board.place(p, 0, 3)
        fr, fc, tr, tc = self.ai.make_move(self.board)
        # Should move from the piece position
        self.assertEqual((fr, fc), (0, 3))
        # Destination should be in bounds
        self.assertTrue(self.board.in_bounds(tr, tc))

    def test_make_move_prioritizes_capture(self):
        # Black commander can eat red sapper
        commander = Piece(PieceType.COMMANDER, 'black')
        sapper = Piece(PieceType.SAPPER, 'red')
        self.board.place(commander, 0, 3)
        self.board.place(sapper, 1, 2)  # (1,2) is not a camp, so attack is valid

        # Run multiple times — all should be captures since only one move
        for _ in range(10):
            # Reset board for each iteration
            self.board = Board()
            self.board.place(Piece(PieceType.COMMANDER, 'black'), 0, 3)
            self.board.place(Piece(PieceType.SAPPER, 'red'), 1, 2)
            fr, fc, tr, tc = self.ai.make_move(self.board)
            self.assertEqual((tr, tc), (1, 2))

    def test_no_moves_raises(self):
        # Only a mine (cannot move)
        mine = Piece(PieceType.MINE, 'black')
        self.board.place(mine, 5, 3)
        with self.assertRaises(ValueError):
            self.ai.make_move(self.board)

    def test_get_all_moves(self):
        p = Piece(PieceType.COMMANDER, 'black')
        self.board.place(p, 5, 3)
        moves = self.ai._get_all_moves(self.board)
        self.assertIsInstance(moves, list)
        self.assertTrue(len(moves) > 0)
        # Each move is (fr, fc, tr, tc)
        for m in moves:
            self.assertEqual(len(m), 4)

    def test_multiple_pieces(self):
        # Two black pieces
        p1 = Piece(PieceType.COMMANDER, 'black')
        p2 = Piece(PieceType.SAPPER, 'black')
        self.board.place(p1, 5, 0)
        self.board.place(p2, 5, 6)
        moves = self.ai._get_all_moves(self.board)
        # Should have moves from both pieces
        from_pieces = {(m[0], m[1]) for m in moves}
        self.assertIn((5, 0), from_pieces)
        self.assertIn((5, 6), from_pieces)


class TestHeuristicAI(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.ai = HeuristicAI(side='black', name='TestAI', difficulty='medium')

    def test_init_difficulty(self):
        self.assertEqual(HeuristicAI('black', difficulty='easy').difficulty, 'easy')
        self.assertEqual(HeuristicAI('black', difficulty='bogus').difficulty, 'medium')

    def test_make_move_valid(self):
        self.board.place(Piece(PieceType.COMMANDER, 'black'), 0, 3)
        fr, fc, tr, tc = self.ai.make_move(self.board)
        self.assertEqual((fr, fc), (0, 3))
        self.assertTrue(self.board.in_bounds(tr, tc))

    def test_hard_captures_flag(self):
        # 黑方司令可吃掉红方军旗 → hard 难度必须吃掉
        board = Board()
        board.place(Piece(PieceType.COMMANDER, 'black'), 8, 2)
        board.place(Piece(PieceType.FLAG, 'red'), 9, 2)
        ai = HeuristicAI(side='black', name='AI', difficulty='hard')
        for _ in range(5):
            b = Board()
            b.place(Piece(PieceType.COMMANDER, 'black'), 8, 2)
            b.place(Piece(PieceType.FLAG, 'red'), 9, 2)
            fr, fc, tr, tc = ai.make_move(b)
            self.assertEqual((tr, tc), (9, 2))

    def test_hard_avoids_mine(self):
        # 黑方司令面对地雷，不应去吃（非工兵撞地雷巨亏）
        b = Board()
        b.place(Piece(PieceType.COMMANDER, 'black'), 8, 3)
        b.place(Piece(PieceType.MINE, 'red'), 9, 3)
        b.place(Piece(PieceType.SAPPER, 'black'), 8, 4)
        ai = HeuristicAI(side='black', name='AI', difficulty='hard')
        fr, fc, tr, tc = ai.make_move(b)
        # 不应选择去撞地雷 (9,3)
        self.assertNotEqual((tr, tc), (9, 3))

    def test_no_moves_raises(self):
        self.board.place(Piece(PieceType.MINE, 'black'), 5, 3)
        with self.assertRaises(ValueError):
            self.ai.make_move(self.board)


if __name__ == "__main__":
    unittest.main()
