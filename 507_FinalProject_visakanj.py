import requests_oauthlib
import requests
import secret_data # file that contains OAuth credentials
import json
import webbrowser
from bs4 import BeautifulSoup
import sqlite3
import unittest

CLIENT_ID = secret_data.CLIENTid
CLIENT_SECRET = secret_data.CLIENTsecret
# access_token = secret_data.SERVERtoken
# access_secret = secret_data.ACCESS_SECRET

redirect_URI = "https://www.programsinformationpeople.org/runestone/oauth"
authorization_url = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

# CACHE
CACHE_FNAME = "spotify_cache.json"
try:
	cache_file = open(CACHE_FNAME, 'r')
	cache_contents = cache_file.read()
	CACHE_DICTION = json.loads(cache_contents)
	cache_file.close()

except:
	CACHE_DICTION = {}

CACHE_GOOGLE = "google_cache.json"
try:
	google_cache_file = open(CACHE_GOOGLE, 'r')
	google_cache_contents = google_cache_file.read()
	CACHE_DICTION_GOOGLE = json.loads(google_cache_contents)
	google_cache_file.close()

except:
	CACHE_DICTION_GOOGLE = {}

# Take user input(s) >> form params dict >> make unique url >> request Google search >> scrape

def params_unique_combination(baseurl, params):
	alphabetized_keys = sorted(params.keys())
	res = []
	for k in alphabetized_keys:
		res.append("{}={}".format(k, params[k]))
	return baseurl + "&".join(res)

def google_make_request_and_cache(baseurl, params):
	global header
	header = {'User-Agent': 'Google_Project'}

	unique_ident = params_unique_combination(baseurl, params)

	if unique_ident in CACHE_DICTION_GOOGLE:
		print("Getting cached data...")
		return CACHE_DICTION_GOOGLE[unique_ident]

	else:
		print("Making a request for new data...")
		resp = requests.get(unique_ident, headers=header)
		CACHE_DICTION_GOOGLE[unique_ident] = resp.text

		dumped_json_cache = json.dumps(CACHE_DICTION_GOOGLE)
		fw = open(CACHE_GOOGLE,"w")
		fw.write(dumped_json_cache)
		fw.close()
		return CACHE_DICTION_GOOGLE[unique_ident]

def get_more_google_data_cache(url):
	global header
	header = {'User-Agent': 'Google_Project'}
	unique_ident = url

	if unique_ident in CACHE_DICTION_GOOGLE:
		print("Getting cached data...")
		return CACHE_DICTION_GOOGLE[unique_ident]

	else:
		print("Making a request for new data...")
		resp = requests.get(unique_ident, headers=header)
		CACHE_DICTION_GOOGLE[unique_ident] = resp.text

		dumped_json_cache = json.dumps(CACHE_DICTION_GOOGLE)
		fw = open(CACHE_GOOGLE,"w")
		fw.write(dumped_json_cache)
		fw.close()
		return CACHE_DICTION_GOOGLE[unique_ident]

def get_more_google_data(url):
	google_page = get_more_google_data_cache(url)
	links = []
	descriptions_list = []
	url_list = []

	page_soup = BeautifulSoup(google_page, 'html.parser')
	content = page_soup.find_all(class_='r')
	
	for link in content:
		link_title = link.text
		if "Images" not in link_title:
			links.append(link_title)

	descriptions = page_soup.find_all(class_ = 'st')

	for description in descriptions:
		descriptions_list.append(description.text)

	page_url_sections = page_soup.find_all(class_ = 'r')
	for page_urls in page_url_sections:
		url_list.append('https://www.google.com' + page_urls.find('a').get('href'))

	return (links, descriptions_list, url_list)

def get_google_data(baseurl, params):
	google_descriptions_dict = {}
	page_count = -19
	links = []
	next_links = []
	descriptions_list = []
	url_list = []
	# make this a function
	google_page = google_make_request_and_cache(baseurl, params)

	page_soup = BeautifulSoup(google_page, 'html.parser')
	content = page_soup.find_all(class_='r')
	
	for link in content:
		link_title = link.text
		if "Images" not in link_title:
			links.append(link_title)

	descriptions = page_soup.find_all(class_ = 'st')

	for description in descriptions:
		descriptions_list.append(description.text)
	# make function through here

	next_link_section = page_soup.find_all('a')
	while page_count < -9:
		next_link = (next_link_section)[page_count].get('href')
		next_links.append(next_link)
		page_count += 1

	page_url_sections = page_soup.find_all(class_ = 'r')
	for page_urls in page_url_sections:
		url_list.append('https://www.google.com' + page_urls.find('a').get('href'))

	# Request for each link in next_links
	for link in next_links:
		(more_titles, more_descriptions, more_urls) = get_more_google_data('http://www.google.com' + link)

		for title in more_titles:
			links.append(title)
		for descr in more_descriptions:
			descriptions_list.append(descr)
		for url in more_urls:
			url_list.append(url)
	
	# DB Table: (1)Link title (2)# of words in title (3)Desc (4)# of words in desc (5)link
	link_words = []
	for link in links:
		link_words.append(len(link.split()))

	desc_words = []
	for desc in descriptions_list:
		desc_words.append(len(desc.split()))

	return (links, link_words, descriptions_list, desc_words, url_list, next_links)
	

def spotify_make_request_and_cache(baseurl, params):
	unique_ident = params_unique_combination(baseurl, params)

	if unique_ident in CACHE_DICTION:
		print("Getting cached data...")
		return CACHE_DICTION[unique_ident]

	else:
		print("Making a request for new data...")
		oauth2inst = requests_oauthlib.OAuth2Session(CLIENT_ID, redirect_uri=redirect_URI)
		auth_url, state = oauth2inst.authorization_url(authorization_url)

		webbrowser.open(auth_url)
		auth_response = input('Confirm authentication and enter the full URL').strip()

		auth_token = oauth2inst.fetch_token(TOKEN_URL, authorization_response = auth_response, client_secret = CLIENT_SECRET)

		r = oauth2inst.get(unique_ident)

		CACHE_DICTION[unique_ident] = json.loads(r.text)
		with open(CACHE_FNAME, "w") as outfile:
			json.dump(CACHE_DICTION, outfile, indent = 4)

		spotify_results = json.loads(r.text)
		JSON_FILE = "spotify_results.json"
		with open(JSON_FILE, "w") as outfile1:
			json.dump(spotify_results, outfile1, indent=4)
		
		return CACHE_DICTION[unique_ident]

def create_tables():
	conn = sqlite3.connect('google_spotify.db')
	cur = conn.cursor()
	statement = '''
			DROP TABLE IF EXISTS 'Google';
		'''
	cur.execute(statement)

	statement = '''
			DROP TABLE IF EXISTS 'Spotify';
		'''
	cur.execute(statement)
	
	statement = '''
			DROP TABLE IF EXISTS 'SpotifyArtists'
		'''
	cur.execute(statement)
	conn.commit()
	# DB Table: (1)Link title (2)# of words in title (3)Desc (4)# of words in desc (5)link
	create_tables_statement = """
			CREATE TABLE 'Google' (
			'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
			'LinkTitle' Text NOT NULL,
			'TitleCount' INTEGER NOT NULL,
			'Description' TEXT NOT NULL,
			'DescriptionCount' INTEGER NOT NULL,
			'URL' TEXT NOT NULL
			);
			CREATE TABLE 'Spotify' (
			'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
			'TrackName' TEXT NOT NULL,
			'Artist' INTEGER NOT NULL,
			'SpotifyId' TEXT NOT NULL,
			'Popularity' INTEGER NOT NULL,
			'Explicit' TEXT NOT NULL,
			'SpotifyLink' TEXT NOT NULL
			);
			CREATE TABLE 'SpotifyArtists' (
			'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
			'ArtistName' TEXT NOT NULL
			)
			"""
	cur.executescript(create_tables_statement)
	conn.commit()
	conn.close()
	return None

user_inputs = input("What to search in Google? (2 terms) ").split()
google_params_dict = {'q':''}
google_search_string = ''
s = '+'
google_search_string = s.join(user_inputs)
google_params_dict['q'] = str(google_search_string)

google_baseurl = 'https://www.google.com/search?'

def write_google_table():
	(a,b,c,d,e,f) = get_google_data(google_baseurl, google_params_dict)

	conn = sqlite3.connect('google_spotify.db')
	cur = conn.cursor()
	i = 0
	while i<100:
		insertion = (None, 
			a[i], 
			b[i], 
			c[i], 
			d[i], 
			e[i])
		insert_statement = """
		INSERT INTO Google
		VALUES (?,?,?,?,?,?)
		"""
		i += 1
		cur.execute(insert_statement, insertion)
	
	conn.commit()
	conn.close()
	return None

def write_spotify_table():
	the_spotify_result = spotify_make_request_and_cache(spotify_baseurl, spotify_params_dict)
	track_names = []
	artists = []
	spotify_ids = []
	popularities = []
	explicits = []
	spotify_links = []

	for thing in the_spotify_result['tracks']['items']:
		artists.append(thing['artists'][0]['name'])
		track_names.append(thing['name'])
		spotify_ids.append(thing['id'])
		popularities.append(thing['popularity'])
		explicits.append(thing['explicit'])
		spotify_links.append(thing['href'])

	conn = sqlite3.connect('google_spotify.db')
	cur = conn.cursor()
	i = 0
	try:
		while i<25:
			insertion = (None, track_names[i], artists[i], spotify_ids[i], popularities[i], explicits[i], spotify_links[i])
			insert_statement = """
			INSERT INTO Spotify
			VALUES (?,?,?,?,?,?,?)
			"""
			i += 1
			cur.execute(insert_statement, insertion)
		conn.commit()
		conn.close()
	except:
		pass

	return None

def google_words():
	(a,b,c,d,e,f) = get_google_data(google_baseurl, google_params_dict)
	word_dict = {}

	for descr in c:
		descr = descr.split()
		for word in descr:
			if word not in word_dict:
				word_dict[word] = 1
			elif word in word_dict:
				word_dict[word] += 1

	sorted_keys = sorted(word_dict, key=word_dict.get)
	index = -1
	search_words = []
	pointless_words = ['the', 'to', 'and', 'of', 'is', 'for', '-', 'a']
	while index > -20:
		word = sorted_keys[index]
		if word[0] != '.' and word not in pointless_words:
			search_words.append(word)
		index -= 1

	return search_words[:10]

######################################
# END OF FUNCTION DEFINITIONS
######################################

# create_tables()
# write_google_table()

# spotify_baseurl = 'https://api.spotify.com/v1/search?'
# spotify_params_dict = {'q':'', 'type':'track', 'limit':25}

# spotify_search_terms = google_words()[:5]

# for term in spotify_search_terms:
# 	spotify_params_dict['q'] = str(term)
# 	write_spotify_table()

# # Write SQL Statement for primary-foreign key relationship
# conn = sqlite3.connect('google_spotify.db')
# cur = conn.cursor()
# statement = '''
# 	SELECT Artist
# 	FROM Spotify
# 	GROUP BY Artist
# 	'''
# cur.execute(statement)
# key_artists = []
# for thing in cur.fetchall():
# 	key_artists.append(thing[0])

# i = 0
# while i < len(key_artists): 
# 	artists_insertion = (None, key_artists[i])
# 	insert_artists_statement = '''
# 		INSERT INTO SpotifyArtists
# 		VALUES (?,?)
# 		'''
# 	cur.execute(insert_artists_statement, artists_insertion)
# 	i += 1
# 	conn.commit()

# e = 1
# while e < len(key_artists):
# 	update_statement = '''
# 	UPDATE Spotify
# 	SET Artist = '''
# 	update_statement += str(e)
# 	update_statement += '''
# 	WHERE Artist = '''
# 	update_statement += "'" + key_artists[e-1] + "'"
# 	e += 1
# 	cur.execute(update_statement)
# 	conn.commit()
# conn.close()

# User preference statement: random / popular
user_preference = input("What songs do you want in your playlist? random or popular? ")

# Create & Return Playlist
random_playlist_statement = '''
	SELECT TrackName, SpotifyArtists.ArtistName
	FROM Spotify
	JOIN SpotifyArtists ON SpotifyArtists.Id = Spotify.Artist
	ORDER BY RANDOM()
	LIMIT 10
'''

popular_playlist_statement = '''
	SELECT TrackName, Artist
	FROM Spotify
	JOIN SpotifyArtists ON SpotifyArtists.Id = Spotify.Artist
	ORDER BY Popularity DESC
	LIMIT 10
'''

song_list = []
conn = sqlite3.connect('google_spotify.db')
cur = conn.cursor()
if user_preference == 'random':
	cur.execute(random_playlist_statement)
	song_list = cur.fetchall()
elif user_preference == 'popular':
	cur.execute(popular_playlist_statement)
	song_list = cur.fetchall()

x = 1
for song in song_list:
	print('')




######################################
# UNIT TESTING
######################################