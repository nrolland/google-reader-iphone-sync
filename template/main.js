function init(){
	// nothing nuch to do yet...
}

function delete_fn(){
	if(confirm("DELETE this file\n(marking it as read)?")) {
		document.location.href='./?action=delete_ref';
	}
	return false;
}

function email(){
	if(confirm("EMAIL this item?")){
		var title_elem = document.getElementById("title").getElementsByTagName('a')[0];
		document.location.href="mailto:?subject=A link for you!&body=" + title_elem.getAttribute('href');
	}
	return false;
}

function star(){
	if(confirm("Mark item as STARRED\n(and delete it from this device)?")){
		document.location.href='./?action=star_ref';
	}
	return false;
}
