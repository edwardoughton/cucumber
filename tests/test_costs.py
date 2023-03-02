import pytest
import math
from cuba.costs import (
    find_cost,
    calc_sharing,
    calc_npv,
    aggregate_costs,
    discount_capex_and_opex,
    discount_opex
)


def test_find_cost(setup_region, setup_costs,
    setup_global_parameters, setup_country_parameters,
    setup_core_lut, setup_infra_sharing_assets,
    setup_cost_types, setup_assets):
    """
    Integration test.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['site_density'] = 0.5

    answer = find_cost(
        setup_region[0],
        setup_assets,
        {'strategy': '3G_epc_wireless_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_infra_sharing_assets,
        setup_cost_types
    )

    assert answer['network_cost'] == 61990.75 #no sharing

    answer = find_cost(
        setup_region[0],
        setup_assets,
        {'strategy': '3G_epc_wireless_passive_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_infra_sharing_assets,
        setup_cost_types
    )

    assert round(answer['network_cost']) == 28331 #share only passive

    answer = find_cost(
        setup_region[0],
        setup_assets,
        {'strategy': '3G_epc_wireless_active_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_infra_sharing_assets,
        setup_cost_types
    )

    assert round(answer['network_cost']) == 20664 #share all passive + active

    answer = find_cost(
        setup_region[0],
        setup_assets,
        {'strategy': '3G_epc_wireless_srn_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_infra_sharing_assets,
        setup_cost_types
    )

    assert round(answer['network_cost']) == 61991 #urban, therefore no sharing

    setup_region[0]['geotype'] = 'rural'

    answer = find_cost(
        setup_region[0],
        setup_assets,
        {'strategy': '3G_epc_wireless_srn_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_infra_sharing_assets,
        setup_cost_types
    )

    assert round(answer['network_cost']) == 20664


def test_calc_sharing(setup_assets, setup_region, setup_option,
    setup_global_parameters, setup_country_parameters,
    setup_infra_sharing_assets):
    """
    Unit test.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1

    answer = calc_sharing(
        setup_assets,
        setup_region[0],
        setup_option,
        setup_country_parameters,
        setup_infra_sharing_assets
    )

    assert answer['equipment'] == 10000

    answer = calc_sharing(
        setup_assets,
        setup_region[0],
        {'strategy': '3G_epc_wireless_passive_baseline_baseline_baseline'},
        setup_country_parameters,
        setup_infra_sharing_assets
    )

    assert round(answer['site_build']) == 3333

    answer = calc_sharing(
        setup_assets,
        setup_region[0],
        {'strategy': '3G_epc_wireless_active_baseline_baseline_baseline'},
        setup_country_parameters,
        setup_infra_sharing_assets
    )

    assert round(answer['equipment']) == 3333

    answer = calc_sharing(
        setup_assets,
        setup_region[0],
        {'strategy': '3G_epc_wireless_srn_baseline_baseline_baseline'},
        setup_country_parameters,
        setup_infra_sharing_assets
    )

    assert round(answer['equipment']) == 10000

    setup_region[0]['geotype'] = 'rural'

    answer = calc_sharing(
        setup_assets,
        setup_region[0],
        {'strategy': '3G_epc_wireless_srn_baseline_baseline_baseline'},
        setup_country_parameters,
        setup_infra_sharing_assets
    )

    assert round(answer['equipment']) == 3333


def test_calc_npv(setup_assets_dict, setup_cost_types, setup_global_parameters,
    setup_country_parameters):
    """
    Unit test.

    """
    answer = calc_npv(setup_assets_dict, setup_cost_types, setup_global_parameters,
        setup_country_parameters)

    assert answer['equipment'] == 11500 #capex and opex
    assert answer['operation_and_maintenance'] == 22452.6 #opex
    assert answer['site_build'] == 11500 #capex


def test_aggregate_costs():
    """
    Unit test.

    """
    cost_by_assets = {
        'equipment': 1,
        'site_rental': 1,
        'operation_and_maintenance': 1,
        'power': 1,
        'backhaul_wireless_small':1,
        'site_build': 1,
        'installation': 1,
        'regional_node': 1,
        'regional_edge': 1,
        'core_node': 1,
        'core_edge': 1,

    }

    answer = aggregate_costs(cost_by_assets)

    assert answer['ran'] == 4
    assert answer['backhaul_fronthaul'] == 1
    assert answer['civils'] == 2
    assert answer['core_network'] == 4


def test_discount_capex_and_opex(setup_global_parameters, setup_country_parameters):
    """
    Unit test.

    """
    assert discount_capex_and_opex(1000, setup_global_parameters, setup_country_parameters) == (
        1195 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))


def test_discount_opex(setup_global_parameters, setup_country_parameters):
    """
    Unit test.

    """
    assert discount_opex(1000, setup_global_parameters, setup_country_parameters) == (
        1952 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))
