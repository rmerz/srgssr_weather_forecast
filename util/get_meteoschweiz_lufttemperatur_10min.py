#!/usr/bin/env python3
#
# Prototype jsonpath implementation for querying the opendata
# meteoschweiz data-set
#
# For jsonpath, see https://goessner.net/articles/JsonPath/
# For jsonpath python implementation, see https://github.com/h2non/jsonpath-ng
# Regarding filter support, see https://github.com/h2non/jsonpath-ng/issues/8
#
import argparse
import requests, json
#from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse


parser = argparse.ArgumentParser ()
parser.add_argument ("--debug", help="Activate debug mode",
                     action="store_true")
parser.add_argument ("--station", help="Station name to query",
                     default='BER',
                     type=str)
args = parser.parse_args ()

def main ():
    if args.debug:
        print ('Query station {:s}'.format (args.station))

    # Note that .csv is also available
    _url = 'http://data.geo.admin.ch/ch.meteoschweiz.messwerte-lufttemperatur-10min/ch.meteoschweiz.messwerte-lufttemperatur-10min_en.json'
    _r = requests.get (_url)
    if args.debug:
        print (json.dumps (_r.json (), indent=2, sort_keys=True, ensure_ascii=False))

    _jsonpath_expr_str = '$.features[?(@.id=="{:s}")].properties.station_name'.format (args.station)
    for match in parse (_jsonpath_expr_str).find(_r.json ()):
        print (match.value)
    _jsonpath_expr_str = '$.features[?(@.id=="{:s}")].properties.value'.format (args.station)
    for match in parse (_jsonpath_expr_str).find(_r.json ()):
        print (match.value)

if __name__ == '__main__':
    main ()
