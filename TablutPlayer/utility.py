import socket
import struct
import json
import numpy as np
DEBUG = False

class Handler:
    def __init__(self, name, role, address):
        self.mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name
        self.role = role
        self.address = address

    def openConnection(self):
        if self.role == 'WHITE' or self.role == "White" or self.role == "white":
            target = (self.address, 5800)
        elif self.role == 'BLACK' or self.role == "Black" or self.role == "black":
            target = (self.address, 5801)
        else:
            raise Exception('Invalid role')

        self.mainSocket.connect(target)
        msg = json.dumps(self.name)
        length = len(msg.encode('UTF-8'))
        self.mainSocket.sendall(length.to_bytes(4, 'big') + msg.encode('UTF-8'))

        return self.recieveState()

    def recieveState(self):
        data = b''
        while len(data) < 4:
            packet = self.mainSocket.recv(4 - len(data))
            if not packet:
                data = None
                break
            data += packet
        length = struct.unpack('>i', data)[0]
        message = self.mainSocket.recv(length)
        jsonState = json.loads(message)
        board, turn, kingPos = self.jsonTranslate(jsonState)
        return board, turn, kingPos

    def sendMove(self, move):
        jsonMove = json.dumps({
            "from": "" + chr(97 + move [0][1]) + str(1 + move[0][0]),
            "to": "" + chr(97 + move [1][1]) + str(1 + move[1][0]),
            "turn": self.role
        })
        self.mainSocket.send(struct.pack('>i', len(jsonMove)))
        self.mainSocket.send(jsonMove.encode())
        print("Move " + chr(97 + move [0][1]) + str(1 + move[0][0]) + " to " + chr(97 + move [1][1]) +
              str(1 + move[1][0]) + " sent.")
        if DEBUG:
            print("Ecco il JSON:")
            print(json.dumps(jsonMove))
        return jsonMove

    def jsonTranslate(self, json_state):
        state = np.array(list(json_state.items()),dtype=object)
        boardStrings = state[0,1]
        turn = state[1,1]
        board = np.zeros((9,9))
        kingPos = (-1,-1)
        for i in range(0,9):
            for j in range(0,9):
                match boardStrings[i][j]:
                    case "EMPTY":
                        pass
                    case "WHITE":
                        board[i][j] = 1
                    case "BLACK":
                        board[i][j] = -1
                    case "KING":
                        board[i][j] = 3
                        kingPos = (i,j)
        return board, turn, kingPos

