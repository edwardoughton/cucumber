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

        equipment_quantity = 0
        regional_nodes = 0
        core_nodes = 0

        for asset in assets:
            if asset['GID_id'] == region['GID_id']:

                if 'equipment' in asset.values():
                    equipment_quantity += asset['quantity']
                if 'regional_node' in asset.values():
                    regional_nodes += asset['quantity']
                if 'core_node' in asset.values():
                    core_nodes += asset['quantity']
        # print(equipment_quantity, regional_nodes, core_nodes)
        equipment_hourly_demand_kwh = equipment_quantity * energy_demand['equipment_kwh']
        regional_nodes_hourly_demand_kwh = regional_nodes * energy_demand['regional_node_kwh']
        core_nodes_hourly_demand_kwh = core_nodes * energy_demand['core_node_kwh']

        equipment_annual_demand_kwh = equipment_hourly_demand_kwh * 12 * 365
        regional_nodes_annual_demand_kwh = regional_nodes_hourly_demand_kwh * 12 * 365
        core_nodes_annual_demand_kwh = core_nodes_hourly_demand_kwh * 12 * 365

        total_annual_energy_demand_kwh = (
            equipment_annual_demand_kwh +
            regional_nodes_annual_demand_kwh +
            core_nodes_annual_demand_kwh
        )

        grid_types = [
            'on_grid',
            'off_grid'
        ]

        for grid_type in grid_types:

            grid_type_handle = grid_type + '_perc'

            elec_demand = total_annual_energy_demand_kwh * (region[grid_type_handle] / 100)
            equip_demand = equipment_annual_demand_kwh * (region[grid_type_handle] / 100)
            regional_nodes_demand = regional_nodes_annual_demand_kwh * (region[grid_type_handle] / 100)
            core_nodes_demand = core_nodes_annual_demand_kwh * (region[grid_type_handle] / 100)

            output.append({
                'GID_id': region['GID_id'],
                'scenario': option['scenario'],
                'strategy': option['strategy'],
                'confidence': global_parameters['confidence'],
                'total_sites': region['total_sites'],
                'total_upgraded_sites': region['total_upgraded_sites'],
                'total_new_sites': region['total_new_sites'],
                'grid_type_perc': region[grid_type_handle],
                'grid_type': grid_type,
                'total_annual_energy_demand_kwh': elec_demand,
                'equipment_annual_demand_kWh': equip_demand,
                'regional_nodes_annual_demand_kwh': regional_nodes_demand,
                'core_nodes_annual_demand_kwh': core_nodes_demand,
            })

    return output
