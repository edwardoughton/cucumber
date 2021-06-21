"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_energy(country, regions, option, global_parameters,
    country_parameters, timesteps):
    """
    For each region, calculate energy consumption and associated emissions.

    Parameters
    ----------
    country : dict
        Country information.
    regions : dataframe
        Geopandas dataframe of all regions.
    option : dict
        Contains the scenario and strategy. The strategy string controls
        the strategy variants being testes in the model and is defined based
        on the type of technology generation, core and backhaul, and the level
        of sharing, subsidy, spectrum and tax.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    output : list of dicts
        Contains all output data.

    """
    output = []

    for region in regions:

        output.append({
            'scenario': option['scenario'],
            'strategy': option['strategy'],
            'confidence': global_parameters['confidence'],
            'total_sites': region['total_sites'],
            'total_upgraded_sites': region['total_upgraded_sites'],
            'total_new_sites': region['total_new_sites'],
        })

    return output
