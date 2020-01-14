// javaScript for chatting

document.addEventListener('DOMContentLoaded',()=>{
	var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

	socket.on('connect', () => {
		document.querySelector('#send').onclick=() =>{
			const message =document.querySelector('#message').value;
			const room=document.querySelector('#cName').innerHTML;
			const username=document.querySelector('#username').innerHTML;
			document.querySelector('#message').value="";
			socket.emit("show message",{'message':message,'room':room,'username':username});
		};
	});
	socket.on('display message',data =>{
		const p = document.createElement('p');
	    p.innerHTML = `<strong>${data.username}:</strong> ${data.time}<br> ${data.message}`;
	    document.querySelector('#message_block').append(p);
	    const hr = document.createElement('hr');
	    document.querySelector('#message_block').append(hr);
	});
});

document.querySelector("#scroll_description").style.display='none';

function myFunction() {
  var x = document.querySelector("#scroll_description");
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}


