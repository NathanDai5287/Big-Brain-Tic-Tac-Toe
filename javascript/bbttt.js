
const PINK = '#ffb6c1';
const BLUE = 'add8e6';
const DARK_PINK = '#d6586b';
const DARK_BLUE = '#3FA0BF';
const GRAY = '#d3d3d3';

class BigBrainTicTacToe {
	constructor() {
		this.color_map = {
			1: { false: BLUE, true: DARK_BLUE },
			'-1': { false: PINK, true: DARK_PINK },
		}

		this.board = new Board();
		this.handler();
	}

	handler() {
		for (let row = 0; row < 9; row++) {
			for (let col = 0; col < 9; col++) {
				var id = row + ' ' + col;
				document.getElementById(id).addEventListener('click', function () {
					game.move(row, col);
				});
			}
		}
	}

	move(row, col) {
		var move = new Move(row = row, col = col);
		var [bigrow, bigcol] = move.big();

		var iplayer = this.board.iplayer;
		var previous = this.board.previous
		var bvalid = this.board.move(row, col);

		if (!bvalid) {
			return;
		}

		var id = row + ' ' + col;
		var button = document.getElementById(id)
		button.innerText = this.board.value_map[iplayer];
		button.borderStyle = 'inset';
		button.style.backgroundColor = this.color_map[iplayer][false];

		var state = this.board.board[bigrow][bigcol];
		var color;
		if (state == null) {
			if (state == 1) {
				color = BLUE;
			} else if (state == -1) {
				color = PINK;
			}

			var r, c;
			for (let neighbor of move.group(move.bigrow, move.bigcol)) {
				[r, c] = neighbor.absolute();
				var id = r + ' ' + c;
				var button = document.getElementById(id);
				button.style.backgroundColor = color;
			}
		}

		[r, c] = move.absolute();
		var id = r + ' ' + c;
		var button = document.getElementById(id);
		button.style.backgroundColor = this.color_map[iplayer][true];
		if (previous != null) {
			[r, c] = previous.absolute();
			var id = r + ' ' + c;
			var button = document.getElementById(id);
			button.style.backgroundColor = this.color_map[-iplayer][false];
		}

		var winner = this.board.bwin();
		if (winner) {
			var message = winner == 1 ? 'X Wins!' : 'O Wins!';
			alert(message);
		}
	}
}

var game = new BigBrainTicTacToe();
