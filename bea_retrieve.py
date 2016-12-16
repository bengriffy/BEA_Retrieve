################################################################################################################
#Author: Ben Griffy
#Institution: University of California, Santa Barbara
#email: griffy@umail.ucsb.edu
#website: https://sites.google.com/site/bengriffy/home
#Date:
################################################################################################################

from __future__ import division

import numpy as np
import pandas as pd
import time
import urllib2
from bs4 import BeautifulSoup
import os
import addfips
import time
import us
import json

def get_bea_series(api_key, series, options, output, year = None):

    opts = ''

    for key in options.keys():
        opts = opts + key + '=' + options[key] + '&'

    for key in series.keys():
        opts = key + '=' + series[key] + '&' + opts

    url_get = 'http://www.bea.gov/api/data?&UserID=' + api_key + '&method=GetData&' + opts + 'ResultFormat=JSON&'
    data_series = urllib2.urlopen(url_get)
    data_series = json.loads(unicode(data_series.read(), "ISO-8859-1"))
    data = data_series.get('BEAAPI').get('Results')

    headers = []
    for header in data.get('Dimensions'):
        headers.append(header['Name'])
        print header

    file = open(output, 'w')
    for header in headers:
        file.write(header + ",")
    file.write("\n")

    for result in data.get('Data'):
        for header in headers:
            item = result.get(header)
            file.write(item + ",")
        file.write("\n")

    file.close()
    print "done!"
    

def interactive_bea_series(api_key, output_file):

    url_get = 'http://www.bea.gov/api/data?&UserID=' + api_key + '&method=GETDATASETLIST&ResultFormat=JSON&'

    available_series = urllib2.urlopen(url_get)

    available_series = json.loads(available_series.read())

    all_series_dict = {}

    i = 1

    for name in available_series.get('BEAAPI').get('Results').get('Dataset'):
        all_series_dict[name['DatasetDescription']] = name['DatasetName']
        all_series_dict[str(i)] = name['DatasetName']
        print str(i) + ": " + name['DatasetDescription']
        i = i + 1

    series_name = raw_input("What series do you want? Please match the exact format listed: ")

    url_get = 'http://www.bea.gov/api/data?&UserID=' + api_key + '&method=getparameterlist&datasetname=' + all_series_dict[series_name] + '&ResultFormat=JSON&'

    available_subseries = urllib2.urlopen(url_get)

    available_subseries = json.loads(available_subseries.read())

    all_subseries_dict = {}
    options_dict = {}

    i = 1

    for name in available_subseries.get('BEAAPI').get('Results').get('Parameter'):
        all_subseries_dict[name['ParameterDescription']] = name['ParameterName']
        all_subseries_dict[str(i)] = name['ParameterName']
        try:
            print str(i) + ': ' + name['ParameterDescription'] + '. The default value is: ' + name['ParameterDefaultValue']
        except:
            print str(i) + ': ' + name['ParameterDescription']
        subseries_value = raw_input("Enter the value for the item that you want to download. Enter \"unknown\" (without quotes) if you aren't sure what the value is. ")
        options_dict[name['ParameterName']] = subseries_value
        i = i + 1 

    series_options = {}

    for option in options_dict.keys():
        if options_dict[option] == "unknown":
            url_get = 'http://www.bea.gov/api/data?&UserID=' + api_key + '&method=GetParameterValues&DatasetName=' + all_series_dict[series_name] + '&ParameterName=' + option + '&ResultFormat=JSON&'
            available_options = urllib2.urlopen(url_get)
            available_options = json.loads(available_options.read())
            try:
                for opt in available_options.get('BEAAPI').get('Results').get('ParamValue'):
                    try:
                        series_options[opt['Description']] = opt[option]
                        print opt['Description']
                    except:
                        series_options[opt['Desc']] = opt[option]
                        print opt['Desc']
                desired_series = raw_input("Was one of these series the one that you wanted? Enter \"N\" if not, otherwise enter the full printed name of the series: ")
                options_dict[option] = series_options[desired_series]
            except:
                print "option " + option + " didn't work"
                pass
    series_dict = {'DatasetName':all_series_dict[series_name]}

    get_bea_series(api_key, series = series_dict, options = options_dict, output = output_file)
