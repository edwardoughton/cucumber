import pytest
from cuba.demand import (estimate_demand, get_per_user_capacity,
    estimate_arpu, discount_arpu)


def test_estimate_demand(
    setup_region,
    setup_region_rural,
    setup_option,
    setup_option_high,
    setup_global_parameters,
    setup_country_parameters,
    setup_timesteps,
    setup_penetration_lut
    ):
    """
    Integration test.

    """
    answer, annual_answer = estimate_demand(
        {'income': 'HIC'},
        setup_country_parameters,
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_timesteps,
        setup_penetration_lut,
        {'urban': {2020: 50}}
    )

    # pop = 10000
    # pen = 50%
    # = 5000 phones
    assert answer[0]['population_with_phones'] == 5000

    # 5000 phones
    # 3 networks
    # = 1667 phones
    assert round(answer[0]['phones_on_network']) == round(5000 / 3)

    # 5000 phones
    # 3 networks
    # 50% smartphones
    # = 833 smartphones
    smartphones_on_network = round(5000 / 3 * (50 / 100))
    assert round(answer[0]['smartphones_on_network']) == smartphones_on_network

    # 1667 phones
    # arpu = 15
    assert round(answer[0]['total_mno_revenue']) == round(15 * 5000 * 12 / 3)

    # 1667 phones
    # arpu = 15
    # area = 2
    assert round(answer[0]['revenue_km2']) == round((15 * 5000 * 12 / 3) / 2)

    # 833 smartphones
    # scenario = 0.56
    # area = 2

    assert round(answer[0]['demand_mbps_km2']) == round(
        smartphones_on_network * 0.56 / 2
    )

    #Check suburban geotype uses urban in the smartphone lut
    setup_region[0]['geotype'] = 'suburban'
    answer, annual_answer = estimate_demand(
        {'income': 'HIC'},
        setup_country_parameters,
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_timesteps,
        setup_penetration_lut,
        {'urban': {2020: 50}}
    )

    # pop = 10000
    # pen = 50%
    # = 5000 phones
    assert answer[0]['population_with_phones'] == 5000

    # 5000 phones
    # 3 networks
    # = 1667 phones
    assert round(answer[0]['phones_on_network']) == round(5000 / 3)

    # 5000 phones
    # 3 networks
    # 50% smartphones
    # = 833 smartphones
    smartphones_on_network = round(5000 / 3 * (50 / 100))
    assert round(answer[0]['smartphones_on_network']) == smartphones_on_network

    answer, annual_answer = estimate_demand(
        {'income': 'HIC'},
        setup_country_parameters,
        setup_region_rural,
        setup_option_high,
        setup_global_parameters,
        setup_timesteps,
        setup_penetration_lut,
        {'rural': {2020: 50}}
    )

    # 5000/3 = 1667 phones on network
    # arpu = 2 * 12 months
    # 40,000 = ((5000/3) * 2 * 12)
    assert round(answer[0]['total_mno_revenue']) == round((5000/3) * 2 * 12)

    setup_region[0]['geotype'] = 'rural'
    setup_region[0]['mean_luminosity_km2'] = 2
    setup_option['strategy'] = '4G_epc_wireless_srn_baseline_baseline_baseline_baseline'
    setup_country_parameters['arpu']['arpu_baseline'] = 7

    #iterate through years to create annual lookup
    setup_timesteps = list(range(2020, 2030))
    setup_penetration_lut = {}
    intermediate = {}
    for i in setup_timesteps:
        setup_penetration_lut[i] = 50
        intermediate[i] = 50

    setup_smartphone_lut = {}
    setup_smartphone_lut['rural'] = intermediate

    answer, annual_answer = estimate_demand(
        {'income': 'HIC'},
        setup_country_parameters,
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_timesteps,
        setup_penetration_lut,
        setup_smartphone_lut
    )

    # pop = 10000
    # pen = 50%
    # = 5000 phones
    assert answer[0]['population_with_phones'] == 5000

    # 5000 phones
    # 1 network
    # = 5000 phones
    assert round(answer[0]['phones_on_network']) == round(5000)

    # 5000 phones
    # 1 network
    # 50% smartphones
    # = 833 smartphones
    smartphones_on_network = round(5000 * (50 / 100))
    assert round(answer[0]['smartphones_on_network']) == smartphones_on_network

    # 5000 phones
    # arpu = 7 # monthly
    # discounted arpur over 10 years @ 5% = 242
    # [120000.0, 114285.71428571428, 108843.53741496598, 103660.51182377712,
    # 98724.29697502582, 94023.13997621505, 89545.8475963953, 85281.75961561457,
    # 81220.72344344243, 77353.06994613566]
    # multplied by 12 months per year
    assert round(answer[0]['total_mno_revenue']) == round(972939)

    # 2500 smartphones
    # scenario = 0.56
    # area = 2
    # demand_mbps_km2 = 125
    #sum [625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0] / 11
    assert round(answer[0]['demand_mbps_km2']) == round(
        ((smartphones_on_network * 0.56 / 2) * 11) / 11
    )

    setup_region[0]['population_total'] = 0
    setup_region[0]['population_km2'] = 0

    answer, annual_answer = estimate_demand(
        {'income': 'HIC'},
        setup_country_parameters,
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_timesteps,
        setup_penetration_lut,
        setup_smartphone_lut
    )

    assert answer[0]['population_with_phones'] == 0


def test_get_per_user_capacity():
    """
    Unit test.

    """
    answer = get_per_user_capacity('urban', {'scenario': 'S1_25_5_1'}, {'traffic_in_the_busy_hour_perc': 15})

    assert round(answer,2) == round((25 / 30) * 0.15 * 8 * 1000 / 3600, 2)

    answer = get_per_user_capacity('suburban', {'scenario': 'S1_25_5_1'}, {'traffic_in_the_busy_hour_perc': 15})

    assert round(answer,2) == round((5 / 30) * 0.15 * 8 * 1000 / 3600, 2)

    answer = get_per_user_capacity('rural', {'scenario': 'S1_25_5_1'}, {'traffic_in_the_busy_hour_perc': 15})

    assert round(answer,2) == round((1 / 30) * 0.15 * 8 * 1000 / 3600, 2)

    answer = get_per_user_capacity('made up geotype', {'scenario': 'S1_25_5_1'}, {'traffic_in_the_busy_hour_perc': 15})

    assert answer == 'Did not recognise geotype'


def test_estimate_arpu(setup_region, setup_timesteps, setup_global_parameters,
    setup_country_parameters):
    """
    Unit test.

    """
    answer = estimate_arpu({'geotype': 'urban'}, 2020, setup_global_parameters,
        setup_country_parameters)

    assert answer == 15

    answer = estimate_arpu({'geotype': 'suburban'}, 2020, setup_global_parameters,
        setup_country_parameters)

    assert answer == 5

    answer = estimate_arpu({'geotype': 'rural'}, 2020, setup_global_parameters,
        setup_country_parameters)

    assert answer == 2
