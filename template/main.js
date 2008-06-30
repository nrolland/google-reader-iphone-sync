function delete_fn(filename, link, next) {
	if(!confirm("Delete this file?")) {
		return false;
	}

	this.xhr = new XMLHttpRequest();
	url = './';
	vars = 'del='+escape(filename);
	xhr.open('POST', url + '?' + vars, true);
	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			resp = xhr.responseText;
			if(resp != 'OK'){
				alert("Error: " + resp);
			} else {
				// it's all good! :)
				var elem = link.parentNode
				elem.parentNode.removeChild(elem)
			}
		}
	}
	xhr.send('');
	
	if(next != null){
		document.location.href = next;
	}
}