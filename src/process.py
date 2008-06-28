from lib.BeautifulSoup import BeautifulSoup

## processing modules:
def insert_alt_text(item):
	"""
	insert bolded image title text after any image on the page
	"""
	soup = item['soup']
	images = soup.findAll('img',{'title':True})
	for img in images:
		desc = BeautifulSoup('<p><b>( %s )</b></p>' % img['title'])
		img.append(desc)
	return item
