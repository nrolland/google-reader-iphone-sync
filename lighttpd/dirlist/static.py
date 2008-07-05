def header(title, title_link):
	return """
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
	<html xmlns="http://www.w3.org/1999/xhtml">
		<head>

			<meta http-equiv="Content-type" content="text/html; charset=utf-8" />
			<meta id="viewport" name="viewport" content="width=device-width; initial-scale=1.0; maximum-scale=1.0; user-scalable=no;" />
			<meta http-equiv="pragma" content="no-cache" />
			<title>
				""" + title + """
			</title>
			<link rel="stylesheet" href="/.dirlist/iphonedirlist.css" type="text/css" />
			<link rel="apple-touch-icon" href="/.dirlist/favicon.png" />

			<script type="text/javascript" language="javascript">
			function initPage() {
				//updateOrientation();
				setTimeout(scrollTo, 0, 0, 1);
			}

			function updateOrientation() {
				/*
				switch(window.orientation) {
					case 0:
					case 180:
						break;
					case -90:
					case 90:
						window.location.reload();	// to fix a problem that Safari automatically set the font size when the orientation changed (try to go into a folder, then press "Back", then change orientation)
						break;
				}
				*/
			}
		
			function delete_fn(filename, link) {
				var do_confirm = document.getElementById("confirm_delete").checked;
				if(do_confirm && (!confirm("Delete this file?"))){
					return false;
				}
			
				action_fn('delete', filename,
					function(){
						// on success, remove the link node from the page:
						var elem = link.parentNode
						elem.parentNode.removeChild(elem);
					})
			}
		
			function action_fn(action, filename, callback){
				this.xhr = new XMLHttpRequest();
				url = './';
				vars = 'action='+action+'&file='+escape(filename);
				xhr.open('POST', url, true);
				xhr.setRequestHeader('User-Agent','XMLHTTP/1.0');
				xhr.setRequestHeader('Content-type','application/x-www-form-urlencoded');
				xhr.onreadystatechange = function() {
					if (xhr.readyState == 4) {
						resp = xhr.responseText;
						if(!resp.match('^OK')){
							alert("Error: " + resp);
							document.location.href = url+'?action=echo&text='+escape(resp);
						} else {
							if(callback != null){
								callback();
							}
						}
					}
				}
				xhr.send(vars);
			}
			</script>

		</head>

		<body onload="initPage(); " onorientationchange="updateOrientation();">
		
			<div id="list">
				<h1>""" + title_link + """</h1>
				<ul>
					<li>
					<form id="settings_frm" method="GET">
						<input type="checkbox" checked="true" id="confirm_delete" />
						<label for="confirm_delete">Confirm deletes</label>
					<form>
					</li>
"""



footer = """
			</ul>
		</div>

		<div id="info" style="position:absolute; left:0px; top:0px; background-color:red">
		</div>
	</body>
</html>
"""