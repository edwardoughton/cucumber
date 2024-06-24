"""
Generating scenarios and strategies.

"""
import os
import configparser
import pandas as pd
from tqdm import tqdm
import random

from misc import find_country_list

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')


def tech_options():
    """
    Generate technology strategy options.

    sps = Stated Policies Scenario
    aps = Announced Pledges Scenario

    capacity_generation_backhaul_energy_year

    """
    output = []

    capacities = [20, 30, 40]
    generations = ['4G', '5G']
    backhaul_types = ['wireless', 'fiber']
    energy_scenarios = ['sps-2022','sps-2030','aps-2030']

    for capacity in capacities:
        for generation in generations:
                for backhaul in backhaul_types:
                    for energy_scenario in energy_scenarios:
                            option = '{}_{}_{}_{}'.format(
                                capacity,
                                generation,
                                backhaul,
                                energy_scenario,
                            )
                            output.append(option)

    return output


PARAMETERS = {
    'smartphone_penetration': 90,
    'traffic_in_the_busy_hour_perc': 20,
    'pop_density_satellite_threshold': 5,
    'return_period': 10,
    'discount_rate': 5,
    'opex_percentage_of_capex': 10,
    'core_perc_of_ran': 10,
    'confidence': [50],
    'tdd_dl_to_ul': '80:20',
    #all costs in $USD
    'cost_equipment': 40000,
    'cost_site_build': 30000,
    'cost_installation': 30000,
    'cost_operation_and_maintenance': 7400,
    'cost_power': 3000,
    'cost_site_rental_urban': 10000,
    'cost_site_rental_suburban': 5000,
    'cost_site_rental_rural': 3000,
    'cost_fiber_urban_m': 20,
    'cost_fiber_suburban_m': 12,
    'cost_fiber_rural_m': 7,
    'cost_wireless_small': 40000,
    'cost_wireless_medium': 40000,
    'cost_wireless_large': 80000,
    #all values in kwh per hour
    #roughly 5 kwh per site
    'energy_equipment_kwh': 0.249,
    'energy_wireless_small_kwh': .06, 
    'energy_wireless_medium_kwh': .06,
    'energy_wireless_large_kwh': .06,
    'energy_fiber_kwh': .06,
    'energy_core_node_kwh': 0,
    'energy_regional_node_kwh': 0,
    #https://blog.wirelessmoves.com/2019/08/cell-site-power-consumption.html
    #https://www.gsma.com/mobilefordevelopment/wp-content/uploads/2015/01/140617-GSMA-report-draft-vF-KR-v7.pdf
}


EMISSIONS_FACTORS = {
    'oil': {
        'carbon_per_kWh': 0.5, #kgs of carbon per kWh
        # 'nitrogen_oxide_per_kWh':0.00009, #kgs of nitrogen oxide (NOx) per kWh
        # 'sulpher_dioxide_per_kWh': 0.007, #kgs of sulpher dioxide (SO2) per kWh
        # 'pm10_per_kWh': 0.002, #kgs of PM10 per kWh
    },
    'natural gas': {
        'carbon_per_kWh': 0.5, #kgs of carbon per kWh
        # 'nitrogen_oxide_per_kWh':0.00009, #kgs of nitrogen oxide (NOx) per kWh
        # 'sulpher_dioxide_per_kWh': 0.007, #kgs of sulpher dioxide (SO2) per kWh
        # 'pm10_per_kWh': 0.002, #kgs of PM10 per kWh
    },
    'coal': {
        'carbon_per_kWh': 1, #kgs of carbon per kWh
        # 'nitrogen_oxide_per_kWh':0.0001, #kgs of nitrogen oxide (NOx) per kWh
        # 'sulpher_dioxide_per_kWh': 0.01, #kgs of sulpher dioxide (SO2) per kWh
        # 'pm10_per_kWh': 0.01, #kgs of PM10 per kWh
    },
    'nuclear': {
        'carbon_per_kWh': 0.5, #kgs of carbon per kWh
        # 'nitrogen_oxide_per_kWh':0.00009, #kgs of nitrogen oxide (NOx) per kWh
        # 'sulpher_dioxide_per_kWh': 0.007, #kgs of sulpher dioxide (SO2) per kWh
        # 'pm10_per_kWh': 0.002, #kgs of PM10 per kWh
    },
    'hydro': {
        'carbon_per_kWh': 0.01, #kgs of carbon per kWh
        # 'nitrogen_oxide_per_kWh':0.0000009, #kgs of nitrogen oxide (NOx) per kWh
        # 'sulpher_dioxide_per_kWh': 0.00007, #kgs of sulpher dioxide (SO2) per kWh
        # 'pm10_per_kWh': 0.00002, #kgs of PM10 per kWh
    },
    'diesel': {
        'carbon_per_kWh': 0.5, #kgs of carbon per kWh
        # 'nitrogen_oxide_per_kWh':0.00009, #kgs of nitrogen oxide (NOx) per kWh
        # 'sulpher_dioxide_per_kWh': 0.007, #kgs of sulpher dioxide (SO2) per kWh
        # 'pm10_per_kWh': 0.002, #kgs of PM10 per kWh
    },
    'renewables': {
        'carbon_per_kWh': 0.1, #kgs of carbon per kWh
        # 'nitrogen_oxide_per_kWh':0.000001, #kgs of nitrogen oxide (NOx) per kWh
        # 'sulpher_dioxide_per_kWh': 0.0001, #kgs of sulpher dioxide (SO2) per kWh
        # 'pm10_per_kWh': 0.00001, #kgs of PM10 per kWh
    },
    'solar pv': {
        'carbon_per_kWh': 0.1, #kgs of carbon per kWh
        # 'nitrogen_oxide_per_kWh':0.000001, #kgs of nitrogen oxide (NOx) per kWh
        # 'sulpher_dioxide_per_kWh': 0.0001, #kgs of sulpher dioxide (SO2) per kWh
        # 'pm10_per_kWh': 0.00001, #kgs of PM10 per kWh
    },
    'wind': {
        'carbon_per_kWh': 0.1, #kgs of carbon per kWh
        # 'nitrogen_oxide_per_kWh':0.000001, #kgs of nitrogen oxide (NOx) per kWh
        # 'sulpher_dioxide_per_kWh': 0.0001, #kgs of sulpher dioxide (SO2) per kWh
        # 'pm10_per_kWh': 0.00001, #kgs of PM10 per kWh
    }
}

if __name__ == '__main__':

    print(generate_tech_options())
