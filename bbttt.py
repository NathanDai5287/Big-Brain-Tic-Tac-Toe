from dependencies import *

from board import Board
from move import Move

from tkinter import *
from tkinter import messagebox

PINK = 'light pink'
BLUE = 'light blue'
DARK_PINK = '#D6586B'
DARK_BLUE = '#3FA0BF'
GREEN = 'light green'
GRAY = 'light gray'
DEFAULT = 'SystemButtonFace'

# DARK_BLUE = BLUE
# DARK_PINK = PINK

# TODO: gray out subbaord on tie
# TODO: end game
# TODO: end game on tie
# TODO: make the last move darker

class SubSquare(Button):
	def __init__(self, master: object, row: int, col: int, **kwargs):
		super().__init__(master=master, **kwargs)

		self.row = row
		self.col = col
		self.move = Move(row=row, col=col)
		self.state = 0 # 0 = empty, 1 = X, -1 = O

	@property
	def absolute(self) -> tuple[int, int]:
		return (self.row, self.col)

	@property
	def relative(self) -> tuple[int, int]:
		return (self.bigrow, self.bigcol, self.subrow, self.subcol)

	@property
	def bigrow(self) -> int:
		return self.row // 3

	@property
	def bigcol(self) -> int:
		return self.col // 3

	@property
	def bigcoord(self) -> tuple[int, int]:
		return (self.bigrow, self.bigcol)

	@property
	def subrow(self) -> int:
		return self.row % 3

	@property
	def subcol(self) -> int:
		return self.col % 3

	def click(self, player: int):
		self.state = player

class BigBrainTicTacToe(Frame):
	color_map = {
		1: {False: BLUE, True: DARK_BLUE},
		-1: {False: PINK, True: DARK_PINK},
	}

	def __init__(self, master: Tk, ai: bool=False, human_player=1):
		super().__init__(master)
		self.grid()

		self.root = master

		self.ai = ai
		self.human_player = human_player

		self.root.bind('<Control-z>', self.undo)

		self.board = Board()
		self.setup_subsquares()

	def setup_subsquares(self):
		self.buttons = np.empty((9, 9), dtype=Board)
		for row in range(9):
			for col in range(9):
				move = Move(row=row, col=col)

				button = SubSquare(self, row, col, width=4, height=2, pady=20, padx=20)
				button.config(command=lambda button=button: self.click(button))

				if (move.bigrow == move.bigcol or move.bigrow + move.bigcol == 2):
					button.config(bg='light gray')

				self.buttons[row, col] = button
				self.buttons[row, col].grid(row=row + 1, column=col, rowspan=1, columnspan=1)

	def color_subboard(self, bigrow: int, bigcol: int, color: str): # BUG: something doesn't work here
		for subrow in range(3):
			for subcol in range(3):
				move = Move(bigrow=bigrow, bigcol=bigcol, subrow=subrow, subcol=subcol)
				row, col = move.absolute
				self.buttons[row, col].config(bg=color)

	def click(self, button: SubSquare, bhuman=True):
		with open('previous.pkl', 'wb') as f:
			pickle.dump(self.board, f)

		row, col = button.absolute
		move = Move(row=row, col=col)
		bigrow, bigcol = move.big

		iplayer = self.board.iplayer
		previous = self.board.previous
		bvalid = self.board.move(row, col)
		bcross = move.bcross()

		if not (bvalid):
			return

		# change the button's state
		self.buttons[row, col].config(
			text=self.board.value_map[iplayer],
			relief=SUNKEN,
			bg=self.color_map[iplayer][False],
		)

		# if the subboard was won, color it
		if not ((status := self.board.board[bigrow, bigcol]) is None):
			if (status == 1):
				color = BLUE
			elif (status == -1):
				color = PINK

			for neighbor in move.group():
				r, c = neighbor.absolute
				self.buttons[r, c].config(bg=color)

		# darken the current move and undarken the previous move
		self.buttons[move.absolute].config(bg=self.color_map[iplayer][True])
		if (previous is not None):
			self.buttons[previous.absolute].config(bg=self.color_map[-iplayer][False])

		# TODO: color possible subboards for the next move and uncolor previous
		# if not (self.board.board[move.sub] is None):
			# self.color_subboard(move.subrow, move.subcol, GREEN)

		# previous = self.board.previous
		# self.color_subboard(previous.bigrow, previous.bigcol, GRAY if previous.bcross() else DEFAULT)

		# TODO: check win
		if (bwin := self.board.bwin()): # display winner
			bagain = messagebox.askyesno(f'{self.board.value_map[-self.board.iplayer]} Wins', 'Play again?')

			if (bagain):
				# self.newgame()
				messagebox.showinfo('Error', 'Unfortunately this does not work yet')
			else:
				exit(0)

		# move computer
		if (self.ai and bhuman and not bwin):
			self.after(1000, lambda: self.ai_move())
			# self.ai_move()

	def undo(self, *args):
		with open('previous.pkl', 'rb') as f:
			self.board = pickle.load(f)

	def dump(self):
		with open('previous.pkl', 'wb') as f:
			pickle.dump(self.board, f)

	def load(self, filename: str='previous.pkl'):
		with open(filename, 'rb') as f:
			self.board = pickle.load(f)

	def newgame(self):
		[button.destroy() for button in self.buttons.flat]

		# self.__init__(self.root, ai=self.ai, human_player=self.human_player)
		self.__init__(Tk(), ai=self.ai, human_player=self.human_player)

	def ai_move(self):
		move = self.board.ai_move()
		self.click(self.buttons[move.row, move.col], bhuman=False)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--ai', action='store_true', help='play against the computer')
	args = parser.parse_args()

	root = Tk()
	root.title("Big Brain Tic-Tac-Toe")
	# game = BigBrainTicTacToe(root, ai=True)
	game = BigBrainTicTacToe(root, ai=False)
	# print(args.ai)
	# game = BigBrainTicTacToe(root, ai=args.ai)
	game.mainloop()
