"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_energy(country, regions, assets, option, global_parameters,
    country_parameters, timesteps, energy_demand): #, tech_lut, on_grid_mix
    """
    For each region, calculate energy consumption and associated emissions.

    Parameters
    ----------
    # country : dict
    #     Country information.
    # regions : dataframe
    #     Geopandas dataframe of all regions.
    # option : dict
    #     Contains the scenario and strategy. The strategy string controls
    #     the strategy variants being testes in the model and is defined based
    #     on the type of technology generation, core and backhaul, and the level
    #     of sharing, subsidy, spectrum and tax.
    # global_parameters : dict
    #     All global model parameters.
    # country_parameters : dict
    #     All country specific parameters.

    Returns
    -------
    output : list of dicts
        Contains all output data.

    """
    output = []

    for region in regions:

        # if not region['GID_id'] == 'COL.14.12_1':
        #     continue

        geotype = region['geotype'].split(' ')[0]
        sharing = option['strategy'].split('_')[3]
        baseline_net_handle = 'baseline' + '_' + geotype
        baseline_networks = country_parameters['networks'][baseline_net_handle]
        if sharing in ['active', 'srn']:
            net_handle = sharing + '_' + geotype
            networks = country_parameters['networks'][net_handle]
            network_division = (networks/baseline_networks)
        else:
            network_division = 1

        equipment_quantity = 0
        regional_nodes = 0
        core_nodes = 0
        wireless_small = 0
        wireless_medium = 0
        wireless_large = 0

        decile_assets = assets[region['decile']]

        for asset in decile_assets:
            if 'equipment' in asset.values():
                equipment_quantity += asset['quantity']
            elif 'regional_node' in asset.values():
                regional_nodes += asset['quantity']
            elif 'core_node' in asset.values():
                core_nodes += asset['quantity']
            elif 'backhaul_wireless_small' in asset.values():
                wireless_small += asset['quantity']
            elif 'backhaul_wireless_medium' in asset.values():
                wireless_medium += asset['quantity']
            elif 'backhaul_wireless_large' in asset.values():
                wireless_large += asset['quantity']

        equipment_hourly_demand_kwh = equipment_quantity * energy_demand['equipment_kwh']
        regional_nodes_hourly_demand_kwh = regional_nodes * energy_demand['regional_node_kwh']
        core_nodes_hourly_demand_kwh = core_nodes * energy_demand['core_node_kwh']
        wireless_small_hourly_demand_kwh = wireless_small * energy_demand['wireless_small_kwh']
        wireless_medium_hourly_demand_kwh = wireless_medium * energy_demand['wireless_medium_kwh']
        wireless_large_hourly_demand_kwh = wireless_large * energy_demand['wireless_large_kwh']

        equipment_annual_demand_kwh = equipment_hourly_demand_kwh * 24 * 365
        regional_nodes_annual_demand_kwh = regional_nodes_hourly_demand_kwh * 24 * 365
        core_nodes_annual_demand_kwh = core_nodes_hourly_demand_kwh * 24 * 365
        wireless_small_annual_demand_kwh = wireless_small_hourly_demand_kwh * 24 * 365
        wireless_medium_annual_demand_kwh = wireless_medium_hourly_demand_kwh * 24 * 365
        wireless_large_annual_demand_kwh = wireless_large_hourly_demand_kwh * 24 * 365

        total_demand_kwh = (
            equipment_annual_demand_kwh +
            regional_nodes_annual_demand_kwh +
            core_nodes_annual_demand_kwh +
            wireless_small_annual_demand_kwh +
            wireless_medium_annual_demand_kwh +
            wireless_large_annual_demand_kwh
        )

        for timestep in timesteps:

            grid_types = [
                'on_grid',
                'grid_other'
            ]

            for grid_type in grid_types:

                grid_type_handle = grid_type + '_perc'

                if sharing in ['baseline', 'passive']:
                    elec_demand = calc_demand(total_demand_kwh, region, grid_type_handle)
                    equip_demand = calc_demand(equipment_annual_demand_kwh, region, grid_type_handle)
                    regional_nodes_demand = calc_demand(regional_nodes_annual_demand_kwh, region, grid_type_handle)
                    core_nodes_demand = calc_demand(core_nodes_annual_demand_kwh, region, grid_type_handle)
                elif sharing == 'srn':
                    if geotype == 'urban' or geotype == 'suburban':
                        elec_demand = calc_demand(total_demand_kwh, region, grid_type_handle)
                        equip_demand = calc_demand(equipment_annual_demand_kwh, region, grid_type_handle)
                        regional_nodes_demand = calc_demand(regional_nodes_annual_demand_kwh, region, grid_type_handle)
                        core_nodes_demand = calc_demand(core_nodes_annual_demand_kwh, region, grid_type_handle)
                    else:
                        elec_demand = (total_demand_kwh * (region[grid_type_handle] / 100)) * network_division
                        equip_demand = equipment_annual_demand_kwh * (region[grid_type_handle] / 100) * network_division
                        regional_nodes_demand = regional_nodes_annual_demand_kwh * (region[grid_type_handle] / 100) * network_division
                        core_nodes_demand = core_nodes_annual_demand_kwh * (region[grid_type_handle] / 100) * network_division
                elif sharing == 'active':

                    elec_demand = (total_demand_kwh * (region[grid_type_handle] / 100)) * network_division
                    equip_demand = equipment_annual_demand_kwh * (region[grid_type_handle] / 100) * network_division
                    regional_nodes_demand = regional_nodes_annual_demand_kwh * (region[grid_type_handle] / 100) * network_division
                    core_nodes_demand = core_nodes_annual_demand_kwh * (region[grid_type_handle] / 100) * network_division
                else:
                    print('Did not reognize sharing scenario')

                wireless_backhaul_demand = (
                    wireless_small_annual_demand_kwh +
                    wireless_medium_annual_demand_kwh +
                    wireless_large_annual_demand_kwh
                    ) * (region[grid_type_handle] / 100)

                output.append({
                    'year': timestep,
                    'GID_0': region['GID_0'],
                    'decile': region['decile'],
                    'geotype': geotype,
                    'scenario': option['scenario'],
                    'strategy': option['strategy'],
                    'confidence': global_parameters['confidence'][0],
                    'grid_type_perc': region[grid_type_handle],
                    'grid_type': grid_type,
                    'network_division': network_division,
                    'mno_energy_annual_demand_kwh': elec_demand,
                    'mno_equipment_annual_demand_kWh': equip_demand,
                    'mno_regional_nodes_annual_demand_kwh': regional_nodes_demand,
                    'mno_core_nodes_annual_demand_kwh': core_nodes_demand,
                    'mno_wireless_backhaul_annual_demand_kwh': wireless_backhaul_demand,
                    'total_energy_annual_demand_kwh': elec_demand * baseline_networks,
                    'total_equipment_annual_demand_kWh': equip_demand * baseline_networks,
                    'total_regional_nodes_annual_demand_kwh': regional_nodes_demand * baseline_networks,
                    'total_core_nodes_annual_demand_kwh': core_nodes_demand * baseline_networks,
                    'total_wireless_backhaul_annual_demand_kwh': wireless_backhaul_demand * baseline_networks,
                })

    return output


def calc_demand(total, region, grid_type_handle):

    demand = total * (region[grid_type_handle] / 100)

    return demand
