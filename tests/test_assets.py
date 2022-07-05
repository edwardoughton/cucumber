import pytest
import math
from cuba.assets import (
    estimate_assets,
    upgrade_site,
    greenfield_site,
    estimate_core_assets,
    get_backhaul_dist,
    regional_net_assets,
    core_net_assets,
    calc_assets,
    estimate_backhaul_type
)

def test_estimate_assets(setup_region, setup_costs,
    setup_global_parameters, setup_country_parameters,
    setup_core_lut):
    """
    Integration test.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['existing_mno_sites'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 0
    setup_region[0]['scenario'] = 'S1_50_50_50'
    setup_region[0]['strategy'] = '3G_epc_wireless_baseline_baseline_baseline_baseline'
    setup_region[0]['confidence'] = [50]

    results = estimate_assets(
        setup_region[0],
        {'scenario': '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline_baseline',
        'strategy': '3G_epc_wireless_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    # print(len(results))
    # for result in results:
    #     if result['asset'] == 'equipment':
    #         assert result['cost_per_unit'] == setup_costs['equipment']
    #     if result['asset'] == 'core_node':
    #         assert result['quantity'] == 2


def test_upgrade_site(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_estimated_sites'] = 1
    setup_region[0]['existing_mno_sites'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['scenario'] = 'S1_50_50_50'
    setup_region[0]['strategy'] = '3G_epc_wireless_baseline_baseline_baseline_baseline'
    setup_region[0]['confidence'] = [50]

    cost_structure = upgrade_site(setup_region[0],
        '4G_epc_wireless_baseline_baseline_baseline_baseline',
        setup_costs, setup_core_lut)

    assert cost_structure['equipment'] == 1
    assert cost_structure['installation'] == 1
    assert cost_structure['site_rental'] == 1
    assert cost_structure['operation_and_maintenance'] == 1
    assert cost_structure['backhaul'] == 250


def test_greenfield_site(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_estimated_sites'] = 1
    setup_region[0]['existing_mno_sites'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['scenario'] = 'S1_50_50_50'
    setup_region[0]['strategy'] = '3G_epc_wireless_baseline_baseline_baseline_baseline'
    setup_region[0]['confidence'] = [50]

    cost_structure = greenfield_site(setup_region[0],
        '4G_epc_wireless_baseline_baseline_baseline_baseline',
        setup_costs, setup_core_lut)

    assert cost_structure['equipment'] == 1
    assert cost_structure['site_build'] == 1
    assert cost_structure['installation'] == 1
    assert cost_structure['site_rental'] == 1
    assert cost_structure['operation_and_maintenance'] == 1
    assert cost_structure['backhaul'] == 250


def test_calc_assets(setup_region, setup_option, setup_costs):
    """
    Unit test.

    """
    setup_region[0]['scenario'] = 'test'
    setup_region[0]['strategy'] = 'test'
    setup_region[0]['confidence'] = 'test'

    asset_structure = {
        'backhaul': 2000,
    }

    assets = calc_assets(setup_region[0], setup_option, asset_structure, 1, 20,
        setup_costs, 'greenfield')

    assert assets[0]['asset'] == 'backhaul_wireless_small'
    assert assets[0]['cost_per_unit'] == 10000

    assets = calc_assets(setup_region[0], setup_option, asset_structure, 1, 0,
        setup_costs, 'brownfield')

    assert len(assets) == 0

    setup_option['strategy'] = '4G_epc_fiber_baseline_baseline_baseline_baseline_baseline_baseline'

    assets = calc_assets(setup_region[0], setup_option, asset_structure, 1, 20,
        setup_costs, 'brownfield')

    assert assets[0]['asset'] == 'backhaul_fiber_urban_m'
    assert assets[0]['cost_per_unit'] == 10
    assert assets[0]['total_cost'] == 20000


def test_estimate_core_assets(setup_region, setup_option, setup_costs,
    setup_core_lut):
    """
    Unit test.

    """
    setup_region[0]['all_new_or_upgraded_sites'] = 0
    setup_region[0]['scenario'] = 'S1_50_50_50'
    setup_region[0]['strategy'] = '3G_epc_wireless_baseline_baseline_baseline_baseline'
    setup_region[0]['confidence'] = [50]

    asset_types = [
        'core_edge',
        'core_node',
        'regional_edge',
        'regional_node',
    ]

    results = estimate_core_assets(setup_region[0], setup_option, setup_costs,
        setup_core_lut, setup_region[0]['all_new_or_upgraded_sites'])

    for asset_type in asset_types:
        for result in results:
            if asset_type == result['asset']:

                asset = result['asset']
                quantity = result['quantity']
                cost_per_unit = result['cost_per_unit']
                total_cost = result['total_cost']
                build_type = result['build_type']

                if not build_type == 'existing':
                    assert cost_per_unit == setup_costs[asset]
                    assert total_cost == setup_costs[asset] * quantity

    setup_option['strategy'] = '4G_epc_fiber_baseline_baseline_baseline_baseline_baseline_baseline'

    results = estimate_core_assets(setup_region[0], setup_option, setup_costs,
        setup_core_lut, setup_region[0]['all_new_or_upgraded_sites'])

    for result in results:
        if asset_type == result['asset']:

            asset = result['asset']
            quantity = result['quantity']
            cost_per_unit = result['cost_per_unit']
            total_cost = result['total_cost']

            if not build_type == 'existing':
                assert cost_per_unit == setup_costs[asset]
                assert total_cost == setup_costs[asset] * quantity

    for result in results:
        if result['asset'] == 'core_node':

            if result['build_type'] == 'new':
                assert result['quantity'] == 2
            if result['build_type'] == 'existing':
                assert result['quantity'] == 1

            assert total_cost == result['quantity'] * result['cost_per_unit']


def test_get_backhaul_dist(setup_region, setup_core_lut):

    assert get_backhaul_dist(setup_region[0], setup_core_lut) == 250

    assert get_backhaul_dist(setup_region[0], {}) == 1414


def test_regional_net_assets(setup_region, setup_core_lut):

    assert regional_net_assets(setup_region[0], 'regional_node', 'new', setup_core_lut) == 2

    assert regional_net_assets(setup_region[0], 'regional_edge', 'new', setup_core_lut) == 1000

    assert regional_net_assets(setup_region[0], '', 'new', setup_core_lut) == 0

    assert regional_net_assets(setup_region[0], 'regional_edge', '', setup_core_lut) == 0


def test_core_net_assets(setup_region, setup_core_lut):

    setup_region[0]['scenario'] = 'S1_50_50_50'
    setup_region[0]['strategy'] = '3G_epc_wireless_baseline_baseline_baseline_baseline'
    setup_region[0]['confidence'] = [50]

    assert core_net_assets(setup_region[0], 'core_node', 'new', setup_core_lut) == 2

    assert core_net_assets(setup_region[0], 'core_edge', 'new', setup_core_lut) == 1000

    assert core_net_assets(setup_region[0], '', 'new', setup_core_lut) == 0

    assert core_net_assets(setup_region[0], 'core_edge', '', setup_core_lut) == 0


def test_estimate_backhaul_type():

    assert estimate_backhaul_type('wireless', 10000, 'rural') == (1, 'wireless_small')

    assert estimate_backhaul_type('wireless', 20000, 'rural') == (1, 'wireless_medium')

    assert estimate_backhaul_type('wireless', 35000, 'rural') == (1, 'wireless_large')

    assert estimate_backhaul_type('wireless', 90000, 'rural') == (2, 'wireless_large')

    assert estimate_backhaul_type('fiber', 10000, 'rural') == (10000, 'fiber_rural_m')

    assert estimate_backhaul_type('', 10000, 'rural') == (0, 'Backhaul tech not recognized')
