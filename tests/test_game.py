"""游戏初始化与 GameSetup 测试"""
import unittest
from jiqi.game import GameSetup
from jiqi.piece import PieceType


class TestGameSetup(unittest.TestCase):
    def test_piece_config_total_24(self):
        total = sum(cnt for _, cnt in GameSetup.PIECE_CONFIG)
        self.assertEqual(total, 24)

    def test_setup_board_piece_counts(self):
        board = GameSetup.setup_board()
        black = board.get_side_pieces('black')
        red = board.get_side_pieces('red')
        self.assertEqual(len(black), 24)
        self.assertEqual(len(red), 24)

    def test_flag_positions(self):
        board = GameSetup.setup_board()
        # Flag should be in one of the two HQ positions (randomly chosen)
        black_hq = [(0, 2), (0, 4)]
        red_hq = [(10, 2), (10, 4)]
        black_flag = None
        red_flag = None
        for r, c in black_hq:
            p = board.get(r, c)
            if p and p.piece_type == PieceType.FLAG:
                black_flag = p
        for r, c in red_hq:
            p = board.get(r, c)
            if p and p.piece_type == PieceType.FLAG:
                red_flag = p
        self.assertIsNotNone(black_flag)
        self.assertEqual(black_flag.side, 'black')
        self.assertIsNotNone(red_flag)
        self.assertEqual(red_flag.side, 'red')

    def test_mine_positions(self):
        board = GameSetup.setup_board()
        # Black mines should be in rows 0-3
        black_mines = [(r, c) for r in range(4) for c in range(7)
                       if board.get(r, c) and board.get(r, c).piece_type == PieceType.MINE]
        self.assertEqual(len(black_mines), 3)
        # Red mines should be in rows 7-10
        red_mines = [(r, c) for r in range(7, 11) for c in range(7)
                     if board.get(r, c) and board.get(r, c).piece_type == PieceType.MINE]
        self.assertEqual(len(red_mines), 3)

    def test_piece_distribution(self):
        board = GameSetup.setup_board()
        black = board.get_side_pieces('black')
        from collections import Counter
        dist = Counter(p.piece_type for _, _, p in black)
        # Check standard distribution
        self.assertEqual(dist[PieceType.COMMANDER], 2)
        self.assertEqual(dist[PieceType.ARMY_COMMANDER], 2)
        self.assertEqual(dist[PieceType.DIVISION_COMMANDER], 2)
        self.assertEqual(dist[PieceType.BRIGADE_COMMANDER], 2)
        self.assertEqual(dist[PieceType.REGIMENT_COMMANDER], 2)
        self.assertEqual(dist[PieceType.BATTALION_COMMANDER], 2)
        self.assertEqual(dist[PieceType.COMPANY_COMMANDER], 2)
        self.assertEqual(dist[PieceType.SAPPER], 3)
        self.assertEqual(dist[PieceType.BOMB], 3)
        self.assertEqual(dist[PieceType.MINE], 3)
        self.assertEqual(dist[PieceType.FLAG], 1)


if __name__ == "__main__":
    unittest.main()
