"""AI 模块 - 启发式 AI（支持 easy / medium / hard 难度）"""

import random
from typing import Tuple
from jiqi.board import Board
from jiqi.piece import PieceType
from jiqi.rules import Rules
from jiqi.player import Player


# 棋子价值（用于评分）
PIECE_VALUES = {
    PieceType.COMMANDER: 100,
    PieceType.ARMY_COMMANDER: 80,
    PieceType.DIVISION_COMMANDER: 60,
    PieceType.BRIGADE_COMMANDER: 50,
    PieceType.REGIMENT_COMMANDER: 40,
    PieceType.BATTALION_COMMANDER: 30,
    PieceType.COMPANY_COMMANDER: 20,
    PieceType.PLATOON_LEADER: 10,
    PieceType.SAPPER: 15,
    PieceType.BOMB: 35,
    PieceType.MINE: 25,
    PieceType.FLAG: 999,
}


class RandomAI(Player):
    """简单 AI：随机选择合法移动（优先吃子）"""

    def __init__(self, side: str, name: str = "AI"):
        super().__init__(side, name)

    def make_move(self, board: Board) -> Tuple[int, int, int, int]:
        """随机选择一个合法移动"""
        all_moves = self._get_all_moves(board)
        if not all_moves:
            raise ValueError(f"{self.name} 没有合法移动")

        # 简单策略：优先吃子
        capture_moves = []
        other_moves = []
        for fr, fc, tr, tc in all_moves:
            target = board.get(tr, tc)
            if target:
                capture_moves.append((fr, fc, tr, tc))
            else:
                other_moves.append((fr, fc, tr, tc))

        if capture_moves:
            return random.choice(capture_moves)
        return random.choice(other_moves)

    def _get_all_moves(self, board: Board) -> list:
        """获取某方所有合法移动"""
        moves = []
        pieces = board.get_side_pieces(self.side)
        for r, c, piece in pieces:
            valid_targets = Rules.get_valid_moves(board, r, c)
            for tr, tc in valid_targets:
                moves.append((r, c, tr, tc))
        return moves


class HeuristicAI(Player):
    """
    启发式 AI：按难度评分选择移动。

    - easy:   随机走棋，偶尔吃子
    - medium: 贪心吃子（优先吃价值高的目标）+ 少量随机
    - hard:   综合评分（吃子价值、推进、保护军旗、风险控制）
    """

    def __init__(self, side: str, name: str = "AI", difficulty: str = "medium"):
        super().__init__(side, name)
        self.difficulty = difficulty if difficulty in ("easy", "medium", "hard") else "medium"
        self.move_count = 0  # 记录该 AI 已走步数，用于打破僵持

    def make_move(self, board: Board) -> Tuple[int, int, int, int]:
        """按难度评分选择移动"""
        all_moves = self._get_all_moves(board)
        if not all_moves:
            raise ValueError(f"{self.name} 没有合法移动")
        self.move_count += 1
        # 对局越长越激进：鼓励冒险吃子、深入敌阵，打破对称僵持
        aggression = min(30, self.move_count * 0.3)

        if self.difficulty == "easy":
            capture_moves = []
            other_moves = []
            for fr, fc, tr, tc in all_moves:
                if board.get(tr, tc):
                    capture_moves.append((fr, fc, tr, tc))
                else:
                    other_moves.append((fr, fc, tr, tc))
            if capture_moves and random.random() < 0.3:
                return random.choice(capture_moves)
            return random.choice(all_moves)

        if self.difficulty == "medium":
            enemy_flag = self._flag_position(board, "red" if self.side == "black" else "black")
            best_move, best_score = None, -1
            for fr, fc, tr, tc in all_moves:
                target = board.get(tr, tc)
                score = random.random()
                if target:
                    # 吃子：按目标价值加分（军旗直接赢）
                    score += PIECE_VALUES[target.piece_type]
                    if target.piece_type == PieceType.FLAG:
                        score += 10000
                    # 工兵挖地雷是赚的；非工兵撞地雷巨亏
                    if target.piece_type == PieceType.MINE:
                        score += 40 if board.get(fr, fc).piece_type == PieceType.SAPPER else -100
                else:
                    # 靠近敌方军旗
                    if enemy_flag:
                        er, ec = enemy_flag
                        score += (20 - (abs(tr - er) + abs(tc - ec))) * 3
                if score > best_score:
                    best_score, best_move = score, (fr, fc, tr, tc)
            return best_move

        # hard: 综合评分
        enemy_flag = self._flag_position(board, "red" if self.side == "black" else "black")
        own_flag = self._flag_position(board, self.side)
        best_move, best_score = None, -1
        for fr, fc, tr, tc in all_moves:
            attacker = board.get(fr, fc)
            target = board.get(tr, tc)
            score = random.random()

            # 核心驱动：靠近敌方军旗（曼哈顿距离越小分越高）
            # 这保证棋子始终朝目标推进，不会在半场徘徊
            if enemy_flag:
                er, ec = enemy_flag
                dist = abs(tr - er) + abs(tc - ec)
                score += (20 - dist) * 4

            # 中央控制
            score += (3 - abs(tc - 3)) * 0.5

            at_val = PIECE_VALUES[attacker.piece_type]

            if target:
                df_val = PIECE_VALUES[target.piece_type]

                if attacker.piece_type == PieceType.BOMB:
                    score += df_val * 1.5  # 炸弹炸高价值目标更划算
                elif df_val > at_val:
                    score += df_val - at_val + 60  # 以小吃大，高收益
                elif at_val > df_val * 1.5 and df_val > 20:
                    score -= at_val - df_val * 0.5  # 大材小用，适度扣分
                else:
                    score += 40  # 正常吃子

                if target.piece_type == PieceType.FLAG:
                    score += 10000  # 吃军旗直接赢
                # 工兵挖地雷是赚的；非工兵撞地雷巨亏
                if target.piece_type == PieceType.MINE:
                    score += 40 if attacker.piece_type == PieceType.SAPPER else -100

            else:
                # 风险评估：只计算落点“相邻”的、能够一步吃到落点的敌方棋子
                for nr, nc in ((tr - 1, tc), (tr + 1, tc), (tr, tc - 1), (tr, tc + 1)):
                    if not board.in_bounds(nr, nc):
                        continue
                    neighbor = board.get(nr, nc)
                    if neighbor and neighbor.side != self.side:
                        nb_val = PIECE_VALUES[neighbor.piece_type]
                        if neighbor.piece_type == PieceType.BOMB:
                            score -= at_val * 0.8  # 落到炸弹旁边危险
                        elif neighbor.piece_type == PieceType.MINE:
                            score -= 15  # 非工兵落点靠近地雷
                        elif nb_val > at_val:
                            score -= min(8, (nb_val - at_val) * 0.15)  # 可能被反吃，轻微扣分
                        # nb_val <= at_val：对方吃了会双输或白吃，风险小

            # 保护己方军旗：高价值棋子留在军旗附近
            if own_flag:
                frg, fcg = own_flag
                if abs(tr - frg) <= 2 and abs(tc - fcg) <= 1:
                    if at_val >= 30:
                        score += 5

            # 工兵/炸弹主动寻找对方地雷：靠近地雷加分
            if attacker.piece_type in (PieceType.SAPPER, PieceType.BOMB):
                for mr, mc, mp in board.get_side_pieces("red" if self.side == "black" else "black"):
                    if mp.piece_type == PieceType.MINE:
                        m_dist = abs(tr - mr) + abs(tc - mc)
                        if m_dist <= 3:
                            score += (4 - m_dist) * 4

            # 低价值棋子（排长/连长/营长）鼓励压上：当炮灰开路
            # 高价值棋子（司令/军长）谨慎：不轻易深入敌阵
            if at_val <= 30:
                score += 12 + aggression * 0.3  # 低价值棋子推进奖励 + 激进加成
            elif at_val >= 80:
                # 高价值棋子：如果落点有敌方威胁，额外扣分（激进度越高扣得越少）
                penalty = max(0, 6 - aggression * 0.1)
                for nr, nc in ((tr - 1, tc), (tr + 1, tc), (tr, tc - 1), (tr, tc + 1)):
                    if not board.in_bounds(nr, nc):
                        continue
                    neighbor = board.get(nr, nc)
                    if neighbor and neighbor.side != self.side and neighbor.piece_type != PieceType.MINE:
                        score -= penalty

            # 激进度加成：对局越长，越鼓励深入敌阵（靠近敌方军旗额外加分）
            if enemy_flag:
                er, ec = enemy_flag
                dist = abs(tr - er) + abs(tc - ec)
                if dist <= 4:
                    score += aggression  # 深入敌阵的激进奖励

            if score > best_score:
                best_score, best_move = score, (fr, fc, tr, tc)
        return best_move

    def _advance_score(self, board: Board, fr: int, fc: int, tr: int, tc: int) -> float:
        """向对方底线推进的得分（medium 难度使用）"""
        if self.side == "black":
            score = max(0, fr - tr) * 6
            if tr <= 5:
                score += 8
            return score
        score = max(0, tr - fr) * 6
        if tr >= 5:
            score += 8
        return score

    def _flag_position(self, board: Board, side: str):
        """查找某方军旗位置"""
        for r, c, p in board.get_side_pieces(side):
            if p.piece_type == PieceType.FLAG:
                return (r, c)
        return None

    def _get_all_moves(self, board: Board) -> list:
        """获取某方所有合法移动"""
        moves = []
        pieces = board.get_side_pieces(self.side)
        for r, c, piece in pieces:
            valid_targets = Rules.get_valid_moves(board, r, c)
            for tr, tc in valid_targets:
                moves.append((r, c, tr, tc))
        return moves
