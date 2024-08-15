import pytest
import math
from cucumber.costs import assess_cost


def test_assess_cost(setup_country, setup_deciles):
    """
    Integration test.

    """
    setup_deciles[0]['total_new_sites'] = 1

    answer = assess_cost(
        setup_country,
        [setup_deciles[0]],
    )

    assert answer[0]['cost_equipment_usd'] == 40000
    assert answer[0]['cost_site_build_usd'] == 30000
    assert answer[0]['cost_installation_usd'] == 30000
    assert answer[0]['cost_operation_and_maintenance_usd'] == 7400
    assert answer[0]['cost_power_usd'] == 3000
    assert answer[0]['total_new_cost_usd'] == 110400


    setup_deciles[0]['total_new_sites'] = 0

    answer = assess_cost(
        setup_country,
        [setup_deciles[0]],
    )

    assert answer[0]['cost_equipment_usd'] == 0
    assert answer[0]['cost_site_build_usd'] == 0
    assert answer[0]['cost_installation_usd'] == 0
    assert answer[0]['cost_operation_and_maintenance_usd'] == 0
    assert answer[0]['cost_power_usd'] == 0
    assert answer[0]['total_new_cost_usd'] == 0

