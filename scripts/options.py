"""
Options consisting of scenarios and strategies.

Country parameters consist of those parameters which are specific
to each country.

Written by Ed Oughton, based on work from the pytal and podis repositories.

April 2021

#strategy is defined based on generation_core_backhaul_sharing_networks_spectrum_tax

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

    scenarios = ['low_20_20_20', 'baseline_20_20_20', 'high_20_20_20',
                'low_10_10_10', 'baseline_10_10_10', 'high_10_10_10',
                'low_5_5_5', 'baseline_5_5_5', 'high_5_5_5']
    generation_core_types = ['3G_umts', '4G_epc', '5G_nsa']
    backhaul_types = ['wireless', 'fiber']
    sharing_types = ['baseline']
    networks_types = ['baseline']
    spectrum_types = ['baseline']
    tax_types = ['baseline']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    strategy = '{}_{}_{}_{}_{}_{}'.format(
                                        generation_core_type,
                                        backhaul,
                                        sharing,
                                        network,
                                        spectrum,
                                        tax
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

    scenarios = ['low_20_20_20', 'baseline_20_20_20', 'high_20_20_20',
                'low_10_10_10', 'baseline_10_10_10', 'high_10_10_10',
                'low_5_5_5', 'baseline_5_5_5', 'high_5_5_5']
    generation_core_types = ['3G_umts', '4G_epc', '5G_nsa']
    backhaul_types = ['wireless', 'fiber']
    sharing_types = ['baseline', 'passive', 'active', 'srn']
    networks_types = ['baseline']
    spectrum_types = ['baseline']
    tax_types = ['baseline']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    strategy = '{}_{}_{}_{}_{}_{}'.format(
                                        generation_core_type,
                                        backhaul,
                                        sharing,
                                        network,
                                        spectrum,
                                        tax
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

    scenarios = ['low_20_20_20', 'baseline_20_20_20', 'high_20_20_20',
                'low_10_10_10', 'baseline_10_10_10', 'high_10_10_10',
                'low_5_5_5', 'baseline_5_5_5', 'high_5_5_5']
    generation_core_types = ['3G_umts', '4G_epc', '5G_nsa']
    backhaul_types = ['wireless', 'fiber']
    sharing_types = ['baseline']
    networks_types = ['baseline']
    spectrum_types = ['baseline', 'low', 'high']
    tax_types = ['baseline', 'low', 'high']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    strategy = '{}_{}_{}_{}_{}_{}'.format(
                                        generation_core_type,
                                        backhaul,
                                        sharing,
                                        network,
                                        spectrum,
                                        tax
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

    scenarios = ['low_20_20_20', 'baseline_20_20_20', 'high_20_20_20',
                'low_10_10_10', 'baseline_10_10_10', 'high_10_10_10',
                'low_5_5_5', 'baseline_5_5_5', 'high_5_5_5']
    generation_core_types = ['4G_epc'] #'3G_umts', '5G_nsa'
    backhaul_types = ['wireless', 'fiber']
    sharing_types = ['baseline', 'srn']
    networks_types = ['baseline']
    spectrum_types = ['baseline', 'low']
    tax_types = ['baseline', 'low']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:
                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    strategy = '{}_{}_{}_{}_{}_{}'.format(
                                        generation_core_type,
                                        backhaul,
                                        sharing,
                                        network,
                                        spectrum,
                                        tax
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
    'core_node': 500000,
    'core_edge': 25,
    'regional_node': 200000,
    'regional_edge': 25,
}


GLOBAL_PARAMETERS = {
    'overbooking_factor': 20,
    'return_period': 10,
    'discount_rate': 5,
    'opex_percentage_of_capex': 10,
    'confidence': [50],#[5, 50, 95]
    'tdd_dl_to_ul': '80:20',
    }
