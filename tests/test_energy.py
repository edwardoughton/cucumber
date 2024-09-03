import pytest
from cucumber.energy import assess_energy#, calc_emissions


def test_assess_energy(
        setup_country, 
        setup_deciles, 
        setup_on_grid_mix
    ):

    #baseline sharing
    setup_deciles[0]['network_existing_sites'] = 1
    setup_deciles[0]['network_new_sites'] = 0
    setup_deciles[0]['backhaul_wireless'] = 1
    setup_deciles[0]['backhaul_fiber'] = 0
    setup_deciles[0]['backhaul_new'] = 0
    setup_deciles[0]['networks'] = 4

    results, energy = assess_energy(
        setup_country, 
        [setup_deciles[0]], 
        setup_on_grid_mix
    )

    assert results[0]['network_existing_energy_kwh'] == 17520
    assert round(energy[0]['network_existing_energy_kwh']) == 2841 

    #baseline sharing
    setup_deciles[0]['network_existing_sites'] = 0
    setup_deciles[0]['network_new_sites'] = 1
    setup_deciles[0]['backhaul_wireless'] = 0
    setup_deciles[0]['backhaul_fiber'] = 0
    setup_deciles[0]['backhaul_new'] = 0
    setup_deciles[0]['networks'] = 4

    results, energy = assess_energy(
        setup_country, 
        [setup_deciles[0]], 
        setup_on_grid_mix
    )

    assert results[0]['network_existing_energy_kwh'] == 0
    assert results[0]['network_new_energy_kwh'] == 8760

    #passive sharing
    setup_deciles[0]['network_existing_sites'] = 1
    setup_deciles[0]['network_new_sites'] = 0
    setup_deciles[0]['backhaul_wireless'] = 1
    setup_deciles[0]['backhaul_fiber'] = 0
    setup_deciles[0]['backhaul_new'] = 0
    setup_deciles[0]['networks'] = 4
    setup_deciles[0]['sharing_scenario'] = 'passive'

    results, energy = assess_energy(
        setup_country, 
        [setup_deciles[0]], 
        setup_on_grid_mix
    )

    assert results[0]['network_existing_energy_kwh'] == 17520
    assert round(energy[0]['network_existing_energy_kwh']) == 2841 

    #active sharing
    setup_deciles[0]['network_existing_sites'] = 1
    setup_deciles[0]['network_new_sites'] = 0
    setup_deciles[0]['backhaul_wireless'] = 1
    setup_deciles[0]['backhaul_fiber'] = 0
    setup_deciles[0]['backhaul_new'] = 0
    setup_deciles[0]['networks'] = 1
    setup_deciles[0]['sharing_scenario'] = 'active'

    results, energy = assess_energy(
        setup_country, 
        [setup_deciles[0]], 
        setup_on_grid_mix
    )

    assert results[0]['network_existing_energy_kwh'] == 4380
    assert round(energy[0]['network_existing_energy_kwh']) == 710 

    #srn sharing - urban
    setup_deciles[0]['network_existing_sites'] = 1
    setup_deciles[0]['network_new_sites'] = 0
    setup_deciles[0]['backhaul_wireless'] = 1
    setup_deciles[0]['backhaul_fiber'] = 0
    setup_deciles[0]['backhaul_new'] = 0
    setup_deciles[0]['networks'] = 1
    setup_deciles[0]['sharing_scenario'] = 'srn'

    results, energy = assess_energy(
        setup_country, 
        [setup_deciles[0]], 
        setup_on_grid_mix
    )

    assert results[0]['network_existing_energy_kwh'] == 17520.0
    assert round(energy[0]['network_existing_energy_kwh']) == 2841 

    #srn sharing - rural
    setup_deciles[0]['network_existing_sites'] = 1
    setup_deciles[0]['network_new_sites'] = 0
    setup_deciles[0]['backhaul_wireless'] = 1
    setup_deciles[0]['backhaul_fiber'] = 0
    setup_deciles[0]['backhaul_new'] = 0
    setup_deciles[0]['networks'] = 1
    setup_deciles[0]['sharing_scenario'] = 'srn'
    setup_deciles[0]['geotype'] = 'rural'

    results, energy = assess_energy(
        setup_country, 
        [setup_deciles[0]], 
        setup_on_grid_mix
    )

    assert results[0]['network_existing_energy_kwh'] == 4380
    assert round(energy[0]['network_existing_energy_kwh']) == 710