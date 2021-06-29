"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_energy(country, regions, assets, option, global_parameters,
    country_parameters, timesteps, energy_demand, tech_lut):
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

        on_grid_demand = total_annual_energy_demand_kwh * region['on_grid_perc']
        off_grid_demand = total_annual_energy_demand_kwh * region['off_grid_perc']

        emissions = calc_emissions(
            on_grid_demand,
            off_grid_demand,
            tech_lut
        )

        output.append({
            'GID_id': region['GID_id'],
            'scenario': option['scenario'],
            'strategy': option['strategy'],
            'confidence': global_parameters['confidence'],
            'total_sites': region['total_sites'],
            'total_upgraded_sites': region['total_upgraded_sites'],
            'total_new_sites': region['total_new_sites'],
            'on_grid_perc': region['on_grid_perc'],
            'off_grid_perc': region['off_grid_perc'],
            'equipment_annual_demand_kWh': equipment_annual_demand_kwh,
            'regional_nodes_annual_demand_kwh': regional_nodes_annual_demand_kwh,
            'core_nodes_annual_demand_kwh': core_nodes_annual_demand_kwh,
            'total_annual_energy_demand_kwh': total_annual_energy_demand_kwh,
            'on_grid_demand_carbon_per_kwh': emissions['on_grid_demand_carbon_per_kwh'],
            'on_grid_nitrogen_oxide_per_kwh': emissions['on_grid_nitrogen_oxide_per_kwh'],
            'on_grid_sulpher_dioxide_per_kwh': emissions['on_grid_sulpher_dioxide_per_kwh'],
            'on_grid_pm10_per_kwh': emissions['on_grid_pm10_per_kwh'],
            'off_grid_demand_carbon_per_kwh': emissions['off_grid_demand_carbon_per_kwh'],
            'off_grid_nitrogen_oxide_per_kwh': emissions['off_grid_nitrogen_oxide_per_kwh'],
            'off_grid_sulpher_dioxide_per_kwh': emissions['off_grid_sulpher_dioxide_per_kwh'],
            'off_grid_pm10_per_kwh': emissions['off_grid_pm10_per_kwh'],
        })

    return output


def calc_emissions(on_grid_demand, off_grid_demand, tech_lut):
    """
    Calculate emissions

    """
    emissions = {}

    on_grid_mix = {
        'hydro': 31,
        'oil': 22,
        'gas': 17,
        'coal': 18,
        'renewables': 12,
    }

    carbon_per_kwh = []
    nitrogen_oxide_per_kwh = []
    sulpher_dioxide_per_kwh = []
    pm10_per_kwh = []

    for energy_type, percentage in on_grid_mix.items():

        emissions_by_type = tech_lut[energy_type]

        carbon_per_kwh.append((percentage / 100) * emissions_by_type['carbon_per_kWh'])
        nitrogen_oxide_per_kwh.append((percentage / 100) * emissions_by_type['nitrogen_oxide_per_kWh'])
        sulpher_dioxide_per_kwh.append((percentage / 100) * emissions_by_type['sulpher_dioxide_per_kWh'])
        pm10_per_kwh.append((percentage / 100) * emissions_by_type['pm10_per_kWh'])

    emissions['on_grid_demand_carbon_per_kwh'] = (
        sum(carbon_per_kwh) / len(carbon_per_kwh)) * on_grid_demand
    emissions['on_grid_nitrogen_oxide_per_kwh'] = (
        sum(nitrogen_oxide_per_kwh) / len(nitrogen_oxide_per_kwh)) * on_grid_demand
    emissions['on_grid_sulpher_dioxide_per_kwh'] = (
        sum(sulpher_dioxide_per_kwh) / len(sulpher_dioxide_per_kwh)) * on_grid_demand
    emissions['on_grid_pm10_per_kwh'] = (
        sum(pm10_per_kwh) / len(pm10_per_kwh)) * on_grid_demand

    emissions_by_type = tech_lut['diesel']

    emissions['off_grid_demand_carbon_per_kwh'] = (
        emissions_by_type['carbon_per_kWh'] * off_grid_demand)
    emissions['off_grid_nitrogen_oxide_per_kwh'] = (
        emissions_by_type['nitrogen_oxide_per_kWh'] * off_grid_demand)
    emissions['off_grid_sulpher_dioxide_per_kwh'] = (
        emissions_by_type['sulpher_dioxide_per_kWh'] * off_grid_demand)
    emissions['off_grid_pm10_per_kwh'] = (
        emissions_by_type['pm10_per_kWh'] * off_grid_demand)

    return emissions
