import pytest
from cuba.emissions import assess_emissions


def test_assess_emissions(setup_data_energy, setup_tech_lut,
    setup_on_grid_mix, setup_timesteps, setup_option, setup_country_parameters):
    """
    Unit test.

    """
    results = assess_emissions(setup_data_energy, setup_tech_lut,
        setup_on_grid_mix, setup_timesteps, setup_option, setup_country_parameters)

    for result in results:

        if result['grid_type'] == 'on_grid':
            print(result)
            assert result['mno_demand_carbon_tonnes'] == 30 / 1e3
            assert result['mno_nitrogen_oxide_tonnes'] == 30 / 1e3
            assert result['mno_sulpher_dioxide_tonnes'] == 30 / 1e3
            assert result['mno_pm10_tonnes'] == 30 / 1e3

            # e.g. (30 kg CO2/kwh / 75 phones on network) * 100 total phones users
            assert result['total_demand_carbon_tonnes'] == (30 / 75) * 100 / 1e3
            assert result['total_nitrogen_oxide_tonnes'] == (30 / 75) * 100 / 1e3
            assert result['total_sulpher_dioxide_tonnes'] == (30 / 75) * 100 / 1e3
            assert result['total_pm10_tonnes'] == (30 / 75) * 100 / 1e3

        if result['grid_type'] == 'off_grid':

            assert result['mno_demand_carbon_tonnes'] == 30 / 1e3
            assert result['mno_nitrogen_oxide_tonnes'] == 30 / 1e3
            assert result['mno_sulpher_dioxide_tonnes'] == 30 / 1e3
            assert result['mno_pm10_tonnes'] == 30 / 1e3

            # e.g. (30 kg CO2/kwh / 75 phones on network) * 100 total phones users
            assert result['total_demand_carbon_tonnes'] == (30 / 75) * 100 / 1e3
            assert result['total_nitrogen_oxide_tonnes'] == (30 / 75) * 100 / 1e3
            assert result['total_sulpher_dioxide_tonnes'] == (30 / 75) * 100 / 1e3
            assert result['total_pm10_tonnes'] == (30 / 75) * 100 / 1e3

    setup_timesteps = [
        2020,
        2021
    ]

    results = assess_emissions(setup_data_energy, setup_tech_lut,
        setup_on_grid_mix, setup_timesteps, setup_option, setup_country_parameters)

    total_carbon = []
    total_nitrogen = []
    total_sulphur = []
    total_pm10 = []

    for result in results:

        total_carbon.append(result['mno_demand_carbon_tonnes'])
        total_nitrogen.append(result['mno_nitrogen_oxide_tonnes'])
        total_sulphur.append(result['mno_sulpher_dioxide_tonnes'])
        total_pm10.append(result['mno_pm10_tonnes'])

        if result['grid_type'] == 'on_grid' and result['year'] == 2021:

            assert result['mno_demand_carbon_tonnes'] == 30 / 1e3
            assert result['mno_nitrogen_oxide_tonnes'] == 30 / 1e3
            assert result['mno_sulpher_dioxide_tonnes'] == 30 / 1e3
            assert result['mno_pm10_tonnes'] == 30 / 1e3

        if result['grid_type'] == 'off_grid' and result['year'] == 2021:

            assert result['mno_demand_carbon_tonnes'] == 30 / 1e3
            assert result['mno_nitrogen_oxide_tonnes'] == 30 / 1e3
            assert result['mno_sulpher_dioxide_tonnes'] == 30 / 1e3
            assert result['mno_pm10_tonnes'] == 30 / 1e3

    assert sum(total_carbon) == 30 * 6 / 1e3
    assert sum(total_nitrogen) == 30 * 6 / 1e3
    assert sum(total_sulphur) == 30 * 6 / 1e3
    assert sum(total_pm10) == 30 * 6 / 1e3

    new_energy_data = []

    for item in setup_data_energy:
        item['strategy'] = '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline_renewable'
        interim = []
        interim.append(item)
        new_energy_data = new_energy_data + interim

    results = assess_emissions(new_energy_data, setup_tech_lut,
        setup_on_grid_mix, [2020], setup_option, setup_country_parameters)

    for result in results:

        if result['grid_type'] == 'on_grid':

            assert result['mno_demand_carbon_tonnes'] == 30 / 1e3
            assert result['mno_nitrogen_oxide_tonnes'] == 30 / 1e3
            assert result['mno_sulpher_dioxide_tonnes'] == 30 / 1e3
            assert result['mno_pm10_tonnes'] == 30 / 1e3

        if result['grid_type'] == 'grid_other':

            assert result['mno_demand_carbon_tonnes'] == 60 / 1e3
            assert result['mno_nitrogen_oxide_tonnes'] == 60 / 1e3
            assert result['mno_sulpher_dioxide_tonnes'] == 60 / 1e3
            assert result['mno_pm10_tonnes'] == 60 / 1e3

        if result['grid_type'] == 'on_grid':

            # e.g. (30 kwh / 75 phones on network) * 100 total phones users
            assert result['total_demand_carbon_tonnes'] == (30 / 75) * 100 / 1e3
            assert result['total_nitrogen_oxide_tonnes'] == (30 / 75) * 100 / 1e3
            assert result['total_sulpher_dioxide_tonnes'] == (30 / 75) * 100 / 1e3
            assert result['total_pm10_tonnes'] == (30 / 75) * 100 / 1e3

        if result['grid_type'] == 'grid_other':

            assert result['total_demand_carbon_tonnes'] == (60 / 75) * 100 / 1e3
            assert result['total_nitrogen_oxide_tonnes'] == (60 / 75) * 100 / 1e3
            assert result['total_sulpher_dioxide_tonnes'] == (60 / 75) * 100 / 1e3
            assert result['total_pm10_tonnes'] == (60 / 75) * 100 / 1e3
