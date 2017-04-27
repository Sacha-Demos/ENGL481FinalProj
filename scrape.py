import requests
import time
import random
from bs4 import BeautifulSoup

#Some sites don't like us scraping :(
headers = {
	'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36"
}

def grab_lyrics(urls, delay=10, random_wait=5):
	for url in urls:
		time.sleep(delay + random.randint(1, random_wait))
		print("Requesting: " + url)
		r = requests.get(url, headers=headers)
		r.encoding = "utf-8"
		f = open(url.split('/')[-1], "a")
		f.write(parse_azlyrics(r.text))
		f.close()
		print("Finished saving file")


def parse_genius(page_text):
	soup = BeautifulSoup(page_text, "html.parser")
	return soup.find_all('lyrics')[0].get_text()

def parse_azlyrics(page_text):
	soup = BeautifulSoup(page_text, "html.parser")
	'''
	g = soup.find_all('div',attrs={"class": "ringtone"})[0].parent.children
	for i in range(12):
		g.__next__()
	'''
	#Should be the 21st div, I've tried it on a few pages
	return '\n'.join(soup.find_all('div')[21].get_text().split('\n')[2:])

def parse_ohhla(page_text):
	soup = BeautifulSoup(page_text, "html.parser")
	return '\n'.join(soup.find_all('pre')[0].get_text().split('\n')[6:])

def get_azlyrics_song_urls(artist_url):
	r = requests.get(artist_url, headers=headers)
	soup = BeautifulSoup(r.text, "html.parser")
	anchors = soup.find_all('div',attrs={"id": "listAlbum"})[0].find_all('a')
	links = []
	for a in anchors:
		if a.has_attr('href'):
			links.append(a['href'])
	links = [link.replace("..", "http://www.azlyrics.com") for link in links]
	return links
