"""棋子测试"""
import unittest
from jiqi.piece import Piece, PieceType


class TestPieceCreation(unittest.TestCase):
    def test_piece_creation(self):
        p = Piece(PieceType.COMMANDER, side="red")
        self.assertEqual(p.piece_type, PieceType.COMMANDER)
        self.assertEqual(p.side, "red")
        self.assertTrue(p.is_alive)

    def test_piece_rank(self):
        self.assertEqual(Piece(PieceType.COMMANDER, "red").rank, 1)
        self.assertEqual(Piece(PieceType.SAPPER, "red").rank, 9)
        self.assertEqual(Piece(PieceType.BOMB, "red").rank, 10)
        self.assertEqual(Piece(PieceType.MINE, "red").rank, 11)
        self.assertEqual(Piece(PieceType.FLAG, "red").rank, 12)

    def test_higher_rank_eats_lower(self):
        commander = Piece(PieceType.COMMANDER, "red")
        soldier = Piece(PieceType.SAPPER, "black")
        self.assertTrue(commander.can_eat(soldier))
        self.assertFalse(soldier.can_eat(commander))

    def test_piece_can_eat_flag(self):
        p = Piece(PieceType.SAPPER, "red")
        flag = Piece(PieceType.FLAG, "black")
        self.assertTrue(p.can_eat(flag))

    def test_bomb_eats_anything(self):
        bomb = Piece(PieceType.BOMB, "red")
        commander = Piece(PieceType.COMMANDER, "black")
        self.assertTrue(bomb.can_eat(commander))

    def test_mine_only_by_sapper_or_bomb(self):
        mine = Piece(PieceType.MINE, "black")
        self.assertFalse(Piece(PieceType.COMMANDER, "red").can_eat(mine))
        self.assertTrue(Piece(PieceType.SAPPER, "red").can_eat(mine))
        self.assertTrue(Piece(PieceType.BOMB, "red").can_eat(mine))

    def test_flag_cannot_eat(self):
        flag = Piece(PieceType.FLAG, "red")
        soldier = Piece(PieceType.SAPPER, "black")
        self.assertFalse(flag.can_eat(soldier))

    def test_mine_cannot_eat(self):
        mine = Piece(PieceType.MINE, "red")
        soldier = Piece(PieceType.SAPPER, "black")
        self.assertFalse(mine.can_eat(soldier))

    def test_movable(self):
        self.assertTrue(Piece(PieceType.COMMANDER, "red").is_movable)
        self.assertFalse(Piece(PieceType.MINE, "red").is_movable)
        self.assertFalse(Piece(PieceType.FLAG, "red").is_movable)


if __name__ == "__main__":
    unittest.main()
