"""
Country Assessment list

"""

COUNTRY_LIST = [
    {
        'country_name': 'Chile',
        'preferred_name': 'Chile',
        'iso3': 'CHL',
        'iso2': 'CH',
        'regional_level': 3,
        'region': 'LAC',
        'cluster': 'C6',
        # 'coverage_4G': 70,
        'pop_density_km2': 500,
        'settlement_size': 500,
        'core_node_size': 500,
        'subs_growth_low': 2,
        'sp_growth_low_urban': 2,
        'sp_growth_low_rural': 2,
        'subs_growth_baseline': 4,
        'sp_growth_baseline_urban': 4,
        'sp_growth_baseline_rural': 4,
        'subs_growth_high': 6,
        'sp_growth_high_urban': 6,
        'sp_growth_high_rural': 6,
        'phone_ownership_male': 50,
        'phone_ownership_female': 50,
    },
    {
        'country_name': 'Colombia',
        'preferred_name': 'Colombia',
        'iso3': 'COL',
        'iso2': 'CO',
        'regional_level': 2,
        'core_node_level': 1,
        'regional_node_level': 2,
        'region': 'LAC',
        'regions_to_exclude_GID_1': ['COL.26_1'],
        # 'regions_to_exclude-GID_2': ['COL.26_1'],
        # 'coverage_4G': 70,
        'pop_density_km2': 100,
        'settlement_size': 200,
        'core_node_size': 2000,
        'subs_growth_low': .5,
        'sp_growth_low_urban': .5,
        'sp_growth_low_rural': .5,
        'subs_growth_baseline': 1.5,
        'sp_growth_baseline_urban': 1.5,
        'sp_growth_baseline_rural': 1.5,
        'subs_growth_high': 2.5,
        'sp_growth_high_urban': 2.5,
        'sp_growth_high_rural': 2.5,
        'phone_ownership_male': 50,
        'phone_ownership_female': 50,
        'figsize':(9,8),
        'rounding': 0,
        'rounding_policy': 0,
    },
]


COUNTRY_PARAMETERS = {
    'CHL': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 15,
            'medium': 10,
            'low': 5,
        },
        'networks': {
            'baseline_urban': 4,
            'baseline_suburban': 4,
            'baseline_rural': 4,
            'shared_urban': 4,
            'shared_suburban': 4,
            'shared_rural': 1,
        },
        'frequencies': {
            '3G': [
                {
                    'frequency': 850,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 2100,
                    'bandwidth': '2x10',
                },
            ],
            '4G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 2600,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'wacc': 8, #http://www.waccexpert.com/
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.25,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.15,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 200,
            'tax_low': 10,
            'tax_baseline': 27, #source: https://www.sii.cl/ayudas/aprenda_sobre/3072-1-3080.html
            'tax_high': 45,
            'administration_percentage_of_network_cost': 20,
            },
        'energy': {
            ##based on GSMA there are 9,152 ongrid towers, 554 using renewables, 121 diesel
            ##Check the GSMA spreadsheet in raw/gsma
            'perc_ongrid': 98, #98.75,
            'perc_other': 2, #1.25, #offgrid diesel
        },
    },
    'COL': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 12,
            'medium': 9,
            'low': 4,
        },
        'networks': {
            'baseline_urban': 3,
            'baseline_suburban': 3,
            'baseline_rural': 3,
            'shared_urban': 3,
            'shared_suburban': 3,
            'shared_rural': 1,
        },
        'frequencies': {
            '3G': [
                {
                    'frequency': 1900,
                    'bandwidth': '2x10',
                    # 'status': 'active',
                },
            ],
            '4G': [
                {
                    'frequency': 850,
                    'bandwidth': '2x10',
                    # 'status': 'active',
                },
                # {
                #     'frequency': 1700,
                #     'bandwidth': '2x10',
                #     # 'status': 'active',
                # },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                    # 'status': 'inactive',
                },
                {
                    'frequency': 3500,
                    'bandwidth': ' 1x40',
                    # 'status': 'inactive',
                },
            ]
        },
        'financials': {
            'wacc': 15, #http://www.waccexpert.com/
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.3, #refine
            'spectrum_capacity_baseline_usd_mhz_pop': 0.2,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 200,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 45,
            'administration_percentage_of_network_cost': 20,
            },
        'energy': {
            ##based on GSMA there are 14,012 ongrid towers, 2,855 using renewables, 611 diesel
            ##Check the GSMA spreadsheet in raw/gsma
            'perc_ongrid': 80.2, #98.75,
            'perc_other': 19.8, #1.25, #offgrid diesel
            },
        },
    }
