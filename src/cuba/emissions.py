"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_emissions(country, deciles, on_grid_mix, emissions_fectors):
    """
    Estimate emissions.

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
        
        decile_dict = {}
        existing_total_emissions_t_co2 = 0
        new_total_emissions_t_co2 = 0

        #2030: {'renewables': 60.0, 'nuclear': 17.0, 'gas': 18.0, 'coal': 6.0}
        # annual_on_grid_mix = on_grid_mix[2030] 

        for energy_type, percentage in on_grid_mix.items():

            emissions_by_type = emissions_fectors[energy_type.lower()]['carbon_per_kWh']

            energy_type_key = 'existing_emissions_t_co2_' + energy_type
            existing_emissions_t_co2 = round(
                float(decile['total_existing_energy_kwh']) * 
                (percentage / 100) * float(emissions_by_type) / 1000, 1
            )
            decile_dict[energy_type_key] = existing_emissions_t_co2
            existing_total_emissions_t_co2 += existing_emissions_t_co2

            energy_type_key = 'new_emissions_t_co2_' + energy_type

            new_emissions_t_co2 = round(
                float(decile['total_new_energy_kwh']) * 
                (percentage / 100) * float(emissions_by_type) / 1000, 1
            )
            decile_dict[energy_type_key] = new_emissions_t_co2
            new_total_emissions_t_co2 += new_emissions_t_co2

        decile_dict['existing_total_emissions_t_co2'] = existing_total_emissions_t_co2
        decile_dict['new_total_emissions_t_co2'] = new_total_emissions_t_co2
        
        output.append(decile.update(decile_dict)) #dict2.update(dict1)

    return output
