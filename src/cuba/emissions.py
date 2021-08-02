"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_emissions(data_energy, tech_lut, on_grid_mix, timesteps, option):
    """
    Calculate emissions.

    """
    output = []

    for timestep in timesteps:

        for item in data_energy:

            strategy = item['strategy']

            power_strategy = strategy.split('_')[7]

            if timestep == item['year']:

                annual_on_grid_mix = on_grid_mix[timestep]

                if item['grid_type'] == 'on_grid':

                    carbon_per_kwh = []
                    nitrogen_oxide_per_kwh = []
                    sulpher_dioxide_per_kwh = []
                    pm10_per_kwh = []

                    for energy_type, percentage in annual_on_grid_mix.items():

                        emissions_by_type = tech_lut[energy_type]

                        carbon_per_kwh.append((percentage / 100) * emissions_by_type['carbon_per_kWh'])
                        nitrogen_oxide_per_kwh.append((percentage / 100) * emissions_by_type['nitrogen_oxide_per_kWh'])
                        sulpher_dioxide_per_kwh.append((percentage / 100) * emissions_by_type['sulpher_dioxide_per_kWh'])
                        pm10_per_kwh.append((percentage / 100) * emissions_by_type['pm10_per_kWh'])

                    demand_carbon_per_kwh = (
                        sum(carbon_per_kwh) / len(carbon_per_kwh)) * item['total_energy_annual_demand_kwh']
                    nitrogen_oxide_per_kwh = (
                        sum(nitrogen_oxide_per_kwh) / len(nitrogen_oxide_per_kwh)) * item['total_energy_annual_demand_kwh']
                    sulpher_dioxide_per_kwh = (
                        sum(sulpher_dioxide_per_kwh) / len(sulpher_dioxide_per_kwh)) * item['total_energy_annual_demand_kwh']
                    pm10_per_kwh = (
                        sum(pm10_per_kwh) / len(pm10_per_kwh)) * item['total_energy_annual_demand_kwh']

                if item['grid_type'] == 'grid_other' and power_strategy == 'baseline':

                    emissions_by_type = tech_lut['diesel']

                    demand_carbon_per_kwh = (
                        emissions_by_type['carbon_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    nitrogen_oxide_per_kwh = (
                        emissions_by_type['nitrogen_oxide_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    sulpher_dioxide_per_kwh = (
                        emissions_by_type['sulpher_dioxide_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    pm10_per_kwh = (
                        emissions_by_type['pm10_per_kWh'] * item['total_energy_annual_demand_kwh'])

                if item['grid_type'] == 'grid_other' and power_strategy == 'renewable':

                    emissions_by_type = tech_lut['renewables']

                    demand_carbon_per_kwh = (
                        emissions_by_type['carbon_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    nitrogen_oxide_per_kwh = (
                        emissions_by_type['nitrogen_oxide_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    sulpher_dioxide_per_kwh = (
                        emissions_by_type['sulpher_dioxide_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    pm10_per_kwh = (
                        emissions_by_type['pm10_per_kWh'] * item['total_energy_annual_demand_kwh'])

                output.append({
                    'year': timestep,
                    'GID_id': item['GID_id'],
                    'scenario': item['scenario'],
                    'strategy': item['strategy'],
                    'confidence': item['confidence'],
                    'total_sites': item['total_sites'],
                    'total_upgraded_sites': item['total_upgraded_sites'],
                    'total_new_sites': item['total_new_sites'],
                    'grid_type_perc': item['grid_type_perc'],
                    'grid_type': item['grid_type'],
                    'total_energy_annual_demand_kwh': item['total_energy_annual_demand_kwh'],
                    'demand_carbon_per_kwh': demand_carbon_per_kwh,
                    'nitrogen_oxide_per_kwh': nitrogen_oxide_per_kwh,
                    'sulpher_dioxide_per_kwh': sulpher_dioxide_per_kwh,
                    'pm10_per_kwh': pm10_per_kwh,
                })

    return output
