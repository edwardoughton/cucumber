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

def generate_tech_options():
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


# OPTIONS = {
#     'technology_options': generate_tech_options(),

# }


COSTS = {
    #all costs in $USD
    'equipment': 40000,
    'site_build': 30000,
    'installation': 30000,
    'operation_and_maintenance': 7400,
    'power': 3000,
    'site_rental_urban': 10000,
    'site_rental_suburban': 5000,
    'site_rental_rural': 3000,
    'fiber_urban_m': 20,
    'fiber_suburban_m': 12,
    'fiber_rural_m': 7,
    'wireless_small': 40000,
    'wireless_medium': 40000,
    'wireless_large': 80000,
}


GLOBAL_PARAMETERS = {
    'traffic_in_the_busy_hour_perc': 20,
    'return_period': 10,
    'discount_rate': 5,
    'opex_percentage_of_capex': 10,
    'core_perc_of_ran': 10,
    'confidence': [50],
    'tdd_dl_to_ul': '80:20',
    }


COST_TYPES = {
    'equipment': 'capex',
    'site_build': 'capex',
    'installation': 'capex',
    'site_rental': 'opex',
    'site_rental_urban': 'opex',
    'site_rental_suburban': 'opex',
    'site_rental_rural': 'opex',
    'operation_and_maintenance': 'opex',
    'backhaul': 'capex_and_opex',
    'backhaul_fiber_urban_m': 'capex_and_opex',
    'backhaul_fiber_suburban_m': 'capex_and_opex',
    'backhaul_fiber_rural_m': 'capex_and_opex',
    'backhaul_wireless_small': 'capex_and_opex',
    'backhaul_wireless_medium': 'capex_and_opex',
    'backhaul_wireless_large': 'capex_and_opex',
    'regional_node': 'capex_and_opex',
    'regional_edge': 'capex_and_opex',
    'core_node': 'capex_and_opex',
    'core_edge': 'capex_and_opex',
}


ENERGY_DEMAND = {
    #all values in kwh per hour
    #roughly 5 kwh per site
    'equipment_kwh': 0.249,
    'wireless_small_kwh': .06, 
    'wireless_medium_kwh': .06,
    'wireless_large_kwh': .06,
    'core_node_kwh': 0,
    'regional_node_kwh': 0,
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

    # random.seed(10)

    # countries = find_country_list([])

    # if not os.path.exists(DATA_INTERMEDIATE):
    #     os.makedirs(DATA_INTERMEDIATE)

    # for country in tqdm(countries):#[::-1]:#[:1]:

    #     output = []

    #     iso3 = country['iso3']

    #     if not iso3 == "GBR":
    #         continue

    #     OUTPUT_COUNTRY = os.path.join(DATA_INTERMEDIATE, iso3)

    #     if not os.path.exists(OUTPUT_COUNTRY):
    #         os.makedirs(OUTPUT_COUNTRY)

    #     for i in range(0, 100):
        
    #         output.append({
    #             'iteration': i,
    #             'constellation': constellation_params['name'], 
    #             'number_of_satellites': constellation_params['number_of_satellites'],
    #             'number_of_ground_stations': (
    #                 constellation_params['number_of_ground_stations']),
    #             'subscribers_low': constellation_params['subscribers'][0],
    #             'subscribers_baseline': constellation_params['subscribers'][1],
    #             'subscribers_high': constellation_params['subscribers'][2],
    #             'altitude_km': altitude_km,
    #             'elevation_angle': elevation_angle,
    #             'dl_frequency_hz': dl_frequency_hz,
    #             'power_dbw': power_dbw,
    #             'receiver_gain_db': receiver_gain,
    #             'earth_atmospheric_losses_db': earth_atmospheric_losses,
    #             'antenna_diameter_m': antenna_diameter_m,
    #             'total_area_earth_km_sq' : (
    #                 constellation_params['total_area_earth_km_sq']),
    #             'ideal_coverage_area_per_sat_sqkm': ideal_coverage_area_per_sat_sqkm,
    #             'percent_coverage' : constellation_params['percent_coverage'],
    #             'speed_of_light': constellation_params['speed_of_light'],
    #             'antenna_efficiency' : constellation_params['antenna_efficiency'],
    #             'all_other_losses_db' : constellation_params['all_other_losses_db'],
    #             'number_of_beams' : constellation_params['number_of_beams'],
    #             'number_of_channels' : constellation_params['number_of_channels'],
    #             'polarization' : constellation_params['polarization'],
    #             'dl_bandwidth_hz' : constellation_params['dl_bandwidth_hz'],
    #             'subscriber_traffic_percent' : (
    #                 constellation_params['subscriber_traffic_percent'])
    #         })

    #     df = pd.DataFrame.from_dict(output)
    #     filename = 'options_{}.csv'.format(iso3)      
    #     path_out = os.path.join(OUTPUT_COUNTRY, filename)
    #     df.to_csv(path_out, index = False)