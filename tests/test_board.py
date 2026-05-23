"""棋盘测试"""
import unittest
from jiqi.board import Board
from jiqi.piece import Piece, PieceType


class TestBoard(unittest.TestCase):
    def test_board_creation(self):
        board = Board()
        self.assertEqual(board.width, 7)
        self.assertEqual(board.height, 11)
        self.assertIsNone(board.get(0, 0))

    def test_place_and_get(self):
        board = Board()
        p = Piece(PieceType.COMMANDER, side="red")
        self.assertTrue(board.place(p, 0, 0))
        self.assertEqual(board.get(0, 0), p)

    def test_place_on_occupied_fails(self):
        board = Board()
        p1 = Piece(PieceType.COMMANDER, side="red")
        p2 = Piece(PieceType.ARMY_COMMANDER, side="red")
        board.place(p1, 0, 0)
        self.assertFalse(board.place(p2, 0, 0))

    def test_remove(self):
        board = Board()
        p = Piece(PieceType.COMMANDER, side="red")
        board.place(p, 0, 0)
        removed = board.remove(0, 0)
        self.assertEqual(removed, p)
        self.assertIsNone(board.get(0, 0))

    def test_move(self):
        board = Board()
        p = Piece(PieceType.COMMANDER, side="red")
        board.place(p, 0, 0)
        captured = board.move(p, 0, 0, 1, 1)
        self.assertIsNone(captured)
        self.assertIsNone(board.get(0, 0))
        self.assertEqual(board.get(1, 1), p)

    def test_move_captures(self):
        board = Board()
        p1 = Piece(PieceType.COMMANDER, side="red")
        p2 = Piece(PieceType.SAPPER, side="black")
        board.place(p1, 0, 0)
        board.place(p2, 1, 1)
        captured = board.move(p1, 0, 0, 1, 1)
        self.assertEqual(captured, p2)
        self.assertFalse(captured.is_alive)

    def test_get_side_pieces(self):
        board = Board()
        p1 = Piece(PieceType.COMMANDER, side="red")
        p2 = Piece(PieceType.SAPPER, side="red")
        p3 = Piece(PieceType.COMMANDER, side="black")
        board.place(p1, 0, 0)
        board.place(p2, 0, 1)
        board.place(p3, 1, 0)
        red_pieces = board.get_side_pieces("red")
        self.assertEqual(len(red_pieces), 2)

    def test_railway(self):
        board = Board()
        self.assertTrue(board.is_on_railway(2, 0))
        self.assertTrue(board.is_on_railway(2, 3))
        self.assertTrue(board.is_on_railway(9, 5))
        self.assertFalse(board.is_on_railway(3, 3))


if __name__ == "__main__":
    unittest.main()
