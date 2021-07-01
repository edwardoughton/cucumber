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
            'off_grid_perc': 50,
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
        setup_timesteps, energy_demand) #, setup_tech_lut, setup_on_grid_mix

    assert results[0]['equipment_annual_demand_kWh'] == (4380 * 0.5)
    assert results[0]['regional_nodes_annual_demand_kwh'] == (4380 * 0.5)
    assert results[0]['core_nodes_annual_demand_kwh'] == (4380 * 0.5)
    assert results[0]['total_annual_energy_demand_kwh'] == ((4380 * 0.5) * 3)

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
            'off_grid_perc': 0,
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
            'off_grid_perc': 100,
        },
    ]

    results = assess_energy('CHL', regions, assets, setup_option,
        setup_global_parameters, setup_country_parameters,
        setup_timesteps, energy_demand) #, setup_tech_lut, setup_on_grid_mix

    for region in results:

        if region['grid_type_perc'] == 100 and region['grid_type'] == 'on_grid':
            assert region['total_annual_energy_demand_kwh'] == ((4380 * 3) * 1)
        if region['grid_type_perc'] == 100 and region['grid_type'] == 'off_grid':
            assert region['total_annual_energy_demand_kwh'] == ((4380 * 3) * 1)



# def test_calc_emissions(setup_tech_lut, setup_on_grid_mix):

#     results = calc_emissions(4380, 'on_grid', setup_tech_lut, setup_on_grid_mix)

#     assert results['demand_carbon_per_kwh'] == 4380
#     assert results['nitrogen_oxide_per_kwh'] == 4380
#     assert results['sulpher_dioxide_per_kwh'] == 4380
#     assert results['pm10_per_kwh'] == 4380

#     results = calc_emissions(4380, 'off_grid', setup_tech_lut, setup_on_grid_mix)

#     assert results['demand_carbon_per_kwh'] == 4380
#     assert results['nitrogen_oxide_per_kwh'] == 4380
#     assert results['sulpher_dioxide_per_kwh'] == 4380
#     assert results['pm10_per_kwh'] == 4380
