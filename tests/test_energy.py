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
    ]

    energy_demand = {
        'equipment_kwh': 1,
        'core_node_kwh': 1,
        'regional_node_kwh': 1,
    }

    results = assess_energy('CHL', regions, assets, setup_option,
        setup_global_parameters, setup_country_parameters,
        setup_timesteps, energy_demand)

    assert results[0]['equipment_annual_demand_kWh'] == 4380
    assert results[0]['regional_nodes_annual_demand_kwh'] == 4380
    assert results[0]['core_nodes_annual_demand_kwh'] == 4380
    assert results[0]['total_annual_energy_demand_kwh'] == (4380 * 3)
