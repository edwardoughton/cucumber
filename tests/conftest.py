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

# @fixture(scope='function')
# def setup_region():
#     return [{
#     'GID_0': 'MWI',
#     'GID_id': 'MWI.1.1.1_1',
#     'wb_region': 'SSA',
#     'mean_luminosity_km2': 26.736407691655717,
#     'population_total': 10000,
#     'pop_under_10_pop': 0,
#     'area_km2': 2,
#     'population_km2': 5000,
#     'decile': 100,
#     'geotype': 'urban',
#     'demand_mbps_km2': 5000,
#     }]


# @fixture(scope='function')
# def setup_region_rural():
#     return [{
#     'GID_0': 'MWI',
#     'GID_id': 'MWI.1.1.1_1',
#     'wb_region': 'SSA',
#     'mean_luminosity_km2': 26.736407691655717,
#     'population_total': 10000,
#     'pop_under_10_pop': 0,
#     'area_km2': 2,
#     'population_km2': 5000,
#     'decile': 100,
#     'geotype': 'rural',
#     }]


# @fixture(scope='function')
# def setup_option():
#     return { #generation_core_backhaul_sharing_networks_spectrum_tax_integration
#         'scenario': 'S1_50_50_50',
#         'strategy': '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline'

#     }

# @fixture(scope='function')
# def setup_option_high():
#     return {
#         'scenario': 'S1_50_50_50',
#         'strategy': '4G_epc_wireless_baseline_baseline_high_high_high'
#     }


# @fixture(scope='function')
# def setup_global_parameters():
#     return {
#         'traffic_in_the_busy_hour_perc': 15,
#         'opex_percentage_of_capex': 10,
#         'core_perc_of_ran': 10,
#         'overbooking_factor': 100,
#         'return_period': 2,
#         'discount_rate': 5,
#         'confidence': [1, 10, 50],
#     }


# @fixture(scope='function')
# def setup_country_parameters():
#     return {
#         'luminosity': {
#             'high': 5,
#             'medium': 1,
#         },
#         'arpu': {
#             'arpu_high': 15,
#             'arpu_baseline': 5,
#             'arpu_low': 2,
#         },
#         'networks': {
#             'baseline_urban': 3,
#             'baseline_suburban': 3,
#             'baseline_rural': 3,
#             'passive_urban': 3,
#             'passive_suburban': 3,
#             'passive_rural': 3,
#             'active_urban': 1,
#             'active_suburban': 1,
#             'active_rural': 1,
#             'srn_urban': 3,
#             'srn_suburban': 3,
#             'srn_rural': 1,
#         },
#         'frequencies': {
#             '4G': [
#                 {
#                     'frequency': 800,
#                     'bandwidth': '2x10',
#                     'status': 'inactive',
#                 },
#                 {
#                     'frequency': 1800,
#                     'bandwidth': '2x10',
#                     'status': 'inactive',
#                 },
#                 # {
#                 #     'frequency': 2100,
#                 #     'bandwidth': '2x10',
#                 #     'status': 'active',
#                 # },
#             ],
#             '5G': [
#                 {
#                     'frequency': 700,
#                     'bandwidth': '2x10',
#                     'status': 'inactive',
#                 },
#                 {
#                     'frequency': 3500,
#                     'bandwidth': '1x50',
#                     'status': 'inactive',
#                 },
#                 {
#                     'frequency': 26000,
#                     'bandwidth': '2x10',
#                     'status': 'active',
#                 },
#             ]
#         },
#         'financials': {
#             'wacc': 15,
#             'profit_margin': 20,
#             'spectrum_coverage_baseline_usd_mhz_pop': 1,
#             'spectrum_capacity_baseline_usd_mhz_pop': 1,
#             'spectrum_cost_low': 50,
#             'spectrum_cost_high': 50,
#             'tax_low': 10,
#             'tax_baseline': 25,
#             'tax_high': 40,
#             'acquisition_per_subscriber': 10,
#             'administration_percentage_of_network_cost': 10
#             },
#         }


# @fixture(scope='function')
# def setup_timesteps():
#     return [
#         2020,
#         # 2021,
#         # 2022,
#         # 2023,
#         # 2024,
#         # 2025,
#         # 2026,
#         # 2027,
#         # 2028,
#         # 2029,
#         # 2030
#     ]


# @fixture(scope='function')
# def setup_penetration_lut():
#     return {
#         2020: 50,
#         # 2021: 75,
#     }


# @fixture(scope='function')
# def setup_costs():
#     return {
#         #all costs in $USD
#         'equipment': 40000,
#         'site_build': 30000,
#         'installation': 30000,
#         'site_rental_urban': 9600,
#         'site_rental_suburban': 4000,
#         'site_rental_rural': 2000,
#         'operation_and_maintenance': 7400,
#         'power': 2200,
#         'wireless_small': 10000,
#         'wireless_medium': 20000,
#         'wireless_large': 40000,
#         'fiber_urban_m': 10,
#         'fiber_suburban_m': 5,
#         'fiber_rural_m': 2,
#         'core_node': 100000,
#         'core_edge': 20,
#         'regional_node': 100000,
#         'regional_edge': 10,
#         # 'per_site_spectrum_acquisition_cost': 1000,
#         # 'per_site_administration_cost': 100,
#     }




# @fixture(scope='function')
# def setup_ci():
#     return 50

# @fixture(scope='function')
# def setup_core_lut():
#     return {
#         'core_edge': {
#             'MWI.1.1.1_1_new': 1000,
#             'MWI.1.1.1_1_existing': 1000
#         },
#         'core_node': {
#             'MWI.1.1.1_1_new': 2,
#             'MWI.1.1.1_1_existing': 2
#         },
#         'regional_edge': {
#             'MWI.1.1.1_1_new': 1000,
#             'MWI.1.1.1_1_existing': 1000
#         },
#         'regional_node': {
#             'MWI.1.1.1_1_new': 2,
#             'MWI.1.1.1_1_existing': 2
#         },
#     }

# @fixture(scope='function')
# def setup_empty_core_lut():
#     return {
#         'core_edge': {
#             'MWI.1.1.1_1_new': 0,
#             'MWI.1.1.1_1_existing': 0
#         },
#         'core_node': {
#             'MWI.1.1.1_1_new': 0,
#             'MWI.1.1.1_1_existing': 0
#         },
#         'regional_edge': {
#             'MWI.1.1.1_1_new': 0,
#             'MWI.1.1.1_1_existing': 0
#         },
#         'regional_node': {
#             'MWI.1.1.1_1_new': 0,
#             'MWI.1.1.1_1_existing': 0
#         },
#     }

# @fixture(scope='function')
# def setup_infra_sharing_assets():
#     return {
#     'baseline': [],
#     'passive': [
#         'site_build',
#         'installation',
#         'site_rental',
#         'backhaul',
#         'backhaul_fiber_urban_m',
#         'backhaul_fiber_suburban_m',
#         'backhaul_fiber_rural_m',
#         'backhaul_wireless_small',
#         'backhaul_wireless_medium',
#         'backhaul_wireless_large',
#     ],
#     'active': [
#         'equipment',
#         'site_build',
#         'installation',
#         'site_rental',
#         'operation_and_maintenance',
#         'power',
#         'backhaul',
#         'backhaul_fiber_urban_m',
#         'backhaul_fiber_suburban_m',
#         'backhaul_fiber_rural_m',
#         'backhaul_wireless_small',
#         'backhaul_wireless_medium',
#         'backhaul_wireless_large',
#     ],
#     'srn': [
#         'equipment',
#         'site_build',
#         'installation',
#         'site_rental',
#         'operation_and_maintenance',
#         'power',
#         'backhaul',
#         'backhaul_fiber_urban_m',
#         'backhaul_fiber_suburban_m',
#         'backhaul_fiber_rural_m',
#         'backhaul_wireless_small',
#         'backhaul_wireless_medium',
#         'backhaul_wireless_large',
#     ],
# }


# @fixture(scope='function')
# def setup_cost_types():
#     return {
#     'equipment': 'capex',
#     'site_build': 'capex',
#     'installation': 'capex',
#     'site_rental': 'opex',
#     'operation_and_maintenance': 'opex',
#     'power': 'opex',
#     'backhaul': 'capex_and_opex',
#     'backhaul_fiber_urban_m': 'capex_and_opex',
#     'backhaul_fiber_suburban_m': 'capex_and_opex',
#     'backhaul_fiber_rural_m': 'capex_and_opex',
#     'backhaul_wireless_small': 'capex_and_opex',
#     'backhaul_wireless_medium': 'capex_and_opex',
#     'backhaul_wireless_large': 'capex_and_opex',
#     'regional_node': 'capex_and_opex',
#     'regional_edge': 'capex_and_opex',
#     'core_node': 'capex_and_opex',
#     'core_edge': 'capex_and_opex',
# }


# @fixture(scope='function')
# def setup_assets():
#     return [
#         {
#             'GID_id': 'MWI.1.1.1_1', 'asset': 'equipment', 'quantity': 1,
#             'cost_per_unit': 10000, 'total_cost': 10000, 'build_type': 'new'
#         },
#         {
#             'GID_id': 'MWI.1.1.1_1', 'asset': 'site_build', 'quantity': 1,
#             'cost_per_unit': 10000, 'total_cost': 10000, 'build_type': 'new'
#         },
#         {
#             'GID_id': 'MWI.1.1.1_1', 'asset': 'installation', 'quantity': 1,
#             'cost_per_unit': 10000, 'total_cost': 10000, 'build_type': 'upgraded'
#         },
#         {
#             'GID_id': 'MWI.1.1.1_1', 'asset': 'backhaul_wireless_small', 'quantity': 2000,
#             'cost_per_unit': 10, 'total_cost': 20000, 'build_type': 'upgraded'
#         },
#         {
#             'GID_id': 'MWI.1.1.1_1', 'asset': 'installation', 'quantity': 1,
#             'cost_per_unit': 10000, 'total_cost': 10000, 'build_type': 'existing'
#         },
#         {
#             'GID_id': 'MWI.1.1.1_1', 'asset': 'backhaul', 'quantity': 2000,
#             'cost_per_unit': 10, 'total_cost': 20000, 'build_type': 'existing'
#         },
#     ]


# @fixture(scope='function')
# def setup_assets_dict():
#     return {
#         'backhaul_wireless_small': 10000,
#         'core_node': 10000,
#         'site_rental_rural': 10000,
#         'equipment': 10000,
#         'installation': 10000,
#         'site_build': 10000,
#         'core_edge': 10000,
#         'operation_and_maintenance': 10000
#     }


# @fixture(scope='function')
# def setup_tech_lut():
#     return {
#         'oil': {
#             'carbon_per_kWh': 1, #kgs of carbon per kWh
#             'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
#             'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
#             'pm10_per_kWh': 1, #kgs of PM10 per kWh
#         },
#         'gas': {
#             'carbon_per_kWh': 1, #kgs of carbon per kWh
#             'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
#             'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
#             'pm10_per_kWh': 1, #kgs of PM10 per kWh
#         },
#         'coal': {
#             'carbon_per_kWh': 1, #kgs of carbon per kWh
#             'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
#             'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
#             'pm10_per_kWh': 1, #kgs of PM10 per kWh
#         },
#         'nuclear': {
#             'carbon_per_kWh': 1, #kgs of carbon per kWh
#             'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
#             'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
#             'pm10_per_kWh': 1, #kgs of PM10 per kWh
#         },
#         'hydro': {
#             'carbon_per_kWh': 1, #kgs of carbon per kWh
#             'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
#             'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
#             'pm10_per_kWh': 1, #kgs of PM10 per kWh
#         },
#         'diesel': {
#             'carbon_per_kWh': 2, #kgs of carbon per kWh
#             'nitrogen_oxide_per_kWh': 2, #kgs of nitrogen oxide (NOx) per kWh
#             'sulpher_dioxide_per_kWh': 2, #kgs of sulpher dioxide (SO2) per kWh
#             'pm10_per_kWh': 2, #kgs of PM10 per kWh
#         },
#         'renewables': {
#             'carbon_per_kWh': 1, #kgs of carbon per kWh
#             'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
#             'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
#             'pm10_per_kWh': 1, #kgs of PM10 per kWh
#         }
#     }


# @fixture(scope='function')
# def setup_on_grid_mix():
#     return {
#         2020: {
#             'hydro': 100,
#             'oil': 100,
#             'gas': 100,
#             'coal': 100,
#             'renewables': 100,
#         },
#         2021: {
#             'hydro': 100,
#             'oil': 100,
#             'gas': 100,
#             'coal': 100,
#             'renewables': 100,
#         }
#     }


# @fixture(scope='function')
# def setup_data_energy():
#     return [
#         {
#             'year': 2020,
#             'GID_0': 'CHL',
#             'GID_id': 'CHL.1.1.1_1',
#             'wb_region': 'SSA',
#             'geotype': 'rural',
#             'decile': 1,
#             'scenario': 'low_20_20_20',
#             'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline_baseline',
#             'confidence': [50],
#             'total_sites': 131,
#             'total_upgraded_sites': 131,
#             'total_new_sites': 231,
#             'grid_type_perc': 8.142493638676845,
#             'grid_type': 'on_grid',
#             'asset_type': 'new',
#             'mno_energy_annual_demand_kwh': 30,
#             'mno_equipment_annual_demand_kWh': 10,
#             'mno_regional_nodes_annual_demand_kwh': 10,
#             'mno_core_nodes_annual_demand_kwh': 10,
#             'total_energy_annual_demand_kwh': 40,
#             'phones_on_network': 75,
#             'population_with_phones': 100,
#             'phones_on_network_to_total_phones_ratio': 0.75,
#         },
#         {
#             'year': 2020,
#             'GID_0': 'CHL',
#             'GID_id': 'CHL.1.1.1_1',
#             'wb_region': 'SSA',
#             'geotype': 'rural',
#             'decile': 1,
#             'scenario': 'low_20_20_20',
#             'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline_baseline',
#             'confidence': [50],
#             'total_sites': 131,
#             'total_upgraded_sites': 131,
#             'total_new_sites': 231,
#             'grid_type_perc': 91.85750636132316,
#             'grid_type': 'grid_other',
#             'asset_type': 'new',
#             'mno_energy_annual_demand_kwh': 30,
#             'mno_equipment_annual_demand_kWh': 10,
#             'mno_regional_nodes_annual_demand_kwh': 10,
#             'mno_core_nodes_annual_demand_kwh': 10,
#             'total_energy_annual_demand_kwh': 40,
#             'phones_on_network': 75,
#             'population_with_phones': 100,
#             'phones_on_network_to_total_phones_ratio': 0.75,
#         },
#         {
#             'year': 2021,
#             'GID_0': 'CHL',
#             'GID_id': 'CHL.1.1.1_1',
#             'wb_region': 'SSA',
#             'geotype': 'rural',
#             'decile': 1,
#             'scenario': 'low_20_20_20',
#             'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline_baseline',
#             'confidence': [50],
#             'total_sites': 131,
#             'total_upgraded_sites': 131,
#             'total_new_sites': 231,
#             'grid_type_perc': 8.142493638676845,
#             'grid_type': 'on_grid',
#             'asset_type': 'new',
#             'mno_energy_annual_demand_kwh': 30,
#             'mno_equipment_annual_demand_kWh': 10,
#             'mno_regional_nodes_annual_demand_kwh': 10,
#             'mno_core_nodes_annual_demand_kwh': 10,
#             'total_energy_annual_demand_kwh': 40,
#             'phones_on_network': 75,
#             'population_with_phones': 100,
#             'phones_on_network_to_total_phones_ratio': 0.75,
#         },
#         {
#             'year': 2021,
#             'GID_0': 'CHL',
#             'GID_id': 'CHL.1.1.1_1',
#             'wb_region': 'SSA',
#             'geotype': 'rural',
#             'decile': 1,
#             'scenario': 'low_20_20_20',
#             'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline_baseline',
#             'confidence': [50],
#             'total_sites': 131,
#             'total_upgraded_sites': 131,
#             'total_new_sites': 231,
#             'grid_type_perc': 91.85750636132316,
#             'grid_type': 'grid_other',
#             'asset_type': 'new',
#             'mno_energy_annual_demand_kwh': 30,
#             'mno_equipment_annual_demand_kWh': 10,
#             'mno_regional_nodes_annual_demand_kwh': 10,
#             'mno_core_nodes_annual_demand_kwh': 10,
#             'total_energy_annual_demand_kwh': 40,
#             'phones_on_network': 75,
#             'population_with_phones': 100,
#             'phones_on_network_to_total_phones_ratio': 0.75,
#         }
#     ]
