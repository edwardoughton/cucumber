"""
Options consisting of scenarios and strategies.

Country parameters consist of those parameters which are specific
to each country.

Written by Ed Oughton, based on work from the pytal and podis repositories.

April 2021

#strategy is defined based on generation_core_backhaul_sharing_networks_spectrum_tax_power

generation: technology generation, so 3G or 4G
core: type of core data transport network, eg. evolved packet core (4G)
backhaul: type of backhaul, so fiber or wireless
sharing: the type of infrastructure sharing, active, passive etc..
network: relates to the number of networks, as defined in country parameters
spectrum: type of spectrum strategy, so baseline, high or low
tax: type of taxation strategy, so baseline, high or low

"""


def generate_tech_options():
    """
    Generate technology strategy options.

    """
    output = []

    scenarios = [
                # 'low_100_100_100', 'baseline_100_100_100','high_100_100_100',
                # 'low_50_50_50',
                'baseline_50_50_50',
                # 'high_50_50_50',
                # 'low_25_25_25', 'baseline_25_25_25', 'high_25_25_25',
                ]
    generation_core_types = ['4G_epc', '5G_nsa'] #'3G_umts',
    backhaul_types = ['wireless', 'fiber']
    sharing_types = ['baseline']
    networks_types = ['baseline']
    spectrum_types = ['baseline']
    tax_types = ['baseline']
    power_types = ['baseline']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    for power in power_types:
                                        strategy = '{}_{}_{}_{}_{}_{}_{}'.format(
                                            generation_core_type,
                                            backhaul,
                                            sharing,
                                            network,
                                            spectrum,
                                            tax,
                                            power
                                        )
                                        output.append({
                                            'scenario': scenario,
                                            'strategy': strategy
                                        })

    return output


def generate_business_model_options():
    """
    Generate business model strategy options.

    """
    output = []

    scenarios = ['low_100_100_100', 'baseline_100_100_100','high_100_100_100',
                'low_50_50_50', 'baseline_50_50_50','high_50_50_50',
                'low_25_25_25', 'baseline_25_25_25', 'high_25_25_25',
                ]
    generation_core_types = ['4G_epc'] #'3G_umts', , '5G_nsa'
    backhaul_types = ['wireless'] #, 'fiber'
    sharing_types = ['baseline', 'passive', 'active', 'srn']
    networks_types = ['baseline']
    spectrum_types = ['baseline']
    tax_types = ['baseline']
    power_types = ['baseline']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    for power in power_types:
                                        strategy = '{}_{}_{}_{}_{}_{}_{}'.format(
                                            generation_core_type,
                                            backhaul,
                                            sharing,
                                            network,
                                            spectrum,
                                            tax,
                                            power
                                        )
                                        output.append({
                                            'scenario': scenario,
                                            'strategy': strategy
                                        })

    return output


def generate_policy_options():
    """
    Generate policy strategy options.

    """
    output = []

    scenarios = ['low_100_100_100', 'baseline_100_100_100','high_100_100_100',
                'low_50_50_50', 'baseline_50_50_50','high_50_50_50',
                'low_25_25_25', 'baseline_25_25_25', 'high_25_25_25',
                ]
    generation_core_types = ['4G_epc'] #'3G_umts', , '5G_nsa'
    backhaul_types = ['wireless'] #, 'fiber'
    sharing_types = ['baseline']
    networks_types = ['baseline']
    spectrum_types = ['baseline', 'low', 'high']
    tax_types = ['baseline', 'low', 'high']
    power_types = ['baseline']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    for power in power_types:
                                        strategy = '{}_{}_{}_{}_{}_{}_{}'.format(
                                            generation_core_type,
                                            backhaul,
                                            sharing,
                                            network,
                                            spectrum,
                                            tax,
                                            power
                                        )
                                        output.append({
                                            'scenario': scenario,
                                            'strategy': strategy
                                        })

    return output


def generate_mixed_options():
    """
    Generate policy strategy options.

    """
    output = []

    scenarios = ['low_100_100_100', 'baseline_100_100_100','high_100_100_100',
                'low_50_50_50', 'baseline_50_50_50','high_50_50_50',
                'low_25_25_25', 'baseline_25_25_25', 'high_25_25_25',
                ]
    generation_core_types = ['4G_epc'] #'3G_umts', '5G_nsa'
    backhaul_types = ['wireless', 'fiber']
    sharing_types = ['baseline', 'srn']
    networks_types = ['baseline']
    spectrum_types = ['baseline', 'low']
    tax_types = ['baseline', 'low']
    power_types = ['baseline']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    for power in power_types:
                                        strategy = '{}_{}_{}_{}_{}_{}_{}'.format(
                                            generation_core_type,
                                            backhaul,
                                            sharing,
                                            network,
                                            spectrum,
                                            tax,
                                            power
                                        )
                                        output.append({
                                            'scenario': scenario,
                                            'strategy': strategy
                                        })

    return output


def generate_power_options():
    """
    Generate energy strategy options.

    """
    output = []

    scenarios = ['low_100_100_100', 'baseline_100_100_100','high_100_100_100',
                'low_50_50_50', 'baseline_50_50_50','high_50_50_50',
                'low_25_25_25', 'baseline_25_25_25', 'high_25_25_25',
                ]
    generation_core_types = ['4G_epc', '5G_nsa']
    backhaul_types = ['wireless', 'fiber']
    sharing_types = ['baseline']
    networks_types = ['baseline']
    spectrum_types = ['baseline']
    tax_types = ['baseline']
    power_types = ['baseline', 'renewable']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    for power in power_types:
                                        strategy = '{}_{}_{}_{}_{}_{}_{}'.format(
                                            generation_core_type,
                                            backhaul,
                                            sharing,
                                            network,
                                            spectrum,
                                            tax,
                                            power
                                        )
                                        output.append({
                                            'scenario': scenario,
                                            'strategy': strategy
                                        })

    return output


def business_model_power_options():
    """
    Generate energy strategy options.

    """
    output = []

    scenarios = ['low_100_100_100', 'baseline_100_100_100','high_100_100_100',
                'low_50_50_50', 'baseline_50_50_50','high_50_50_50',
                'low_25_25_25', 'baseline_25_25_25', 'high_25_25_25',
                ]
    generation_core_types = ['4G_epc', '5G_nsa'] #'3G_umts',
    backhaul_types = ['wireless', 'fiber']
    sharing_types = ['baseline', 'passive', 'active', 'srn']
    networks_types = ['baseline']
    spectrum_types = ['baseline']
    tax_types = ['baseline']
    power_types = ['baseline']#, 'renewable']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    for power in power_types:
                                        strategy = '{}_{}_{}_{}_{}_{}_{}'.format(
                                            generation_core_type,
                                            backhaul,
                                            sharing,
                                            network,
                                            spectrum,
                                            tax,
                                            power
                                        )
                                        output.append({
                                            'scenario': scenario,
                                            'strategy': strategy
                                        })

    return output


OPTIONS = {
    'technology_options': generate_tech_options(),
    'business_model_options': generate_business_model_options(),
    'policy_options': generate_policy_options(),
    'mixed_options': generate_mixed_options(),
    'power_options': generate_power_options(),
    'business_model_power_options': business_model_power_options(),
}


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
    'fiber_urban_m': 25,
    'fiber_suburban_m': 15,
    'fiber_rural_m': 10,
    'wireless_small': 15000,
    'wireless_medium': 20000,
    'wireless_large': 45000,
    # 'core_node': 500000,
    # 'core_edge': 25,
    # 'regional_node': 200000,
    # 'regional_edge': 25,
}


GLOBAL_PARAMETERS = {
    'traffic_in_the_busy_hour_perc': 20,
    # 'overbooking_factor': 20,
    'return_period': 10,
    'discount_rate': 5,
    'opex_percentage_of_capex': 10,
    'confidence': [50],#[5, 50, 95]
    'tdd_dl_to_ul': '80:20',
    }


INFRA_SHARING_ASSETS = {
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


COST_TYPES = {
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


ENERGY_DEMAND = {
    #all costs in $USD
    'equipment_kwh': 5,
    'core_node_kwh': 0,
    'regional_node_kwh': 0,
    'wireless_small_kwh': 5, #Faruk et al. 2019
    'wireless_medium_kwh': 10,
    'wireless_large_kwh': 15,
}


TECH_LUT = {
    'oil': {
        'carbon_per_kWh': 0.5, #kgs of carbon per kWh
        'nitrogen_oxide_per_kWh':0.00009, #kgs of nitrogen oxide (NOx) per kWh
        'sulpher_dioxide_per_kWh': 0.007, #kgs of sulpher dioxide (SO2) per kWh
        'pm10_per_kWh': 0.002, #kgs of PM10 per kWh
    },
    'gas': {
        'carbon_per_kWh': 0.5, #kgs of carbon per kWh
        'nitrogen_oxide_per_kWh':0.00009, #kgs of nitrogen oxide (NOx) per kWh
        'sulpher_dioxide_per_kWh': 0.007, #kgs of sulpher dioxide (SO2) per kWh
        'pm10_per_kWh': 0.002, #kgs of PM10 per kWh
    },
    'coal': {
        'carbon_per_kWh': 1, #kgs of carbon per kWh
        'nitrogen_oxide_per_kWh':0.0001, #kgs of nitrogen oxide (NOx) per kWh
        'sulpher_dioxide_per_kWh': 0.01, #kgs of sulpher dioxide (SO2) per kWh
        'pm10_per_kWh': 0.01, #kgs of PM10 per kWh
    },
    'nuclear': {
        'carbon_per_kWh': 0.5, #kgs of carbon per kWh
        'nitrogen_oxide_per_kWh':0.00009, #kgs of nitrogen oxide (NOx) per kWh
        'sulpher_dioxide_per_kWh': 0.007, #kgs of sulpher dioxide (SO2) per kWh
        'pm10_per_kWh': 0.002, #kgs of PM10 per kWh
    },
    'hydro': {
        'carbon_per_kWh': 0.01, #kgs of carbon per kWh
        'nitrogen_oxide_per_kWh':0.0000009, #kgs of nitrogen oxide (NOx) per kWh
        'sulpher_dioxide_per_kWh': 0.00007, #kgs of sulpher dioxide (SO2) per kWh
        'pm10_per_kWh': 0.00002, #kgs of PM10 per kWh
    },
    'diesel': {
        'carbon_per_kWh': 0.5, #kgs of carbon per kWh
        'nitrogen_oxide_per_kWh':0.00009, #kgs of nitrogen oxide (NOx) per kWh
        'sulpher_dioxide_per_kWh': 0.007, #kgs of sulpher dioxide (SO2) per kWh
        'pm10_per_kWh': 0.002, #kgs of PM10 per kWh
    },
    'renewables': {
        'carbon_per_kWh': 0.1, #kgs of carbon per kWh
        'nitrogen_oxide_per_kWh':0.000001, #kgs of nitrogen oxide (NOx) per kWh
        'sulpher_dioxide_per_kWh': 0.0001, #kgs of sulpher dioxide (SO2) per kWh
        'pm10_per_kWh': 0.00001, #kgs of PM10 per kWh
    }
}
