import pytest
from cuba.emissions import assess_emissions


def test_assess_emissions(setup_data_energy, setup_tech_lut,
    setup_on_grid_mix, setup_timesteps, setup_option):
    """
    Unit test.

    """
    results = assess_emissions(setup_data_energy, setup_tech_lut,
        setup_on_grid_mix, setup_timesteps, setup_option)

    for result in results:

        if result['grid_type'] == 'on_grid':

            assert result['demand_carbon_per_kwh'] == 30
            assert result['nitrogen_oxide_per_kwh'] == 30
            assert result['sulpher_dioxide_per_kwh'] == 30
            assert result['pm10_per_kwh'] == 30

        if result['grid_type'] == 'off_grid':

            assert result['demand_carbon_per_kwh'] == 30
            assert result['nitrogen_oxide_per_kwh'] == 30
            assert result['sulpher_dioxide_per_kwh'] == 30
            assert result['pm10_per_kwh'] == 30

    setup_timesteps = [
        2020,
        2021
    ]

    results = assess_emissions(setup_data_energy, setup_tech_lut,
        setup_on_grid_mix, setup_timesteps, setup_option)

    total_carbon = []
    total_nitrogen = []
    total_sulphur = []
    total_pm10 = []

    for result in results:

        total_carbon.append(result['demand_carbon_per_kwh'])
        total_nitrogen.append(result['nitrogen_oxide_per_kwh'])
        total_sulphur.append(result['sulpher_dioxide_per_kwh'])
        total_pm10.append(result['pm10_per_kwh'])

        if result['grid_type'] == 'on_grid' and result['year'] == 2021:

            assert result['demand_carbon_per_kwh'] == 30
            assert result['nitrogen_oxide_per_kwh'] == 30
            assert result['sulpher_dioxide_per_kwh'] == 30
            assert result['pm10_per_kwh'] == 30

        if result['grid_type'] == 'off_grid' and result['year'] == 2021:

            assert result['demand_carbon_per_kwh'] == 30
            assert result['nitrogen_oxide_per_kwh'] == 30
            assert result['sulpher_dioxide_per_kwh'] == 30
            assert result['pm10_per_kwh'] == 30

    assert sum(total_carbon) == 30 * 6
    assert sum(total_nitrogen) == 30 * 6
    assert sum(total_sulphur) == 30 * 6
    assert sum(total_pm10) == 30 * 6

    new_energy_data = []

    for item in setup_data_energy:
        item['strategy'] = '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline_renewable'
        interim = []
        interim.append(item)
        new_energy_data = new_energy_data + interim

    results = assess_emissions(new_energy_data, setup_tech_lut,
        setup_on_grid_mix, [2020], setup_option)

    for result in results:

        if result['grid_type'] == 'on_grid':

            assert result['demand_carbon_per_kwh'] == 30
            assert result['nitrogen_oxide_per_kwh'] == 30
            assert result['sulpher_dioxide_per_kwh'] == 30
            assert result['pm10_per_kwh'] == 30

        if result['grid_type'] == 'grid_other':

            assert result['demand_carbon_per_kwh'] == 60
            assert result['nitrogen_oxide_per_kwh'] == 60
            assert result['sulpher_dioxide_per_kwh'] == 60
            assert result['pm10_per_kwh'] == 60
