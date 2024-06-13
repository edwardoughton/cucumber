"""
Estimate demand

Written by Ed Oughton.

Winter 2020

"""

def estimate_demand(country, deciles):
    """
    Estimate demand metrics.

    Parameters
    ----------
    country : dict
        All country metadata.
    deciles : list of dicts
        Data for all deciles (one dict per decile).

    Returns
    -------
    deciles : list of dicts
        Data for all deciles (one dict per decile).

    """
    output = []

    for decile in deciles:

        if not decile['area_km2'] > 0:
            continue

        geotype = decile['geotype'].split(' ')[0]

        decile['income'] = country['income']
        decile['wb_region'] = country['wb_region']
        decile['iea_classification'] = country['iea_classification']

        decile['penetration'] = 0.90 #(penetration_lut[timestep] / 100)

        #number of cell phones per member of the population.
        decile['population_with_phones'] = (
            decile['population_total'] * decile['penetration'])
        
        # #total number of phones on the network being modeled.
        # decile['phones_on_network'] = (
        #     decile['population_with_phones'] / 4) #networks

        # #get phone density
        # decile['phone_density_on_network_km2'] = (
        #     decile['phones_on_network'] / decile['area_km2'])

        #add regional smartphone penetration
        decile['smartphone_penetration'] = .90 #smartphone_lut[geotype_sps][timestep]

        decile['population_with_smartphones'] = (
            decile['population_with_phones'] *
            (decile['smartphone_penetration']))

        # decile['smartphones_on_network'] = (
        #     decile['phones_on_network'] *
        #     (decile['smartphone_penetration'] / 100)
        # )

        # #get smartphone density
        # decile['sp_density_on_network_km2'] = (
        #     decile['smartphones_on_network'] / decile['area_km2']
        # )

        scenario_per_user_mbps = get_per_user_capacity('suburban', decile)

        #demand_mbps_km2 : float
        #total demand in mbps / km^2.
        decile['demand_mbps_km2'] = (
            (decile['population_with_smartphones'] *
            scenario_per_user_mbps / #User demand in Mbps
            decile['area_km2']
            ))

        output.append(decile)

    return output


def get_per_user_capacity(geotype, option):
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
    global_parameters : dict
        Contains all global parameters, e.g. traffic in the busy hour. 

    Returns
    -------
    per_user_capacity : int
        The targetted per user capacity in Mbps.

    """
    global_parameters = {'traffic_in_the_busy_hour_perc': 15}
    if geotype.split(' ')[0] == 'urban':

        per_month_gb = int(option['capacity'])
        per_day_gb = per_month_gb / 30
        busy_hour_gb = per_day_gb * (global_parameters['traffic_in_the_busy_hour_perc'] / 100)
        per_user_mbps = busy_hour_gb * 1000 * 8 / 3600
        return round(per_user_mbps, 2)

    elif geotype.split(' ')[0] == 'suburban':

        per_month_gb = int(option['capacity'])
        per_day_gb = per_month_gb / 30
        busy_hour_gb = per_day_gb * (global_parameters['traffic_in_the_busy_hour_perc'] / 100)
        per_user_mbps = busy_hour_gb * 1000 * 8 / 3600
        return round(per_user_mbps, 2)

    elif geotype.split(' ')[0] == 'rural':

        per_month_gb = int(option['capacity'])
        per_day_gb = per_month_gb / 30
        busy_hour_gb = per_day_gb * (global_parameters['traffic_in_the_busy_hour_perc'] / 100)
        per_user_mbps = busy_hour_gb * 1000 * 8 / 3600
        return round(per_user_mbps, 2)

    else:
        return 'Did not recognise geotype'

