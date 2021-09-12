from dependencies import *

from move import Move

# sys.stdout = open('stdout.out', 'w')

class SubBoard:
	x_win = np.array([
			[1, 0, 1],
			[0, 1, 0],
			[1, 0, 1],
		])

	o_win = np.array([
			[-1, -1, -1],
			[-1, 0, -1],
			[-1, -1, -1],
		])

	def __init__(self):
		self.board = np.full((3, 3), None)

	def __repr__(self):
		return str(self.board)

	def __getitem__(self, coord: tuple[int, int]) -> int:
		return self.board[coord]

	@property
	def empty(self) -> set[tuple[int, int]]:
		return {(i, j) for i in range(3) for j in range(3) if self.board[i, j] is None}

	@property
	def winner(self) -> int:
		"""who has won the SubBoard

		Returns:
				int: None if no winner yet; 0 if tie; -1 or 1 if player has won
		"""

		# check rows
		for i in range(3):
			if self.board[i, 0] == self.board[i, 1] == self.board[i, 2] and self.board[i, 0] is not None:
				return self.board[i, 0]

		# check columns
		for j in range(3):
			if self.board[0, j] == self.board[1, j] == self.board[2, j] and self.board[0, j] is not None:
				return self.board[0, j]

		# check diagonals
		if self.board[0, 0] == self.board[1, 1] == self.board[2, 2] and self.board[0, 0] is not None:
			return self.board[0, 0]
		if self.board[0, 2] == self.board[1, 1] == self.board[2, 0] and self.board[0, 2] is not None:
			return self.board[0, 2]

		# check for tie
		if self.empty == set():
			return 0

		# no winner yet
		return None

	def validate_move(self, row: int, col: int) -> bool:
		if ((row, col) in self.empty):
			return True

	def move(self, row: int, col: int, iplayer: int) -> bool:
		self.board[row, col] = iplayer

class Board:
	value_map = {-1: 'O',
							 None: '~',
							 1: 'X'}

	def __init__(self):
		# big board
		# None if nobody has won the subboard
		# 0 or 1 if player 0 or 1 has won
		self.board = np.full((3, 3), None)
		self.subboards = np.array([deepcopy([deepcopy(SubBoard()) for row in range(3)]) for col in range(3)]) # 9 subboards arranged in 3 x 3 grid

		self.iplayer = 1 # tracks which player should go
		self.previous: Move = None # previous move. None represents no previous moves

	def __repr__(self):
		out = ''

		out += '  0 1 2  3 4 5  6 7 8\n'

		for row in range(9):
			if (row % 3 == 0 and row != 0):
				out += '\n'
			out += str(row) + ' '

			for col in range(9):
				move = Move(row=row, col=col)
				(bigrow, bigcol), (subrow, subcol) = move.relative

				if (self.board[bigrow, bigcol] is None):
					value = self.value_map[self.subboards[bigrow, bigcol][subrow, subcol]]
				else:
					value = self.value_map[self.subboards[bigrow, bigcol].winner]

				if (col % 3 == 0 and col != 0):
					out += ' '

				out += value + ' '

			out += '\n'

		return out

	def validate_move(self, move: Move) -> bool:
		"""validates a move

		Args:
				move (Move): move to validate

		Returns:
				bool: True if the move is valid, False otherwise
		"""

		(bigrow, bigcol), (subrow, subcol) = move.relative

		if not (self.board[bigrow, bigcol] is None): # if the subboard that move is trying to play in has already been won
			return False

		if not ((subrow, subcol) in self.subboards[bigrow, bigcol].empty): # if the move has already been made
			return False

		if (self.previous is not None):
			if not (move.bigrow == self.previous.subrow and move.bigcol == self.previous.subcol): # if it's not corresponding
				if not (self.subboards[self.previous.subrow, self.previous.subcol].winner is None): # if the previous subboard has not been won
					return True
				return False

		return True

	def bwin(self) -> int:
		"""who has won the board

		Returns:
				int: None if no winner yet; 0 if tie; -1 or 1 if player has won
		"""

		# check rows
		for row in range(3):
			if self.board[row, 0] == self.board[row, 1] == self.board[row, 2] and self.board[row, 0] is not None:
				return self.board[row, 0]

		# check columns
		for col in range(3):
			if self.board[0, col] == self.board[1, col] == self.board[2, col] and self.board[0, col] is not None:
				return self.board[0, col]

		# check diagonals
		if self.board[0, 0] == self.board[1, 1] == self.board[2, 2] and self.board[0, 0] is not None:
			return self.board[0, 0]
		if self.board[0, 2] == self.board[1, 1] == self.board[2, 0] and self.board[0, 2] is not None:
			return self.board[0, 2]

		# check for tie
		for row in self.board:
			for col in row:
				if row is None:
					return None

		# no winner yet
		return None

	def move(self, row: int, col: int) -> bool:
		"""makes a move

		Args:
				move (Move): move to make

		Returns:
				bool: True if the move was made, False otherwise
		"""

		move = Move(row=row, col=col)

		if not (self.validate_move(move)):
			print('Invalid Move')
			print(f'{self.value_map[self.iplayer]} to move')

			return False

		(bigrow, bigcol), (subrow, subcol) = move.relative

		self.subboards[bigrow, bigcol].move(subrow, subcol, self.iplayer)

		status = self.subboards[bigrow, bigcol].winner
		if (status is not None): # if the subboard game has ended
			self.board[bigrow][bigcol] = status

		self.iplayer = -self.iplayer
		self.previous = move

		if ((winner := self.bwin()) is not None):
			if (winner == 1):
				print('X wins')
			elif (winner == -1):
				print('O wins')
			elif (winner == 0):
				print('Tie')

		return True

if __name__ == '__main__':
	board = Board()

	moves = [
		Move(row=0, col=1),
		Move(row=0, col=3),
		Move(row=1, col=1),
		Move(row=3, col=3),
		Move(row=2, col=1),
	]

	# # move = Move(row=0, col=0)
	[board.move(move) for move in moves]

	open('moves.log', 'a').write('\n\n')
	while (True):
		print(board, flush=True)

		row, col = map(int, input().split())
		print()

		move = Move(row=row, col=col)
		board.move(move)

		with open('log', 'a') as f:
			f.write(str(row) + ' ' + str(col) + '\n')

	# move = Move(1, 2, 3, 4)
	# print(type(move))
