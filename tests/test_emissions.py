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
    setup_deciles[0]['total_existing_energy_kwh'] = 1000000
    setup_deciles[0]['total_new_energy_kwh'] = 0

    results, emissions = assess_emissions(
        setup_country,
        [setup_deciles[0]],
        setup_on_grid_mix,
        setup_emissions_lut
    )

    assert round(emissions[0]['existing_energy_kwh'],0) == 162131
    assert round(emissions[0]['new_energy_kwh'],0) == 0
    assert round(emissions[0]['existing_emissions_t_co2'],0) == 2
    assert round(emissions[0]['new_emissions_t_co2'],0) == 0

    setup_deciles[0]['total_existing_energy_kwh'] = 0
    setup_deciles[0]['total_new_energy_kwh'] = 1000000

    results, emissions = assess_emissions(
        setup_country,
        [setup_deciles[0]],
        setup_on_grid_mix,
        setup_emissions_lut
    )

    assert round(emissions[0]['existing_energy_kwh'],0) == 0
    assert round(emissions[0]['new_energy_kwh'],0) == 162131
    assert round(emissions[0]['existing_emissions_t_co2'],0) == 0
    assert round(emissions[0]['new_emissions_t_co2'],0) == 2