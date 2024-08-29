from pytest import fixture


@fixture(scope='function')
def setup_country():
    return {
    'GID_0': 'GBR',
    'income': 'HIC',
    'wb_region': 'SSA',
    'backhaul_fiber_perc': 50,
    'country_name': 'United Kingdom', 
    'iso3': 'GBR', 
    'iso2': 'GB', 
    'regional_level': 2, 
    'income': 'HIC', 
    'wb_region': 'Europe and Central Asia', 
    'iea_classification': 'Europe', 
    'smartphone_penetration': 90, 
    'traffic_in_the_busy_hour_perc': 20, 
    'pop_density_satellite_threshold': 5, 
    'return_period': 10, 
    'discount_rate': 5, 
    'opex_percentage_of_capex': 10, 
    'core_perc_of_ran': 10, 
    'confidence': [50], 
    'tdd_dl_to_ul': '80:20', 
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
    'energy_equipment_kwh': 1, 
    'energy_wireless_small_kwh': 1, 
    'energy_wireless_medium_kwh': 1, 
    'energy_wireless_large_kwh': 1, 
    'energy_fiber_kwh': 1, 
    'energy_core_node_kwh': 0, 
    'energy_regional_node_kwh': 0
    }


@fixture(scope='function')
def setup_deciles():
    return [
    {
        'GID_0': 'GBR', 
        'decile': 1, 
        'population_total': 13164301.8203125, 
        'area_km2': 2315, 
        'population_km2': 5686.5235, 
        'total_existing_sites': 8313, 
        'total_existing_sites_4G': 8313, 
        'backhaul_wireless': 5406.0, 
        'backhaul_fiber': 2654.0, 
        'on_grid_perc': 95.0, 
        'grid_other_perc': 5.0, 
        'geotype': 'urban', 
        'capacity': '40', 
        'generation': '5G', 
        'backhaul': 'wireless', 
        'energy_scenario': 'aps-2030'
    }, 
    {
        'GID_0': 'GBR', 
        'decile': 2, 
        'population_total': 7618144.6875, 
        'area_km2': 2632, 
        'population_km2': 2894.4319, 
        'total_existing_sites': 4812, 
        'total_existing_sites_4G': 4812, 
        'backhaul_wireless': 3010.0, 
        'backhaul_fiber': 1655.0, 
        'on_grid_perc': 95.0, 
        'grid_other_perc': 5.0, 
        'geotype': 'suburban 1', 
        'capacity': '40', 
        'generation': '5G', 
        'backhaul': 'wireless', 
        'energy_scenario': 'aps-2030'
    }
]


@fixture(scope='function')
def setup_capacity_lut():
    return {
        ('macro', '700', '5G', '90'): [
            (0.01, 1),
            (0.02, 2),
            (0.05, 5),
            (0.15, 15),
            (2, 100)
        ],
        ('macro', '800', '4G', '50'): [
            (0.01, 1),
            (0.02, 2),
            (0.05, 5),
            (0.15, 15),
            (2, 100)
        ],
        ('macro', '1800', '4G', '50'): [
            (0.01, 5),
            (0.02, 10),
            (0.05, 20),
            (0.15, 40),
            (2, 1000)
        ],
        ('macro', '2600', '4G', '50'): [
            (0.01, 5),
            (0.02, 10),
            (0.05, 20),
            (0.15, 40),
            (2, 1000)
        ],
        ('macro', '3500', '5G', '90'): [
            (0.01, 5),
            (0.02, 10),
            (0.05, 20),
            (0.15, 40),
            (2, 1000)
        ],
    }


@fixture(scope='function')
def setup_on_grid_mix():
    return {
        'solar pv': 0.16213092134860485, 
        'wind': 0.2807526976617037, 
        'hydro': 0.1505782779307272, 
        'bioenergy': 0.06117067647647605, 
        'nuclear': 0.17396124149480488, 
        'hydrogen and ammonia': 2.5830393332314468e-05, 
        'fossil fuels with ccus': 0.0005704211860886112, 
        'unabated coal': 0.06133857403313609, 
        'unabated natural gas': 0.1045872626025413, 
        'oil': 0.004884096872585128
    }

@fixture(scope='function')
def setup_emissions_lut():
    return {
        'Europe': {
            'aps-2030': {
                'bioenergy': 10, 
                'unabated natural gas': 10, 
                'oil': 10, 
                'unabated coal': 10, 
                'solar pv': 10, 
                'wind': 10, 
                'hydro': 10, 
                'nuclear': 10, 
                'hydrogen and ammonia': 10, 
                'fossil fuels with ccus': 10
                }
            }
        }
