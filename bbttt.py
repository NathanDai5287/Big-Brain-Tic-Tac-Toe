from dependencies import *

from board import Board
from move import Move

from tkinter import *

PINK = 'light pink'
BLUE = 'light blue'
DARK_PINK = '#D6586B'
DARK_BLUE = '#3FA0BF'

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

	def __init__(self, master: Tk):
		super().__init__(master)
		self.grid()

		self.root = master

		self.board = Board()
		self.setup_subsquares()

	def setup_subsquares(self):
		self.buttons = np.empty((9, 9), dtype=Board)
		for row in range(9):
			for col in range(9):
				move = Move(row=row, col=col)

				button = SubSquare(self, row, col, width=4, height=2) # TODO: color the subboards with gray background
				button.config(command=lambda button=button: self.click(button))

				if (move.bigrow == move.bigcol or move.bigrow + move.bigcol == 2):
					button.config(bg='light gray')

				self.buttons[row, col] = button
				self.buttons[row, col].grid(row=row + 1, column=col, rowspan=1, columnspan=1)

	def recolor_subboard(self, bigrow: int, bigcol: int, color: str):
		for subrow in range(3):
			for subcol in range(3):
				move = Move(bigrow=bigrow, bigcol=bigcol, subrow=subrow, subcol=subcol)
				row, col = move.absolute
				self.buttons[row, col].config(bg=color)

	def click(self, button: SubSquare):
		row, col = button.absolute
		move = Move(row=row, col=col)
		bigrow, bigcol = move.big

		iplayer = self.board.iplayer
		bvalid = self.board.move(row, col)
		bcross = move.bcross()

		if not (bvalid):
			return

		# change the button's state
		self.buttons[row, col].config(
			text=self.board.value_map[iplayer],
			relief=SUNKEN,
			bg=self.color_map[iplayer][bcross],
		)

		# if the subboard was won, color it
		if not ((status := self.board.board[bigrow, bigcol]) is None):
			if (status == 1):
				color = DARK_BLUE if bcross else BLUE
			elif (status == -1):
				color = DARK_PINK if bcross else PINK

			for neighbor in move.group():
				r, c = neighbor.absolute
				self.buttons[r, c].config(bg=color)

if __name__ == "__main__":
	root = Tk()
	root.title("Big Brain Tic-Tac-Toe")
	game = BigBrainTicTacToe(root)
	game.mainloop()
