from enum import Enum


class PieceType(Enum):
    COMMANDER = 1
    ARMY_COMMANDER = 2
    DIVISION_COMMANDER = 3
    BRIGADE_COMMANDER = 4
    REGIMENT_COMMANDER = 5
    BATTALION_COMMANDER = 6
    COMPANY_COMMANDER = 7
    PLATOON_LEADER = 8
    SAPPER = 9
    BOMB = 10
    MINE = 11
    FLAG = 12


class Piece:
    __slots__ = ("piece_type", "side", "is_alive")

    def __init__(self, piece_type: PieceType, side: str = "human"):
        self.piece_type = piece_type
        self.side = side
        self.is_alive = True

    @property
    def is_mine(self) -> bool:
        return self.side == "human"

    @property
    def rank(self) -> int:
        return self.piece_type.value

    def can_eat(self, target: "Piece") -> bool:
        if not target.is_alive:
            return False

        # This piece's type matters
        pt = self.piece_type
        tp = target.piece_type

        # FLAG can't eat anything
        if pt == PieceType.FLAG:
            return False

        # MINE can't eat anything
        if pt == PieceType.MINE:
            return False

        # BOMB can eat anything (both die in battle)
        if pt == PieceType.BOMB:
            return True

        # FLAG can't be eaten (it's captured only by special rules)
        if tp == PieceType.FLAG:
            return False

        # MINE can only be eaten by SAPPER or BOMB
        if tp == PieceType.MINE:
            return pt == PieceType.SAPPER

        # Normal pieces: lower rank number = higher rank, lower rank eats higher rank
        return self.rank < target.rank
