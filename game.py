import numpy as np
import logging

init_state = (
    (1,   2, 11,  3,  4,  6, 16,  7),
    (10, 25, 13, 12,  5,  0, 14,  8),
    (9,  20, 18, 27, 22, 23, 15, 24),
    (17, 26, 19, 28, 21, 29, 30, 31),
)

final_state = (
    (1, 2, 3, 4, 5, 6, 7, 8),
    (9, 10, 11, 12, 13, 14, 15, 16),
    (17, 18, 19, 20, 21, 22, 23, 24),
    (25, 26, 27, 28, 29, 30, 31, 0),
)

EMPTY_TILE = 0


def load_state(state_2d):
    return np.array(state_2d, dtype=np.int).flatten()


final_board = load_state(final_state)


def clone_and_swap(state_2d, y0, y1):
    clone = np.copy(state_2d)
    clone[y0], clone[y1] = clone[y1], clone[y0]
    return clone


def possible_moves(state_2d, size_cols):
    res = []
    y = np.where(state_2d == EMPTY_TILE)[0][0]
    if y % size_cols > 0:
        left = clone_and_swap(state_2d, y, y - 1)
        res.append(left)
    if y % size_cols + 1 < size_cols:
        right = clone_and_swap(state_2d, y, y + 1)
        res.append(right)
    if y - size_cols >= 0:
        up = clone_and_swap(state_2d, y, y - size_rows)
        res.append(up)
    if y + size_cols < np.size(state_2d):
        down = clone_and_swap(state_2d, y, y + size_rows)
        res.append(down)
    return res


class Game:

    def __init__(self):
        self.currentPlayer = 1
        self.cols = 8
        self.rows = 4
        self.pieces = {}
        self.load_pieces()
        self.gameState = None
        self.reset()
        self.actionSpace = load_state(init_state)
        self.grid_shape = (self.cols, self.rows)
        self.input_shape = (2, self.cols, self.rows)
        self.name = 'n-puzzle'
        self.state_size = len(self.gameState.binary)
        self.action_size = len(self.actionSpace)

    def load_pieces(self):
        self.pieces = {}
        for i in range(1, self.cols * self.rows):
            self.pieces[str(i)] = "{:2d}".format(i)
        self.pieces[str(0)] = "  "

    def reset(self):
        self.gameState = GameState(self.rows, self.cols, load_state(init_state), self.pieces, 1)
        self.currentPlayer = 1
        return self.gameState

    def step(self, action):
        next_state, value, done = self.gameState.takeAction(action)
        self.gameState = next_state
        self.currentPlayer = -self.currentPlayer
        info = None
        return next_state, value, done, info

    def identities(self, state, actionValues):
        identities = [(state, actionValues)]
        currentBoard = state.board
        currentAV = actionValues
        currentBoard = np.array([currentBoard[i] for i in range(self.cols * self.rows)])
        currentAV = np.array([currentAV[i] for i in range(self.cols * self.rows)])
        identities.append((GameState(currentBoard, state.playerTurn), currentAV))
        return identities


class GameState:
    def __init__(self, size_rows, size_cols, board, pieces, playerTurn):
        self.size_rows = size_rows
        self.size_cols = size_cols
        self.board = board
        self.pieces = pieces
        self.playerTurn = playerTurn
        self.binary = self._binary()
        self.id = self._convertStateToId()
        self.allowedActions = self._allowedActions()
        self.isEndGame = self._checkForEndGame()
        self.value = self._getValue()
        self.score = self._getScore()

    def _allowedActions(self):
        allowed = []
        y = np.where(self.board == EMPTY_TILE)[0][0]
        if y % self.size_cols > 0:
            allowed.append(y - 1)
        if y % self.size_cols + 1 < self.size_cols:
            allowed.append(y + 1)
        if y - self.size_cols >= 0:
            allowed.append(y - self.size_cols)
        if y + self.size_cols < np.size(self.board):
            allowed.append(y + self.size_cols)
        return allowed

    def _binary(self):
        currentplayer_position = np.zeros(len(self.board), dtype=np.int)
        currentplayer_position[self.board == self.playerTurn] = 1

        other_position = np.zeros(len(self.board), dtype=np.int)
        other_position[self.board == -self.playerTurn] = 1

        position = np.append(currentplayer_position, other_position)
        return position

    def _convertStateToId(self):
        player1_position = np.zeros(len(self.board), dtype=np.int)
        player1_position[self.board == 1] = 1

        other_position = np.zeros(len(self.board), dtype=np.int)
        other_position[self.board == -1] = 1

        position = np.append(player1_position, other_position)

        id = ''.join(map(str, position))

        return id

    def _checkForEndGame(self):
        return 1 if (self.board == final_board).all() else 0

    def _getValue(self):
        if self._checkForEndGame():
            return (-1, -1, 1)
        else:
            return (0, 0, 0)

    def _getScore(self):
        tmp = self.value
        return (tmp[1], tmp[2])

    def takeAction(self, action):
        newBoard = np.array(self.board)
        newBoard[action] = self.playerTurn

        newState = GameState(self.size_rows, self.size_cols, newBoard, self.pieces, -self.playerTurn)

        value = 0
        done = 0

        if newState.isEndGame:
            value = newState.value[0]
            done = 1

        return (newState, value, done)

    def render(self, logger):
        board = np.reshape(self.board, (self.size_rows, self.size_cols))
        for r in range(self.size_rows):
            s = str([self.pieces[str(x)] for x in board[r]])
            logger.info([self.pieces[str(x)] for x in board[r]])
        logger.info('-' * len(s))
