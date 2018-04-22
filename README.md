# SI507FinalProject

PROJECT: Google Search Playlist
- Transform the user's Google search results into a playlist of songs from Spotify

DATA SOURCES
Google (Crawling multiple pages)

Spotify API (OAuth 2)
- API instructions: https://beta.developer.spotify.com/documentation/web-api/quick-start/

- Secret Keys: https://beta.developer.spotify.com/dashboard/applications
	Obtain Client ID and a Client Secret

- Incorporating with a file called 'secret_data.py'
	Create 'secret_data.py' (empty)

	'CLIENTid' = [your Client ID]
	'CLIENTsecret' = [your Client Secret]
	
	...e.g....
	CLIENTid = "1234567"
	CLIENTsecret = "abcdefgh"

PRESENTATION
Plotly
- create a Plotly account (if necessary)

CODE
- Structure
	(1) Function Definitions --> (2) user inputs, some updates --> (3) Data Presentation

- Important functions & database creation
	create_tables() - creates empty tables (drops if they exist)
	
	write_google_table() - requests Google crawling data and writes into database

	write_spotify_table() - OAuth2 requests Spotify and writes track data into table for each search term


USER GUIDE
- Running this program
	1) Run program in terminal
	2) Enter 3 words (separated by spaces) to be searched in Google
	3) Authorize Spotify when pop-ups appear and copy redirect uri's into terminal
	4) Input 'random' or 'popular' for playlist type
	5) Select presentation option (A-D) or 'quit'

	* You will be prompted at each step and given brief instructions.
	You will also be given options for possible inputs






