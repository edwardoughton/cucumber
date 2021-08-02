import pytest
from cuba.energy import assess_energy#, calc_emissions


def test_assess_energy(setup_region, setup_option, setup_global_parameters,
    setup_country_parameters, setup_timesteps, setup_tech_lut, setup_on_grid_mix):

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
            'on_grid_perc': 50,
            'grid_other_perc': 50,
        },
    ]

    assets = [
        {
        'scenario': 'low_20_20_20',
        'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline',
        'confidence': 50,
        'GID_id':  'a',
        'asset': 'equipment',
        'quantity': 1,
        },
        {
        'scenario': 'low_20_20_20',
        'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline',
        'confidence': 50,
        'GID_id':  'a',
        'asset': 'regional_node',
        'quantity': 1,
        },
        {
        'scenario': 'low_20_20_20',
        'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline',
        'confidence': 50,
        'GID_id':  'a',
        'asset': 'core_node',
        'quantity': 1,
        },
        {
        'scenario': 'low_20_20_20',
        'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline',
        'confidence': 50,
        'GID_id':  'a',
        'asset': 'wireless_small',
        'quantity': 1,
        },
        {
        'scenario': 'low_20_20_20',
        'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline',
        'confidence': 50,
        'GID_id':  'a',
        'asset': 'wireless_medium',
        'quantity': 1,
        },
        {
        'scenario': 'low_20_20_20',
        'strategy': '3G_umts_wireless_baseline_baseline_baseline_baseline',
        'confidence': 50,
        'GID_id':  'a',
        'asset': 'wireless_large',
        'quantity': 1,
        },
    ]

    energy_demand = {
        'equipment_kwh': 1,
        'core_node_kwh': 1,
        'regional_node_kwh': 1,
        'wireless_small_kwh': 1,
        'wireless_medium_kwh': 1,
        'wireless_large_kwh': 1,
    }

    results = assess_energy('CHL', regions, assets, setup_option,
        setup_global_parameters, setup_country_parameters,
        setup_timesteps, energy_demand)

    assert results[0]['equipment_annual_demand_kWh'] == (4380 * 0.5)
    assert results[0]['regional_nodes_annual_demand_kwh'] == (4380 * 0.5)
    assert results[0]['core_nodes_annual_demand_kwh'] == (4380 * 0.5)
    assert results[0]['wireless_backhaul_annual_demand_kwh'] == ((4380 * 3) * 0.5)
    assert results[0]['total_energy_annual_demand_kwh'] == (
        ((4380 * 0.5) * 3) + ((4380 * 3) * 0.5)
    )

    regions = [
        {
            'GID_id': 'a',
            'geotype': 'urban',
            'population_total': 1000,
            'population_km2': 500,
            'total_sites': 10,
            'total_upgraded_sites': 5,
            'total_new_sites': 5,
            'on_grid_perc': 100,
            'grid_other_perc': 0,
        },
        {
            'GID_id': 'a',
            'geotype': 'urban',
            'population_total': 1000,
            'population_km2': 500,
            'total_sites': 10,
            'total_upgraded_sites': 5,
            'total_new_sites': 5,
            'on_grid_perc': 0,
            'grid_other_perc': 100,
        },
    ]

    results = assess_energy('CHL', regions, assets, setup_option,
        setup_global_parameters, setup_country_parameters,
        setup_timesteps, energy_demand)

    for region in results:

        if region['grid_type_perc'] == 100 and region['grid_type'] == 'on_grid':
            assert region['total_energy_annual_demand_kwh'] == ((4380 * 6) * 1)
        if region['grid_type_perc'] == 100 and region['grid_type'] == 'off_grid':
            assert region['total_energy_annual_demand_kwh'] == ((4380 * 6) * 1)


    setup_timesteps = [
        2020,
        2021,
    ]

    results = assess_energy('CHL', regions, assets, setup_option,
        setup_global_parameters, setup_country_parameters,
        setup_timesteps, energy_demand
    ) # should produce 8 results, 2 regions, 2 grid types over 2 timesteps

    total_energy = 0

    for region in results:
        total_energy += region['total_energy_annual_demand_kwh']

    assert total_energy == ((4380 * 6) * 1) * 4
