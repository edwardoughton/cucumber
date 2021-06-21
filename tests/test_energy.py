import pytest
from cuba.energy import assess_energy


def test_assess_energy(setup_region, setup_option, setup_global_parameters,
    setup_country_parameters, setup_timesteps):

    setup_region[0]['new_sites'] = 1

    regions = [
        {
            'GID_id': 'a',
            'geotype': 'urban',
            'population_total': 1000,
            'population_km2': 500,
            'total_sites': 10,
            'total_upgraded_sites': 5,
            'total_new_sites': 5,
        },
        # {
        #     'GID_id': 'b',
        #     'geotype': 'urban',
        #     'population_total': 1000,
        #     'population_km2': 500,

        # },
    ]

    results = assess_energy('CHL', regions, setup_option,
        setup_global_parameters, setup_country_parameters,
        setup_timesteps)

    assert results[0]['total_sites'] == 10
