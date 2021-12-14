document.getElementById('play').addEventListener('click', function() {
	var time = document.getElementById('time').value;
	var url = new URL(window.location.href);

	url.pathname = '/play.html';
	url.searchParams.set('time', time);

	// alert(url.toString());
	window.location.href = url.href;
})
