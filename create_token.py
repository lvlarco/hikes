# Credit to Paul's Geek Dad Blog
# url: http://pdwhomeautomation.blogspot.com/2016/01/fitbit-api-access-using-oauth20-and.html

import base64
import urllib2
import urllib
import os
import json

# These are the secrets etc from Fitbit developer
OAuthTwoClientID = "22D8Y4"
ClientOrConsumerSecret = "0891ed91ce01d52e5c89e0da4a83b4e6"

# This is the Fitbit URL
TokenURL = "https://api.fitbit.com/oauth2/token"

# I got this from the first verifier part when authorising my application
AuthorisationCode = "b6b38b0a2a1a1a10aacf6a696f7181ef1c9aa9e5"

# Form the data payload
BodyText = {'code': AuthorisationCode,
            'redirect_uri': 'https://lvlarco.github.io/projects.html',
            'client_id': OAuthTwoClientID,
            'grant_type': 'authorization_code'}

BodyURLEncoded = urllib.urlencode(BodyText)
print BodyURLEncoded

# Start the request
req = urllib2.Request(TokenURL,BodyURLEncoded)

# Add the headers, first we base64 encode the client id and client secret with a : inbetween and create
# the authorisation header
req.add_header('Authorization', 'Basic ' + base64.b64encode(OAuthTwoClientID + ":" + ClientOrConsumerSecret))
req.add_header('Content-Type', 'application/x-www-form-urlencoded')

# Fire off the request
try:
    response = urllib2.urlopen(req)

    FullResponse = response.read()
    print "Output >>> " + FullResponse
    token_file = "./tokens.txt"
    if os.path.isfile(token_file):
        os.remove(token_file)
    f = open(token_file, 'w')
    parsed_json = json.loads(FullResponse)
    f.write(parsed_json['access_token']+'\n'+parsed_json['refresh_token'])
#     f.write(parsed_json['refresh_token'])
except urllib2.URLError as e:
    print e.code
    print e.read()
