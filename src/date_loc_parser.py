""" This file takes a .json file of strings comprised of addresses and/or locations and outputs
a list of dicts of {address:A, date_iso:B, ranking:C}. """

import json

from tqdm import tqdm
import datefinder
from country_list import countries_for_language
import pandas as pd

import config as args

TZ_FORMAT = 'T00:00:00Z'
EN_COUNTRY_DICT = dict(countries_for_language('en'))
DE_COUNTRY_DICT = dict(countries_for_language('de'))
EN_CITY_PANDAS = pd.read_csv('../data_json/GeoLite2-City-Locations-en.csv')
DE_CITY_PANDAS = pd.read_csv('../data_json/GeoLite2-City-Locations-de.csv')


def string_parser(unparsed_str):
    """ takes an unparsed string and returns a dict of the wanted format """
    date_iso = ''
    address = ''
    address_ranking = 0
    date_ranking = 0

    for datefinder_output in datefinder.find_dates(unparsed_str, index=True):
    # there should only be one couple but the output of datefinder is a generator
    # so using a for is mostly for convenience
        date, date_idx = datefinder_output
        date_iso = str(date.date())
        if date_iso[-2] == '13':
        # datefinder defaults to the 13th when not given a day
            if not '13' in unparsed_str:
                date_iso = date_iso[:-3]
        unparsed_str = unparsed_str[:date_idx[0]] + unparsed_str[date_idx[1]:]


    if unparsed_str:
        address, address_ranking = get_address(unparsed_str)

    date_ranking = get_date_ranking(date_iso)
    ranking = date_ranking + address_ranking

    return {'address':address, 'date_iso':date_iso, 'ranking':ranking}

def clean_string(raw_string):
    """ takes a raw string and gets rid of some troublesome parts """
    if TZ_FORMAT in raw_string:
        raw_string = raw_string.replace(TZ_FORMAT, '')
    raw_string = raw_string.replace(',', ' ')
    raw_string = raw_string.replace('.', ' ')
    return raw_string

def get_date_ranking(date_iso):
    """ computes the ranking of given date_iso """
    info_check = date_iso.count('-')
    date_ranking = 0
    if info_check:
        date_ranking += args.MONTH_SCORE
        if info_check == 2:
            date_ranking += args.DAY_SCORE
    return date_ranking

def get_address(semi_parsed_str):
    """ Gets an address from the reamining unparsed string """
    english = False
    german = False
    cnt_name = ''
    city_name = ''
    address_ranking = 0

    for country_code, country_name in EN_COUNTRY_DICT.items():
        if country_name in semi_parsed_str:
            cnt_code = country_code
            cnt_name = country_name
            semi_parsed_str = semi_parsed_str.replace(country_name, '')
            english = True
            address_ranking += args.COUNTRY_SCORE
    if not english:
        for country_code, country_name in DE_COUNTRY_DICT.items():
            if country_name in semi_parsed_str:
                cnt_code = country_code
                cnt_name = country_name
                semi_parsed_str = semi_parsed_str.replace(country_name, '')
                german = True
                address_ranking += args.COUNTRY_SCORE

    if not cnt_name:
        en_cities = list(EN_CITY_PANDAS['city_name'])
        en_cities = [x for x in en_cities if not isinstance(x, float)]
        for city in en_cities:
            if city in semi_parsed_str:
                city_name = city
                semi_parsed_str = semi_parsed_str.replace(city, '')
                address_ranking += args.CITY_SCORE
        if not city_name:
            de_cities = list(DE_CITY_PANDAS['city_name'])
            de_cities = [x for x in de_cities if not isinstance(x, float)]
            for city in de_cities:
                if city in semi_parsed_str:
                    city_name = city
                    semi_parsed_str = semi_parsed_str.replace(city, '')
                    address_ranking += args.CITY_SCORE

    if english:
        en_cities = list(EN_CITY_PANDAS['city_name'].where(EN_CITY_PANDAS['country_iso_code'] == cnt_code))
        en_cities = [x for x in en_cities if not isinstance(x, float)]
        for city in en_cities:
            if city in semi_parsed_str:
                city_name = city
                semi_parsed_str = semi_parsed_str.replace(city, '')
                address_ranking += args.CITY_SCORE
    if german:
        de_cities = list(DE_CITY_PANDAS['city_name'].where(DE_CITY_PANDAS['country_iso_code'] == cnt_code))
        de_cities = [x for x in de_cities if not isinstance(x, float)]
        for city in de_cities:
            if city in semi_parsed_str:
                city_name = city
                semi_parsed_str = semi_parsed_str.replace(city, '')
                address_ranking += args.CITY_SCORE

    return ', '.join((city_name, cnt_name, semi_parsed_str)), address_ranking


def main(string_list):
    list_dicts = []
    for raw_string in tqdm(string_list):
        unparsed_string = clean_string(raw_string)
        date_loc_dict = string_parser(unparsed_string)
        list_dicts.append(date_loc_dict)
    with open(str(args.OUTPUT_FILE), 'w') as outfile:
        json.dump(list_dicts, outfile)


if __name__ == "__main__":

    if args.OUTPUT_FILE.exists():
        print('A file already exists in ouptut destination, delete it or change its name before continuing')
        raise SystemExit

    with open(str(args.FILE_TO_PARSE), 'r', encoding='latin-1') as file_to_p:
        string_list = json.load(file_to_p)
    main(string_list)
