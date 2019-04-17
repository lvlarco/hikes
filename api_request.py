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
import pandas as pd


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


def GetConfig():
    print "Reading from the config file"
    FileObj = open(IniFile,'r')
    AccToken = FileObj.readline()
    RefToken = FileObj.readline()
    FileObj.close()
    # See if the strings have newline characters on the end.  If so, strip them
    if AccToken.find("\n") > 0:
        AccToken = AccToken[:-1]
    if RefToken.find("\n") > 0:
        RefToken = RefToken[:-1]
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


def intraday_call(activityType, timeStep, date):
    """Makes a call to pull 1-day worth of data for specific activity.

    :param activityType: str. Defines what type of activity. Could be from the following: calories, steps, distance,
    floors, elevation, heart
    :param timeStep: str. Defines time step for activityType
    """
    if activityType == 'heart' and timeStep != '1sec':
        timeStep = '1sec'
        print('Changing time step to 1 second')
    intradayData = auth2_client.intraday_time_series('activities/{}'.format(activityType), base_date=date,
                                                     detail_level=timeStep)
    # pprint('Time series data:\n', intradayData['activities-{}-intraday'.format(activityType)], indent=1, width=1)
    activity_df = intraday_df(intradayData, activityType)
    return activity_df


def intraday_df(data, activity_type):
    """Creates dataframe for intraday calls"""
    time_list = []
    val_list = []
    for i in data['activities-{}-intraday'.format(activity_type)]['dataset']:
        val_list.append(i['value'])
        time_list.append(i['time'])
    activity_df = pd.DataFrame({'Heart Rate': val_list, 'Time': time_list})
    return activity_df


def create_csv(dataframe, activity_type, day):
    """Creates a csv file from a pandas dataframe to the ./files folder as [activity]_[date].csv"""
    filepath = './files/fitbit_data/{0}_{1}.csv'.format(activity_type, day)
    print('Saving CSV as {}'.format(filepath))
    dataframe.to_csv(filepath)


if __name__ == "__main__":
    AccessToken = ""
    RefreshToken = ""
    AccessToken, RefreshToken = GetConfig()

    # server = Oauth2.OAuth2Server(clientID, clientSecret)
    # server.browser_authorize()
    # AccessToken = str(server.fitbit.client.session.token['access_token'])
    # RefreshToken = str(server.fitbit.client.session.token['refresh_token'])

    auth2_client = fitbit.Fitbit(clientID, clientSecret, oauth2=True,
                                 access_token=AccessToken, refresh_token=RefreshToken)
    yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    specific_date = "2018-04-11"

    # parameters to fill
    activity = 'heart'
    step = '15min'
    date = specific_date

    body = auth2_client.body()
    activities = auth2_client.activities()
    sleep = auth2_client.sleep()
    activity_df = intraday_call(activity, step, date)
    create_csv(activity_df, activity, date)
    # print(activity_df)



    # resourcePath = "steps"
    # intraday = auth2_client.intraday_time_series('activities/{}'.format(resourcePath), base_date=yesterday, detail_level='15min')
    # pprint(intraday['activities-{}-intraday'.format(resourcePath)], indent=1, width=1)

    # headerValue = {
    #         'Authorization': 'Bearer ' + AccessToken
    #     }
    # actURL = 'https://api.fitbit.com/1/user/-/activities/steps/date/2019-03-27/1d/15min'
    # actReq = requests.get(actURL, headers=headerValue)
    # print(actReq)

    # MakeAPICall(fitbitURL, AccessToken, RefreshToken)
