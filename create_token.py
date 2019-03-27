# Credit to Paul's Geek Dad Blog
# url: http://pdwhomeautomation.blogspot.com/2016/01/fitbit-api-access-using-oauth20-and.html

import base64
import urllib2
import urllib
import os
import json

# These are the secrets etc from Fitbit developer
OAuthTwoClientID = "22D8Y4"
ClientOrConsumerSecret = "c577dc3f1bfddfeb28da655892cf5c70"

# This is the Fitbit URL
TokenURL = "https://api.fitbit.com/oauth2/token"

# I got this from the first verifier part when authorising my application
AuthorisationCode = "8d703f8f8025210d39dfa720af71d1d233df8aba"

# Form the data payload
BodyText = {'code': AuthorisationCode,
            'redirect_uri': 'https://lvlarco.github.io/projects/hikes/hikes',
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
