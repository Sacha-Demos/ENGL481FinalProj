import requests
import time
import random
from bs4 import BeautifulSoup
import os

#Some sites don't like us scraping :(
headers = {
	'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36"
}

def grab_lyrics(urls, delay=10, random_wait=5):
	url_count = 0
	for url in urls:
		time.sleep(delay + random.randint(1, random_wait))
		print("Requesting[" + str(url_count) +"]: " + url)
		r = requests.get(url, headers=headers)
		r.encoding = "utf-8"
		filename = ('/').join(url.split('/')[-2:]).replace(".html",".txt")
		os.makedirs(url.split('/')[-2], exist_ok=True)
		f = open(filename, "w")
		f.write(parse_azlyrics(r.text))
		f.close()
		print("Finished saving file")
		url_count += 1


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

def get_azlyrics_album_data(artist_urls, delay=10, random_wait=5):
	album_data = [["Name", "Artist", "ReleaseYear"]]
	song_data = [["Name", "Album", "Filename", "Url"]]
	for artist_url in artist_urls:
		time.sleep(delay + random.randint(1, random_wait))
		r = requests.get(artist_url, headers=headers)
		soup = BeautifulSoup(r.text, "html.parser")
		#artist = (' ').join(soup.find_all('strong')[0].text.split()[:-1])
		artist = soup.find_all('meta', attrs={"name": "keywords"})[0]['content'].split(',')[0]
		elements = soup.find_all('div', attrs={"id": "listAlbum"})[0].findChildren()
		album = "unknown " + artist
		release = "unk"
		for element in elements:
			if(element.name == 'div'):
				if element.has_attr("class"):
					children = element.find_all('b')
					if(len(children) == 0):
						album = "Misc: " + artist
						release = "unk"
					else:
						album = children[0].text.replace('"','').replace(',','.')
						release = element.text.split()[-1].replace("(","").replace(")","")
					album_data.append([album, artist, release])
			elif(element.name == 'a'):
				if element.has_attr("href"):
					url = element["href"].replace("..", "http://www.azlyrics.com")
					filename = ('/').join(url.split('/')[-2:]).replace(".html","")
					song_data.append([element.text.replace(",","."), album, filename, url])
	f = open("album_data.csv", "w")
	f.write(("\n").join([(", ").join(row) for row in album_data]))
	f.close()

	f = open("song_data.csv", "w")
	f.write(("\n").join([(", ").join(row) for row in song_data]))
	f.close()
