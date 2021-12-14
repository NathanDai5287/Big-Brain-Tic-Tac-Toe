const PINK = '#ffb6c1';
const BLUE = '#add8e6';
const DARK_PINK = '#d6586b';
const DARK_BLUE = '#3FA0BF';
const GRAY = '#d3d3d3';

class BigBrainTicTacToe {
	constructor(aiPlayer) {
		this.color_map = {
			1: { false: BLUE, true: DARK_BLUE },
			'-1': { false: PINK, true: DARK_PINK },
		}

		this.board = new Board();
		this.handler();

		this.aiPlayer = aiPlayer;

		this.timer = new Timer(this.getTime());
		var [min, sec] = this.timer.time(1);
		this.setTime(min, sec);
	}

	getTime() {
		var url = new URL(window.location.href);
		var time = url.searchParams.get('time');

		return time;
	}

	setTime(min, sec) {
		for (let label of document.getElementsByClassName('time')) {
			label.innerText = min + ':' + String(sec).padStart(2, '0');
		}
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
		this.timer.swap();
		if (this.board.previous == null) {
			this.timer.start();
			this.update = setInterval(() => { this.updateTimer() }, 500);
		}

		var move = new Move(row, col);
		var [bigrow, bigcol] = move.big();

		var iplayer = this.board.iplayer;
		var previous = this.board.previous
		var bvalid = this.board.move(row, col);

		if (!bvalid) {
			return;
		}

		for (let nextrow = 0; nextrow < 3; nextrow++) {
			for (let nextcol = 0; nextcol < 3; nextcol++) {
				this.uncolor_subboard(nextrow, nextcol);
			}
		}

		var [nextbigrow, nextbigcol] = this.board.next_subboard();
		if (nextbigrow == -1 && nextbigcol == -1) {
			for (let nextrow = 0; nextrow < 3; nextrow++) {
				for (let nextcol = 0; nextcol < 3; nextcol++) {
					if (this.board.board[nextrow][nextcol] != null) {
						this.color_subboard(nextrow, nextcol);
					}
				}
			}
		} else {
			this.color_subboard(nextbigrow, nextbigcol);
		}

		var id = row + ' ' + col;
		var button = document.getElementById(id)
		button.innerText = this.board.value_map[iplayer];
		button.borderStyle = 'inset';
		button.style.backgroundColor = this.color_map[iplayer][false];

		var state = this.board.board[bigrow][bigcol];
		var color;
		if (state != null) {
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

	updateTimer() {
		var [minutes, seconds] = this.timer.time(this.board.iplayer);
		var time = minutes + ':' + String(seconds).padStart(2, '0');

		document.getElementById(this.timer.getid()).innerText = time;
	}

	color_possible() {
		for (let bigrow = 0; bigrow < 3; bigrow++) {
			for (let bigcol = 0; bigcol < 3; bigcol++) {
				uncolor_subboard(bigrow, bigcol);
			}
		}

		var [bigrow, bigcol] = this.board.next_subboard();
		this.color_subboard(bigrow, bigcol);
	}

	color_subboard(bigrow, bigcol) {
		var move, id;
		for (let subrow = 0; subrow < 3; subrow++) {
			for (let subcol = 0; subcol < 3; subcol++) {
				move = new Move(null, null, bigrow, bigcol, subrow, subcol);
				id = move.id();
				var button = document.getElementById(id);
				button.classList.add('selected');
			}
		}
	}

	uncolor_subboard(bigrow, bigcol) {
		var move, id;
		for (let subrow = 0; subrow < 3; subrow++) {
			for (let subcol = 0; subcol < 3; subcol++) {
				move = new Move(null, null, bigrow, bigcol, subrow, subcol);
				id = move.id();
				var button = document.getElementById(id);
				button.classList.remove('selected');
			}
		}
	}

	undo() {
		this.board.undo();
	}

	minimax(depth, player, alpha, beta) {
		var moves = Array.from(this.board.possible_moves());

		var score, best_move;

		if (depth == 0 || moves.length == 0) {

		}

		var move;
		var row, col;
		for (let move of moves) {
			[row, col] = move.absolute();
			this.move(row, col);

			var score = this.minimax(depth - 1, -player, alpha, beta).score;

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
		}
	}
}

class Timer {
	constructor(nminutes) {
		var seconds = 60 * nminutes;

		this.xsec = seconds; // in seconds
		this.osec = seconds; // in seconds;

		this.playing = 1; // 1 is x | -1 is o | 0 if not playing
		this.getid();
	}

	time(player) {
		if (player == 1) {
			var minutes = Math.floor(this.xsec / 60);
			var seconds = this.xsec % 60;
		} else if (player == -1) {
			var minutes = Math.floor(this.osec / 60);
			var seconds = this.osec % 60;
		}

		return [minutes, seconds];
	}

	getid() {
		this.id = this.playing == 1 ? 'x-timer' : 'o-timer';
		return this.id;
	}

	swap() {
		this.playing *= -1;
	}

	start() {
		this.timer = setInterval(() => {
			if (this.playing == 1) {
				this.xsec--;
				if (this.xsec == 0) {
					this.stoptimer();
					alert('X has run out of time!');
				}
			} else if (this.playing == -1) {
				this.osec--;
				if (this.osec == 0) {
					this.stoptimer();
					alert('O has run out of time!');
				}
			}
		}, 1000);
	}

	stoptimer() {
		clearInterval(this.timer);
	}
}

var game = new BigBrainTicTacToe();

// var timer = new Timer(3);
// timer.starttimer();
// setInterval(() => {console.log(timer.xsec)}, 200);
