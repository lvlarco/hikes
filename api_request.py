# Credit to Paul's Geek Dad Blog
# url: http://pdwhomeautomation.blogspot.com/2016/01/fitbit-api-access-using-oauth20-and.html

import base64
import urllib2
import urllib
import sys
import json
import os
from pprint import pprint
import requests
from requests import HTTPError
import fitbit
import gather_keys_oauth2 as Oauth2
import datetime


fitbitURL = "https://api.fitbit.com/1/user/-/profile.json"
# Use this URL to refresh the access token
TokenURL = "https://api.fitbit.com/oauth2/token"
# Get and write the tokens from here
IniFile = "./tokens.txt"

clientID = '22D8Y4'
clientSecret = '0891ed91ce01d52e5c89e0da4a83b4e6'

# Some constants defining API error handling responses
TokenRefreshedOK = "Token refreshed OK"
ErrorInAPI = "Error when making API call that I couldn't handle"


# Get the config from the config file.  This is the access and refresh tokens
def GetConfig():
    print "Reading from the config file"
    
    # Open the file
    FileObj = open(IniFile,'r')
    
    # Read first two lines - first is the access token, second is the refresh token
    AccToken = FileObj.readline()
    RefToken = FileObj.readline()
    
    # Close the file
    FileObj.close()
    
    # See if the strings have newline characters on the end.  If so, strip them
    if AccToken.find("\n") > 0:
        AccToken = AccToken[:-1]
    if RefToken.find("\n") > 0:
        RefToken = RefToken[:-1]
    
    # Return values
    return AccToken, RefToken


def WriteConfig(AccToken,RefToken):
    print "Writing new token to the config file"
    print "Writing this: " + AccToken + " and " + RefToken
    
    # Delete the old config file
    os.remove(IniFile)
    
    # Open and write to the file
    FileObj = open(IniFile,'w')
    FileObj.write(AccToken + "\n")
    FileObj.write(RefToken + "\n")
    FileObj.close()


# Make a HTTP POST to get a new
def GetNewAccessToken(RefToken):
    print "Getting a new access token"
    # Form the data payload
    BodyText = {'grant_type': 'refresh_token',
                'refresh_token': RefToken}
    # URL Encode it
    BodyURLEncoded = urllib.urlencode(BodyText)
    print "Using this as the body when getting access token >>" + BodyURLEncoded

    # Start the request
    tokenreq = urllib2.Request(TokenURL,BodyURLEncoded)

    # Add the headers, first we base64 encode the client id and client secret
    # with a : inbetween and create the authorisation header
    tokenreq.add_header('Authorization', 'Basic ' + base64.b64encode(clientID + ":" + clientSecret))
    tokenreq.add_header('Content-Type', 'application/x-www-form-urlencoded')

    # Fire off the request
    try:
        tokenresponse = urllib2.urlopen(tokenreq)

        # See what we got back.  If it's this part of  the code it was OK
        FullResponse = tokenresponse.read()

        # Need to pick out the access token and write it to the config file.  Use a JSON manipluation module
        ResponseJSON = json.loads(FullResponse)

        # Read the access token as a string
        NewAccessToken = str(ResponseJSON['access_token'])
        NewRefreshToken = str(ResponseJSON['refresh_token'])
        # Write the access token to the ini file
        WriteConfig(NewAccessToken,NewRefreshToken)

        print "New access token output >>> " + FullResponse
    except urllib2.URLError as e:
        # Getting to this part of the code means we got an error
        print "An error was raised when getting the access token.  Need to stop here"
        print e.code
        print e.read()
        sys.exit()


# This makes an API call.  It also catches errors and tries to deal with them
def MakeAPICall(InURL,AccToken,RefToken):
    # url = "http://httpbin.org/status/404"
    headerValue = {
        'Authorization': 'Bearer ' + AccToken
    }
    try:
        request = requests.get(InURL, headers=headerValue)
        # activitiesRequest = requests.get(activitiesURL, headers=headerValue)
        request.raise_for_status()
        print("Result code: {0}".format(request.status_code))
        print("Returned data: \n{0}".format(request.content))
        # print "I used this access token " + AccToken
        return True, request
    except HTTPError as err:
        print("Error: {0}".format(err))
        if err.response.status_code == 401:
            GetNewAccessToken(RefToken)
            return False, TokenRefreshedOK
        return False, ErrorInAPI

# Main part of the code
# Declare these global variables that we'll use for the access and refresh tokens
AccessToken = ""
RefreshToken = ""

print "Fitbit API Test Code"

# Get the config
AccessToken, RefreshToken = GetConfig()

# server = Oauth2.OAuth2Server(clientID, clientSecret)
# server.browser_authorize()
#
# ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMkQ4WTQiLCJzdWIiOiI2NUZKUTkiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcmFjdCBybG9jIHJ3ZWkgcmhyIHJwcm8gcm51dCByc2xlIiwiZXhwIjoxNTUzNzM0MjkwLCJpYXQiOjE1NTM3MDU0OTB9.E1HKqFsEYxnfb8cG7g9AbsH2r8BXZUvvNgYcqX1vwR0'
# print('access token: {0}'.format(ACCESS_TOKEN))
# REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
REFRESH_TOKEN = 'd63389ace1179137f39dba31721232f74f370bdab86be352f426080ab5108ff6'
# print('access token: {0}'.format(REFRESH_TOKEN))
auth2_client = fitbit.Fitbit(clientID, clientSecret, oauth2=True,\
                             access_token=AccessToken, refresh_token=RefreshToken)
yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
today = str(datetime.datetime.now().strftime("%Y-%m-%d"))

body = auth2_client.body()
activities = auth2_client.activities()
sleep = auth2_client.sleep()

# headerValue = {
#         'Authorization': 'Bearer ' + AccessToken
#     }
# actURL = 'https://api.fitbit.com/1/user/-/activities/steps/date/2019-03-27/1d/15min'
# actReq = requests.get(actURL, headers=headerValue)
# print(actReq)


resourcePath = "steps" # calories, steps, distance, floors, elevation, heart

intraday = auth2_client.intraday_time_series('activities/{}'.format(resourcePath), base_date=yesterday, detail_level='15min')
pprint(intraday['activities-{}-intraday'.format(resourcePath)], indent=1, width=1)


# MakeAPICall(fitbitURL, AccessToken, RefreshToken)
