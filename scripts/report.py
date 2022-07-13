"""
Generate country reports.

Written by Ed Oughton.

May 2021

"""
import os
import configparser
import pandas as pd
import glob

from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

from countries import COUNTRY_LIST

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
RESULTS = os.path.join(BASE_PATH, '..', 'results')
IMAGES = "D:\\Github\\cuba\\reports\\images" #unfortunately needs hard coding
OUTPUT = os.path.join(BASE_PATH, '..', 'reports', 'countries')


def generate_report(country):
    """
    Meta function to generate a report.
    """
    iso3 = country['iso3']

    sites = get_sites(iso3)
    tech_percs = get_tech_percentages(iso3)
    share_percs = get_sharing_data(iso3)
    policy_percs = get_policy_data(iso3)
    energy_percs = get_emissions_data(iso3)
    power_percs = get_power_data(iso3)
    shared_energy_percs = get_shared_emissions_data(iso3)

    policy_inputs = get_policy_inputs(iso3)
    energy_gen = get_energy_gen_inputs(country['iea_group'])
    hist_emissions = historical_emissions(iso3)

    path = os.path.join(BASE_PATH, '..', 'reports', 'templates')
    env = Environment(loader=FileSystemLoader(path))

    template = env.get_template('template.html')

    template_vars = {
        "css_location": "D:\\Github\\cuba\\reports\\templates\\style_template.css",
        "prefered_name" : country['prefered_name'],
        "country": iso3,
        "figure_1": os.path.join(IMAGES, iso3, 'social_costs_by_strategy.png'),
        # "upgraded_sites_baseline_50gbmonth_3g_w": sites['baseline_50gbmonth_3g_w']['total_upgraded_sites'],
        # "new_sites_baseline_50gbmonth_3g_w": sites['baseline_50gbmonth_3g_w']['total_new_sites'],
        "upgraded_sites_baseline_50gbmonth_4g_w": sites['baseline_50gbmonth_4g_w']['total_upgraded_sites'],
        "new_sites_baseline_50gbmonth_4g_w": sites['baseline_50gbmonth_4g_w']['total_new_sites'],
        "upgraded_sites_baseline_50gbmonth_5g_w": sites['baseline_50gbmonth_5g_w']['total_upgraded_sites'],
        "new_sites_baseline_50gbmonth_5g_w": sites['baseline_50gbmonth_5g_w']['total_new_sites'],
        # "baseline_50gbmonth_3g_w": tech_percs['baseline_50gbmonth_3g_w']['social_cost_bn'],
        "baseline_50gbmonth_4g_w": tech_percs['baseline_50gbmonth_4g_w']['social_cost_bn'],
        "baseline_50gbmonth_5g_w": tech_percs['baseline_50gbmonth_5g_w']['social_cost_bn'],
        # "w_over_fb_3g_50gbmonth": round(abs(tech_percs['baseline_50gbmonth_3g_w']['w_over_fb'])),
        "w_over_fb_4g_50gbmonth": round(abs(tech_percs['baseline_50gbmonth_4g_w']['w_over_fb'])),
        "w_over_fb_5g_50gbmonth": round(abs(tech_percs['baseline_50gbmonth_5g_w']['w_over_fb'])),
        # "perc_saving_vs_3g_4g_50gbmonth": round(abs(tech_percs['baseline_50gbmonth_4g_w']['perc_saving_vs_3g'])),
        # "perc_saving_vs_3g_5g_50gbmonth": round(abs(tech_percs['baseline_50gbmonth_5g_w']['perc_saving_vs_3g'])),
        # "low_50gbmonth_3g_w": tech_percs['low_50gbmonth_3g_w']['social_cost_bn'],
        "low_50gbmonth_4g_w": tech_percs['low_50gbmonth_4g_w']['social_cost_bn'],
        "low_50gbmonth_5g_w": tech_percs['low_50gbmonth_5g_w']['social_cost_bn'],
        # "high_50gbmonth_3g_w": tech_percs['high_50gbmonth_3g_w']['social_cost_bn'],
        "high_50gbmonth_4g_w": tech_percs['high_50gbmonth_4g_w']['social_cost_bn'],
        "high_50gbmonth_5g_w": tech_percs['high_50gbmonth_5g_w']['social_cost_bn'],
        # "baseline_25gbmonth_3g_w": tech_percs['baseline_25gbmonth_3g_w']['social_cost_bn'],
        "baseline_25gbmonth_4g_w": tech_percs['baseline_25gbmonth_4g_w']['social_cost_bn'],
        "baseline_25gbmonth_5g_w": tech_percs['baseline_25gbmonth_5g_w']['social_cost_bn'],
        # "baseline_100gbmonth_3g_w": tech_percs['baseline_100gbmonth_3g_w']['social_cost_bn'],
        "baseline_100gbmonth_4g_w": tech_percs['baseline_100gbmonth_4g_w']['social_cost_bn'],
        "baseline_100gbmonth_5g_w": tech_percs['baseline_100gbmonth_5g_w']['social_cost_bn'],
        "figure_2": os.path.join(IMAGES, iso3, 'social_costs_by_sharing_strategy.png'),
        "passive_vs_base_4g_50gbmonth": round(abs(share_percs['baseline_50gbmonth_passive']['saving_against_baseline'])),
        "active_vs_base_4g_50gbmonth": round(abs(share_percs['baseline_50gbmonth_active']['saving_against_baseline'])),
        "srn_vs_base_4g_50gbmonth": round(abs(share_percs['baseline_50gbmonth_srn']['saving_against_baseline'])),
        "passive_cost_4g_50gbmonth": share_percs['baseline_50gbmonth_passive']['social_cost_bn'],
        "active_cost_4g_50gbmonth": share_percs['baseline_50gbmonth_active']['social_cost_bn'],
        "srn_cost_4g_50gbmonth": share_percs['baseline_50gbmonth_srn']['social_cost_bn'],
        "figure_3": os.path.join(IMAGES, iso3, 'social_costs_by_policy_options.png'),
        "tax_low": int(float(policy_inputs['tax_low'])),
        "tax_baseline": int(float(policy_inputs['tax_baseline'])),
        "tax_high": int(float(policy_inputs['tax_high'])),
        "perc_lowtax": policy_percs['baseline_50gbmonth_lowtax']['perc_against_baseline'],
        "perc_hightax": policy_percs['baseline_50gbmonth_hightax']['perc_against_baseline'],
        "lowtax_cost_4g_50gbmonth": policy_percs['baseline_50gbmonth_lowtax']['social_cost_bn'],
        "hightax_cost_4g_50gbmonth": policy_percs['baseline_50gbmonth_hightax']['social_cost_bn'],
        "baselinetax_cost_4g_50gbmonth": policy_percs['baseline_50gbmonth_baseline']['social_cost_bn'],
        "profit_margin": int(float(policy_inputs['profit_margin'])),
        "spectrum_coverage_baseline_usd_mhz_pop": policy_inputs['spectrum_coverage_baseline_usd_mhz_pop'],
        "spectrum_capacity_baseline_usd_mhz_pop": policy_inputs['spectrum_capacity_baseline_usd_mhz_pop'],
        "spectrum_cost_low": int(float(policy_inputs['spectrum_cost_low'])),
        "spectrum_cost_high": int(float(policy_inputs['spectrum_cost_high'])),
        "perc_lowspectrum": policy_percs['baseline_50gbmonth_lowspectrumfees']['perc_against_baseline'],
        "perc_highspectrum": policy_percs['baseline_50gbmonth_highspectrumfees']['perc_against_baseline'],
        "lowspectrum_cost_4g_50gbmonth": policy_percs['baseline_50gbmonth_lowspectrumfees']['social_cost_bn'],
        "highspectrum_cost_4g_50gbmonth": policy_percs['baseline_50gbmonth_highspectrumfees']['social_cost_bn'],

        "iea_group": country['iea_group'],
        "coal_2020_perc": energy_gen['coal_2020_perc'],
        "gas_2020_perc": energy_gen['gas_2020_perc'],
        "renewables_2020_perc": energy_gen['renewables_2020_perc'],
        "nuclear_2020_perc": energy_gen['nuclear_2020_perc'],
        "coal_2030_perc": energy_gen['coal_2030_perc'],
        "gas_2030_perc": energy_gen['gas_2030_perc'],
        "renewables_2030_perc": energy_gen['renewables_2030_perc'],
        "nuclear_2030_perc": energy_gen['nuclear_2030_perc'],

        "figure_4": os.path.join(IMAGES, iso3, 'energy_emissions.png'),
        "figure_5": os.path.join(IMAGES, iso3, 'health_emissions.png'),

        "energy_baseline_25gbmonth_4g_w": float(round(energy_percs['baseline_25gbmonth_4g_w']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_25gbmonth_4g_fb": float(round(energy_percs['baseline_25gbmonth_4g_fb']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_25gbmonth_5g_w": float(round(energy_percs['baseline_25gbmonth_5g_w']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_25gbmonth_5g_fb": float(round(energy_percs['baseline_25gbmonth_5g_fb']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_50gbmonth_4g_w": float(round(energy_percs['baseline_50gbmonth_4g_w']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_50gbmonth_4g_fb": float(round(energy_percs['baseline_50gbmonth_4g_fb']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_50gbmonth_5g_w": float(round(energy_percs['baseline_50gbmonth_5g_w']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_50gbmonth_5g_fb": float(round(energy_percs['baseline_50gbmonth_5g_fb']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_100gbmonth_4g_w": float(round(energy_percs['baseline_100gbmonth_4g_w']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_100gbmonth_4g_fb": float(round(energy_percs['baseline_100gbmonth_4g_fb']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_100gbmonth_5g_w": float(round(energy_percs['baseline_100gbmonth_5g_w']['total_energy_annual_demand_kwh']/1e9,1)),
        "energy_baseline_100gbmonth_5g_fb": float(round(energy_percs['baseline_100gbmonth_5g_fb']['total_energy_annual_demand_kwh']/1e9,1)),

        "carbon_baseline_25gbmonth_4g_w": float(round(energy_percs['baseline_25gbmonth_4g_w']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_25gbmonth_4g_fb": float(round(energy_percs['baseline_25gbmonth_4g_fb']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_25gbmonth_5g_w": float(round(energy_percs['baseline_25gbmonth_5g_w']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_25gbmonth_5g_fb": float(round(energy_percs['baseline_25gbmonth_5g_fb']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_50gbmonth_4g_w": float(round(energy_percs['baseline_50gbmonth_4g_w']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_50gbmonth_4g_fb": float(round(energy_percs['baseline_50gbmonth_4g_fb']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_50gbmonth_5g_w": float(round(energy_percs['baseline_50gbmonth_5g_w']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_50gbmonth_5g_fb": float(round(energy_percs['baseline_50gbmonth_5g_fb']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_100gbmonth_4g_w": float(round(energy_percs['baseline_100gbmonth_4g_w']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_100gbmonth_4g_fb": float(round(energy_percs['baseline_100gbmonth_4g_fb']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_100gbmonth_5g_w": float(round(energy_percs['baseline_100gbmonth_5g_w']['total_demand_carbon_tonnes']/1e6,1)),
        "carbon_baseline_100gbmonth_5g_fb": float(round(energy_percs['baseline_100gbmonth_5g_fb']['total_demand_carbon_tonnes']/1e6,1)),

        "nitrogen_baseline_25gbmonth_4g_w": float(round(energy_percs['baseline_25gbmonth_4g_w']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_25gbmonth_4g_fb": float(round(energy_percs['baseline_25gbmonth_4g_fb']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_25gbmonth_5g_w": float(round(energy_percs['baseline_25gbmonth_5g_w']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_25gbmonth_5g_fb": float(round(energy_percs['baseline_25gbmonth_5g_fb']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_50gbmonth_4g_w": float(round(energy_percs['baseline_50gbmonth_4g_w']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_50gbmonth_4g_fb": float(round(energy_percs['baseline_50gbmonth_4g_fb']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_50gbmonth_5g_w": float(round(energy_percs['baseline_50gbmonth_5g_w']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_50gbmonth_5g_fb": float(round(energy_percs['baseline_50gbmonth_5g_fb']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_100gbmonth_4g_w": float(round(energy_percs['baseline_100gbmonth_4g_w']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_100gbmonth_4g_fb": float(round(energy_percs['baseline_100gbmonth_4g_fb']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_100gbmonth_5g_w": float(round(energy_percs['baseline_100gbmonth_5g_w']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "nitrogen_baseline_100gbmonth_5g_fb": float(round(energy_percs['baseline_100gbmonth_5g_fb']['total_nitrogen_oxide_tonnes']/1e3,1)),

        "sulpher_baseline_25gbmonth_4g_w": float(round(energy_percs['baseline_25gbmonth_4g_w']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_25gbmonth_4g_fb": float(round(energy_percs['baseline_25gbmonth_4g_fb']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_25gbmonth_5g_w": float(round(energy_percs['baseline_25gbmonth_5g_w']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_25gbmonth_5g_fb": float(round(energy_percs['baseline_25gbmonth_5g_fb']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_50gbmonth_4g_w": float(round(energy_percs['baseline_50gbmonth_4g_w']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_50gbmonth_4g_fb": float(round(energy_percs['baseline_50gbmonth_4g_fb']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_50gbmonth_5g_w": float(round(energy_percs['baseline_50gbmonth_5g_w']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_50gbmonth_5g_fb": float(round(energy_percs['baseline_50gbmonth_5g_fb']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_100gbmonth_4g_w": float(round(energy_percs['baseline_100gbmonth_4g_w']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_100gbmonth_4g_fb": float(round(energy_percs['baseline_100gbmonth_4g_fb']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_100gbmonth_5g_w": float(round(energy_percs['baseline_100gbmonth_5g_w']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "sulpher_baseline_100gbmonth_5g_fb": float(round(energy_percs['baseline_100gbmonth_5g_fb']['total_sulpher_dioxide_tonnes']/1e3,1)),

        "pm10_baseline_25gbmonth_4g_w": float(round(energy_percs['baseline_25gbmonth_4g_w']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_25gbmonth_4g_fb": float(round(energy_percs['baseline_25gbmonth_4g_fb']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_25gbmonth_5g_w": float(round(energy_percs['baseline_25gbmonth_5g_w']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_25gbmonth_5g_fb": float(round(energy_percs['baseline_25gbmonth_5g_fb']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_50gbmonth_4g_w": float(round(energy_percs['baseline_50gbmonth_4g_w']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_50gbmonth_4g_fb": float(round(energy_percs['baseline_50gbmonth_4g_fb']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_50gbmonth_5g_w": float(round(energy_percs['baseline_50gbmonth_5g_w']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_50gbmonth_5g_fb": float(round(energy_percs['baseline_50gbmonth_5g_fb']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_100gbmonth_4g_w": float(round(energy_percs['baseline_100gbmonth_4g_w']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_100gbmonth_4g_fb": float(round(energy_percs['baseline_100gbmonth_4g_fb']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_100gbmonth_5g_w": float(round(energy_percs['baseline_100gbmonth_5g_w']['total_pm10_tonnes']/1e3,1)),
        "pm10_baseline_100gbmonth_5g_fb": float(round(energy_percs['baseline_100gbmonth_5g_fb']['total_pm10_tonnes']/1e3,1)),

        "perc_energy_baseline_25gbmonth_4g_w": energy_percs['baseline_25gbmonth_4g_w']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_25gbmonth_4g_fb": energy_percs['baseline_25gbmonth_4g_fb']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_25gbmonth_5g_w": energy_percs['baseline_25gbmonth_5g_w']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_25gbmonth_5g_fb": energy_percs['baseline_25gbmonth_5g_fb']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_50gbmonth_4g_w": energy_percs['baseline_50gbmonth_4g_w']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_50gbmonth_4g_fb": energy_percs['baseline_50gbmonth_4g_fb']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_50gbmonth_5g_w": energy_percs['baseline_50gbmonth_5g_w']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_50gbmonth_5g_fb": energy_percs['baseline_50gbmonth_5g_fb']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_100gbmonth_4g_w": energy_percs['baseline_100gbmonth_4g_w']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_100gbmonth_4g_fb": energy_percs['baseline_100gbmonth_4g_fb']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_100gbmonth_5g_w": energy_percs['baseline_100gbmonth_5g_w']['perc_energy_dif_vs_4G'],
        "perc_energy_baseline_100gbmonth_5g_fb": energy_percs['baseline_100gbmonth_5g_fb']['perc_energy_dif_vs_4G'],

        "perc_carbon_baseline_25gbmonth_4g_w": energy_percs['baseline_25gbmonth_4g_w']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_25gbmonth_4g_fb": energy_percs['baseline_25gbmonth_4g_fb']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_25gbmonth_5g_w": energy_percs['baseline_25gbmonth_5g_w']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_25gbmonth_5g_fb": energy_percs['baseline_25gbmonth_5g_fb']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_50gbmonth_4g_w": energy_percs['baseline_50gbmonth_4g_w']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_50gbmonth_4g_fb": energy_percs['baseline_50gbmonth_4g_fb']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_50gbmonth_5g_w": energy_percs['baseline_50gbmonth_5g_w']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_50gbmonth_5g_fb": energy_percs['baseline_50gbmonth_5g_fb']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_100gbmonth_4g_w": energy_percs['baseline_100gbmonth_4g_w']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_100gbmonth_4g_fb": energy_percs['baseline_100gbmonth_4g_fb']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_100gbmonth_5g_w": energy_percs['baseline_100gbmonth_5g_w']['perc_carbon_dif_vs_4G'],
        "perc_carbon_baseline_100gbmonth_5g_fb": energy_percs['baseline_100gbmonth_5g_fb']['perc_carbon_dif_vs_4G'],

        "perc_nitrogen_baseline_25gbmonth_4g_w": energy_percs['baseline_25gbmonth_4g_w']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_25gbmonth_4g_fb": energy_percs['baseline_25gbmonth_4g_fb']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_25gbmonth_5g_w": energy_percs['baseline_25gbmonth_5g_w']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_25gbmonth_5g_fb": energy_percs['baseline_25gbmonth_5g_fb']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_50gbmonth_4g_w": energy_percs['baseline_50gbmonth_4g_w']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_50gbmonth_4g_fb": energy_percs['baseline_50gbmonth_4g_fb']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_50gbmonth_5g_w": energy_percs['baseline_50gbmonth_5g_w']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_50gbmonth_5g_fb": energy_percs['baseline_50gbmonth_5g_fb']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_100gbmonth_4g_w": energy_percs['baseline_100gbmonth_4g_w']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_100gbmonth_4g_fb": energy_percs['baseline_100gbmonth_4g_fb']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_100gbmonth_5g_w": energy_percs['baseline_100gbmonth_5g_w']['perc_nitrogen_dif_vs_4G'],
        "perc_nitrogen_baseline_100gbmonth_5g_fb": energy_percs['baseline_100gbmonth_5g_fb']['perc_nitrogen_dif_vs_4G'],

        "perc_sulpher_baseline_25gbmonth_4g_w": energy_percs['baseline_25gbmonth_4g_w']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_25gbmonth_4g_fb": energy_percs['baseline_25gbmonth_4g_fb']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_25gbmonth_5g_w": energy_percs['baseline_25gbmonth_5g_w']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_25gbmonth_5g_fb": energy_percs['baseline_25gbmonth_5g_fb']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_50gbmonth_4g_w": energy_percs['baseline_50gbmonth_4g_w']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_50gbmonth_4g_fb": energy_percs['baseline_50gbmonth_4g_fb']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_50gbmonth_5g_w": energy_percs['baseline_50gbmonth_5g_w']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_50gbmonth_5g_fb": energy_percs['baseline_50gbmonth_5g_fb']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_100gbmonth_4g_w": energy_percs['baseline_100gbmonth_4g_w']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_100gbmonth_4g_fb": energy_percs['baseline_100gbmonth_4g_fb']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_100gbmonth_5g_w": energy_percs['baseline_100gbmonth_5g_w']['perc_sulpher_dif_vs_4G'],
        "perc_sulpher_baseline_100gbmonth_5g_fb": energy_percs['baseline_100gbmonth_5g_fb']['perc_sulpher_dif_vs_4G'],

        "perc_pm10_baseline_25gbmonth_4g_w": energy_percs['baseline_25gbmonth_4g_w']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_25gbmonth_4g_fb": energy_percs['baseline_25gbmonth_4g_fb']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_25gbmonth_5g_w": energy_percs['baseline_25gbmonth_5g_w']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_25gbmonth_5g_fb": energy_percs['baseline_25gbmonth_5g_fb']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_50gbmonth_4g_w": energy_percs['baseline_50gbmonth_4g_w']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_50gbmonth_4g_fb": energy_percs['baseline_50gbmonth_4g_fb']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_50gbmonth_5g_w": energy_percs['baseline_50gbmonth_5g_w']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_50gbmonth_5g_fb": energy_percs['baseline_50gbmonth_5g_fb']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_100gbmonth_4g_w": energy_percs['baseline_100gbmonth_4g_w']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_100gbmonth_4g_fb": energy_percs['baseline_100gbmonth_4g_fb']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_100gbmonth_5g_w": energy_percs['baseline_100gbmonth_5g_w']['perc_pm10_dif_vs_4G'],
        "perc_pm10_baseline_100gbmonth_5g_fb": energy_percs['baseline_100gbmonth_5g_fb']['perc_pm10_dif_vs_4G'],

        "figure_6": os.path.join(IMAGES, iso3, 'power_strategies.png'),

        "perc_carbon_baseline_50gbmonth_4g_w_renewables": round(abs(power_percs['baseline_50gbmonth_4g_w_renewables']['perc_carbon_dif_vs_renewables'])),
        "perc_carbon_baseline_50gbmonth_4g_fb_renewables": round(abs(power_percs['baseline_50gbmonth_4g_fb_renewables']['perc_carbon_dif_vs_renewables'])),
        "perc_carbon_baseline_50gbmonth_5g_w_renewables": round(abs(power_percs['baseline_50gbmonth_5g_w_renewables']['perc_carbon_dif_vs_renewables'])),
        "perc_carbon_baseline_50gbmonth_5g_fb_renewables": round(abs(power_percs['baseline_50gbmonth_5g_fb_renewables']['perc_carbon_dif_vs_renewables'])),

        "perc_nitrogen_baseline_50gbmonth_4g_w_renewables": round(abs(power_percs['baseline_50gbmonth_4g_w_renewables']['perc_nitrogen_dif_vs_renewables'])),
        "perc_nitrogen_baseline_50gbmonth_4g_fb_renewables": round(abs(power_percs['baseline_50gbmonth_4g_fb_renewables']['perc_nitrogen_dif_vs_renewables'])),
        "perc_nitrogen_baseline_50gbmonth_5g_w_renewables": round(abs(power_percs['baseline_50gbmonth_5g_w_renewables']['perc_nitrogen_dif_vs_renewables'])),
        "perc_nitrogen_baseline_50gbmonth_5g_fb_renewables": round(abs(power_percs['baseline_50gbmonth_5g_fb_renewables']['perc_nitrogen_dif_vs_renewables'])),

        "perc_sulpher_baseline_50gbmonth_4g_w_renewables": round(abs(power_percs['baseline_50gbmonth_4g_w_renewables']['perc_sulpher_dif_vs_renewables'])),
        "perc_sulpher_baseline_50gbmonth_4g_fb_renewables": round(abs(power_percs['baseline_50gbmonth_4g_fb_renewables']['perc_sulpher_dif_vs_renewables'])),
        "perc_sulpher_baseline_50gbmonth_5g_w_renewables": round(abs(power_percs['baseline_50gbmonth_5g_w_renewables']['perc_sulpher_dif_vs_renewables'])),
        "perc_sulpher_baseline_50gbmonth_5g_fb_renewables": round(abs(power_percs['baseline_50gbmonth_5g_fb_renewables']['perc_sulpher_dif_vs_renewables'])),

        "perc_pm10_baseline_50gbmonth_4g_w_renewables": round(abs(power_percs['baseline_50gbmonth_4g_w_renewables']['perc_pm10_dif_vs_renewables'])),
        "perc_pm10_baseline_50gbmonth_4g_fb_renewables": round(abs(power_percs['baseline_50gbmonth_4g_fb_renewables']['perc_pm10_dif_vs_renewables'])),
        "perc_pm10_baseline_50gbmonth_5g_w_renewables": round(abs(power_percs['baseline_50gbmonth_5g_w_renewables']['perc_pm10_dif_vs_renewables'])),
        "perc_pm10_baseline_50gbmonth_5g_fb_renewables": round(abs(power_percs['baseline_50gbmonth_5g_fb_renewables']['perc_pm10_dif_vs_renewables'])),

        "historical_co2": round(hist_emissions['historical_co2'],1),
        "co2_per_unit_energy": round(hist_emissions['co2_per_unit_energy'],2),

        "shared_energy_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['total_energy_annual_demand_kwh']/1e9,1)),
        "shared_energy_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['total_energy_annual_demand_kwh']/1e9,1)),
        "shared_energy_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['total_energy_annual_demand_kwh']/1e9,1)),
        "shared_energy_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['total_energy_annual_demand_kwh']/1e9,1)),
        "shared_energy_baseline_100gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_baseline']['total_energy_annual_demand_kwh']/1e9,1)),
        "shared_energy_baseline_100gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_passive']['total_energy_annual_demand_kwh']/1e9,1)),
        "shared_energy_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['total_energy_annual_demand_kwh']/1e9,1)),
        "shared_energy_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['total_energy_annual_demand_kwh']/1e9,1)),

        "shared_carbon_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['total_demand_carbon_tonnes']/1e6,1)),
        "shared_carbon_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['total_demand_carbon_tonnes']/1e6,1)),
        "shared_carbon_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['total_demand_carbon_tonnes']/1e6,1)),
        "shared_carbon_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['total_demand_carbon_tonnes']/1e6,1)),
        "shared_carbon_baseline_100gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_baseline']['total_demand_carbon_tonnes']/1e6,1)),
        "shared_carbon_baseline_100gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_passive']['total_demand_carbon_tonnes']/1e6,1)),
        "shared_carbon_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['total_demand_carbon_tonnes']/1e6,1)),
        "shared_carbon_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['total_demand_carbon_tonnes']/1e6,1)),

        "shared_nitrogen_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "shared_nitrogen_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "shared_nitrogen_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "shared_nitrogen_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "shared_nitrogen_baseline_100gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_baseline']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "shared_nitrogen_baseline_100gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_passive']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "shared_nitrogen_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['total_nitrogen_oxide_tonnes']/1e3,1)),
        "shared_nitrogen_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['total_nitrogen_oxide_tonnes']/1e3,1)),

        "shared_sulpher_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "shared_sulpher_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "shared_sulpher_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "shared_sulpher_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "shared_sulpher_baseline_100gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_baseline']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "shared_sulpher_baseline_100gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_passive']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "shared_sulpher_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['total_sulpher_dioxide_tonnes']/1e3,1)),
        "shared_sulpher_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['total_sulpher_dioxide_tonnes']/1e3,1)),

        "shared_pm10_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['total_pm10_tonnes']/1e3,1)),
        "shared_pm10_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['total_pm10_tonnes']/1e3,1)),
        "shared_pm10_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['total_pm10_tonnes']/1e3,1)),
        "shared_pm10_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['total_pm10_tonnes']/1e3,1)),
        "shared_pm10_baseline_100gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_baseline']['total_pm10_tonnes']/1e3,1)),
        "shared_pm10_baseline_100gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_passive']['total_pm10_tonnes']/1e3,1)),
        "shared_pm10_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['total_pm10_tonnes']/1e3,1)),
        "shared_pm10_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['total_pm10_tonnes']/1e3,1)),

        "perc_shared_energy_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_4g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_baseline']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_5g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_baseline']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_5g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_baseline']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_4g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_passive']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_5g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_passive']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_5g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_passive']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_active']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_active']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_active']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_srn']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_srn']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_50gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_srn']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_100gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_active']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_100gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_active']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_100gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_active']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_100gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_srn']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_100gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_srn']['energy_saving_against_baseline'],1)),
        "perc_shared_energy_baseline_100gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_srn']['energy_saving_against_baseline'],1)),

        "perc_shared_carbon_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_4g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_baseline']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_5g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_baseline']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_5g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_baseline']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_4g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_passive']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_5g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_passive']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_5g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_passive']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_active']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_active']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_active']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_srn']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_srn']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_50gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_srn']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_baseline']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_4g_fb_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_baseline']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_5g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_baseline']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_5g_fb_baseline": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_baseline']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_passive']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_4g_fb_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_passive']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_5g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_passive']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_5g_fb_passive": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_passive']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_active']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_active']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_active']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_srn']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_srn']['carbon_saving_against_baseline'],1)),
        "perc_shared_carbon_baseline_100gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_srn']['carbon_saving_against_baseline'],1)),

        "perc_shared_nitrogen_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_4g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_baseline']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_5g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_baseline']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_5g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_baseline']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_4g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_passive']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_5g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_passive']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_5g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_passive']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_active']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_active']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_active']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_srn']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_srn']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_50gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_srn']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_baseline']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_4g_fb_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_baseline']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_5g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_baseline']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_5g_fb_baseline": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_baseline']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_passive']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_4g_fb_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_passive']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_5g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_passive']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_5g_fb_passive": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_passive']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_active']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_active']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_active']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_srn']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_srn']['nitrogen_saving_against_baseline'],1)),
        "perc_shared_nitrogen_baseline_100gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_srn']['nitrogen_saving_against_baseline'],1)),

        "perc_shared_sulpher_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_4g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_baseline']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_5g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_baseline']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_5g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_baseline']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_4g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_passive']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_5g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_passive']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_5g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_passive']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_active']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_active']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_active']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_srn']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_srn']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_50gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_srn']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_baseline']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_4g_fb_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_baseline']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_5g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_baseline']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_5g_fb_baseline": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_baseline']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_passive']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_4g_fb_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_passive']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_5g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_passive']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_5g_fb_passive": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_passive']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_active']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_active']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_active']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_srn']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_srn']['sulpher_saving_against_baseline'],1)),
        "perc_shared_sulpher_baseline_100gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_srn']['sulpher_saving_against_baseline'],1)),

        "perc_shared_pm10_baseline_50gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_baseline']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_4g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_baseline']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_5g_w_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_baseline']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_5g_fb_baseline": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_baseline']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_passive']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_4g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_passive']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_5g_w_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_passive']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_5g_fb_passive": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_passive']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_active']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_active']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_active']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_active']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_w_srn']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_4g_fb_srn']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_w_srn']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_50gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_50gbmonth_5g_fb_srn']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_4g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_baseline']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_4g_fb_baseline": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_baseline']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_5g_w_baseline": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_baseline']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_5g_fb_baseline": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_baseline']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_4g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_passive']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_4g_fb_passive": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_passive']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_5g_w_passive": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_passive']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_5g_fb_passive": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_passive']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_4g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_active']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_4g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_active']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_5g_w_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_active']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_5g_fb_active": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_active']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_4g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_w_srn']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_4g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_4g_fb_srn']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_5g_w_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_w_srn']['pm10_saving_against_baseline'],1)),
        "perc_shared_pm10_baseline_100gbmonth_5g_fb_srn": float(round(shared_energy_percs['baseline_100gbmonth_5g_fb_srn']['pm10_saving_against_baseline'],1)),



        "figure_7": os.path.join(IMAGES, iso3, 'energy_emissions_sharing.png'),
        "figure_8": os.path.join(IMAGES, iso3, 'health_emissions_sharing.png'),

    }

    html_out = template.render(template_vars)

    filename = 'Oughton, E.J. (2022) Assessment of 4G and 5G Universal Broadband Infrastructure Strategies for {}.pdf'.format(
        country['prefered_name'])
    path = os.path.join(OUTPUT, filename)

    pisa.showLogging()
    convert_html_to_pdf(html_out, path)


def get_sites(iso3):
    """
    Load data.
    """
    output = {}

    filename = 'national_market_results_technology_options.csv'
    path = os.path.join(RESULTS, 'model_results', iso3, filename)
    data = pd.read_csv(path)

    data.loc[data['scenario'].str.endswith('25_25_25', na=False), 'capacity'] = '25gbmonth'
    data.loc[data['scenario'].str.endswith('50_50_50', na=False), 'capacity'] = '50gbmonth'
    data.loc[data['scenario'].str.endswith('100_100_100', na=False), 'capacity'] = '100gbmonth'

    data.loc[data['scenario'].str.startswith('low', na=False), 'scenario'] = 'Low'
    data.loc[data['scenario'].str.startswith('baseline', na=False), 'scenario'] = 'Baseline'
    data.loc[data['scenario'].str.startswith('high', na=False), 'scenario'] = 'High'

    data['strategy'] = data['strategy'].replace(['3G_umts_wireless_baseline_baseline_baseline_baseline_baseline'], '3G (W)')
    data['strategy'] = data['strategy'].replace(['3G_umts_fiber_baseline_baseline_baseline_baseline'], '3G (FB)')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline_baseline'], '4G (W)')
    data['strategy'] = data['strategy'].replace(['4G_epc_fiber_baseline_baseline_baseline_baseline_baseline'], '4G (FB)')
    data['strategy'] = data['strategy'].replace(['5G_nsa_wireless_baseline_baseline_baseline_baseline_baseline'], '5G (W)')
    data['strategy'] = data['strategy'].replace(['5G_nsa_fiber_baseline_baseline_baseline_baseline_baseline'], '5G (FB)')

    data['generation'] = data['strategy'].str.split(' ').str[0]
    data['backhaul'] = data['strategy'].str.split(' ').str[1]

    for idx, row in data.iterrows():

        key = '{}_{}_{}_{}'.format(
            row['scenario'].lower().replace(' ', ''),
            row['capacity'].lower().replace(' ', ''),
            row['generation'].lower(),
            row['backhaul'].lower().replace('(','').replace(')',''),
        )

        output[key] = {
            'total_upgraded_sites': row['total_upgraded_sites'],
            'total_new_sites': row['total_new_sites'],
        }

    return output


def get_tech_percentages(iso3):
    """
    Load data.
    """
    output = {}

    filename = 'percentages_technologies_{}.csv'.format(iso3)
    path = os.path.join(RESULTS, 'percentages', filename)
    data = pd.read_csv(path)

    for idx, row in data.iterrows():

        key = '{}_{}_{}_{}'.format(
            row['scenario'].lower(),
            row['capacity'].lower().replace(' ', ''),
            row['generation'].lower(),
            row['backhaul'].lower().replace('(','').replace(')',''),
        )

        output[key] = {
            'social_cost_bn': round(row['social_cost'] / 1e9),
            'perc_saving_vs_3g': round(row['perc_saving_vs_3G'], 1),
            'w_over_fb': round(row['w_over_fb'], 1),
        }

    return output


def get_sharing_data(iso3):
    """
    Load data.
    """
    output = {}

    filename = 'percentages_sharing_{}.csv'.format(iso3)
    path = os.path.join(RESULTS, 'percentages', filename)
    data = pd.read_csv(path)

    for idx, row in data.iterrows():

        key = '{}_{}_{}'.format(
            row['scenario'].lower(),
            row['capacity'].lower().replace(' ', ''),
            row['strategy_x'].lower(),
        )

        output[key] = {
            'social_cost_bn': round(row['social_cost_x'] / 1e9),
            'saving_against_baseline': round(row['saving_against_baseline'], 1),
        }

    return output


def get_policy_data(iso3):
    """
    Load data.
    """
    output = {}

    filename = 'percentages_policy_{}.csv'.format(iso3)
    path = os.path.join(RESULTS, 'percentages', filename)
    data = pd.read_csv(path)

    for idx, row in data.iterrows():

        key = '{}_{}_{}'.format(
            row['scenario'].lower(),
            row['capacity'].lower().replace(' ', ''),
            row['strategy_x'].lower().replace(' ', ''),
        )

        output[key] = {
            'social_cost_bn': round(row['social_cost_x'] / 1e9, 2),
            'perc_against_baseline': round(row['saving_against_baseline'], 1),
        }

    return output


def get_emissions_data(iso3):
    """
    Load data.

    """
    output = {}

    filename = 'percentages_emissions_{}.csv'.format(iso3)
    path = os.path.join(RESULTS, 'percentages', filename)
    data = pd.read_csv(path)

    for idx, row in data.iterrows():

        key = '{}_{}_{}_{}'.format(
            row['scenario'].lower(),
            row['capacity'].lower().replace(' ', ''),
            row['generation'].lower(),
            row['backhaul'].lower().replace('(','').replace(')',''),
        )

        if row['perc_energy_dif_vs_4G'] == 'nan':
            perc_energy_dif_vs_4G = 0
        else:
            perc_energy_dif_vs_4G = row['perc_energy_dif_vs_4G']

        if row['perc_carbon_dif_vs_4G'] == 'nan':
            perc_carbon_dif_vs_4G = 0
        else:
            perc_carbon_dif_vs_4G = row['perc_carbon_dif_vs_4G']

        if row['perc_nitrogen_dif_vs_4G'] == 'nan':
            perc_nitrogen_dif_vs_4G = 0
        else:
            perc_nitrogen_dif_vs_4G = row['perc_nitrogen_dif_vs_4G']

        if row['perc_sulpher_dif_vs_4G'] == 'nan':
            perc_sulpher_dif_vs_4G = 0
        else:
            perc_sulpher_dif_vs_4G = row['perc_sulpher_dif_vs_4G']

        if row['perc_pm10_dif_vs_4G'] == 'nan':
            perc_pm10_dif_vs_4G = 0
        else:
            perc_pm10_dif_vs_4G = row['perc_pm10_dif_vs_4G']

        output[key] = {
            'total_energy_annual_demand_kwh': row['total_energy_annual_demand_kwh'],
            'total_demand_carbon_tonnes': row['total_demand_carbon_tonnes'],
            'total_nitrogen_oxide_tonnes': row['total_nitrogen_oxide_tonnes'],
            'total_sulpher_dioxide_tonnes': row['total_sulpher_dioxide_tonnes'],
            'total_pm10_tonnes': row['total_pm10_tonnes'],
            'perc_energy_dif_vs_4G': perc_energy_dif_vs_4G,
            'perc_carbon_dif_vs_4G': perc_carbon_dif_vs_4G,
            'perc_nitrogen_dif_vs_4G': perc_nitrogen_dif_vs_4G,
            'perc_sulpher_dif_vs_4G': perc_sulpher_dif_vs_4G,
            'perc_pm10_dif_vs_4G': perc_pm10_dif_vs_4G,
        }

    return output


def get_power_data(iso3):
    """
    Load data.

    """
    output = {}

    filename = 'percentages_power_{}.csv'.format(iso3)
    path = os.path.join(RESULTS, 'percentages', filename)
    data = pd.read_csv(path)

    for idx, row in data.iterrows():

        key = '{}_{}_{}_{}_{}'.format(
            row['scenario'].lower(),
            row['capacity'].lower().replace(' ', ''),
            row['generation'].lower(),
            row['backhaul'].lower().replace('(','').replace(')',''),
            row['power'].lower(),
        )

        if row['perc_carbon_dif_vs_renewables'] == 'nan':
            perc_carbon_dif_vs_renewables = 0
        else:
            perc_carbon_dif_vs_renewables = row['perc_carbon_dif_vs_renewables']

        if row['perc_nitrogen_dif_vs_renewables'] == 'nan':
            perc_nitrogen_dif_vs_renewables = 0
        else:
            perc_nitrogen_dif_vs_renewables = row['perc_nitrogen_dif_vs_renewables']

        if row['perc_sulpher_dif_vs_renewables'] == 'nan':
            perc_sulpher_dif_vs_renewables = 0
        else:
            perc_sulpher_dif_vs_renewables = row['perc_sulpher_dif_vs_renewables']

        if row['perc_pm10_dif_vs_renewables'] == 'nan':
            perc_pm10_dif_vs_renewables = 0
        else:
            perc_pm10_dif_vs_renewables = row['perc_pm10_dif_vs_renewables']

        output[key] = {
            # 'total_energy_annual_demand_kwh': round(row['total_energy_annual_demand_kwh']),
            'total_demand_carbon_tonnes': round(row['total_demand_carbon_tonnes']),
            'total_nitrogen_oxide_tonnes': round(row['total_nitrogen_oxide_tonnes']),
            'total_sulpher_dioxide_tonnes': round(row['total_sulpher_dioxide_tonnes']),
            'total_pm10_tonnes': round(row['total_pm10_tonnes']),
            # 'perc_energy_dif_vs_renewables': perc_energy_dif_vs_renewables,
            'perc_carbon_dif_vs_renewables': perc_carbon_dif_vs_renewables,
            'perc_nitrogen_dif_vs_renewables': perc_nitrogen_dif_vs_renewables,
            'perc_sulpher_dif_vs_renewables': perc_sulpher_dif_vs_renewables,
            'perc_pm10_dif_vs_renewables': perc_pm10_dif_vs_renewables,
        }

    return output


def get_shared_emissions_data(iso3):
    """
    Load shared data.

    """
    output = {}

    filename = 'percentages_emissions_business_model_{}.csv'.format(iso3)
    path = os.path.join(RESULTS, 'percentages', filename)
    data = pd.read_csv(path)

    for idx, row in data.iterrows():

        key = '{}_{}_{}_{}_{}'.format(
            row['scenario'].lower(),
            row['capacity'].lower().replace(' ', ''),
            row['generation'].lower(),
            row['backhaul'].lower().replace('(','').replace(')',''),
            row['sharing_x'].lower(),
        )

        output[key] = {
            'total_energy_annual_demand_kwh': round(row['total_energy_annual_demand_kwh_x']),
            'total_demand_carbon_tonnes': round(row['total_demand_carbon_tonnes_x']),
            'total_nitrogen_oxide_tonnes': round(row['total_nitrogen_oxide_tonnes_x']),
            'total_sulpher_dioxide_tonnes': round(row['total_sulpher_dioxide_tonnes_x']),
            'total_pm10_tonnes': round(row['total_pm10_tonnes_x']),
            'energy_saving_against_baseline': round(row['energy_saving_against_baseline'], 1),
            'carbon_saving_against_baseline': round(row['carbon_saving_against_baseline'], 1),
            'nitrogen_saving_against_baseline': round(row['nitrogen_saving_against_baseline'], 1),
            'sulpher_saving_against_baseline': round(row['sulpher_saving_against_baseline'], 1),
            'pm10_saving_against_baseline': round(row['pm10_saving_against_baseline'], 1),
        }

    return output


def get_policy_inputs(iso3):
    """
    """
    output = {}

    filename = 'parameters_policy_options_*.csv'
    path = os.path.join(RESULTS, 'model_results', iso3, filename)
    files = glob.glob(path)
    latest_file_path = max(files, key=os.path.getctime)

    data = pd.read_csv(latest_file_path)

    for idx, row in data.iterrows():

        output[row['parameter'].lower()] = row['value']

    return output


def get_energy_gen_inputs(iea_group):
    """

    """
    output = {}

    filename = 'iea_forecast.csv'
    path = os.path.join(DATA_RAW, 'IEA_data', filename)
    data = pd.read_csv(path)

    for idx, row in data.iterrows():

        if row['region'] == iea_group:

            handle = '{}_{}_perc'.format(row['type'], row['year'])

            output[handle] = int(round(row['share']))

    return output


def historical_emissions(iso3):
    """
    Process historical emissions.

    """
    output = {}

    path = os.path.join(DATA_RAW, 'Emissions', 'owid-co2-data_original_datset.csv')
    data = pd.read_csv(path)
    data = data[data.iso_code == iso3]
    data = data[data.year == 2020]
    data = data.to_dict('records')

    for item in data:
        output['historical_co2'] = item['co2']
        output['co2_per_unit_energy'] = item['co2_per_unit_energy']

    return output


def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return False on success and True on errors
    return pisa_status.err


if __name__ == '__main__':

    if not os.path.exists(os.path.join(OUTPUT)):
        os.makedirs(os.path.join(OUTPUT))

    for country in COUNTRY_LIST:

        if not country['iso3'] == 'COL':
            continue

        generate_report(country)
