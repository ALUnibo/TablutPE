import numpy as np
import math
import time
from copy import deepcopy
DEBUG = False


class TablutAI:
    def __init__(self, role, timer, depth=3, cutoff=5):
        self.role = role
        self.timer = timer
        if timer < 50:
            depth -= 1
        self.depth = depth * 2 + 1
        self.cutoff = cutoff
        self.camps = [(0, 3), (0, 4), (0, 5), (1, 4), (3, 0), (3, 8), (4, 0), (4, 1), (4, 4), (4, 7), (4, 8), (5, 0),
                      (5, 8), (7, 4), (8, 3), (8, 4), (8, 5)]
        if role == 'WHITE':
            self.best = -10000
        else:
            self.best = 10000

    def boardEvaluate(self, board, king):
        stateValue = 0
        if king[0] in [0, 8] or king[1] in [0, 8]:  # Victory condition
            return 10000
        if (king == (4, 4) and board[4][5] + board[4][3] + board[3][4] + board[5][4] == -4) or (  # Loss condition
                king in [(3, 4), (4, 5), (5, 4), (4, 3)] and
                board[king[0] + 1][king[1]] + board[king[0] - 1][king[1]] +
                board[king[0]][king[1] + 1] + board[king[0]][king[1] - 1] == -3) or (
                king not in [(3, 4), (4, 5), (5, 4), (4, 3), (4, 4)] and (board[king[0]][king[1] + 1] +
                                                                          board[king[0]][king[1] - 1] == -2 or
                                                                          board[king[0] + 1][king[1]] +
                                                                          board[king[0] - 1][king[1]] == -2)) or (
                ((king[0] + 1, king[1]) in self.camps and board[king[0] - 1][king[1]] == -1) or
                ((king[0] - 1, king[1]) in self.camps and board[king[0] + 1][king[1]] == -1) or
                ((king[0], king[1] + 1) in self.camps and board[king[0]][king[1] + 1] == -1) or
                ((king[0], king[1] - 1) in self.camps and board[king[0]][king[1] - 1] == -1)):
            return -10000
        stateValue += np.sum(board)
        stateValue += math.sqrt((king[0] - 4) ** 2 + (king[1] - 4) ** 2) * 0.5  # King distance
        return stateValue

    def getMoves(self, board, role, kingPos):
        moves = []
        if role == 0:
            pawn = 1
            for move in self.movesForPawn(kingPos[0], kingPos[1], deepcopy(board)):
                moves.append(move)
        else:
            pawn = -1
        for i in range(0, 9):
            for j in range(0, 9):
                if board[i][j] == pawn:
                    for move in self.movesForPawn(i, j, board):
                        moves.append(move)
        return np.array(moves)

    def movesForPawn(self, iStart, jStart, board):
        moves = []
        i = iStart + 1
        j = jStart
        while i < 9 and ((i, j) not in self.camps or (iStart, jStart) in self.camps) and board[i][j] == 0:
            moves.append(((iStart, jStart), (i, j)))
            i += 1
        i = iStart - 1
        j = jStart
        while i >= 0 and ((i, j) not in self.camps or (iStart, jStart) in self.camps) and board[i][j] == 0:
            moves.append(((iStart, jStart), (i, j)))
            i -= 1
        i = iStart
        j = jStart + 1
        while j < 9 and ((i, j) not in self.camps or (iStart, jStart) in self.camps) and board[i][j] == 0:
            moves.append(((iStart, jStart), (i, j)))
            j += 1
        i = iStart
        j = jStart - 1
        while j >= 0 and ((i, j) not in self.camps or (iStart, jStart) in self.camps) and board[i][j] == 0:
            moves.append(((iStart, jStart), (i, j)))
            j -= 1
        return moves

    def searchBestMove(self, board, kingPos, start):
        if self.role == 'WHITE':
            return self.searchBestMoveWhite(board, kingPos, start, self.depth, True)
        else:
            return self.searchBestMoveBlack(board, kingPos, start, self.depth, True)

    def searchBestMoveWhite(self, board, kingPos, start, depth, original=True):
        role = 0
        self.best = -10000
        moves = self.getMoves(deepcopy(board), (self.depth - depth) % 2, kingPos)
        if len(moves) == 0:
            if (self.depth - depth) % 2 == 0:
                return -10000
            else:
                return 10000
        cutoff = self.cutoff
        if original and len(moves) > 40:
            cutoff = cutoff - 1

        scores = np.ones(len(moves)) * -10000
        for count, move in enumerate(moves):
            B, K = self.applyMove(deepcopy(board), move, kingPos)  # Get new board and kingPos
            scores[count] = self.boardEvaluate(B, K)
        order = np.argsort(scores)
        if (self.depth - depth) % 2 == 0:
            order = np.flip(order)
        for count, el in enumerate(order):
            if depth > 1:
                if time.perf_counter() - start < (self.timer - 3) and (original or count < cutoff) \
                        and abs(scores[el]) != 10000:
                    if self.best - scores[el] > 1:
                        continue
                    B, K = self.applyMove(deepcopy(board), moves[el], kingPos)
                    scores[el] = self.searchBestMoveWhite(B, K, start, depth - 1, False)
                    if original:
                        if DEBUG:
                            print(f"Move {moves[el][0]} to {moves[el][1]} evaluated as worth {scores[el]} points")
                            print(f"El = {el}, count = {count}, move = {moves[el][0]} to {moves[el][1]}")
                        if scores[el] > self.best:
                            self.best = scores[el]
        if original:
            if DEBUG:
                print(
                    f"The best move is {moves[np.argmax(scores)][0]} to {moves[np.argmax(scores)][1]},\n"
                    f"which is worth {np.amax(scores)} points!\n"
                    f"Elapsed time: {time.perf_counter() - start}s")
            return moves[np.argmax(scores[:count])]
        else:
            if (self.depth - depth) % 2 == role:
                return np.amax(scores)
            else:
                return np.amin(scores)

    def searchBestMoveBlack(self, board, kingPos, start, depth=0, original=True):
        role = 1
        self.best = 10000
        moves = self.getMoves(deepcopy(board), (self.depth - depth + 1) % 2, kingPos)
        if len(moves) == 0:
            if (self.depth - depth + 1) % 2 == 0:
                return -10000
            else:
                return 10000

        cutoff = self.cutoff
        if original and len(moves) > 40:
            cutoff = cutoff - 1
        scores = np.ones(len(moves)) * 10000
        for count, move in enumerate(moves):
            B, K = self.applyMove(deepcopy(board), move, kingPos)  # Get new board and kingPos
            scores[count] = self.boardEvaluate(B, K)
        order = np.argsort(scores)
        if (self.depth - depth) % 2 == 1:
            order = np.flip(order)
        for count, el in enumerate(order):
            if depth > 1:
                if time.perf_counter() - start < (self.timer - 3) and (original or count < cutoff) \
                        and abs(scores[el]) != 10000:
                    if self.best - scores[el] < -1:
                        continue
                    B, K = self.applyMove(deepcopy(board), moves[el], kingPos)
                    scores[el] = self.searchBestMoveBlack(B, K, start, depth - 1, False)
                    if original:
                        if DEBUG:
                            print(f"Move {moves[el][0]} to {moves[el][1]} evaluated as worth {scores[el]} points")
                            print(f"El = {el}, count = {count}, move = {moves[el][0]} to {moves[el][1]}")
                        if scores[el] > self.best:
                            self.best = scores[el]
        if original:
            if DEBUG:
                print(
                    f"The best move is {moves[np.argmin(scores)][0]} to {moves[np.argmin(scores)][1]},\n"
                    f"which is worth {np.amin(scores)} points!\n"
                    f"Elapsed time: {time.perf_counter() - start}s")
            return moves[np.argmin(scores[:count])]
        else:
            if (self.depth - depth) % 2 == role:
                return np.amax(scores)
            else:
                return np.amin(scores)

    def applyMove(self, board, move, kingPos):
        (From, To) = move
        board[To[0]][To[1]] = board[From[0]][From[1]]
        board[From[0]][From[1]] = 0
        if board[To[0]][To[1]] == 3:
            kingPos = (To[0],To[1])
        # Checking if a piece is captured in all 4 directions
        if To[0] not in [0, 1] and (
                (board[To[0]][To[1]] == board[To[0] - 2][To[1]] != board[To[0] - 1][To[1]] != 3) or (
                (To[0] - 2,To[1]) in self.camps and board[To[0]][To[1]] != board[To[0] - 1][To[1]] and
                board[To[0] - 1][To[1]] not in [0,3])):
            board[To[0] - 1][To[1]] = 0
        if To[0] not in [7, 8] and (
                (board[To[0]][To[1]] == board[To[0] + 2][To[1]] != board[To[0] + 1][To[1]] != 3) or (
                (To[0] + 2,To[1]) in self.camps and board[To[0]][To[1]] != board[To[0] + 1][To[1]] and
                board[To[0] + 1][To[1]] not in [0,3])):
            board[To[0] + 1][To[1]] = 0
        if To[1] not in [0, 1] and (
                (board[To[0]][To[1]] == board[To[0]][To[1] - 2] != board[To[0]][To[1] - 1] != 3) or (
                (To[0],To[1] - 2) in self.camps and board[To[0]][To[1]] != board[To[0]][To[1] - 1] and
                board[To[0]][To[1] - 1] not in [0,3])):
            board[To[0]][To[1] - 1] = 0
        if To[1] not in [7, 8] and (
                (board[To[0]][To[1]] == board[To[0]][To[1] + 2] != board[To[0]][To[1] + 1] != 3) or (
                (To[0],To[1] + 2) in self.camps and board[To[0]][To[1]] != board[To[0]][To[1] + 1] and
                board[To[0]][To[1] + 1] not in [0,3])):
            board[To[0]][To[1] + 1] = 0
        if move[0][0] == 8 and move[0][1] == 3 and move[1][0] == 6 and move[1][1] == 3:
            return board, kingPos
        return board, kingPos
