#!/usr/bin/env python3
#
import argparse
import yaml, json
# https://requests-oauthlib.readthedocs.io/en/latest/api.html and
# https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

parser = argparse.ArgumentParser ()
parser.add_argument ("--debug", help="Print the returned json content",
                     action="store_true")
parser.add_argument ("--week", help="Display the weekly forecast",
                     action="store_true")
parser.add_argument ("--lat", help="Latitude, if used, overwrite any input from the configuration file",
                     type=float)
parser.add_argument ("--lon", help="Longitude, if used, overwrite any input from the configuration file",
                     type=float)
args = parser.parse_args ()

def parse_current_ttt (forecast):
    ttt =  parse_tt_from_values_list (forecast["current_hour"][0]["values"])
    if ttt is not None:
        return ttt
    return None

def parse_tt_from_values_list (values_list,key_string="ttt"):
    for values in values_list:
        for key,val in values.items ():
            if key == key_string:
                return val
    return None

def parse_7_ttnx (forecast):
    unit_ttn = forecast["units"]["ttn"]["unit"]
    tt = ""
    for item in forecast["7days"]:
        tt +=  "\n" + item["formatted_date"] + ": min " + parse_tt_from_values_list (item["values"],"ttn") + ", max " + parse_tt_from_values_list (item["values"],"ttx") + " " + unit_ttn
    return tt



def main ():
    # Load configuration, including id and secret
    with open ('.srgssr_local_weather_config.yaml') as config_file:
        config = yaml.load (config_file,yaml.SafeLoader)
        client_id = config['credentials']['client_id']
        client_secret = config['credentials']['client_secret']
        lat = config['location']['lat']
        lon = config['location']['lon']
    if args.lat:
        lat = args.lat
    if args.lon:
        lon = args.lon

    client = BackendApplicationClient (client_id=client_id)
    oauth = OAuth2Session (client=client)
    token = oauth.fetch_token (token_url='https://api.srgssr.ch/oauth/v1/accesstoken?grant_type=client_credentials',
                               client_id=client_id, client_secret=client_secret)

    # Need to modify thee token type (I don't know why)
    token['token_type'] = 'Bearer'
    with  OAuth2Session (client_id, token=token) as client:
        # See https://requests.readthedocs.io/en/latest/api/#requests.Session
        #
        if args.week:
            # See https://developer.srgssr.ch/apis/srgssr-weather/docs/weeksforecastbyid
            url = 'https://api.srgssr.ch/forecasts/v1.0/weather/7day?latitude={}&longitude={}'.format (lat,lon)
        else:
            # See https://developer.srgssr.ch/apis/srgssr-weather/docs/currentforecast
            url = 'https://api.srgssr.ch/forecasts/v1.0/weather/current?latitude={}&longitude={}'.format (lat,lon)
        r = client.get (url)

        forecast = json.loads (r.text)
        if args.debug:
            print (json.dumps (forecast, indent=2, sort_keys=True, ensure_ascii=False))
            # print (r.json ()) # print (r.text)

        location = forecast["info"]["name"]["de"]
        if args.week:
            print ("{:s}:{:s}".format (location,parse_7_ttnx (forecast)))
        else:
            # The API returns lists, that's painful to parse
            ttt = parse_current_ttt (forecast)
            unit_ttt = forecast["units"]["ttt"]["unit"]
            print ("{:s}: {:s} {:s}".format (location,ttt,unit_ttt))

if __name__ == "__main__":
    main ()
