"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_energy(country, deciles):
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

    return output

