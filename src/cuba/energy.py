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

    for decile in deciles:

        #get energy use for existing sites in 1 year
        decile['total_existing_energy_kwh'] =  (
            decile['total_existing_sites'] * 1 * #kwh per site
            24 * 365 
        )

        #get energy use for all sites in 1 year
        decile['total_new_energy_kwh'] =  (
            decile['total_new_sites'] * 1 * #kwh per site
            24 * 365  
        )

        output.append(decile)

    return output

