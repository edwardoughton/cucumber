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
    }
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
            'low': 7,
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
                    'frequency': 1800,
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
            'spectrum_coverage_baseline_usd_mhz_pop': 0.2,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 200,
            'tax_low': 10,
            'tax_baseline': 27, #source: https://www.sii.cl/ayudas/aprenda_sobre/3072-1-3080.html
            'tax_high': 45,
            'administration_percentage_of_network_cost': 20,
            },
        },
    }
