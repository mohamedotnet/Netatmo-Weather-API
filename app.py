from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
import os
import requests
import time
from datetime import datetime
import helper

app = Flask(__name__)

""" API credentials """
client_id = r'6015e1687e631318cd7ef0de'
client_secret = r'bRhk0zW15f2M8HI9dAUoPmpTvQMW'
authorization_base_url = 'https://api.netatmo.com/oauth2/authorize'
token_url = 'https://api.netatmo.com/oauth2/token'
scope = ['read_station', 'read_thermostat']
redirect_uri = 'http://localhost:5000/callback'

# device and module IDs to test 
device_id =  '70:ee:50:3f:13:36'
module_id = '02:00:00:3f:0a:54'

""" 
    Calculate timestamps of today and the day a week before
    date_begin = week_before_timestamp
    date_end = today_timestamp
"""
today = str(datetime.today())[0:10]
today_timestamp = time.mktime(datetime.strptime(today, "%Y-%m-%d").timetuple())
week_before_timestamp = today_timestamp - (24*3600*7)


""" First step in the authentication flow: calling the browser in order to OAuth 2 """
@app.route("/")
def demo():
    # We use the 'read_station' scope in order to get the temperature - for the purpose of this technical challenge
    oauth = OAuth2Session(client_id, scope=scope[0])
    authorization_url, state = oauth.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, as indicated in the dev guide
    session['oauth_state'] = state

    # Redirect the user to the redirect_uri
    return redirect(authorization_url)


""" 
    The callback where two additional parameters are added: code and state 
    The goal is to get the token in order to access the netatmo api
"""
@app.route("/callback", methods=["GET"])
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    oauth = OAuth2Session(client_id, state=state, redirect_uri=redirect_uri)
    token = oauth.fetch_token(token_url, code = code, include_client_id=True, client_secret = client_secret, authorization_response=request.url)
   
    # Store the fetched token in the session ; it will be used later to retrieve public data
    session['oauth_token'] = token

    return redirect(url_for('.weather'))


@app.route("/weather", methods=["GET"])
def weather():
    access_token = session['oauth_token']['access_token']

    # Inject the access token to the request header to get an api access
    headers = {
        'authorization': 'Bearer ' + access_token
    }
    payload = { 'device_id': device_id,
                'module_id': module_id,
                'scale': 'max',
                'date_begin': week_before_timestamp,
                'date_end': today_timestamp,
                'optimize': 'true',
                'type': 'Temperature',
                }

    r = requests.get('https://api.netatmo.net/api/getmeasure', headers=headers, params=payload)

    # Handle request errors
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return "Error: " + r.json()['error']['message']
    
    # Extract data if there is no error
    temperatures = r.json()["body"]
    
    min, max, avg = helper.get_min_max_avg_temperature(temperatures)
    return 'Minimum Temperature: {0} -- Maximum Temperature: {1} -- Average Temperature: {2}\n'.format(min, max, avg)


if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)