function delete_fn(){
	if(!confirm("Delete this file?")) {
		return false;
	}
	document.location.href='./?action=delete_ref';
	return false;
}

function email(){
	var title_elem = document.getElementById("title").getElementsByTagName('a')[0];
	//var desc = escape(title_elem.firstChild.nodeValue);
	document.location.href="mailto:?subject=A link for you!&body=" + title_elem.getAttribute('href');
	return false;
}