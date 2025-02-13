"""
Generate UQ inputs.

"""
import os
import configparser
import pandas as pd
import random
from options import all_options

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')

def generate_uq(global_parameters, options):
    """
    Function to generate uncertainty quantification inputs:

    """
    output = []

    for option in options:

        for i in range(0, 100):

            traffic_in_the_busy_hour_perc = random.randint(
                global_parameters['traffic_in_the_busy_hour_perc_low'], 
                global_parameters['traffic_in_the_busy_hour_perc_high']
            )
            pop_density_satellite_threshold = random.randint(
                global_parameters['pop_density_satellite_threshold_low'], 
                global_parameters['pop_density_satellite_threshold_high']
            )
            cost_equipment = random.randint(
                global_parameters['cost_equipment_low'], 
                global_parameters['cost_equipment_high']
            )
            cost_site_build = random.randint(
                global_parameters['cost_site_build_low'], 
                global_parameters['cost_site_build_high']
            )
            cost_installation = random.randint(
                global_parameters['cost_installation_low'], 
                global_parameters['cost_installation_high']
            )
            cost_operation_and_maintenance = random.randint(
                global_parameters['cost_operation_and_maintenance_low'], 
                global_parameters['cost_operation_and_maintenance_high']
            )
            cost_power = random.randint(
                global_parameters['cost_power_low'], 
                global_parameters['cost_power_high']
            )
            cost_fiber_urban_m = random.randint(
                global_parameters['cost_fiber_urban_m_low'], 
                global_parameters['cost_fiber_urban_m_high']
            )
            cost_fiber_suburban_m = random.randint(
                global_parameters['cost_fiber_suburban_m_low'], 
                global_parameters['cost_fiber_suburban_m_high']
            )
            cost_fiber_rural_m = random.randint(
                global_parameters['cost_fiber_rural_m_low'], 
                global_parameters['cost_fiber_rural_m_high']
            )
            cost_wireless_small = random.randint(
                global_parameters['cost_wireless_small_low'], 
                global_parameters['cost_wireless_small_high']
            )
            cost_wireless_medium = random.randint(
                global_parameters['cost_wireless_medium_low'], 
                global_parameters['cost_wireless_medium_high']
            )
            cost_wireless_large = random.randint(
                global_parameters['cost_wireless_large_low'], 
                global_parameters['cost_wireless_large_high']
            )
            energy_equipment_kwh = random.randint(
                global_parameters['energy_equipment_kwh_low'], 
                global_parameters['energy_equipment_kwh_high']
            )
            energy_wireless_small_kwh = random.randint(
                global_parameters['energy_wireless_small_kwh_low'], 
                global_parameters['energy_wireless_small_kwh_high']
            )
            energy_wireless_medium_kwh = random.randint(
                global_parameters['energy_wireless_medium_kwh_low'], 
                global_parameters['energy_wireless_medium_kwh_high']
            )
            energy_wireless_large_kwh = random.randint(
                global_parameters['energy_wireless_large_kwh_low'], 
                global_parameters['energy_wireless_large_kwh_high']
            )
            energy_fiber_kwh = random.uniform(
                global_parameters['energy_fiber_kwh_low'], 
                global_parameters['energy_fiber_kwh_high']
            )

            output.append({
                'iteration': i,
                'option': option,
                'smartphone_penetration': global_parameters['smartphone_penetration'],
                'traffic_in_the_busy_hour_perc': traffic_in_the_busy_hour_perc,
                'pop_density_satellite_threshold': pop_density_satellite_threshold,
                'return_period': global_parameters['return_period'],
                'discount_rate': global_parameters['discount_rate'],
                'opex_percentage_of_capex': global_parameters['opex_percentage_of_capex'],
                'core_perc_of_ran': global_parameters['core_perc_of_ran'],
                'confidence': global_parameters['confidence'],
                'tdd_dl_to_ul': global_parameters['tdd_dl_to_ul'],
                'cost_equipment': cost_equipment,
                'cost_site_build': cost_site_build,
                'cost_installation': cost_installation,
                'cost_operation_and_maintenance': cost_operation_and_maintenance,
                'cost_power': cost_power,
                'cost_fiber_urban_m': cost_fiber_urban_m,
                'cost_fiber_suburban_m': cost_fiber_suburban_m,
                'cost_fiber_rural_m': cost_fiber_rural_m,
                'cost_wireless_small': cost_wireless_small,
                'cost_wireless_medium': cost_wireless_medium,
                'cost_wireless_large': cost_wireless_large,
                'energy_equipment_kwh': energy_equipment_kwh,
                'energy_wireless_small_kwh': energy_wireless_small_kwh, 
                'energy_wireless_medium_kwh': energy_wireless_medium_kwh,
                'energy_wireless_large_kwh': energy_wireless_large_kwh,
                'energy_fiber_kwh': energy_fiber_kwh,
            })

    output = pd.DataFrame(output)
    path = os.path.join(DATA_INTERMEDIATE, 'uq_inputs.csv')
    output.to_csv(path, index=False)

    return output


if __name__ == '__main__':

    PARAMETERS = {
        'smartphone_penetration': 90,
        'traffic_in_the_busy_hour_perc_low': 15,
        'traffic_in_the_busy_hour_perc_baseline': 20,
        'traffic_in_the_busy_hour_perc_high': 25,
        'pop_density_satellite_threshold_low': 3,
        'pop_density_satellite_threshold_baseline': 5,
        'pop_density_satellite_threshold_high': 8,
        'return_period': 10,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'core_perc_of_ran': 10,
        'confidence': 50,
        'tdd_dl_to_ul': '80:20',
        'cost_equipment_low': 35000,
        'cost_equipment_baseline': 40000,
        'cost_equipment_high': 45000,
        'cost_site_build_low': 25000,
        'cost_site_build_baseline': 30000,
        'cost_site_build_high': 35000,
        'cost_installation_low': 25000,
        'cost_installation_baseline': 30000,
        'cost_installation_high': 35000,
        'cost_operation_and_maintenance_low': 6400,
        'cost_operation_and_maintenance_baseline': 7400,
        'cost_operation_and_maintenance_high': 8400,
        'cost_power_low': 2000,
        'cost_power_baseline': 3000,
        'cost_power_high': 4000,
        'cost_fiber_urban_m_low': 18,
        'cost_fiber_urban_m_baseline': 20,
        'cost_fiber_urban_m_high': 22,
        'cost_fiber_suburban_m_low': 10,
        'cost_fiber_suburban_m_baseline': 12,
        'cost_fiber_suburban_m_high': 22,
        'cost_fiber_rural_m_low': 5,
        'cost_fiber_rural_m_baseline': 7,
        'cost_fiber_rural_m_high': 9,
        'cost_wireless_small_low': 35000,
        'cost_wireless_small_baseline': 40000,
        'cost_wireless_small_high': 45000,
        'cost_wireless_medium_low': 45000,
        'cost_wireless_medium_baseline': 50000,
        'cost_wireless_medium_high': 55000,
        'cost_wireless_large_low': 55000,
        'cost_wireless_large_baseline': 60000,        
        'cost_wireless_large_high': 65000,
        'energy_equipment_kwh_low': 4,
        'energy_equipment_kwh_baseline': 5,
        'energy_equipment_kwh_high': 6,
        'energy_wireless_small_kwh_low': 1, 
        'energy_wireless_small_kwh_baseline': 2, 
        'energy_wireless_small_kwh_high': 3, 
        'energy_wireless_medium_kwh_low': 2,
        'energy_wireless_medium_kwh_baseline': 3,
        'energy_wireless_medium_kwh_high': 4,
        'energy_wireless_large_kwh_low': 3,
        'energy_wireless_large_kwh_baseline': 4,
        'energy_wireless_large_kwh_high': 5,
        'energy_fiber_kwh_low': .04,
        'energy_fiber_kwh_baseline': .06,
        'energy_fiber_kwh_high': .07,
    }

    options = all_options()
    generate_uq(PARAMETERS, options)