from jiqi.piece import Piece, PieceType


def test_piece_creation():
    p = Piece(PieceType.COMMANDER, side="human")
    assert p.piece_type == PieceType.COMMANDER
    assert p.side == "human"
    assert p.is_alive is True
    assert p.is_mine is True


def test_piece_rank():
    assert Piece(PieceType.COMMANDER).rank == 1
    assert Piece(PieceType.MINE).rank == 11
    assert Piece(PieceType.FLAG).rank == 12


def test_piece_cannot_eat_flag():
    p = Piece(PieceType.SAPPER)
    flag = Piece(PieceType.FLAG)
    assert not p.can_eat(flag)


def test_bomb_eats_anything():
    bomb = Piece(PieceType.BOMB)
    commander = Piece(PieceType.COMMANDER)
    assert bomb.can_eat(commander)


def test_mine_only_by_sapper_or_bomb():
    mine = Piece(PieceType.MINE)
    assert not Piece(PieceType.COMMANDER).can_eat(mine)
    assert Piece(PieceType.SAPPER).can_eat(mine)
    assert Piece(PieceType.BOMB).can_eat(mine)
