class Move:
	def __init__(self, row: int=None, col: int=None, bigrow: int=None, bigcol: int=None, subrow: int=None, subcol: int=None):
		if (None in {row, col}):
			assert None not in {bigrow, bigcol, subrow, subcol}
			absolute = False
		elif (None in {bigrow, bigcol, subrow, subcol}):
			assert None not in {row, col}
			absolute = True

		if (absolute):
			bigrow, subrow = divmod(row, 3)
			bigcol, subcol = divmod(col, 3)
		else:
			row = bigrow * 3 + subrow
			col = bigcol * 3 + subcol

		self.row = row
		self.col = col
		self.bigrow = bigrow
		self.bigcol = bigcol
		self.subrow = subrow
		self.subcol = subcol

	def __repr__(self):
		return str(self.absolute) + '\n' + str(self.relative)

	@property
	def relative(self) -> tuple[tuple[int, int], tuple[int, int]]:
		return ((self.bigrow, self.bigcol), (self.subrow, self.subcol))

	@property
	def absolute(self) -> tuple[int, int]:
		return (self.row, self.col)
