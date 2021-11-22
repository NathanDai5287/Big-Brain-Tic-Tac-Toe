from dependencies import *

from move import Move
from ttt import TicTacToe

class SubBoard:

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

	@property
	def as_tuple(self):
		return tuple(map(tuple, self.board))

	def validate_move(self, row: int, col: int) -> bool:
		if ((row, col) in self.empty):
			return True

	def move(self, row: int, col: int, iplayer: int) -> bool:
		self.board[row, col] = iplayer

class Board:
	value_map = {-1: 'O',
							 None: '~',
							 1: 'X'}

	lines = {
			((0, 0), (0, 1), (0, 2)), ((0, 2), (1, 1), (2, 0)), ((2, 0), (2, 1), (2, 2)), # rows
			((0, 1), (1, 1), (2, 1)), ((0, 0), (1, 1), (2, 2)), ((1, 0), (1, 1), (1, 2)), # columns
			((0, 0), (1, 0), (2, 0)), ((0, 2), (1, 2), (2, 2)) # diagonals
		}

	with open('ttt.pkl', 'rb') as f:
		fitness = pickle.load(f)

	def __init__(self):
		# big board
		# None if nobody has won the subboard
		# 0 or 1 if player 0 or 1 has won
		self.board = np.full((3, 3), None)
		self.subboards = np.array([deepcopy([deepcopy(SubBoard()) for row in range(3)]) for col in range(3)]) # 9 subboards arranged in 3 x 3 grid

		self.iplayer = 1 # tracks which player should go
		self.previous: Move = None # previous move. None represents no previous moves

		# TEMP: subject to change
		self.importance = np.array([ # importance score of each subboard CHANGE
			[1, 0, 1],
			[0, 2, 0],
			[1, 0, 1],
		], dtype=float)

		self.initial = self.importance.copy()

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

	@property
	def absolute(self) -> np.array:
		absolute = np.empty((9, 9), dtype=int)
		for row in range(9):
			for col in range(9):
				move = Move(row=row, col=col)
				(bigrow, bigcol), (subrow, subcol) = move.relative
				absolute[row, col] = self.subboards[bigrow, bigcol][subrow, subcol]

		return absolute

	def next_subboard(self) -> tuple[int, int]:
		"""returns the next subboard to play in; -1 if any

		Returns:
				tuple[int, int]: the next subboard to play in
		"""

		bigrow, bigcol = self.previous.sub

		if (self.subboards[bigrow, bigcol].winner is None):
			return bigrow, bigcol

		return (-1, -1)

	def possible_moves(self) -> list[Move]: # BUG: make sure the subboard is corresponding
		"""finds the possible moves that can be made

		Returns:
				set[Move]: set of possible moves
		"""

		moves = []
		for row in range(9):
			for col in range(9):
				move = Move(row=row, col=col)
				if (self.validate_move(move)):
					moves.append(move)

		return moves

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

	def bwin(self) -> int: # REFACTOR: refactor using self.lines
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
			print(move)
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

	# returns the average importance score of all the subboards that have not been won
	def total_importance(self) -> float:
		total = 0
		counter = 0
		for row in range(3):
			for col in range(3):
				if (self.board[row, col] is None):
					total += self.importance[row, col]
					counter += 1

		return total / counter

	def scale_importance(self, lower: float=0, upper: float=10):
		smallest = np.amin(self.importance)
		largest = np.amax(self.importance)

		def f(x):
			m = (upper - lower) / (largest - smallest)

			return m * (x - smallest) + lower

		transformation = np.vectorize(f)

		self.importance = transformation(self.importance)

	def ai_move(self, bdumb=False) -> Move:
		def dumb():
			possible = self.possible_moves()
			for move in possible:
				hypothetical = deepcopy(self)
				row, col = move.absolute
				bigrow, bigcol = move.big
				subrow, subcol = move.sub

				if (self.board[subrow, subcol] is not None):
					continue

				hypothetical.move(row, col)

				if (hypothetical.board[bigrow, bigcol] == self.iplayer):
					return move

			move = random.choice(self.possible_moves())

			return move

		if (bdumb):
			dumb()

		for bigrow in range(3):
			for bigcol in range(3):
				subboard = self.subboards[bigrow, bigcol]

				# self vs. opponent move count

				count = 0
				for subrow in range(3):
					for subcol in range(3):
						# if (self.board[subrow, subcol] is not None):
							# print('Won')
							# count += 5 * self.total_importance()
							# count += 5000000
						if (subboard[subrow, subcol] == -self.iplayer):
							count += 1
						elif (subboard[subrow, subcol] == self.iplayer):
							count -= 1

				self.importance[bigrow, bigcol] += count

		# same as line 358
		# increase importance if the subboard is won
		# for row in range(3):
			# for col in range(3):
				# if (self.board[row, col] is not None):
					# self.importance[row, col] += 50000

		# the subboards that can lead to a win have higher scores

		# raise the score of all subboards in the line by their average importance
		shift = np.full((3, 3), 0, dtype=float)
		for a, b, c in self.lines: # TODO:
			average = (abs(self.importance[a]) + abs(self.importance[b]) + abs(self.importance[c])) / 3

			# if (a != None or b != None or c != None): # CONFUCIOUS: idk why this is here
				# average *= -1

			shift[a] += average
			shift[b] += average
			shift[c] += average

		self.importance += shift

		self.scale_importance()

		# add importance to subboards that have been won
		for row in range(3):
			for col in range(3):
				if (self.board[row, col] is not None):
					self.importance[row, col] = 10

		# possible = [(row, col) for row in range(3) for col in range(3) if subboard[row, col] is None]

		scores = sorted(self.importance.flatten(), reverse=True)

		bigrow, bigcol = self.next_subboard()
		subboard = self.subboards[bigrow, bigcol]

		if ((bigrow, bigcol) == (-1, -1)): # TODO: handle case where the player is sent to a taken subboard
			bigrow, bigcol = random.choice(np.where(self.importance == np.amax(self.importance)))

		if (self.importance[bigrow, bigcol] >= scores[2]): # BUG: sending me to taken square
			print('Important')

			ttt = TicTacToe(self.subboards[bigrow, bigcol], self.iplayer)

			for row in range(3):
				for col in range(3):
					if (self.board[row, col] is not None):
						hypothetical = deepcopy(ttt)
						hypothetical.move(row, col)

						score = self.fitness[hypothetical] # BUG: not all states are in self.fitness ex: two O in one subboard

						self.importance[row, col] -= 2 * score

			scores = sorted(self.importance.flatten())
			for score in scores: # BUG: if all of the important subboards are taken, this will cause an error
				# TODO: use numpy.amax to find the highest score

				useless_coords = list(map(tuple, np.asarray(np.where(np.isclose(self.importance, score))).T))
				useless_coords = [coord for coord in useless_coords if subboard[coord] is None]

				if (useless_coords):
					selection = random.choice(np.transpose(np.where(self.importance == np.amax(self.importance))))
					break

		if (self.importance[bigrow, bigcol] < scores[2]): # if the player was not sent to an important subboard
			# useless = np.asarray(np.where(self.importance == scores[-1])).T
			# selection = random.choice(useless)
			for score in scores[::-1]:
				useless_coords = list(map(tuple, np.asarray(np.where(np.isclose(self.importance, score))).T))
				useless_coords = [coord for coord in useless_coords if subboard[coord] is None]

				if (useless_coords):
					selection = random.choice(useless_coords)
					break

			print('not important')

		# elif (self.importance[bigrow, bigcol] > scores[2]): # if the player was sent to an important subboard
			# TODO: pick the best move that will do the least damange

			# scores = sorted(self.importance.flatten(), reverse=True)

		move = Move(bigrow=bigrow, bigcol=bigcol, subrow=selection[0], subcol=selection[1])

		print(self.importance)

		return move

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
