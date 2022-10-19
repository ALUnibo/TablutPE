import sys
import utility
import tablutAI
import time
import copy
import numpy as np
DEBUG = False

# Input management
name = "Python Elite"
role = str(sys.argv[1])
timer = int(sys.argv[2])
print("I'll be playing as " + role + " with a " + str(timer) + "s timer in the name of the " + name)
if len(sys.argv) == 4:
    address = sys.argv[3]
else:
    address = 'localhost'

handler = utility.Handler(name, role, address)
board, turn, kingPos = handler.openConnection()

TestBoard = [[ 0,  0,  0, -1, -1, -1,  0,  0,  0],
             [ 0,  0,  0,  0, -1,  0,  0,  0,  0],
             [ 0,  0,  0,  0,  1,  0,  0,  0,  0],
             [-1,  0,  0,  0,  1,  0,  0,  0, -1],
             [-1, -1,  1,  1,  3,  1,  1, -1, -1],
             [-1,  0,  0,  0,  1,  0,  0,  0, -1],
             [ 0,  0,  0,  0,  1,  0,  0,  0,  0],
             [ 0,  0,  0,  0, -1,  0,  0,  0,  0],
             [ 0,  0,  0, -1, -1, -1,  0,  0,  0]]

TestKingPos = (-1, -1)
for i in range(0, 9):
    for j in range(0, 9):
        if TestBoard[i][j] == 3:
            TestKingPos = (i, j)
            break
    else:
        continue
    break

AI = tablutAI.TablutAI(role, timer, depth=3, cutoff=4)
# bestMove = AI.searchBestMove(TestBoard, TestKingPos, time.perf_counter())

winCondition = False

if role == "WHITE" or role == "White" or role == "white":
    print("Opening move, e3 to f3!")
    handler.sendMove(((2, 4), (2, 5)))
    board, turn, kingPos = handler.recieveState()
while not winCondition:
    if turn == role:
        print("Looking for the best move, please wait...")
        bestMove = AI.searchBestMove(board, kingPos, time.perf_counter())
        handler.sendMove(bestMove)
    else:
        print("Waiting for enemy move...")
    board, turn, kingPos = handler.recieveState()
    if DEBUG:
        print("Here's the current state of the game:")
        print(board)

