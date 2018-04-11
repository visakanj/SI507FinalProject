import requests_oauthlib
import requests
import secret_data # file that contains OAuth credentials
import json
import webbrowser

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

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}={}".format(k, params[k]))
    return baseurl + "&".join(res)

# def call_spotify():
# 	oauth2inst = requests_oauthlib.OAuth2Session(CLIENT_ID, redirect_uri=redirect_URI)
# 	auth_url, state = oauth2inst.authorization_url(authorization_url)

# 	webbrowser.open(auth_url)
# 	auth_response = input('Confirm authentication and enter the full URL').strip()

# 	auth_token = oauth2inst.fetch_token(TOKEN_URL, authorization_response = auth_response, client_secret = CLIENT_SECRET)

# 	r = oauth2inst.get('https://api.spotify.com/v1/search?q=Kanye&type=track&limit=5')
# 	response_dict = json.loads(r.text)
# 	print(json.dumps(response_dict, indent = 2))

def make_request_and_cache(baseurl, params):
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

spotify_baseurl = 'https://api.spotify.com/v1/search?'
params_dict = {'q':'Welcome', 'type':'track', 'limit':5}
make_request_and_cache(spotify_baseurl, params_dict)




