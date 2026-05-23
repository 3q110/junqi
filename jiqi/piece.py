"""棋子模块 - 定义棋子类型、等级、吃子规则"""
from enum import Enum


class PieceType(Enum):
    """棋子类型枚举"""
    COMMANDER = "司令"
    ARMY_COMMANDER = "军长"
    DIVISION_COMMANDER = "师长"
    BRIGADE_COMMANDER = "旅长"
    REGIMENT_COMMANDER = "团长"
    BATTALION_COMMANDER = "营长"
    COMPANY_COMMANDER = "连长"
    PLATOON_LEADER = "排长"
    SAPPER = "工兵"
    BOMB = "炸弹"
    MINE = "地雷"
    FLAG = "军旗"


class Piece:
    """棋子类"""

    # 等级映射：数字越小等级越高
    RANK = {
        PieceType.COMMANDER: 1,
        PieceType.ARMY_COMMANDER: 2,
        PieceType.DIVISION_COMMANDER: 3,
        PieceType.BRIGADE_COMMANDER: 4,
        PieceType.REGIMENT_COMMANDER: 5,
        PieceType.BATTALION_COMMANDER: 6,
        PieceType.COMPANY_COMMANDER: 7,
        PieceType.PLATOON_LEADER: 8,
        PieceType.SAPPER: 9,
        PieceType.BOMB: 10,
        PieceType.MINE: 11,
        PieceType.FLAG: 12,
    }

    def __init__(self, piece_type: PieceType, side: str):
        """
        Args:
            piece_type: 棋子类型
            side: 所属方 ("red" 或 "black")
        """
        self.piece_type = piece_type
        self.side = side
        self.is_alive = True

    @property
    def rank(self) -> int:
        """棋子等级（数字越小越高）"""
        return self.RANK[self.piece_type]

    @property
    def name(self) -> str:
        """棋子中文名称"""
        return self.piece_type.value

    @property
    def is_movable(self) -> bool:
        """是否可移动（地雷和军旗不可移动）"""
        return self.piece_type not in (PieceType.MINE, PieceType.FLAG)

    def can_eat(self, target: "Piece") -> bool:
        """
        判断是否能吃掉目标棋子。

        规则：
        - 军旗不能主动吃子
        - 地雷不能主动吃子
        - 炸弹与任何棋子同归于尽（可以"吃"但自己也死）
        - 工兵可以挖地雷
        - 炸弹可以炸地雷
        - 地雷只能被工兵或炸弹消灭
        - 普通棋子按等级比较（等级高的吃等级低的）
        - 任何棋子可以吃军旗（除军旗自身）
        """
        if not target.is_alive:
            return False
        if self.piece_type == PieceType.FLAG:
            return False
        if self.piece_type == PieceType.MINE:
            return False
        # 炸弹可以吃任何棋子（同归于尽）
        if self.piece_type == PieceType.BOMB:
            return True
        # 任何棋子可以吃军旗
        if target.piece_type == PieceType.FLAG:
            return True
        # 地雷只能被工兵或炸弹消灭
        if target.piece_type == PieceType.MINE:
            return self.piece_type == PieceType.SAPPER
        # 普通比较：等级高的吃等级低的
        return self.rank < target.rank

    def __repr__(self):
        return f"Piece({self.name}, {self.side})"
