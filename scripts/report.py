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

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

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

    policy_inputs = get_policy_inputs(iso3)

    path = os.path.join(BASE_PATH, '..', 'reports', 'templates')
    env = Environment(loader=FileSystemLoader(path))

    template = env.get_template('template.html')

    template_vars = {
        "css_location": "D:\\Github\\cuba\\reports\\templates\\style_template.css",
        "prefered_name" : country['prefered_name'],
        "country": iso3,
        "figure_1": os.path.join(IMAGES, iso3, 'social_costs_by_strategy.png'),
        "upgraded_sites_baseline_10mbps_3g_w": sites['baseline_10mbps_3g_w']['total_upgraded_sites'],
        "new_sites_baseline_10mbps_3g_w": sites['baseline_10mbps_3g_w']['total_new_sites'],
        "upgraded_sites_baseline_10mbps_4g_w": sites['baseline_10mbps_4g_w']['total_upgraded_sites'],
        "new_sites_baseline_10mbps_4g_w": sites['baseline_10mbps_4g_w']['total_new_sites'],
        "upgraded_sites_baseline_10mbps_5g_w": sites['baseline_10mbps_5g_w']['total_upgraded_sites'],
        "new_sites_baseline_10mbps_5g_w": sites['baseline_10mbps_5g_w']['total_new_sites'],
        "baseline_10mbps_3g_w": tech_percs['baseline_10mbps_3g_w']['social_cost_bn'],
        "baseline_10mbps_4g_w": tech_percs['baseline_10mbps_4g_w']['social_cost_bn'],
        "baseline_10mbps_5g_w": tech_percs['baseline_10mbps_5g_w']['social_cost_bn'],
        "w_over_fb_3g_10mbps": round(abs(tech_percs['baseline_10mbps_3g_w']['w_over_fb'])),
        "w_over_fb_4g_10mbps": round(abs(tech_percs['baseline_10mbps_4g_w']['w_over_fb'])),
        "w_over_fb_5g_10mbps": round(abs(tech_percs['baseline_10mbps_5g_w']['w_over_fb'])),
        "perc_saving_vs_3g_4g_10mbps": round(abs(tech_percs['baseline_10mbps_4g_w']['perc_saving_vs_3g'])),
        "perc_saving_vs_3g_5g_10mbps": round(abs(tech_percs['baseline_10mbps_5g_w']['perc_saving_vs_3g'])),
        "low_10mbps_3g_w": tech_percs['low_10mbps_3g_w']['social_cost_bn'],
        "low_10mbps_4g_w": tech_percs['low_10mbps_4g_w']['social_cost_bn'],
        "low_10mbps_5g_w": tech_percs['low_10mbps_5g_w']['social_cost_bn'],
        "high_10mbps_3g_w": tech_percs['high_10mbps_3g_w']['social_cost_bn'],
        "high_10mbps_4g_w": tech_percs['high_10mbps_4g_w']['social_cost_bn'],
        "high_10mbps_5g_w": tech_percs['high_10mbps_5g_w']['social_cost_bn'],
        "baseline_5mbps_3g_w": tech_percs['baseline_5mbps_3g_w']['social_cost_bn'],
        "baseline_5mbps_4g_w": tech_percs['baseline_5mbps_4g_w']['social_cost_bn'],
        "baseline_5mbps_5g_w": tech_percs['baseline_5mbps_5g_w']['social_cost_bn'],
        "baseline_20mbps_3g_w": tech_percs['baseline_20mbps_3g_w']['social_cost_bn'],
        "baseline_20mbps_4g_w": tech_percs['baseline_20mbps_4g_w']['social_cost_bn'],
        "baseline_20mbps_5g_w": tech_percs['baseline_20mbps_5g_w']['social_cost_bn'],
        "figure_2": os.path.join(IMAGES, iso3, 'social_costs_by_sharing_strategy.png'),
        "passive_vs_base_4g_10mbps": round(abs(share_percs['baseline_10mbps_passive']['saving_against_baseline'])),
        "active_vs_base_4g_10mbps": round(abs(share_percs['baseline_10mbps_active']['saving_against_baseline'])),
        "srn_vs_base_4g_10mbps": round(abs(share_percs['baseline_10mbps_srn']['saving_against_baseline'])),
        "passive_cost_4g_10mbps": share_percs['baseline_10mbps_passive']['social_cost_bn'],
        "active_cost_4g_10mbps": share_percs['baseline_10mbps_active']['social_cost_bn'],
        "srn_cost_4g_10mbps": share_percs['baseline_10mbps_srn']['social_cost_bn'],
        "figure_3": os.path.join(IMAGES, iso3, 'social_costs_by_policy_options.png'),
        "tax_low": int(float(policy_inputs['tax_low'])),
        "tax_baseline": int(float(policy_inputs['tax_baseline'])),
        "tax_high": int(float(policy_inputs['tax_high'])),
        "perc_lowtax": policy_percs['baseline_10mbps_lowtax']['perc_against_baseline'],
        "perc_hightax": policy_percs['baseline_10mbps_hightax']['perc_against_baseline'],
        "lowtax_cost_4g_10mbps": policy_percs['baseline_10mbps_lowtax']['social_cost_bn'],
        "hightax_cost_4g_10mbps": policy_percs['baseline_10mbps_hightax']['social_cost_bn'],
        "baselinetax_cost_4g_10mbps": policy_percs['baseline_10mbps_baseline']['social_cost_bn'],
        "profit_margin": int(float(policy_inputs['profit_margin'])),
        "spectrum_coverage_baseline_usd_mhz_pop": policy_inputs['spectrum_coverage_baseline_usd_mhz_pop'],
        "spectrum_capacity_baseline_usd_mhz_pop": policy_inputs['spectrum_capacity_baseline_usd_mhz_pop'],
        "spectrum_cost_low": int(float(policy_inputs['spectrum_cost_low'])),
        "spectrum_cost_high": int(float(policy_inputs['spectrum_cost_high'])),
        "perc_lowspectrum": policy_percs['baseline_10mbps_lowspectrumfees']['perc_against_baseline'],
        "perc_highspectrum": policy_percs['baseline_10mbps_highspectrumfees']['perc_against_baseline'],
        "lowspectrum_cost_4g_10mbps": policy_percs['baseline_10mbps_lowspectrumfees']['social_cost_bn'],
        "highspectrum_cost_4g_10mbps": policy_percs['baseline_10mbps_highspectrumfees']['social_cost_bn'],
    }

    html_out = template.render(template_vars)

    filename = 'Oughton, E.J. (2021) Assessment of 5G Infrastructure Strategies for {}.pdf'.format(
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

    data.loc[data['scenario'].str.endswith('5_5_5', na=False), 'capacity'] = '5 Mbps'
    data.loc[data['scenario'].str.endswith('10_10_10', na=False), 'capacity'] = '10 Mbps'
    data.loc[data['scenario'].str.endswith('20_20_20', na=False), 'capacity'] = '20 Mbps'

    data.loc[data['scenario'].str.startswith('low', na=False), 'scenario'] = 'Low'
    data.loc[data['scenario'].str.startswith('baseline', na=False), 'scenario'] = 'Baseline'
    data.loc[data['scenario'].str.startswith('high', na=False), 'scenario'] = 'High'

    data['strategy'] = data['strategy'].replace(['3G_umts_wireless_baseline_baseline_baseline_baseline'], '3G (W)')
    data['strategy'] = data['strategy'].replace(['3G_umts_fiber_baseline_baseline_baseline_baseline'], '3G (FB)')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline'], '4G (W)')
    data['strategy'] = data['strategy'].replace(['4G_epc_fiber_baseline_baseline_baseline_baseline'], '4G (FB)')
    data['strategy'] = data['strategy'].replace(['5G_nsa_wireless_baseline_baseline_baseline_baseline'], '5G (W)')
    data['strategy'] = data['strategy'].replace(['5G_nsa_fiber_baseline_baseline_baseline_baseline'], '5G (FB)')

    data['generation'] = data['strategy'].str.split(' ').str[0]
    data['backhaul'] = data['strategy'].str.split(' ').str[1]

    for idx, row in data.iterrows():

        key = '{}_{}_{}_{}'.format(
            row['scenario'].lower(),
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
            'social_cost_bn': round(row['social_cost'] / 1e9, 2),
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
            'social_cost_bn': round(row['social_cost_x'] / 1e9, 2),
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

    country = {
        'iso3': 'CHL',
        'prefered_name': 'Chile',
    }

    generate_report(country)
