import pytest
from cucumber.energy import assess_energy#, calc_emissions


def test_assess_energy(
        setup_country, 
        setup_deciles, 
        setup_on_grid_mix
    ):

    setup_deciles[0]['total_existing_sites'] = 1
    setup_deciles[0]['total_new_sites'] = 0
    setup_deciles[0]['backhaul_wireless'] = 1
    setup_deciles[0]['backhaul_fiber'] = 0
    setup_deciles[0]['backhaul_new'] = 0

    results, energy = assess_energy(
        setup_country, 
        [setup_deciles[0]], 
        setup_on_grid_mix
    )

    assert results[0]['total_existing_energy_kwh'] == 17520
    assert energy[0]['new_existing_energy_kwh'] == 0 

    setup_deciles[0]['total_existing_sites'] = 0
    setup_deciles[0]['total_new_sites'] = 1
    setup_deciles[0]['backhaul_wireless'] = 0
    setup_deciles[0]['backhaul_fiber'] = 0
    setup_deciles[0]['backhaul_new'] = 0

    results, energy = assess_energy(
        setup_country, 
        [setup_deciles[0]], 
        setup_on_grid_mix
    )

    assert results[0]['total_existing_energy_kwh'] == 0
    assert results[0]['total_new_energy_kwh'] == 8760

