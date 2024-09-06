"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_emissions(country, deciles, on_grid_mix, emissions_lut):
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
    emissions = []

    for decile in deciles:

        decile_dict = {}
        existing_network_emissions_t_co2 = 0
        new_network_emissions_t_co2 = 0
    
        region = country['iea_classification']
        scenario = decile['energy_scenario']

        for energy_type, percentage in on_grid_mix.items():

            emissions_by_type = emissions_lut[region][scenario][energy_type]
            emissions_by_type_kg = emissions_by_type / 1000

            energy_type_key = 'existing_emissions_t_co2_' + energy_type
            existing_energy_kwh = (float(decile['network_existing_energy_kwh']) * 
                percentage)
            existing_emissions_t_co2 = round((existing_energy_kwh * 
                float(emissions_by_type_kg)) / 1000, 5
            )

            decile_dict[energy_type_key] = existing_emissions_t_co2
            existing_network_emissions_t_co2 += existing_emissions_t_co2
            # print(existing_emissions_t_co2)
            energy_type_key = 'new_emissions_t_co2_' + energy_type
            new_energy_kwh = (float(decile['network_new_energy_kwh']) * 
                percentage)
            new_emissions_t_co2 = round(
                new_energy_kwh * float(emissions_by_type_kg) / 1000, 5
            )
            # print(new_emissions_t_co2, new_energy_kwh, float(emissions_by_type_kg))
            decile_dict[energy_type_key] = new_emissions_t_co2
            new_network_emissions_t_co2 += new_emissions_t_co2

            emissions.append({
                'country_name': country['country_name'],
                'iso3': country['iso3'],
                'decile': decile['decile'],
                # 'population': decile['population_total'],  
                # 'area_km2': decile['area_km2'],        
                # 'population_km2': decile['population_km2'],
                'capacity': decile['capacity'],
                'generation': decile['generation'],
                'backhaul': decile['backhaul'],
                'energy_scenario': decile['energy_scenario'],
                'sharing_scenario': decile['sharing_scenario'],
                'income': country['income'],
                'wb_region': country['wb_region'],
                'adb_region': country['adb_region'],
                'iea_classification': country['iea_classification'],
                'product': energy_type,
                'existing_energy_kwh': existing_energy_kwh,
                'new_energy_kwh': new_energy_kwh,
                'existing_emissions_t_co2': existing_emissions_t_co2,
                'new_emissions_t_co2': new_emissions_t_co2,
            })

        decile_dict['network_existing_emissions_t_co2'] = existing_network_emissions_t_co2
        decile_dict['network_new_emissions_t_co2'] = new_network_emissions_t_co2
        decile.update(decile_dict)
        # print(decile_dict)
        output.append(decile) #dict2.update(dict1)
    # print(output[0]['existing_emissions_t_co2_oil'])
    return output, emissions
