"""
Collect results.

Written by Ed Oughton.

December 2022

"""
import os
import configparser
import pandas as pd

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

RESULTS = os.path.join(BASE_PATH, '..', 'results', 'model_results')


def collect_results(filename):
    """
    Collect results.

    """
    print('Working on {}'.format(filename))

    countries = [
        name for name in os.listdir(RESULTS) if os.path.isdir(
                os.path.join(RESULTS, name)
            )
        ]

    output = []

    for iso3 in countries:

        # if not iso3 == 'GBR':
        #     continue

        path_in = os.path.join(RESULTS, iso3)
        items = os.listdir(path_in)

        for item in items:

            if not item == filename:
                continue

            data = pd.read_csv(os.path.join(RESULTS, iso3, filename))
            data = data.to_dict('records')
            output = output + data

    if len(output) == 0:
        return

    output = pd.DataFrame(output)
    folder = os.path.join(RESULTS, '..', 'global_results')
    if not os.path.exists(folder):
        os.mkdir(folder)
    path = os.path.join(folder, filename)
    output.to_csv(path, index=False)

    return


if __name__ == "__main__":

    collect_results('decile_market_cost_results_technology_options.csv')
    collect_results('national_market_cost_results_technology_options.csv')
    # collect_results('national_market_cost_results_business_model_options.csv')
    # collect_results('national_market_cost_results_policy_options.csv')
    # collect_results('emissions_technology_options.csv')
    # collect_results('power_emissions_power_options.csv')
    # collect_results('emissions_national_business_model_power_options.csv')
