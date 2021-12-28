function deepClone(obj) {
	if (obj === null || typeof obj !== "object")
		return obj
	var props = Object.getOwnPropertyDescriptors(obj)
	for (var prop in props) {
		props[prop].value = deepClone(props[prop].value)
	}
	return Object.create(
		Object.getPrototypeOf(obj),
		props
	)
}

class Move {
	// constructor(row, col, bigrow, bigcol, subrow, subcol, iplayer) {
	constructor(...args) {
		var row = args[0]; var col = args[1]; var bigrow = args[2]; var bigcol = args[3]; var subrow = args[4]; var subcol = args[5]; var iplayer = args[6];

		var absolute;
		if (row == undefined || col == undefined) {
			absolute = false;
		} else if (bigrow == undefined || bigcol == undefined || subrow == undefined || subcol == undefined) {
			absolute = true;
		}

		var bigrow, bigcol, subrow, subcol;
		if (absolute) {
			bigrow = Math.floor(row / 3);
			subrow = row % 3;

			bigcol = Math.floor(col / 3);
			subcol = col % 3;
		} else {
			row = bigrow * 3 + subrow;
			col = bigcol * 3 + subcol;
		}

		this.row = row;
		this.col = col;
		this.bigrow = bigrow;
		this.bigcol = bigcol;
		this.subrow = subrow;
		this.subcol = subcol;

		this.iplayer = iplayer;
	}

	relative() {
		return [[this.bigrow, this.bigcol], [this.subrow, this.subcol]];
	}

	absolute() {
		return [this.row, this.col];
	}

	big() {
		return [this.bigrow, this.bigcol];
	}

	sub() {
		return [this.subrow, this.subcol];
	}

	bcross() {
		return this.bigrow == this.bigcol || this.bigrow + this.bigcol == 2;
	}

	*group(bigrow, bigcol) {
		var moves = [];
		for (let subrow = 0; subrow < 3; subrow++) {
			for (let subcol = 0; subcol < 3; subcol++) {
				yield new Move(null, null, bigrow, bigcol, subrow, subcol, null);
				// moves.push(Move(bigrow = this.bigrow, bigcol = this.bigcol, subrow = subrow, subcol = subcol));
			}
		}

		return moves;
	}

	id() {
		let [row, col] = this.absolute();
		return row + ' ' + col;
	}
}

class SubBoard {
	constructor() {
		this.board = [
			[null, null, null],
			[null, null, null],
			[null, null, null],
		];

		this.score = 0;
	}

	get(row, col) {
		return this.board[row][col];
	}

	empty() {
		var coords = [];
		for (let row = 0; row < 3; row++) {
			for (let col = 0; col < 3; col++) {
				if (this.board[row][col] == null) {
					coords.push([row, col]);
				}
			}
		}

		return coords;
	}

	winner() {
		for (let i = 0; i < 3; i++) {
			if (this.board[i][0] == this.board[i][1] && this.board[i][1] == this.board[i][2] && this.board[i][0] != null) {
				return this.board[i][0];
			}
		}

		for (let j = 0; j < 3; j++) {
			if (this.board[0][j] == this.board[1][j] && this.board[1][j] == this.board[2][j] && this.board[0][j] != null) {
				return this.board[0][j];
			}
		}

		if (this.board[0][0] == this.board[1][1] && this.board[1][1] == this.board[2][2] && this.board[0][0] != null) {
			return this.board[0][0];
		}
		if (this.board[0][2] == this.board[1][1] && this.board[1][1] == this.board[2][0] && this.board[0][2] != null) {
			return this.board[0][2];
		}

		if (this.empty().length == 0) {
			return 0;
		}

		return null;
	}

	validate_move(row, col) {
		if (this.empty().includes([row, col])) {
			return true;
		}

		return false;
	}

	next_subboard() {
		var [bigrow, bigcol] = this.previous.sub();

		if (this.subboards[bigrow][bigcol].winner() == null) {
			return [bigrow, bigcol];
		}

		return [-1, -1];
	}

	move(row, col, iplayer) {
		this.board[row][col] = iplayer;
	}

	undo(row, col) {
		this.board[row][col] = null;
	}
}

class Board {
	constructor(aiPlayer) {
		this.value_map = {
			'-1': 'O',
			null: '~',
			1: 'X',
		};

		this.board = [
			[null, null, null],
			[null, null, null],
			[null, null, null],
		];

		this.subboards = [
			[new SubBoard(), new SubBoard(), new SubBoard()],
			[new SubBoard(), new SubBoard(), new SubBoard()],
			[new SubBoard(), new SubBoard(), new SubBoard()],
		];

		this.lines = [
			[[0, 0], [0, 1], [0, 2]], [[0, 2], [1, 1], [2, 0]], [[2, 0], [2, 1], [2, 2]],
			[[0, 1], [1, 1], [2, 1]], [[0, 0], [1, 1], [2, 2]], [[1, 0], [1, 1], [1, 2]],
			[[0, 0], [1, 0], [2, 0]], [[0, 2], [1, 2], [2, 2]],
		];

		this.iplayer = 1;
		this.previous = null;

		this.aiPlayer = aiPlayer;
		this.score = 0;
	}

	__repr__() {
		var out = '';
		out += '  0 1 2  3 4 5  6 7 8\n';

		var move;
		var bigrow, bigcol, subrow, subcol;
		var value;

		for (let row = 0; row < 9; row++) {
			if (row % 3 == 0 && row != 0) {
				out += '\n';
			}
			out += row + ' ';

			for (let col = 0; col < 9; col++) {
				move = new Move(row = row, col = col);
				bigrow = move.bigrow; bigcol = move.bigcol; subrow = move.subrow; subcol = move.subcol;

				if (this.board[bigrow][bigcol] == null) {
					value = this.value_map[this.subboards[bigrow][bigcol].get(subrow, subcol)];
				} else {
					value = this.value_map[this.subboards[bigrow][bigcol].winner()];
				}

				if (col % 3 == 0 && col != 0) {
					out += ' ';
				}

				out += value + ' ';
			}

			out += '\n';
		}

		return out;
	}

	next_subboard() {
		var [bigrow, bigcol] = this.previous.sub();

		if (this.subboards[bigrow][bigcol].winner() == null) {
			return [bigrow, bigcol];
		}

		return [-1, -1];
	}

	*possible_moves() {
		var moves = [];

		var move;
		for (let row = 0; row < 3; row++) {
			for (let col = 0; col < 3; col++) {
				move = new Move(row = row, col = col);

				if (this.validate_move(move)) {
					// moves.push(move);
					yield move;
				}
			}
		}

		return moves;
	}

	contains(coords, target) {
		for (let i = 0; i < coords.length; i++) {
			if (coords[i][0] == target[0] && coords[i][1] == target[1]) {
				return true;
			}
		}

		return false;
	}

	validate_move(move) {
		var relative = move.relative();
		var [bigrow, bigcol] = relative[0];
		var [subrow, subcol] = relative[1];

		if (this.board[bigrow][bigcol] != null) {
			return false;
		}

		var empty = this.subboards[bigrow][bigcol].empty()
		if (!this.contains(empty, [subrow, subcol])) {
			return false;
		}

		if (this.previous != null) {
			if (move.bigrow != this.previous.subrow || move.bigcol != this.previous.subcol) {
				if (this.subboards[this.previous.subrow][this.previous.subcol].winner() != null) {
					return true;
				}
				return false;
			}
		}

		return true;
	}

	bwin() {
		for (let row = 0; row < 3; row++) {
			if (this.board[row][0] == this.board[row][1] == this.board[row][2] && this.board[row][0] != null) {
				return this.board[row][0];
			}
		}

		for (let col = 0; col < 3; col++) {
			if (this.board[0][col] == this.board[1][col] == this.board[2][col] && this.board[0][col] != null) {
				return this.board[0][col];
			}
		}

		if (this.board[0][0] == this.board[1][1] == this.board[2][2] && this.board[0][0] != null) {
			return this.board[0][0];
		}
		if (this.board[0][2] == this.board[1][1] == this.board[2][0] && this.board[0][2] != null) {
			return this.board[0][2];
		}

		for (let i = 0; i < 3; i++) {
			for (let j = 0; j < 3; j++) {
				if (this.board[i][j] == null) {
					return null;
				}
			}
		}
		return null;
	}

	move(row, col) {
		var move = new Move(row = row, col = col);

		if (!this.validate_move(move)) {
			console.log('Invalid move');
			return false;
		}

		var relative = move.relative();

		var [bigrow, bigcol] = relative[0];
		var [subrow, subcol] = relative[1];

		this.subboards[bigrow][bigcol].move(subrow, subcol, this.iplayer);

		var state = this.subboards[bigrow][bigcol].winner();
		if (state != null) {
			this.board[bigrow][bigcol] = state;
		}

		this.iplayer = -this.iplayer;
		this.previous = move;

		var winner = this.bwin();
		if (winner != null) {
			switch (winner) {
				case 1:
					console.log('X wins!');
					break;
				case -1:
					console.log('O wins!');
					break;
				case 0:
					console.log('Draw!');
					break;
			}
		}

		return true;
	}

	undo() {
		this.iplayer *= -1;

		var relative = this.previous.relative();
		var [bigrow, bigcol] = relative[0];
		var [subrow, subcol] = relative[1];

		this.subboards[bigrow][bigcol].undo(subrow, subcol);
		this.board[bigrow][bigcol] = null;
	}

	minimax(depth, player, alpha, beta) {
		var moves = Array.from(this.possible_moves());

		var score, best_move;

		if (depth == 0 || moves.length == 0) {
			score = this.getScore();

			return {
				score: score,
				move: null,
			}
		}

		for (let move of moves) {
			this.move(move);
			score = this.minimax(depth + 1, player == 1, alpha, beta).score;

			if (player == this.aiPlayer) {
				if (score > alpha) {
					alpha = score;
					best_move = move;
				}
			} else {
				if (score < beta) {
					beta = score;
					best_move = move;
				}
			}

			this.undo();
			if (alpha > beta) {
				break;
			}
		}

		return {
			score: player == this.aiPlayer ? alpha : beta,
			move: best_move,
		};
	}

	// getScore() {

	// }

	// scoreLine(line) {
		// var counter = {
			// X: 0,
			// O: 0,
			// tie: 0,
		// };

		// for ()
	// }
}