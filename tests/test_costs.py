import pytest
import math
from cucumber.costs import assess_cost


def test_assess_cost(setup_country, setup_deciles):
    """
    Integration test.

    """
    #baseline sharing
    setup_deciles[0]['population_with_smartphones'] = 4000
    setup_deciles[0]['smartphones_on_network'] = 1000
    setup_deciles[0]['network_new_sites'] = 1
    setup_deciles[0]['networks'] = 4
    setup_deciles[0]['sharing_scenario'] = 'baseline'

    answer = assess_cost(
        setup_country,
        [setup_deciles[0]],
    )

    assert answer[0]['network_cost_equipment_usd'] == 40000
    assert answer[0]['network_cost_site_build_usd'] == 30000
    assert answer[0]['network_cost_installation_usd'] == 30000
    assert answer[0]['network_cost_operation_and_maintenance_usd'] == 7400
    assert answer[0]['network_cost_power_usd'] == 3000
    assert answer[0]['network_new_cost_usd'] == 110400

    assert answer[0]['total_cost_equipment_usd'] == 40000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_site_build_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_installation_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_operation_and_maintenance_usd'] == 7400 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_power_usd'] == 3000 * setup_deciles[0]['networks']
    assert answer[0]['total_new_cost_usd'] == 110400 * setup_deciles[0]['networks']

    #baseline sharing
    setup_deciles[0]['network_new_sites'] = 0
    setup_deciles[0]['sharing_scenario'] = 'baseline'

    answer = assess_cost(
        setup_country,
        [setup_deciles[0]],
    )

    assert answer[0]['network_cost_equipment_usd'] == 0
    assert answer[0]['network_cost_site_build_usd'] == 0
    assert answer[0]['network_cost_installation_usd'] == 0
    assert answer[0]['network_cost_operation_and_maintenance_usd'] == 0
    assert answer[0]['network_cost_power_usd'] == 0
    assert answer[0]['network_new_cost_usd'] == 0

    assert answer[0]['total_cost_equipment_usd'] == 0
    assert answer[0]['total_cost_site_build_usd'] == 0
    assert answer[0]['total_cost_installation_usd'] == 0
    assert answer[0]['total_cost_operation_and_maintenance_usd'] == 0
    assert answer[0]['total_cost_power_usd'] == 0
    assert answer[0]['total_new_cost_usd'] == 0

    #passive sharing
    setup_deciles[0]['population_with_smartphones'] = 4000
    setup_deciles[0]['smartphones_on_network'] = 1000
    setup_deciles[0]['network_new_sites'] = 1
    setup_deciles[0]['networks'] = 4
    setup_deciles[0]['sharing_scenario'] = 'passive'

    answer = assess_cost(
        setup_country,
        [setup_deciles[0]],
    )

    assert answer[0]['network_cost_equipment_usd'] == 40000
    assert answer[0]['network_cost_site_build_usd'] == 30000
    assert answer[0]['network_cost_installation_usd'] == 30000
    assert answer[0]['network_cost_operation_and_maintenance_usd'] == 7400
    assert answer[0]['network_cost_power_usd'] == 3000
    assert answer[0]['network_new_cost_usd'] == 110400

    assert answer[0]['total_cost_equipment_usd'] == 40000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_site_build_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_installation_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_operation_and_maintenance_usd'] == 7400 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_power_usd'] == 3000 * setup_deciles[0]['networks']
    assert answer[0]['total_new_cost_usd'] == 110400 * setup_deciles[0]['networks']

    #active sharing
    setup_deciles[0]['population_with_smartphones'] = 4000
    setup_deciles[0]['smartphones_on_network'] = 1000
    setup_deciles[0]['network_new_sites'] = 1
    setup_deciles[0]['networks'] = 1
    setup_deciles[0]['sharing_scenario'] = 'active'

    answer = assess_cost(
        setup_country,
        [setup_deciles[0]],
    )

    assert answer[0]['network_cost_equipment_usd'] == 40000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_site_build_usd'] == 30000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_installation_usd'] == 30000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_operation_and_maintenance_usd'] == 7400 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_power_usd'] == 3000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_new_cost_usd'] == 110400 * (setup_deciles[0]['networks'] / 4)

    assert answer[0]['total_cost_equipment_usd'] == 40000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_site_build_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_installation_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_operation_and_maintenance_usd'] == 7400 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_power_usd'] == 3000 * setup_deciles[0]['networks']
    assert answer[0]['total_new_cost_usd'] == 110400 * setup_deciles[0]['networks']

    #srn sharing
    setup_deciles[0]['population_with_smartphones'] = 4000
    setup_deciles[0]['smartphones_on_network'] = 1000
    setup_deciles[0]['network_new_sites'] = 1
    setup_deciles[0]['geotype'] = 'urban'
    setup_deciles[0]['networks'] = 4
    setup_deciles[0]['sharing_scenario'] = 'srn'

    answer = assess_cost(
        setup_country,
        [setup_deciles[0]],
    )

    assert answer[0]['network_cost_equipment_usd'] == 40000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_site_build_usd'] == 30000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_installation_usd'] == 30000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_operation_and_maintenance_usd'] == 7400 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_power_usd'] == 3000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_new_cost_usd'] == 110400 * (setup_deciles[0]['networks'] / 4)

    assert answer[0]['total_cost_equipment_usd'] == 40000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_site_build_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_installation_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_operation_and_maintenance_usd'] == 7400 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_power_usd'] == 3000 * setup_deciles[0]['networks']
    assert answer[0]['total_new_cost_usd'] == 110400 * setup_deciles[0]['networks']

    #srn sharing
    setup_deciles[0]['population_with_smartphones'] = 4000
    setup_deciles[0]['smartphones_on_network'] = 1000
    setup_deciles[0]['network_new_sites'] = 1
    setup_deciles[0]['geotype'] = 'rural'
    setup_deciles[0]['networks'] = 1
    setup_deciles[0]['sharing_scenario'] = 'srn'

    answer = assess_cost(
        setup_country,
        [setup_deciles[0]],
    )

    assert answer[0]['network_cost_equipment_usd'] == 40000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_site_build_usd'] == 30000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_installation_usd'] == 30000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_operation_and_maintenance_usd'] == 7400 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_cost_power_usd'] == 3000 * (setup_deciles[0]['networks'] / 4)
    assert answer[0]['network_new_cost_usd'] == 110400 * (setup_deciles[0]['networks'] / 4)

    assert answer[0]['total_cost_equipment_usd'] == 40000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_site_build_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_installation_usd'] == 30000 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_operation_and_maintenance_usd'] == 7400 * setup_deciles[0]['networks']
    assert answer[0]['total_cost_power_usd'] == 3000 * setup_deciles[0]['networks']
    assert answer[0]['total_new_cost_usd'] == 110400 * setup_deciles[0]['networks']