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


def all_options():
    """
    Generate all strategy options.

    sps = Stated Policies Scenario
    aps = Announced Pledges Scenario

    capacity_generation_backhaul_energy_sharing

    """
    output = []

    capacities = [20, 30, 40] 
    generations = ['4G', '5G']
    backhaul_types = ['wireless', 'fiber']
    energy_scenarios = ['aps-2030']#['sps-2022', 'sps-2030','aps-2030']
    sharing_scenarios = ['baseline','passive','active','srn']

    for capacity in capacities:
        for generation in generations:
                for backhaul in backhaul_types:
                    for energy_scenario in energy_scenarios:
                        for sharing_scenario in sharing_scenarios:
                            option = '{}_{}_{}_{}_{}'.format(
                                capacity,
                                generation,
                                backhaul,
                                energy_scenario,
                                sharing_scenario
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
    'energy_equipment_kwh': 5, #0.249,
    'energy_wireless_small_kwh': 2, 
    'energy_wireless_medium_kwh': 3,
    'energy_wireless_large_kwh': 4,
    'energy_fiber_kwh': .06,
    # 'energy_core_node_kwh': 0,
    # 'energy_regional_node_kwh': 0,
    #https://blog.wirelessmoves.com/2019/08/cell-site-power-consumption.html
    #https://www.gsma.com/mobilefordevelopment/wp-content/uploads/2015/01/140617-GSMA-report-draft-vF-KR-v7.pdf
    #https://medium.com/@zodhyatech/how-much-energy-does-a-cell-tower-consume-7efc2c8cdfbf 
}


if __name__ == '__main__':

    print(all_options())

