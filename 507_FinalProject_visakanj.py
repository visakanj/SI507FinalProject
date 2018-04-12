import requests_oauthlib
import requests
import secret_data # file that contains OAuth credentials
import json
import webbrowser
from bs4 import BeautifulSoup
import sqlite3

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

def form_google_params(search_terms):
	# search_terms = [ ]

	# return params dict
	pass

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
	while page_count < -10:
		next_link = (next_link_section)[page_count].get('href')
		next_links.append(next_link)
		page_count += 1

	# Request for each link in next_links

	n = 0
	for link in links:
		google_descriptions_dict[link] = descriptions_list[n]
		n += 1
	
	# DB Table: (1)Link title (2)# of words in title (3)Desc (4)# of words in desc (5)link
	page_url_sections = page_soup.find_all(class_ = 'r')
	for page_urls in page_url_sections:
		url_list.append('https://www.google.com' + page_urls.find('a').get('href'))

	link_words = []
	for link in links:
		link_words.append(len(link.split()))

	desc_words = []
	for desc in descriptions_list:
		desc_words.append(len(desc.split()))

	return (links, link_words, descriptions_list, desc_words, url_list)
	

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
			'SpotifyLink' TEXT NOT NULL
			)
			"""
	cur.executescript(create_tables_statement)
	conn.commit()
	conn.close()
	return None

google_baseurl = 'https://www.google.com/search?'
google_params_dict = {'q':'welcome+happy+help'}

def write_google_table():
	(a,b,c,d,e) = get_google_data(google_baseurl, google_params_dict)

	conn = sqlite3.connect('google_spotify.db')
	cur = conn.cursor()
	i = 0
	while i<9:
		insertion = (None, a[i], b[i], c[i], d[i], e[i])
		insert_statement = """
		INSERT INTO Google
		VALUES (?,?,?,?,?,?)
		"""
		i += 1
		cur.execute(insert_statement, insertion)
	
	conn.commit()
	return None

spotify_baseurl = 'https://api.spotify.com/v1/search?'
spotify_params_dict = {'q':'Happy', 'type':'track', 'limit':10}

def write_spotify_table():
	the_spotify_result = spotify_make_request_and_cache(spotify_baseurl, spotify_params_dict)
	track_names = []
	artists = []
	spotify_ids = []
	popularities = []
	spotify_links = []

	for thing in the_spotify_result['tracks']['items']:
		artists.append(thing['artists'][0]['name'])
		track_names.append(thing['name'])
		spotify_ids.append(thing['id'])
		popularities.append(thing['popularity'])
		spotify_links.append(thing['href'])

	conn = sqlite3.connect('google_spotify.db')
	cur = conn.cursor()
	i = 0
	while i<10:
		insertion = (None, track_names[i], artists[i], spotify_ids[i], popularities[i], spotify_links[i])
		insert_statement = """
		INSERT INTO Spotify
		VALUES (?,?,?,?,?,?)
		"""
		i += 1
		cur.execute(insert_statement, insertion)
	
	conn.commit()

	return None

create_tables()
write_google_table()
write_spotify_table()