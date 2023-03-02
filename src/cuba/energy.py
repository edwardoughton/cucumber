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

        equipment_quantity_new = 0
        equipment_quantity_upgraded = 0
        equipment_quantity_existing = 0
        regional_nodes_new = 0
        regional_nodes_upgraded = 0
        regional_nodes_existing = 0
        core_nodes_new = 0
        core_nodes_upgraded = 0
        core_nodes_existing = 0
        wireless_small_new = 0
        wireless_small_upgraded = 0
        wireless_small_existing = 0
        wireless_medium_new = 0
        wireless_medium_upgraded = 0
        wireless_medium_existing = 0
        wireless_large_new = 0
        wireless_large_upgraded = 0
        wireless_large_existing = 0

        decile_assets = assets[region['decile']]

        for asset in decile_assets:

            if 'equipment' and 'new' in asset.values() :
                equipment_quantity_new += asset['quantity']
            elif 'equipment' and 'upgraded' in asset.values():
                equipment_quantity_upgraded += asset['quantity']
            elif 'equipment' and 'existing' in asset.values():
                equipment_quantity_existing += asset['quantity']

            elif 'regional_node' and 'new' in asset.values():
                regional_nodes_new += asset['quantity']
            elif 'regional_node' and 'upgraded' in asset.values():
                regional_nodes_upgraded += asset['quantity']
            elif 'regional_node' and 'existing' in asset.values():
                regional_nodes_existing += asset['quantity']

            elif 'core_node' and 'new' in asset.values():
                core_nodes_new += asset['quantity']
            elif 'core_node' and 'upgraded' in asset.values():
                core_nodes_upgraded += asset['quantity']
            elif 'core_node' and 'existing' in asset.values():
                core_nodes_existing += asset['quantity']

            elif 'backhaul_wireless_small' and 'new' in asset.values():
                wireless_small_new += asset['quantity']
            elif 'backhaul_wireless_small' and 'upgraded' in asset.values():
                wireless_small_upgraded += asset['quantity']
            elif 'backhaul_wireless_small' and 'existing' in asset.values():
                wireless_small_existing += asset['quantity']

            elif 'backhaul_wireless_medium' and 'new' in asset.values():
                wireless_medium_new += asset['quantity']
            elif 'backhaul_wireless_medium' and 'upgraded' in asset.values():
                wireless_medium_upgraded += asset['quantity']
            elif 'backhaul_wireless_medium' and 'existing' in asset.values():
                wireless_medium_existing += asset['quantity']

            elif 'backhaul_wireless_large' and 'new' in asset.values():
                wireless_large_new += asset['quantity']
            elif 'backhaul_wireless_large' and 'upgraded' in asset.values():
                wireless_large_upgraded += asset['quantity']
            elif 'backhaul_wireless_large' and 'existing' in asset.values():
                wireless_large_existing += asset['quantity']

        equipment_hourly_demand_kwh_new = equipment_quantity_new * energy_demand['equipment_kwh']
        regional_nodes_hourly_demand_kwh_new = regional_nodes_new * energy_demand['regional_node_kwh']
        core_nodes_hourly_demand_kwh_new = core_nodes_new * energy_demand['core_node_kwh']
        wireless_small_hourly_demand_kwh_new = wireless_small_new * energy_demand['wireless_small_kwh']
        wireless_medium_hourly_demand_kwh_new = wireless_medium_new * energy_demand['wireless_medium_kwh']
        wireless_large_hourly_demand_kwh_new = wireless_large_new * energy_demand['wireless_large_kwh']

        equipment_hourly_demand_kwh_upgraded = equipment_quantity_upgraded * energy_demand['equipment_kwh']
        regional_nodes_hourly_demand_kwh_upgraded = regional_nodes_upgraded * energy_demand['regional_node_kwh']
        core_nodes_hourly_demand_kwh_upgraded = core_nodes_upgraded * energy_demand['core_node_kwh']
        wireless_small_hourly_demand_kwh_upgraded = wireless_small_upgraded * energy_demand['wireless_small_kwh']
        wireless_medium_hourly_demand_kwh_upgraded = wireless_medium_upgraded * energy_demand['wireless_medium_kwh']
        wireless_large_hourly_demand_kwh_upgraded = wireless_large_upgraded * energy_demand['wireless_large_kwh']

        equipment_hourly_demand_kwh_existing = equipment_quantity_existing * energy_demand['equipment_kwh']
        regional_nodes_hourly_demand_kwh_existing = regional_nodes_existing * energy_demand['regional_node_kwh']
        core_nodes_hourly_demand_kwh_existing = core_nodes_existing * energy_demand['core_node_kwh']
        wireless_small_hourly_demand_kwh_existing = wireless_small_existing * energy_demand['wireless_small_kwh']
        wireless_medium_hourly_demand_kwh_existing = wireless_medium_existing * energy_demand['wireless_medium_kwh']
        wireless_large_hourly_demand_kwh_existing = wireless_large_existing * energy_demand['wireless_large_kwh']

        equipment_annual_demand_kwh_new = equipment_hourly_demand_kwh_new * 24 * 365
        regional_nodes_annual_demand_kwh_new = regional_nodes_hourly_demand_kwh_new * 24 * 365
        core_nodes_annual_demand_kwh_new = core_nodes_hourly_demand_kwh_new * 24 * 365
        wireless_small_annual_demand_kwh_new = wireless_small_hourly_demand_kwh_new * 24 * 365
        wireless_medium_annual_demand_kwh_new = wireless_medium_hourly_demand_kwh_new * 24 * 365
        wireless_large_annual_demand_kwh_new = wireless_large_hourly_demand_kwh_new * 24 * 365

        equipment_annual_demand_kwh_upgraded = equipment_hourly_demand_kwh_upgraded * 24 * 365
        regional_nodes_annual_demand_kwh_upgraded = regional_nodes_hourly_demand_kwh_upgraded * 24 * 365
        core_nodes_annual_demand_kwh_upgraded = core_nodes_hourly_demand_kwh_upgraded * 24 * 365
        wireless_small_annual_demand_kwh_upgraded = wireless_small_hourly_demand_kwh_upgraded * 24 * 365
        wireless_medium_annual_demand_kwh_upgraded = wireless_medium_hourly_demand_kwh_upgraded * 24 * 365
        wireless_large_annual_demand_kwh_upgraded = wireless_large_hourly_demand_kwh_upgraded * 24 * 365

        equipment_annual_demand_kwh_existing = equipment_hourly_demand_kwh_existing * 24 * 365
        regional_nodes_annual_demand_kwh_existing = regional_nodes_hourly_demand_kwh_existing * 24 * 365
        core_nodes_annual_demand_kwh_existing = core_nodes_hourly_demand_kwh_existing * 24 * 365
        wireless_small_annual_demand_kwh_existing = wireless_small_hourly_demand_kwh_existing * 24 * 365
        wireless_medium_annual_demand_kwh_existing = wireless_medium_hourly_demand_kwh_existing * 24 * 365
        wireless_large_annual_demand_kwh_existing = wireless_large_hourly_demand_kwh_existing * 24 * 365

        total_demand_kwh_new = (
            equipment_annual_demand_kwh_new +
            regional_nodes_annual_demand_kwh_new +
            core_nodes_annual_demand_kwh_new +
            wireless_small_annual_demand_kwh_new +
            wireless_medium_annual_demand_kwh_new +
            wireless_large_annual_demand_kwh_new
        )

        total_demand_kwh_upgraded = (
            equipment_annual_demand_kwh_upgraded +
            regional_nodes_annual_demand_kwh_upgraded +
            core_nodes_annual_demand_kwh_upgraded +
            wireless_small_annual_demand_kwh_upgraded +
            wireless_medium_annual_demand_kwh_upgraded +
            wireless_large_annual_demand_kwh_upgraded
        )

        total_demand_kwh_existing = (
            equipment_annual_demand_kwh_existing +
            regional_nodes_annual_demand_kwh_existing +
            core_nodes_annual_demand_kwh_existing +
            wireless_small_annual_demand_kwh_existing +
            wireless_medium_annual_demand_kwh_existing +
            wireless_large_annual_demand_kwh_existing
        )

        for timestep in timesteps:

            grid_types = [
                'on_grid',
                'grid_other'
            ]

            for grid_type in grid_types:

                grid_type_handle = grid_type + '_perc'

                if sharing in ['baseline', 'passive']:
                    elec_demand_new = calc_demand(total_demand_kwh_new, region, grid_type_handle)
                    equip_demand_new = calc_demand(equipment_annual_demand_kwh_new, region, grid_type_handle)
                    regional_nodes_demand_new = calc_demand(regional_nodes_annual_demand_kwh_new, region, grid_type_handle)
                    core_nodes_demand_new = calc_demand(core_nodes_annual_demand_kwh_new, region, grid_type_handle)

                    elec_demand_upgraded = calc_demand(total_demand_kwh_upgraded, region, grid_type_handle)
                    equip_demand_upgraded = calc_demand(equipment_annual_demand_kwh_upgraded, region, grid_type_handle)
                    regional_nodes_demand_upgraded = calc_demand(regional_nodes_annual_demand_kwh_upgraded, region, grid_type_handle)
                    core_nodes_demand_upgraded = calc_demand(core_nodes_annual_demand_kwh_upgraded, region, grid_type_handle)

                    elec_demand_existing = calc_demand(total_demand_kwh_existing, region, grid_type_handle)
                    equip_demand_existing = calc_demand(equipment_annual_demand_kwh_existing, region, grid_type_handle)
                    regional_nodes_demand_existing = calc_demand(regional_nodes_annual_demand_kwh_existing, region, grid_type_handle)
                    core_nodes_demand_existing = calc_demand(core_nodes_annual_demand_kwh_existing, region, grid_type_handle)

                elif sharing == 'srn':
                    if geotype == 'urban' or geotype == 'suburban':
                        elec_demand_new = calc_demand(total_demand_kwh_new, region, grid_type_handle)
                        equip_demand_new = calc_demand(equipment_annual_demand_kwh_new, region, grid_type_handle)
                        regional_nodes_demand_new = calc_demand(regional_nodes_annual_demand_kwh_new, region, grid_type_handle)
                        core_nodes_demand_new = calc_demand(core_nodes_annual_demand_kwh_new, region, grid_type_handle)

                        elec_demand_upgraded = calc_demand(total_demand_kwh_upgraded, region, grid_type_handle)
                        equip_demand_upgraded = calc_demand(equipment_annual_demand_kwh_upgraded, region, grid_type_handle)
                        regional_nodes_demand_upgraded = calc_demand(regional_nodes_annual_demand_kwh_upgraded, region, grid_type_handle)
                        core_nodes_demand_upgraded = calc_demand(core_nodes_annual_demand_kwh_upgraded, region, grid_type_handle)

                        elec_demand_existing = calc_demand(total_demand_kwh_existing, region, grid_type_handle)
                        equip_demand_existing = calc_demand(equipment_annual_demand_kwh_existing, region, grid_type_handle)
                        regional_nodes_demand_existing = calc_demand(regional_nodes_annual_demand_kwh_existing, region, grid_type_handle)
                        core_nodes_demand_existing = calc_demand(core_nodes_annual_demand_kwh_existing, region, grid_type_handle)

                    else:
                        elec_demand_new = (total_demand_kwh_new * (region[grid_type_handle] / 100)) * network_division
                        equip_demand_new = equipment_annual_demand_kwh_new * (region[grid_type_handle] / 100) * network_division
                        regional_nodes_demand_new = regional_nodes_annual_demand_kwh_new * (region[grid_type_handle] / 100) * network_division
                        core_nodes_demand_new = core_nodes_annual_demand_kwh_new * (region[grid_type_handle] / 100) * network_division

                        elec_demand_upgraded = (total_demand_kwh_upgraded * (region[grid_type_handle] / 100)) * network_division
                        equip_demand_upgraded = equipment_annual_demand_kwh_upgraded * (region[grid_type_handle] / 100) * network_division
                        regional_nodes_demand_upgraded = regional_nodes_annual_demand_kwh_upgraded * (region[grid_type_handle] / 100) * network_division
                        core_nodes_demand_upgraded = core_nodes_annual_demand_kwh_upgraded * (region[grid_type_handle] / 100) * network_division

                        elec_demand_existing = (total_demand_kwh_existing * (region[grid_type_handle] / 100)) * network_division
                        equip_demand_existing = equipment_annual_demand_kwh_existing * (region[grid_type_handle] / 100) * network_division
                        regional_nodes_demand_existing = regional_nodes_annual_demand_kwh_existing * (region[grid_type_handle] / 100) * network_division
                        core_nodes_demand_existing = core_nodes_annual_demand_kwh_existing * (region[grid_type_handle] / 100) * network_division

                elif sharing == 'active':

                    elec_demand_new = (total_demand_kwh_new * (region[grid_type_handle] / 100)) * network_division
                    equip_demand_new = equipment_annual_demand_kwh_new * (region[grid_type_handle] / 100) * network_division
                    regional_nodes_demand_new = regional_nodes_annual_demand_kwh_new * (region[grid_type_handle] / 100) * network_division
                    core_nodes_demand_new = core_nodes_annual_demand_kwh_new * (region[grid_type_handle] / 100) * network_division

                    elec_demand_upgraded = (total_demand_kwh_upgraded * (region[grid_type_handle] / 100)) * network_division
                    equip_demand_upgraded = equipment_annual_demand_kwh_upgraded * (region[grid_type_handle] / 100) * network_division
                    regional_nodes_demand_upgraded = regional_nodes_annual_demand_kwh_upgraded * (region[grid_type_handle] / 100) * network_division
                    core_nodes_demand_upgraded = core_nodes_annual_demand_kwh_upgraded * (region[grid_type_handle] / 100) * network_division

                    elec_demand_existing = (total_demand_kwh_existing * (region[grid_type_handle] / 100)) * network_division
                    equip_demand_existing = equipment_annual_demand_kwh_existing * (region[grid_type_handle] / 100) * network_division
                    regional_nodes_demand_existing = regional_nodes_annual_demand_kwh_existing * (region[grid_type_handle] / 100) * network_division
                    core_nodes_demand_existing = core_nodes_annual_demand_kwh_existing * (region[grid_type_handle] / 100) * network_division

                else:
                    print('Did not reognize sharing scenario')

                wireless_backhaul_demand_new = (
                    wireless_small_annual_demand_kwh_new +
                    wireless_medium_annual_demand_kwh_new +
                    wireless_large_annual_demand_kwh_new
                    ) * (region[grid_type_handle] / 100)

                wireless_backhaul_demand_upgraded = (
                    wireless_small_annual_demand_kwh_upgraded +
                    wireless_medium_annual_demand_kwh_upgraded +
                    wireless_large_annual_demand_kwh_upgraded
                    ) * (region[grid_type_handle] / 100)

                wireless_backhaul_demand_existing = (
                    wireless_small_annual_demand_kwh_existing +
                    wireless_medium_annual_demand_kwh_existing +
                    wireless_large_annual_demand_kwh_existing
                    ) * (region[grid_type_handle] / 100)

                output.append({
                    'year': timestep,
                    'GID_0': region['GID_0'],
                    'decile': region['decile'],
                    'income': country['income'],
                    'geotype': geotype,
                    'scenario': option['scenario'],
                    'strategy': option['strategy'],
                    'confidence': global_parameters['confidence'][0],
                    'grid_type_perc': region[grid_type_handle],
                    'grid_type': grid_type,
                    'network_division': network_division,

                    'mno_energy_annual_demand_kwh_new': elec_demand_new,
                    'mno_equipment_annual_demand_kWh_new': equip_demand_new,
                    'mno_regional_nodes_annual_demand_kwh_new': regional_nodes_demand_new,
                    'mno_core_nodes_annual_demand_kwh_new': core_nodes_demand_new,
                    'mno_wireless_backhaul_annual_demand_kwh_new': wireless_backhaul_demand_new,
                    'total_energy_annual_demand_kwh_new': elec_demand_new * baseline_networks,
                    'total_equipment_annual_demand_kWh_new': equip_demand_new * baseline_networks,
                    'total_regional_nodes_annual_demand_kwh_new': regional_nodes_demand_new * baseline_networks,
                    'total_core_nodes_annual_demand_kwh_new': core_nodes_demand_new * baseline_networks,
                    'total_wireless_backhaul_annual_demand_kwh_new': wireless_backhaul_demand_new * baseline_networks,

                    'mno_energy_annual_demand_kwh_upgraded': elec_demand_upgraded,
                    'mno_equipment_annual_demand_kWh_upgraded': equip_demand_upgraded,
                    'mno_regional_nodes_annual_demand_kwh_upgraded': regional_nodes_demand_upgraded,
                    'mno_core_nodes_annual_demand_kwh_upgraded': core_nodes_demand_upgraded,
                    'mno_wireless_backhaul_annual_demand_kwh_upgraded': wireless_backhaul_demand_upgraded,
                    'total_energy_annual_demand_kwh_upgraded': elec_demand_upgraded * baseline_networks,
                    'total_equipment_annual_demand_kWh_upgraded': equip_demand_upgraded * baseline_networks,
                    'total_regional_nodes_annual_demand_kwh_upgraded': regional_nodes_demand_upgraded * baseline_networks,
                    'total_core_nodes_annual_demand_kwh_upgraded': core_nodes_demand_upgraded * baseline_networks,
                    'total_wireless_backhaul_annual_demand_kwh_upgraded': wireless_backhaul_demand_upgraded * baseline_networks,

                    'mno_energy_annual_demand_kwh_existing': elec_demand_existing,
                    'mno_equipment_annual_demand_kWh_existing': equip_demand_existing,
                    'mno_regional_nodes_annual_demand_kwh_existing': regional_nodes_demand_existing,
                    'mno_core_nodes_annual_demand_kwh_existing': core_nodes_demand_existing,
                    'mno_wireless_backhaul_annual_demand_kwh_existing': wireless_backhaul_demand_existing,
                    'total_energy_annual_demand_kwh_existing': elec_demand_existing * baseline_networks,
                    'total_equipment_annual_demand_kWh_existing': equip_demand_existing * baseline_networks,
                    'total_regional_nodes_annual_demand_kwh_existing': regional_nodes_demand_existing * baseline_networks,
                    'total_core_nodes_annual_demand_kwh_existing': core_nodes_demand_existing * baseline_networks,
                    'total_wireless_backhaul_annual_demand_kwh_existing': wireless_backhaul_demand_existing * baseline_networks,

                })

    return output


def calc_demand(total, region, grid_type_handle):

    demand = total * (region[grid_type_handle] / 100)

    return demand
