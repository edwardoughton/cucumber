"""


"""
import os
import pandas as pd
import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']


def find_country_list(continent_list):
    """
    This function produces country information by continent.
    Parameters
    ----------
    continent_list : list
        Contains the name of the desired continent, e.g. ['Africa']
    Returns
    -------
    countries : list of dicts
        Contains all desired country information for countries in
        the stated continent.
    """
    glob_info_path = os.path.join(BASE_PATH, 'global_information_dice.csv')
    countries = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")

    if len(continent_list) > 0:
        data = countries.loc[countries['continent'].isin(continent_list)]
    else:
        data = countries

    output = []

    for index, country in data.iterrows():

        if country['ignore'] == 1:
            continue

        output.append({
            'country_name': country['country'],
            'iso3': country['ISO_3digit'],
            'iso2': country['ISO_2digit'],
            'regional_level': country['lowest'],
            'continent2': country['continent2'],
            'iea_classification': country['iea_classification'],
            'subs_growth_low': float(country['subs_growth_low']),
            'subs_growth_baseline': float(country['subs_growth_baseline']),
            'subs_growth_high': float(country['subs_growth_high']),
            'smartphone_penetration': float(country['smartphone_penetration']),
            'sp_growth_low': float(country['sp_growth_low']),
            'sp_growth_baseline': float(country['sp_growth_baseline']),
            'sp_growth_high': float(country['sp_growth_high']),
            # 'pop_density_km2': float(country['pop_density_km2']),
            # 'settlement_size': float(country['settlement_size']),
            'backhaul_fiber_perc': int(country['backhaul_fiber_perc']),
            'income': country['income'],
        })

    return output
