import pytest
from cucumber.emissions import assess_emissions


def test_assess_emissions(        
        setup_country,
        setup_deciles,
        setup_on_grid_mix,
        setup_emissions_lut
    ):
    """
    Unit test.

    """
    setup_deciles[0]['network_existing_energy_kwh'] = 1000000
    setup_deciles[0]['network_new_energy_kwh'] = 0

    results, emissions = assess_emissions(
        setup_country,
        [setup_deciles[0]],
        {'oil': .5},
        {'Europe': {'aps-2030': {'oil': 1}}} 
    )

    answer = (
        (setup_deciles[0]['network_existing_energy_kwh'] * .5) *
        (1/1000) / 1000
    )

    assert results[0]['existing_emissions_t_co2_oil'] == answer
    assert results[0]['network_existing_emissions_t_co2'] == answer
    assert results[0]['network_new_emissions_t_co2'] == 0
    assert emissions[0]['existing_energy_kwh'] == 500000.0
    assert emissions[0]['new_energy_kwh'] == 0
    assert emissions[0]['existing_emissions_t_co2'] == 0.5
    assert emissions[0]['new_emissions_t_co2'] == 0

    setup_deciles[0]['network_existing_energy_kwh'] = 0
    setup_deciles[0]['network_new_energy_kwh'] = 1000000

    results, emissions = assess_emissions(
        setup_country,
        [setup_deciles[0]],
        {'oil': .5},
        {'Europe': {'aps-2030': {'oil': 1}}} 
    )

    answer = (
        (setup_deciles[0]['network_new_energy_kwh'] * .5) *
        (1/1000) / 1000
    )

    assert results[0]['existing_emissions_t_co2_oil'] == 0.0
    assert results[0]['network_new_emissions_t_co2'] == answer
    assert emissions[0]['existing_energy_kwh'] == 0
    assert emissions[0]['new_energy_kwh'] == 500000.0
    assert emissions[0]['existing_emissions_t_co2'] == 0
    assert emissions[0]['new_emissions_t_co2'] == 0.5

    setup_deciles[0]['network_existing_energy_kwh'] = 1000000
    setup_deciles[0]['network_new_energy_kwh'] = 1000000

    results, emissions = assess_emissions(
        setup_country,
        [setup_deciles[0]],
        {'oil': .5, 'hydro': .01},
        {'Europe': {'aps-2030': {'oil': 1, 'hydro': 0.01}}} 
    )

    assert results[0]['network_existing_emissions_t_co2'] == 0.5001
    assert results[0]['network_new_emissions_t_co2'] == 0.5001
    #dict1
    assert emissions[0]['existing_energy_kwh'] == 500000.0
    assert emissions[0]['new_energy_kwh'] == 500000.0
    assert emissions[0]['existing_emissions_t_co2'] == 0.5
    assert emissions[0]['new_emissions_t_co2'] == 0.5
    #dict2
    assert emissions[1]['existing_energy_kwh'] == 10000.0
    assert emissions[1]['new_energy_kwh'] == 10000.0
    assert emissions[1]['existing_emissions_t_co2'] == 0.0001
    assert emissions[1]['new_emissions_t_co2'] == 0.0001
