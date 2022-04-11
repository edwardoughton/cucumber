"""
Process IEA data.

Written by Ed Oughton.

April 2022.

"""
import os
import configparser
# import json
# import csv
# import math
import pandas as pd
# import geopandas as gpd
# import rasterio
# from rasterio.mask import mask
# # from rasterstats import zonal_stats
# from shapely.geometry import box
# from random import uniform

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def load_data():
    """
    Load in data.

    """
    path = os.path.join(DATA_RAW, 'iea_data', 'WEO2021_Free_Data_Regions.csv')
    data = pd.read_csv(path)

    return data


def process(data):
    """
    Process data.

    """
    data = data[data.Flow == 'Electricity generation']
    data = data[data.Product != 'Total']
    data = data[data.Scenario == 'Stated Policies Scenario']
    data = data.replace({'Product' : { 'Coal' : 'coal', 'Natural gas' : 'gas',
        'Solar PV' : 'renewables', 'Wind' : 'renewables', 'Nuclear' : 'nuclear',
        'Renewables' : 'renewables'}})
    start_year = 2020
    end_year = 2030
    data = data[data.Year.isin([start_year, end_year])]

    # data = data[data.Region == 'Central and South America']
    regions = data.Region.unique()


    data = data[['Region', 'Product', 'Year', 'Value', 'Unit']]
    products = data.Product.unique()#[:1]

    output = []

    for region in regions:
        for product in products:

            subset = data[(data.Region == region) & (data.Product == product)]
            start = subset.loc[subset.Year == start_year, 'Value'].values[0]
            end = subset.loc[subset.Year == end_year, 'Value'].values[0]
            increment = (end - start) /(end_year - start_year)

            subset = subset.to_dict('records')
            for year in range(start_year, end_year+1):

                if year == 2020:
                    Value = start

                Value = start + ((year - start_year) * increment)

                output.append({
                    'region': region,
                    'type': product,
                    'year': year,
                    'value': round(Value),
                    'unit': 'TWh',
                })

    path = os.path.join(DATA_RAW, 'iea_data', 'iea_forecast.csv')
    output = pd.DataFrame(output)

    output['share'] = round(output['value'] /
        output.groupby(['year', 'region'])['value'].transform('sum') * 100)

    output.to_csv(path, index=False)


    return


if __name__ == '__main__':

    data = load_data()

    process(data)
