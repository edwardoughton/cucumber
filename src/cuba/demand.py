"""
Estimate demand

Written by Ed Oughton.

Winter 2020

"""

def estimate_demand(regions, option, global_parameters, country_parameters,
    timesteps, penetration_lut, smartphone_lut):
    """
    Estimate demand metrics including:
        - Total number of basic phone and smartphone users
        - Total data demand (in Mbps per square kilometer)
        - Total revenue (net present value over the assessment period in USD)

    Parameters
    ----------
    regions : list of dicts
        Data for all regions (one dict per region).
    option : dict
        Contains the scenario and strategy. The strategy string controls
        the strategy variants being tested in the model and is defined based
        on the type of technology generation, core and backhaul, and the
        strategy for infrastructure sharing, the number of networks in each
        geotype, spectrum and taxation.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.
    timesteps : list
        All years for the assessment period.
    penetration_lut : list of dicts
        Contains annual cell phone penetration values.
    smartphone_lut : list of dicts
        Contains annual penetration values for smartphones.

    Returns
    -------
    regions : list of dicts
        Data for all regions (one dict per region).

    """
    output = []
    annual_output = []

    # generation_core_backhaul_sharing_networks_spectrum_tax
    network_strategy = option['strategy'].split('_')[3]

    for region in regions:

        if not region['area_km2'] > 0:
            continue

        geotype = region['geotype'].split(' ')[0]

        net_handle = network_strategy + '_' + geotype.split(' ')[0]

        networks = country_parameters['networks'][net_handle]

        if geotype == 'suburban':
            #smartphone lut only has urban-rural split, hence no suburban
            geotype_sps = 'urban'
        else:
            geotype_sps = geotype.split(' ')[0]

        revenue = []
        demand_mbps_km2 = []

        scenario_per_user_mbps = get_per_user_capacity(
            region['geotype'], option, global_parameters)

        for timestep in timesteps:

            region['arpu_discounted_monthly'] = estimate_arpu(
                region,
                timestep,
                global_parameters,
                country_parameters
            )

            # year_gender = '{}_{}'.format(timestep, 'female')
            # region['penetration_female'] = penetration_lut[year_gender]
            # year_gender = '{}_{}'.format(timestep, 'male')
            # region['penetration_male'] = penetration_lut[year_gender]
            region['penetration'] = (penetration_lut[timestep] / 100)

            #Number of cell phones per member of the population.
            region['population_with_phones'] = (
                region['population_total'] * region['penetration'])
            # region['population_with_phones_f_over_10'] = (
            #     (region['population_f_over_10']) *
            #     (region['penetration'] / 100))
            # region['population_with_phones_m_over_10'] = (
            #     (region['population_m_over_10']) *
            #     (region['penetration'] / 100))

            #Total number of phones on the network being modeled.
            region['phones_on_network'] = (
                region['population_with_phones'] / networks)
            # region['phones_on_network_f_over_10'] = (
            #     (region['population_with_phones_f_over_10']) / networks)
            # region['phones_on_network_m_over_10'] = (
            #     (region['population_with_phones_m_over_10']) / networks)

            #get phone density
            region['phone_density_on_network_km2'] = (
                region['phones_on_network'] / region['area_km2'])
            # region['phone_density_on_network_km2_f_over_10'] = (
            #     region['phones_on_network_f_over_10'] / region['area_km2'])
            # region['phone_density_on_network_km2_m_over_10'] = (
            #     region['phones_on_network_m_over_10'] / region['area_km2'])

            #add regional smartphone penetration
            region['smartphone_penetration'] = smartphone_lut[geotype_sps][timestep]

            #phones : int
            #Total number of smartphones on the network being modeled.
            region['population_with_smartphones'] = (
                region['population_with_phones'] *
                (region['smartphone_penetration'] / 100))
            # region['population_with_smartphones_f_over_10'] = (
            #     region['population_with_phones_f_over_10'] *
            #     (region['smartphone_penetration'] / 100))
            # region['population_with_smartphones_m_over_10'] = (
            #     region['population_with_phones_m_over_10'] *
            #     (region['smartphone_penetration'] / 100))

            #phones : int
            #Total number of smartphones on the network being modeled.
            region['smartphones_on_network'] = (
                region['phones_on_network'] *
                (region['smartphone_penetration'] / 100)
            )

            #get smartphone density
            region['sp_density_on_network_km2'] = (
                region['smartphones_on_network'] / region['area_km2']
            )

            # demand_mbps_km2 : float
            # Total demand in mbps / km^2.
            demand_mbps_km2.append(
                (region['smartphones_on_network'] *
                scenario_per_user_mbps / #User demand in Mbps
                # global_parameters['overbooking_factor'] /
                region['area_km2']
                ))

            annual_revenue = (
                region['arpu_discounted_monthly'] *
                region['phones_on_network'] *
                12
            )

            revenue.append(annual_revenue)

            annual_output.append({
                'GID_0': region['GID_0'],
                'decile': region['decile'],
                'scenario': option['scenario'],
                'strategy': option['strategy'],
                'confidence': global_parameters['confidence'][0],
                'year': timestep,
                'population': region['population_total'],
                # 'population_f_over_10': region['population_f_over_10'],
                # 'population_m_over_10': region['population_m_over_10'],
                'area_km2': region['area_km2'],
                'population_km2': region['population_km2'],
                'geotype': region['geotype'].split(' ')[0],
                'arpu_discounted_monthly': region['arpu_discounted_monthly'],
                # 'penetration_female': region['penetration_female'],
                # 'penetration_male': region['penetration_male'],
                'penetration': region['penetration'],
                'population_with_phones': region['population_with_phones'],
                # 'population_with_phones_f_over_10': region['population_with_phones_f_over_10'],
                # 'population_with_phones_m_over_10': region['population_with_phones_m_over_10'],
                'phones_on_network': region['phones_on_network'],
                'smartphone_penetration': region['smartphone_penetration'],
                'population_with_smartphones': region['population_with_smartphones'],
                # 'population_with_smartphones_f_over_10': region['population_with_smartphones_f_over_10'],
                # 'population_with_smartphones_m_over_10': region['population_with_smartphones_m_over_10'],
                'smartphones_on_network': region['smartphones_on_network'],
                'revenue': annual_revenue,
            })

        region['scenario_per_user_mbps'] = scenario_per_user_mbps
        region['demand_mbps_km2'] = max(demand_mbps_km2)
        region['total_mno_revenue'] = round(sum(revenue))
        region['revenue_km2'] = round(sum(revenue) / region['area_km2'])

        output.append(region)

    return output, annual_output


def get_per_user_capacity(geotype, option, global_parameters):
    """
    Function to return the per user data rate by scenario,
    from the scenario string.

    Parameters
    ----------
    geotype : string
        Settlement patterns, such as urban, suburban or rural.
    option : dict
        Contains the scenario and strategy. The strategy string controls
        the strategy variants being tested in the model and is defined based
        on the type of technology generation, core and backhaul, and the
        strategy for infrastructure sharing, the number of networks in each
        geotype, spectrum and taxation.
    Returns
    -------
    per_user_capacity : int
        The targetted per user capacity in Mbps.
    """
    if geotype.split(' ')[0] == 'urban':

        per_month_gb = int(option['scenario'].split('_')[1])
        per_day_gb = per_month_gb / 30
        busy_hour_gb = per_day_gb * (global_parameters['traffic_in_the_busy_hour_perc'] / 100)
        per_user_mbps = busy_hour_gb * 1000 * 8 / 3600
        return round(per_user_mbps, 2)

    elif geotype.split(' ')[0] == 'suburban':

        per_month_gb = int(option['scenario'].split('_')[2])
        per_day_gb = per_month_gb / 30
        busy_hour_gb = per_day_gb * (global_parameters['traffic_in_the_busy_hour_perc'] / 100)
        per_user_mbps = busy_hour_gb * 1000 * 8 / 3600
        return round(per_user_mbps, 2)

    elif geotype.split(' ')[0] == 'rural':

        per_month_gb = int(option['scenario'].split('_')[3])
        per_day_gb = per_month_gb / 30
        busy_hour_gb = per_day_gb * (global_parameters['traffic_in_the_busy_hour_perc'] / 100)
        per_user_mbps = busy_hour_gb * 1000 * 8 / 3600
        return round(per_user_mbps, 2)

    else:
        return 'Did not recognise geotype'


def estimate_arpu(region, timestep, global_parameters, country_parameters):
    """
    Allocate consumption category given a specific luminosity.
    Parameters
    ----------
    region : dicts
        Data for a single region.
    timestep : int
        Time period (year) to discount against.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.
    Returns
    -------
    discounted_arpu : float
        The discounted Average Revenue Per User (ARPU) over the time period.
    """
    timestep = timestep - 2020

    if region['geotype'] == 'urban':
        arpu = country_parameters['arpu']['arpu_high']
        return discount_arpu(arpu, timestep, global_parameters)

    elif region['geotype'] == 'suburban':
        arpu = country_parameters['arpu']['arpu_baseline']
        return discount_arpu(arpu, timestep, global_parameters)

    elif region['geotype'] == 'rural':
        arpu = country_parameters['arpu']['arpu_low']
        return discount_arpu(arpu, timestep, global_parameters)

    else:
        arpu = country_parameters['arpu']['arpu_baseline']
        return discount_arpu(arpu, timestep, global_parameters)


def discount_arpu(arpu, timestep, global_parameters):
    """
    Discount arpu based on return period.
    192,744 = 23,773 / (1 + 0.05) ** (0:9)
    Parameters
    ----------
    arpu : float
        Average revenue per user.
    timestep : int
        Time period (year) to discount against.
    global_parameters : dict
        All global model parameters.
    Returns
    -------
    discounted_arpu : float
        The discounted revenue over the desired time period.
    """
    discount_rate = global_parameters['discount_rate'] / 100

    discounted_arpu = arpu / (1 + discount_rate) ** timestep

    return discounted_arpu
