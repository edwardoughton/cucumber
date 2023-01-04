"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_emissions(data_energy, tech_lut, on_grid_mix, timesteps, option, country_parameters):
    """
    Calculate emissions.

    """
    output = []

    for timestep in timesteps:

        for item in data_energy:

            geotype = item['geotype'].split(' ')[0]
            net_handle = option['strategy'].split('_')[4] + '_' + geotype

            power_strategy = option['strategy'].split('_')[7]

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

                    mno_demand_carbon_per_kwh = (
                        sum(carbon_per_kwh) / len(carbon_per_kwh)) * item['mno_energy_annual_demand_kwh']
                    mno_nitrogen_oxide_per_kwh = (
                        sum(nitrogen_oxide_per_kwh) / len(nitrogen_oxide_per_kwh)) * item['mno_energy_annual_demand_kwh']
                    mno_sulpher_dioxide_per_kwh = (
                        sum(sulpher_dioxide_per_kwh) / len(sulpher_dioxide_per_kwh)) * item['mno_energy_annual_demand_kwh']
                    mno_pm10_per_kwh = (
                        sum(pm10_per_kwh) / len(pm10_per_kwh)) * item['mno_energy_annual_demand_kwh']

                    total_demand_carbon_per_kwh = (
                        sum(carbon_per_kwh) / len(carbon_per_kwh)) * item['total_energy_annual_demand_kwh']
                    total_nitrogen_oxide_per_kwh = (
                        sum(nitrogen_oxide_per_kwh) / len(nitrogen_oxide_per_kwh)) * item['total_energy_annual_demand_kwh']
                    total_sulpher_dioxide_per_kwh = (
                        sum(sulpher_dioxide_per_kwh) / len(sulpher_dioxide_per_kwh)) * item['total_energy_annual_demand_kwh']
                    total_pm10_per_kwh = (
                        sum(pm10_per_kwh) / len(pm10_per_kwh)) * item['total_energy_annual_demand_kwh']

                if item['grid_type'] == 'grid_other' and power_strategy == 'baseline':

                    emissions_by_type = tech_lut['diesel']

                    mno_demand_carbon_per_kwh = (
                        emissions_by_type['carbon_per_kWh'] * item['mno_energy_annual_demand_kwh'])
                    mno_nitrogen_oxide_per_kwh = (
                        emissions_by_type['nitrogen_oxide_per_kWh'] * item['mno_energy_annual_demand_kwh'])
                    mno_sulpher_dioxide_per_kwh = (
                        emissions_by_type['sulpher_dioxide_per_kWh'] * item['mno_energy_annual_demand_kwh'])
                    mno_pm10_per_kwh = (
                        emissions_by_type['pm10_per_kWh'] * item['mno_energy_annual_demand_kwh'])

                    total_demand_carbon_per_kwh = (
                        emissions_by_type['carbon_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    total_nitrogen_oxide_per_kwh = (
                        emissions_by_type['nitrogen_oxide_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    total_sulpher_dioxide_per_kwh = (
                        emissions_by_type['sulpher_dioxide_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    total_pm10_per_kwh = (
                        emissions_by_type['pm10_per_kWh'] * item['total_energy_annual_demand_kwh'])

                if item['grid_type'] == 'grid_other' and power_strategy == 'renewable':

                    emissions_by_type = tech_lut['renewables']

                    mno_demand_carbon_per_kwh = (
                        emissions_by_type['carbon_per_kWh'] * item['mno_energy_annual_demand_kwh'])
                    mno_nitrogen_oxide_per_kwh = (
                        emissions_by_type['nitrogen_oxide_per_kWh'] * item['mno_energy_annual_demand_kwh'])
                    mno_sulpher_dioxide_per_kwh = (
                        emissions_by_type['sulpher_dioxide_per_kWh'] * item['mno_energy_annual_demand_kwh'])
                    mno_pm10_per_kwh = (
                        emissions_by_type['pm10_per_kWh'] * item['mno_energy_annual_demand_kwh'])

                    total_demand_carbon_per_kwh = (
                        emissions_by_type['carbon_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    total_nitrogen_oxide_per_kwh = (
                        emissions_by_type['nitrogen_oxide_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    total_sulpher_dioxide_per_kwh = (
                        emissions_by_type['sulpher_dioxide_per_kWh'] * item['total_energy_annual_demand_kwh'])
                    total_pm10_per_kwh = (
                        emissions_by_type['pm10_per_kWh'] * item['total_energy_annual_demand_kwh'])

                output.append({
                    'year': timestep,
                    'GID_0': item['GID_0'],
                    'decile': item['decile'],
                    'scenario': item['scenario'],
                    'strategy': item['strategy'],
                    'confidence': item['confidence'],
                    'grid_type_perc': item['grid_type_perc'],
                    'grid_type': item['grid_type'],
                    'mno_energy_annual_demand_kwh': item['mno_energy_annual_demand_kwh'],
                    'mno_demand_carbon_tonnes': mno_demand_carbon_per_kwh / 1e3,
                    'mno_nitrogen_oxide_tonnes': mno_nitrogen_oxide_per_kwh / 1e3,
                    'mno_sulpher_dioxide_tonnes': mno_sulpher_dioxide_per_kwh / 1e3,
                    'mno_pm10_tonnes': mno_pm10_per_kwh / 1e3,
                    'total_energy_annual_demand_kwh': item['total_energy_annual_demand_kwh'],
                    'total_demand_carbon_tonnes': total_demand_carbon_per_kwh / 1e3,
                    'total_nitrogen_oxide_tonnes': total_nitrogen_oxide_per_kwh / 1e3,
                    'total_sulpher_dioxide_tonnes': total_sulpher_dioxide_per_kwh / 1e3,
                    'total_pm10_tonnes': total_pm10_per_kwh / 1e3,
                })

    return output
