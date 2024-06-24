"""
Cost module
Author: Edward Oughton
Date: June 2021

"""
import math
from itertools import tee
import collections, functools, operator
import pandas as pd


def assess_cost(country, deciles):
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

        decile['cost_equipment_usd'] =  (
            decile['total_new_sites'] * 
            country['cost_equipment']  
        )

        decile['cost_site_build_usd'] =  (
            decile['total_new_sites'] * 
            country['cost_site_build']  
        )

        decile['cost_installation_usd'] =  (
            decile['total_new_sites'] * 
            country['cost_installation']  
        )

        decile['cost_operation_and_maintenance_usd'] =  (
            decile['total_new_sites'] * 
            country['cost_operation_and_maintenance']  
        )

        decile['cost_power_usd'] =  (
            decile['total_new_sites'] * 
            country['cost_power']  
        )

        decile['total_new_cost_usd'] = (
            decile['cost_equipment_usd'] + 
            decile['cost_site_build_usd'] +
            decile['cost_installation_usd'] + 
            decile['cost_operation_and_maintenance_usd'] +
            decile['cost_power_usd']  
        )

        output.append(decile)

    return output

