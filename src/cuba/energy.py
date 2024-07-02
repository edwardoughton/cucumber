"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_energy(country, deciles, on_grid_mix):
    """
    Estimate energy consumption.

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
    energy = []
    
    site_kwh = country['energy_equipment_kwh'] #1 #kwh per site
    wireless_bh_kwh = country['energy_wireless_medium_kwh'] #0.5 #kwh per link
    fiber_bh_kwh = country['energy_fiber_kwh'] #0.01 #kwh per link
    
    for decile in deciles:

        if decile['backhaul'] == 'wireless':
            selected_backhaul = wireless_bh_kwh
        elif decile['backhaul'] == 'fiber':
            selected_backhaul = fiber_bh_kwh

        existing_site_energy_kwh = (
            decile['total_existing_sites'] * site_kwh * #kwh per site
            24 * 365
        )
        existing_backhaul_energy_kwh = (
            (decile['backhaul_wireless'] * wireless_bh_kwh * 24 * 365) + #kwh per site
            (decile['backhaul_fiber'] * fiber_bh_kwh * 24 * 365) 
        )
        #get energy use for existing sites in 1 year
        decile['total_existing_energy_kwh'] = (
            existing_site_energy_kwh + existing_backhaul_energy_kwh
        )

        new_site_energy_kwh = (
            decile['total_new_sites'] * site_kwh * #kwh per site
            24 * 365
        )
        new_backhaul_energy_kwh = (
            (decile['backhaul_new'] * selected_backhaul * 24 * 365)
        )
        #get energy use for new sites in 1 year
        decile['total_new_energy_kwh'] = (
            new_site_energy_kwh + new_backhaul_energy_kwh
        )

        output.append(decile)

        for energy_type, percentage in on_grid_mix.items():

            existing_energy_kwh = round(
                float(decile['total_existing_energy_kwh']) * 
                (percentage / 100) , 1
            )
            new_energy_kwh = round(
                float(decile['total_new_energy_kwh']) * 
                (percentage / 100) , 1
            )

            energy.append({
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
                'income': country['income'],
                'wb_region': country['wb_region'],
                'iea_classification': country['iea_classification'],
                'product': energy_type,
                'total_existing_energy_kwh': existing_energy_kwh,
                'new_existing_energy_kwh': new_energy_kwh,
            })

    return output, energy

