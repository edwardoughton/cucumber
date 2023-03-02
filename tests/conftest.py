from pytest import fixture


@fixture(scope='function')
def setup_country():
    return {
    'GID_0': 'MWI',
    'income': 'HIC',
    'backhaul_fiber_perc': 50,
    }


@fixture(scope='function')
def setup_region():
    return [{
    'GID_0': 'MWI',
    'GID_id': 'MWI.1.1.1_1',
    'mean_luminosity_km2': 26.736407691655717,
    'population_total': 10000,
    'pop_under_10_pop': 0,
    'area_km2': 2,
    'population_km2': 5000,
    'decile': 100,
    'geotype': 'urban',
    'demand_mbps_km2': 5000,
    }]


@fixture(scope='function')
def setup_region_rural():
    return [{
    'GID_0': 'MWI',
    'GID_id': 'MWI.1.1.1_1',
    'mean_luminosity_km2': 26.736407691655717,
    'population_total': 10000,
    'pop_under_10_pop': 0,
    'area_km2': 2,
    'population_km2': 5000,
    'decile': 100,
    'geotype': 'rural',
    }]


@fixture(scope='function')
def setup_option():
    return { #generation_core_backhaul_sharing_networks_spectrum_tax_integration
        'scenario': 'S1_50_50_50',
        'strategy': '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline'

    }

@fixture(scope='function')
def setup_option_high():
    return {
        'scenario': 'S1_50_50_50',
        'strategy': '4G_epc_wireless_baseline_baseline_high_high_high'
    }


@fixture(scope='function')
def setup_global_parameters():
    return {
        'traffic_in_the_busy_hour_perc': 15,
        'opex_percentage_of_capex': 10,
        'overbooking_factor': 100,
        'return_period': 2,
        'discount_rate': 5,
        'confidence': [1, 10, 50],
    }


@fixture(scope='function')
def setup_country_parameters():
    return {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'arpu_high': 15,
            'arpu_baseline': 5,
            'arpu_low': 2,
        },
        'networks': {
            'baseline_urban': 3,
            'baseline_suburban': 3,
            'baseline_rural': 3,
            'passive_urban': 3,
            'passive_suburban': 3,
            'passive_rural': 3,
            'active_urban': 1,
            'active_suburban': 1,
            'active_rural': 1,
            'srn_urban': 3,
            'srn_suburban': 3,
            'srn_rural': 1,
        },
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                    'status': 'inactive',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x10',
                    'status': 'inactive',
                },
                # {
                #     'frequency': 2100,
                #     'bandwidth': '2x10',
                #     'status': 'active',
                # },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                    'status': 'inactive',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                    'status': 'inactive',
                },
                {
                    'frequency': 26000,
                    'bandwidth': '2x10',
                    'status': 'active',
                },
            ]
        },
        'financials': {
            'wacc': 15,
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 1,
            'spectrum_capacity_baseline_usd_mhz_pop': 1,
            'spectrum_cost_low': 50,
            'spectrum_cost_high': 50,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            'acquisition_per_subscriber': 10,
            'administration_percentage_of_network_cost': 10
            },
        }


@fixture(scope='function')
def setup_timesteps():
    return [
        2020,
        # 2021,
        # 2022,
        # 2023,
        # 2024,
        # 2025,
        # 2026,
        # 2027,
        # 2028,
        # 2029,
        # 2030
    ]


@fixture(scope='function')
def setup_penetration_lut():
    return {
        2020: 50,
        # 2021: 75,
    }


@fixture(scope='function')
def setup_costs():
    return {
        #all costs in $USD
        'equipment': 40000,
        'site_build': 30000,
        'installation': 30000,
        'site_rental_urban': 9600,
        'site_rental_suburban': 4000,
        'site_rental_rural': 2000,
        'operation_and_maintenance': 7400,
        'power': 2200,
        'wireless_small': 10000,
        'wireless_medium': 20000,
        'wireless_large': 40000,
        'fiber_urban_m': 10,
        'fiber_suburban_m': 5,
        'fiber_rural_m': 2,
        'core_node': 100000,
        'core_edge': 20,
        'regional_node': 100000,
        'regional_edge': 10,
        # 'per_site_spectrum_acquisition_cost': 1000,
        # 'per_site_administration_cost': 100,
    }


@fixture(scope='function')
def setup_lookup():
    return {
        ('urban', 'macro', '800', '4G', '50'): [
            (0.01, 1),
            (0.02, 2),
            (0.05, 5),
            (0.15, 15),
            (2, 100)
        ],
        ('urban', 'macro', '1800', '4G', '50'): [
            (0.01, 5),
            (0.02, 10),
            (0.05, 20),
            (0.15, 40),
            (2, 1000)
        ],
        ('urban', 'macro', '2600', '4G', '50'): [
            (0.01, 5),
            (0.02, 10),
            (0.05, 20),
            (0.15, 40),
            (2, 1000)
        ],
    }


@fixture(scope='function')
def setup_ci():
    return 50

@fixture(scope='function')
def setup_core_lut():
    return {
        'core_edge': {
            'MWI.1.1.1_1_new': 1000,
            'MWI.1.1.1_1_existing': 1000
        },
        'core_node': {
            'MWI.1.1.1_1_new': 2,
            'MWI.1.1.1_1_existing': 2
        },
        'regional_edge': {
            'MWI.1.1.1_1_new': 1000,
            'MWI.1.1.1_1_existing': 1000
        },
        'regional_node': {
            'MWI.1.1.1_1_new': 2,
            'MWI.1.1.1_1_existing': 2
        },
    }

@fixture(scope='function')
def setup_empty_core_lut():
    return {
        'core_edge': {
            'MWI.1.1.1_1_new': 0,
            'MWI.1.1.1_1_existing': 0
        },
        'core_node': {
            'MWI.1.1.1_1_new': 0,
            'MWI.1.1.1_1_existing': 0
        },
        'regional_edge': {
            'MWI.1.1.1_1_new': 0,
            'MWI.1.1.1_1_existing': 0
        },
        'regional_node': {
            'MWI.1.1.1_1_new': 0,
            'MWI.1.1.1_1_existing': 0
        },
    }

@fixture(scope='function')
def setup_infra_sharing_assets():
    return {
    'baseline': [],
    'passive': [
        'site_build',
        'installation',
        'site_rental',
        'backhaul',
    ],
    'active': [
        'equipment',
        'site_build',
        'installation',
        'site_rental',
        'operation_and_maintenance',
        'power',
        'backhaul',
    ],
    'srn': [
        'equipment',
        'site_build',
        'installation',
        'site_rental',
        'operation_and_maintenance',
        'power',
        'backhaul',
        # 'regional_edge',
        # 'regional_node',
        # 'core_edge',
        # 'core_node',
    ],
}


@fixture(scope='function')
def setup_cost_types():
    return {
    'equipment': 'capex',
    'site_build': 'capex',
    'installation': 'capex',
    'site_rental': 'opex',
    'operation_and_maintenance': 'opex',
    'power': 'opex',
    'backhaul': 'capex_and_opex',
    'regional_node': 'capex_and_opex',
    'regional_edge': 'capex_and_opex',
    'core_node': 'capex_and_opex',
    'core_edge': 'capex_and_opex',
}


@fixture(scope='function')
def setup_assets():
    return [
        {
            'GID_id': 'MWI.1.1.1_1', 'asset': 'equipment', 'quantity': 1,
            'cost_per_unit': 10000, 'total_cost': 10000, 'build_type': 'new'
        },
        {
            'GID_id': 'MWI.1.1.1_1', 'asset': 'site_build', 'quantity': 1,
            'cost_per_unit': 10000, 'total_cost': 10000, 'build_type': 'new'
        },
        {
            'GID_id': 'MWI.1.1.1_1', 'asset': 'installation', 'quantity': 1,
            'cost_per_unit': 10000, 'total_cost': 10000, 'build_type': 'upgraded'
        },
        {
            'GID_id': 'MWI.1.1.1_1', 'asset': 'backhaul', 'quantity': 2000,
            'cost_per_unit': 10, 'total_cost': 20000, 'build_type': 'upgraded'
        },
        {
            'GID_id': 'MWI.1.1.1_1', 'asset': 'installation', 'quantity': 1,
            'cost_per_unit': 10000, 'total_cost': 10000, 'build_type': 'existing'
        },
        {
            'GID_id': 'MWI.1.1.1_1', 'asset': 'backhaul', 'quantity': 2000,
            'cost_per_unit': 10, 'total_cost': 20000, 'build_type': 'existing'
        },
    ]


@fixture(scope='function')
def setup_assets_dict():
    return {
        'wireless_small': 10000,
        'core_node': 10000,
        'site_rental_rural': 10000,
        'equipment': 10000,
        'installation': 10000,
        'site_build': 10000,
        'core_edge': 10000,
        'operation_and_maintenance': 10000
    }


@fixture(scope='function')
def setup_tech_lut():
    return {
        'oil': {
            'carbon_per_kWh': 1, #kgs of carbon per kWh
            'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
            'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
            'pm10_per_kWh': 1, #kgs of PM10 per kWh
        },
        'gas': {
            'carbon_per_kWh': 1, #kgs of carbon per kWh
            'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
            'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
            'pm10_per_kWh': 1, #kgs of PM10 per kWh
        },
        'coal': {
            'carbon_per_kWh': 1, #kgs of carbon per kWh
            'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
            'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
            'pm10_per_kWh': 1, #kgs of PM10 per kWh
        },
        'nuclear': {
            'carbon_per_kWh': 1, #kgs of carbon per kWh
            'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
            'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
            'pm10_per_kWh': 1, #kgs of PM10 per kWh
        },
        'hydro': {
            'carbon_per_kWh': 1, #kgs of carbon per kWh
            'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
            'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
            'pm10_per_kWh': 1, #kgs of PM10 per kWh
        },
        'diesel': {
            'carbon_per_kWh': 2, #kgs of carbon per kWh
            'nitrogen_oxide_per_kWh': 2, #kgs of nitrogen oxide (NOx) per kWh
            'sulpher_dioxide_per_kWh': 2, #kgs of sulpher dioxide (SO2) per kWh
            'pm10_per_kWh': 2, #kgs of PM10 per kWh
        },
        'renewables': {
            'carbon_per_kWh': 1, #kgs of carbon per kWh
            'nitrogen_oxide_per_kWh': 1, #kgs of nitrogen oxide (NOx) per kWh
            'sulpher_dioxide_per_kWh': 1, #kgs of sulpher dioxide (SO2) per kWh
            'pm10_per_kWh': 1, #kgs of PM10 per kWh
        }
    }


@fixture(scope='function')
def setup_on_grid_mix():
    return {
        2020: {
            'hydro': 100,
            'oil': 100,
            'gas': 100,
            'coal': 100,
            'renewables': 100,
        },
        2021: {
            'hydro': 100,
            'oil': 100,
            'gas': 100,
            'coal': 100,
            'renewables': 100,
        }
    }


@fixture(scope='function')
def setup_data_energy():
    return [
        {
            'year': 2020,
            'GID_0': 'CHL',
            'GID_id': 'CHL.1.1.1_1',
            'geotype': 'rural',
            'decile': 1,
            'scenario': 'low_20_20_20',
            'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline_baseline',
            'confidence': [50],
            'total_sites': 131,
            'total_upgraded_sites': 131,
            'total_new_sites': 231,
            'grid_type_perc': 8.142493638676845,
            'grid_type': 'on_grid',
            'mno_energy_annual_demand_kwh': 30,
            'mno_equipment_annual_demand_kWh': 10,
            'mno_regional_nodes_annual_demand_kwh': 10,
            'mno_core_nodes_annual_demand_kwh': 10,
            'total_energy_annual_demand_kwh': 40,
            'phones_on_network': 75,
            'population_with_phones': 100,
            'phones_on_network_to_total_phones_ratio': 0.75,
        },
        {
            'year': 2020,
            'GID_0': 'CHL',
            'GID_id': 'CHL.1.1.1_1',
            'geotype': 'rural',
            'decile': 1,
            'scenario': 'low_20_20_20',
            'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline_baseline',
            'confidence': [50],
            'total_sites': 131,
            'total_upgraded_sites': 131,
            'total_new_sites': 231,
            'grid_type_perc': 91.85750636132316,
            'grid_type': 'grid_other',
            'mno_energy_annual_demand_kwh': 30,
            'mno_equipment_annual_demand_kWh': 10,
            'mno_regional_nodes_annual_demand_kwh': 10,
            'mno_core_nodes_annual_demand_kwh': 10,
            'total_energy_annual_demand_kwh': 40,
            'phones_on_network': 75,
            'population_with_phones': 100,
            'phones_on_network_to_total_phones_ratio': 0.75,
        },
        {
            'year': 2021,
            'GID_0': 'CHL',
            'GID_id': 'CHL.1.1.1_1',
            'geotype': 'rural',
            'decile': 1,
            'scenario': 'low_20_20_20',
            'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline_baseline',
            'confidence': [50],
            'total_sites': 131,
            'total_upgraded_sites': 131,
            'total_new_sites': 231,
            'grid_type_perc': 8.142493638676845,
            'grid_type': 'on_grid',
            'mno_energy_annual_demand_kwh': 30,
            'mno_equipment_annual_demand_kWh': 10,
            'mno_regional_nodes_annual_demand_kwh': 10,
            'mno_core_nodes_annual_demand_kwh': 10,
            'total_energy_annual_demand_kwh': 40,
            'phones_on_network': 75,
            'population_with_phones': 100,
            'phones_on_network_to_total_phones_ratio': 0.75,
        },
        {
            'year': 2021,
            'GID_0': 'CHL',
            'GID_id': 'CHL.1.1.1_1',
            'geotype': 'rural',
            'decile': 1,
            'scenario': 'low_20_20_20',
            'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline_baseline',
            'confidence': [50],
            'total_sites': 131,
            'total_upgraded_sites': 131,
            'total_new_sites': 231,
            'grid_type_perc': 91.85750636132316,
            'grid_type': 'grid_other',
            'mno_energy_annual_demand_kwh': 30,
            'mno_equipment_annual_demand_kWh': 10,
            'mno_regional_nodes_annual_demand_kwh': 10,
            'mno_core_nodes_annual_demand_kwh': 10,
            'total_energy_annual_demand_kwh': 40,
            'phones_on_network': 75,
            'population_with_phones': 100,
            'phones_on_network_to_total_phones_ratio': 0.75,
        }
    ]
