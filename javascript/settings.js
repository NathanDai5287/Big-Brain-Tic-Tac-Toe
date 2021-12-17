document.getElementById('play').addEventListener('click', function() {
	var time = document.getElementById('time').value;
	var url = new URL(window.location.href);

	url.pathname = url.pathname.replace(/\/[^\/]*$/, '/play.html');
	url.searchParams.set('time', time);

	// alert(url.toString());
	window.location.href = url.href;
})

document.getElementById('time').addEventListener('keyup', function(event) {
	event.preventDefault();

	if (event.key == 'Enter') {
		document.getElementById('play').click();
	}
})
