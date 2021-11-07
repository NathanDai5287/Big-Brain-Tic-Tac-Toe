from dependencies import *

from board import SubBoard

class TicTacToe:
	def __init__(self, *subboard: SubBoard):
		if (subboard):
			assert len(subboard) == 2, 'TicTacToe can only be initialized with a SubBoard and the turn'
			assert type(subboard[0]) == SubBoard, 'TicTacToe can only be initialized with a SubBoard'

			subboard, turn = subboard
			self.board = subboard.board
			self.turn = turn
		else:
			self.board = np.full((3, 3), None)
			self.turn = 1

	def __iter__(self):
		for row in range(3):
			for col in range(3):
				yield self.board[row, col]

	def __hash__(self):
		return hash(tuple(self.board.flatten()))

	def __eq__(self, other: object):
		return (self.board == other.board).all()

	def __add__(self, move: tuple[int, int]):
		hypothetical = deepcopy(self)
		hypothetical.move(*move)

		return hypothetical

	def __repr__(self):
		output = '\n'
		for row in range(3):
			for col in range(3):

				if (self.board[row, col] == None):
					output += '~'
				elif (self.board[row, col] == 1):
					output += 'X'
				else:
					output += 'O'

				output += '\t'

			output += '\n'

		return output

	def valid(self, row: int, col: int):
		return self.board[row, col] is None

	def bwin(self):
		for row in range(3):
			if (self.board[row][0] == self.board[row][1] == self.board[row][2] != None):
				return self.board[row, 0]

		for col in range(3):
			if (self.board[0][col] == self.board[1][col] == self.board[2][col] != None):
				return self.board[0, col]

		if (self.board[0][0] == self.board[1][1] == self.board[2][2] != None):
			return self.board[0, 0]

		if (self.board[0][2] == self.board[1][1] == self.board[2][0] != None):
			return self.board[0, 2]

		for row in range(3):
			for col in range(3):
				if (self.board[row, col] is None):
					return None

		return 0

	def move(self, row: int, col: int):
		if not (self.valid(row, col)):
			return

		self.board[row, col] = self.turn

		if (self.bwin()):
			return
		elif (self.board.all() != None):
			return

		self.turn *= -1

		return self

	def available_actions(self):
		return {(row, col) for row in range(3) for col in range(3) if self.board[row][col] == None}

fitness = {}
def evaluate(state: TicTacToe):
	winner = state.bwin()

	if (winner is not None):
		fitness[state] = abs(winner)
		return abs(winner)

	if (state in fitness):
		return fitness[state]

	score = set()
	for row, col in state.available_actions():
		hypothetical = deepcopy(state)
		hypothetical.move(row, col)
		score.add(evaluate(hypothetical))

	fitness[state] = -max(score)

	return fitness[state]

if __name__ == '__main__':
	game = TicTacToe()

	with open('ttt.pkl', 'rb') as f:
		fitness = pickle.load(f)

	while not (game.bwin()):

		scores = [(move, fitness[game + move]) for move in game.available_actions()]
		move = max(scores, key=lambda x: x[-1])[0]

		game.move(*move)
		print(game)

		row = int(input('Row: '))
		col = int(input('Col: '))

		game.move(row, col)

		print(game)
