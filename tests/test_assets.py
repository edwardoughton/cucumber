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

    for result in results:

        if result['asset'] == 'equipment':
            assert result['cost_per_unit'] == setup_costs['equipment']
        if result['asset'] == 'core_node':
            assert result['quantity'] == 2


def test_upgrade_site(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_estimated_sites'] = 1
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


def test_estimate_core_assets(setup_region, setup_option, setup_costs,
    setup_core_lut):
    """
    Unit test.

    """
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
        setup_core_lut)

    for asset_type in asset_types:
        for result in results:
            if asset_type == result['asset']:

                asset = result['asset']
                quantity = result['quantity']
                cost_per_unit = result['cost_per_unit']
                total_cost = result['total_cost']

                assert cost_per_unit == setup_costs[asset]
                assert total_cost == setup_costs[asset] * quantity

    setup_option['strategy'] = '4G_epc_fiber_baseline_baseline_baseline_baseline_baseline_baseline'

    results = estimate_core_assets(setup_region[0], setup_option, setup_costs,
        setup_core_lut)

    for result in results:
        if asset_type == result['asset']:

            asset = result['asset']
            quantity = result['quantity']
            cost_per_unit = result['cost_per_unit']
            total_cost = result['total_cost']

            assert cost_per_unit == setup_costs[asset]
            assert total_cost == setup_costs[asset] * quantity

    for result in results:
        if result['asset'] == 'core_node':

            if result['build_type'] == 'new':
                assert result['quantity'] == 2
            if result['build_type'] == 'existing':
                assert result['quantity'] == 2

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


# def test_calc_assets():


def test_estimate_backhaul_type():

    assert estimate_backhaul_type('wireless', 10000, 'rural') == (1, 'wireless_small')

    assert estimate_backhaul_type('wireless', 20000, 'rural') == (1, 'wireless_medium')

    assert estimate_backhaul_type('wireless', 35000, 'rural') == (1, 'wireless_large')

    assert estimate_backhaul_type('wireless', 90000, 'rural') == (2, 'wireless_large')

    assert estimate_backhaul_type('fiber', 10000, 'rural') == (10000, 'fiber_rural_m')

    assert estimate_backhaul_type('', 10000, 'rural') == (0, 'Backhaul tech not recognized')



# # #test approach is to:
# # #test each function which returns the cost structure
# # #test the function which calculates quantities
# # #test infrastructure sharing strategies
# # #test meta cost function
# # def estimate_assets(setup_region, setup_costs,
# #     setup_global_parameters, setup_country_parameters,
# #     setup_core_lut):
# #     """
# #     Integration test.

# #     """
# #     setup_region[0]['sites_4G'] = 0
# #     setup_region[0]['new_mno_sites'] = 1
# #     setup_region[0]['upgraded_mno_sites'] = 0
# #     setup_region[0]['site_density'] = 0.5
# #     setup_region[0]['backhaul_new'] = 0

# #     answer = find_network_cost(
# #         setup_region[0],
# #         {'strategy': '3G_epc_wireless_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_core_lut
# #     )

# #     assert answer['network_cost'] == 460504.85

# #     setup_region[0]['sites_4G'] = 0
# #     setup_region[0]['new_mno_sites'] = 1
# #     setup_region[0]['upgraded_mno_sites'] = 1
# #     setup_region[0]['site_density'] = 0.5
# #     setup_region[0]['backhaul_new'] = 1

# #     answer = find_network_cost(
# #         setup_region[0],
# #         {'strategy': '3G_epc_wireless_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_core_lut
# #     )

# #     assert answer['network_cost'] == 597858.5499999999

# #     setup_region[0]['sites_4G'] = 0
# #     setup_region[0]['new_mno_sites'] = 1
# #     setup_region[0]['upgraded_mno_sites'] = 1
# #     setup_region[0]['site_density'] = 0.5
# #     setup_region[0]['backhaul_new'] = 2

# #     answer = find_network_cost(
# #         setup_region[0],
# #         {'strategy': '3G_epc_wireless_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_core_lut
# #     )

# #     assert answer['network_cost'] == 611603.35

# #     answer = find_network_cost(
# #         setup_region[0],
# #         {'strategy': '4G_epc_wireless_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_core_lut
# #     )

# #     assert answer['network_cost'] == 611603.35

# #     setup_region[0]['new_mno_sites'] = 0
# #     setup_region[0]['upgraded_mno_sites'] = 1
# #     setup_region[0]['site_density'] = 0.5
# #     setup_region[0]['backhaul_new'] = 0

# #     answer = find_network_cost(
# #         setup_region[0],
# #         {'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_core_lut
# #     )

# #     assert answer['network_cost'] == 705490.4999999999

# #     setup_region[0]['new_mno_sites'] = 0
# #     setup_region[0]['upgraded_mno_sites'] = 1
# #     setup_region[0]['site_density'] = 0.5
# #     setup_region[0]['backhaul_new'] = 1

# #     answer = find_network_cost(
# #         setup_region[0],
# #         {'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_core_lut
# #     )

# #     assert answer['network_cost'] == 708926.6999999998

# #     setup_region[0]['new_mno_sites'] = 1
# #     setup_region[0]['upgraded_mno_sites'] = 1
# #     setup_region[0]['site_density'] = 0.5
# #     setup_region[0]['backhaul_new'] = 2

# #     answer = find_network_cost(
# #         setup_region[0],
# #         {'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_core_lut
# #     )

# #     assert answer['network_cost'] == 875055.6999999998

# #     answer = find_network_cost(
# #         setup_region[0],
# #         {'strategy': '4G_epc_fiber_srn_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_core_lut
# #     )

# #     assert answer['network_cost'] == 875055.6999999998

# #     setup_region[0]['geotype'] = 'rural'

# #     answer = find_network_cost(
# #         setup_region[0],
# #         {'strategy': '4G_epc_fiber_srn_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_core_lut
# #     )

# #     assert answer['network_cost'] == 669457.1666666665



# # def test_core_costs(setup_region, setup_option, setup_costs, setup_core_lut, setup_country_parameters):
# #     """
# #     Unit test.

# #     """
# #     setup_region[0]['upgraded_mno_sites'] = 1
# #     setup_region[0]['new_mno_sites'] = 1
# #     setup_region[0]['total_estimated_sites'] = 2
# #     setup_country_parameters['networks']['baseline_urban'] = 2

# #     assert core_costs(setup_region[0], 'core_edge', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == (setup_costs['core_edge'] * 1000)

# #     assert core_costs(setup_region[0], 'core_node', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == (setup_costs['core_node'] * 2)

# #     assert core_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

# #     setup_region[0]['GID_id'] == 'unknown'

# #     assert core_costs(setup_region[0], 'core_edge', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
# #             (setup_costs['core_edge'] * setup_core_lut['core_edge']['MWI.1.1.1_1_new']) /
# #             (setup_region[0]['total_estimated_sites'] /
# #             (setup_country_parameters['networks']['baseline_urban'])))

# #     #test that no sites returns zero cost
# #     setup_region[0]['upgraded_mno_sites'] = 0
# #     setup_region[0]['new_mno_sites'] = 0

# #     assert core_costs(setup_region[0], 'core_edge', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

# #     assert core_costs(setup_region[0], 'core_node', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

# #     assert core_costs(setup_region[0], 'core_edge', setup_costs,
# #         {}, setup_option['strategy'], setup_country_parameters) == 0

# #     assert core_costs(setup_region[0], 'core_node', setup_costs,
# #         {}, setup_option['strategy'], setup_country_parameters) == 0



#     # cost_structure = upgrade_existing_site(setup_region[0],
#     #     '4g_epc_wireless_passive_baseline_baseline_baseline',
#     #     setup_costs, setup_global_parameters,
#     #     setup_core_lut, setup_country_parameters)

#     # assert cost_structure['site_rental'] == (
#     #     setup_costs['site_rental_urban'] /
#     #     setup_country_parameters['networks']['baseline_urban']
#     #     )
#     # assert cost_structure['backhaul'] == (
#     #     setup_costs['wireless_small'] /
#     #     setup_country_parameters['networks']['baseline_urban']
#     #     )

#     # cost_structure = upgrade_existing_site(setup_region[0],
#     #     '4g_epc_wireless_active_baseline_baseline_baseline',
#     #     setup_costs, setup_global_parameters,
#     #     setup_core_lut, setup_country_parameters)

#     # assert cost_structure['equipment'] == (
#     #     setup_costs['equipment'] /
#     #     setup_country_parameters['networks']['baseline_urban']
#     #     )

#     # cost_structure = upgrade_existing_site(setup_region[0],
#     #     '4G_epc_wireless_srn_baseline_baseline_baseline',
#     #     setup_costs, setup_global_parameters,
#     #     setup_core_lut, setup_country_parameters)

#     # setup_region[0]['geotype'] = 'rural'

#     # cost_structure = upgrade_existing_site(setup_region[0],
#     #     '4G_epc_wireless_srn_baseline_baseline_baseline',
#     #     setup_costs, setup_global_parameters,
#     #     setup_core_lut, setup_country_parameters)

#     # assert round(cost_structure['equipment']) == round(
#     #     setup_costs['equipment'] * (
#     #     1 /
#     #     setup_country_parameters['networks']['baseline_rural']
#     #     )
#     #     )
#     # assert round(cost_structure['operation_and_maintenance']) == round(
#     #     setup_costs['operation_and_maintenance'] * (
#     #     1 /
#     #     setup_country_parameters['networks']['baseline_rural']
#     #     ))
#     # assert round(cost_structure['core_edge']) == round(
#     #     (setup_costs['core_edge'] * 1000)
#     #     )

#     # setup_region[0]['geotype'] = 'urban'

#     # cost_structure = upgrade_existing_site(setup_region[0],
#     #     '4G_epc_wireless_srn_baseline_baseline_baseline',
#     #     setup_costs, setup_global_parameters,
#     #     setup_core_lut, setup_country_parameters)

#     # assert round(cost_structure['equipment']) == round(
#     #     setup_costs['equipment'] #* (
#     #     # 1 /setup_country_parameters['networks']['baseline_rural'])
#     #     )
#     # assert cost_structure['core_edge'] == (
#     #     (setup_costs['core_edge'] * 1000))



# # def test_backhaul_quantity():
# #     """
# #     Unit test.

# #     """
# #     assert backhaul_quantity(2, 1) == 0


# # def test_get_backhaul_costs(setup_region, setup_costs, setup_core_lut, setup_empty_core_lut):
# #     """
# #     Unit test.

# #     """
# #     assert get_backhaul_costs(setup_region[0], 'wireless',
# #         setup_costs, setup_core_lut) == (setup_costs['wireless_small'])

# #     setup_region[0]['area_km2'] = 5000

# #     assert get_backhaul_costs(setup_region[0], 'wireless',
# #         setup_costs, setup_core_lut) == (setup_costs['wireless_small'])

# #     setup_region[0]['area_km2'] = 20000

# #     assert get_backhaul_costs(setup_region[0], 'wireless',
# #         setup_costs, setup_core_lut) == (setup_costs['wireless_medium'])

# #     setup_region[0]['area_km2'] = 100000

# #     assert get_backhaul_costs(setup_region[0], 'wireless',
# #         setup_costs, setup_core_lut) == (setup_costs['wireless_large'] * (55901.69943749474 / 30000))

# #     setup_region[0]['area_km2'] = 2

# #     assert get_backhaul_costs(setup_region[0], 'fiber',
# #         setup_costs, setup_core_lut) == (setup_costs['fiber_urban_m'] * 250)

# #     assert get_backhaul_costs(setup_region[0], 'incorrect_backhaul_tech_name',
# #         setup_costs, setup_core_lut) == 0

# #     assert get_backhaul_costs(setup_region[0], 'fiber',
# #         setup_costs, setup_empty_core_lut) == 14140


# # def test_regional_net_costs(setup_region, setup_option, setup_costs, setup_core_lut,
# #     setup_country_parameters):
# #     """
# #     Unit test.

# #     """
# #     setup_region[0]['total_estimated_sites'] = 6
# #     setup_region[0]['upgraded_mno_sites'] = 0
# #     setup_region[0]['new_mno_sites'] = 6

# #     assert regional_net_costs(setup_region[0], 'regional_edge', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
# #             (setup_costs['regional_edge'] * setup_core_lut['regional_edge']['MWI.1.1.1_1_new']) /
# #             (setup_region[0]['total_estimated_sites'] /
# #             (setup_country_parameters['networks']['baseline_urban'])))

# #     assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
# #             (setup_costs['regional_node'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
# #             (setup_region[0]['total_estimated_sites'] /
# #             (setup_country_parameters['networks']['baseline_urban'])))

# #     setup_region[0]['total_estimated_sites'] = 10
# #     setup_region[0]['new_mno_sites'] = 10

# #     assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
# #             (setup_costs['regional_node'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
# #             (setup_region[0]['total_estimated_sites'] /
# #             (setup_country_parameters['networks']['baseline_urban'])))

# #     setup_core_lut['regional_node']['MWI.1.1.1_1'] = 10
# #     setup_region[0]['area_km2'] = 100

# #     assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
# #             (setup_costs['regional_node'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
# #             (setup_region[0]['total_estimated_sites'] /
# #             (setup_country_parameters['networks']['baseline_urban'])))

# #     assert regional_net_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == 'Asset name not in lut'

# #     setup_region[0]['total_estimated_sites'] = 0
# #     setup_region[0]['new_mno_sites'] = 0

# #     assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

# #     setup_region[0]['GID_id'] = 'unknown GID ID'

# #     assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

# #     #test that no sites returns zero cost
# #     setup_region[0]['total_estimated_sites'] = 0

# #     assert regional_net_costs(setup_region[0], 'regional_edge', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

# #     #test asset name not being in the LUT
# #     assert regional_net_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
# #         setup_core_lut, setup_option['strategy'], setup_country_parameters) == 'Asset name not in lut'



# # def test_calc_costs(setup_region, setup_global_parameters, setup_country_parameters):
# #     """
# #     Unit test.

# #     """
# #     setup_region[0]['sites_4G'] = 0
# #     setup_region[0]['upgraded_mno_sites'] = 1
# #     setup_region[0]['new_mno_sites'] = 1

# #     answer, structure = calc_costs(
# #         setup_region[0],
# #         '4G_epc_wireless_cns_baseline_baseline_baseline_baseline',
# #         {'equipment': 40000},
# #         1,
# #         setup_global_parameters,
# #         setup_country_parameters
# #     )

# #     assert answer == 40000 * (1 + (setup_country_parameters['financials']['wacc'] / 100))

# #     answer, structure = calc_costs(
# #         setup_region[0],
# #         '4G_epc_wireless_cns_baseline_baseline_baseline_baseline',
# #         {'site_rental': 9600},
# #         1,
# #         setup_global_parameters,
# #         setup_country_parameters
# #     )

# #     assert answer == 18743 *  (1 + (setup_country_parameters['financials']['wacc'] / 100))#two years' of rent

# #     answer, structure = calc_costs(setup_region[0],
# #         '4G_epc_wireless_cns_baseline_baseline_baseline_baseline',
# #         {
# #         'equipment': 40000,
# #         'site_rental': 9600,
# #         },
# #         6,
# #         setup_global_parameters,
# #         setup_country_parameters)

# #     #answer = sum of equipment + site_rental
# #     assert answer == (
# #         40000 * (1 + (setup_country_parameters['financials']['wacc'] / 100)) +
# #         18743 *  (1 + (setup_country_parameters['financials']['wacc'] / 100))
# #         )

# #     answer, structure = calc_costs(setup_region[0],
# #         '4G_epc_wireless_cns_baseline_baseline_baseline_baseline',
# #         {
# #         'incorrect_name': 9600,
# #         },
# #         6,
# #         setup_global_parameters,
# #         setup_country_parameters)

# #     assert answer == 0 #two years' of rent


# # def test_discount_capex_and_opex(setup_global_parameters, setup_country_parameters):
# #     """
# #     Unit test.

# #     """
# #     assert discount_capex_and_opex(1000, setup_global_parameters, setup_country_parameters) == (
# #         1195 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))


# # def test_discount_opex(setup_global_parameters, setup_country_parameters):
# #     """
# #     Unit test.

# #     """
# #     assert discount_opex(1000, setup_global_parameters, setup_country_parameters) == (
# #         1952 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))
