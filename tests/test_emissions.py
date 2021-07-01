import pytest
from cuba.emissions import assess_emissions


def test_assess_emissions(setup_data_energy, setup_tech_lut, setup_on_grid_mix):
    """
    Unit test.

    """

    results = assess_emissions(setup_data_energy, setup_tech_lut, setup_on_grid_mix)

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
