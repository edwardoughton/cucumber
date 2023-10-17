"""
Runner for system_simulator.py

Written by Edward Oughton

Adapted from the India5G repository.

January 2022

"""
import os
import sys
import configparser
import csv
import math
from random import choice
import numpy as np
from shapely.geometry import shape, Point, LineString, mapping

from cuba.generate_hex import produce_sites_and_site_areas
from cuba.system_simulator import SimulationManager

np.random.seed(42)

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')


def generate_receivers(site_area, parameters, grid):
    """
    Generate receiver locations as points within the site area.

    Sampling points can either be generated on a grid (grid=1)
    or more efficiently between the transmitter and the edge
    of the site (grid=0) area.

    Parameters
    ----------
    site_area : polygon
        Shape of the site area we want to generate receivers within.
    parameters : dict
        Contains all necessary simulation parameters.
    grid : int
        Binary indicator to dictate receiver generation type.

    Output
    ------
    receivers : List of dicts
        Contains the quantity of desired receivers within the area boundary.

    """
    receivers = []

    if grid == 1:

        geom = shape(site_area[0]['geometry'])
        geom_box = geom.bounds

        minx = geom_box[0]
        miny = geom_box[1]
        maxx = geom_box[2]
        maxy = geom_box[3]

        id_number = 0

        x_axis = np.linspace(
            minx, maxx, num=(
                int(math.sqrt(geom.area) / (math.sqrt(geom.area)/50))
                )
            )
        y_axis = np.linspace(
            miny, maxy, num=(
                int(math.sqrt(geom.area) / (math.sqrt(geom.area)/50))
                )
            )

        xv, yv = np.meshgrid(x_axis, y_axis, sparse=False, indexing='ij')
        for i in range(len(x_axis)):
            for j in range(len(y_axis)):
                receiver = Point((xv[i,j], yv[i,j]))
                indoor_outdoor_probability = np.random.rand(1,1)[0][0]
                if geom.contains(receiver):
                    receivers.append({
                        'type': "Feature",
                        'geometry': {
                            "type": "Point",
                            "coordinates": [xv[i,j], yv[i,j]],
                        },
                        'properties': {
                            'ue_id': "id_{}".format(id_number),
                            "misc_losses": parameters['rx_misc_losses'],
                            "gain": parameters['rx_gain'],
                            "losses": parameters['rx_losses'],
                            "ue_height": float(parameters['rx_height']),
                            "indoor": (True if float(indoor_outdoor_probability) < \
                                float(0.5) else False),
                        }
                    })
                    id_number += 1

                else:
                    pass

    else:

        centroid = shape(site_area[0]['geometry']).centroid

        coord = site_area[0]['geometry']['coordinates'][0][0]
        path = LineString([(coord), (centroid)])
        length = int(path.length)
        increment = int(length / 20)

        indoor = parameters['indoor_users_percentage'] / 100

        id_number = 0
        for increment_value in range(1, 11):
            point = path.interpolate(increment * increment_value)
            indoor_outdoor_probability = np.random.rand(1,1)[0][0]
            receivers.append({
                'type': "Feature",
                'geometry': mapping(point),
                'properties': {
                    'ue_id': "id_{}".format(id_number),
                    "misc_losses": parameters['rx_misc_losses'],
                    "gain": parameters['rx_gain'],
                    "losses": parameters['rx_losses'],
                    "ue_height": float(parameters['rx_height']),
                    "indoor": (True if float(indoor_outdoor_probability) < \
                        float(indoor) else False),
                }
            })
            id_number += 1

    return receivers


def obtain_percentile_values(results, transmission_type, parameters, confidence_intervals):
    """

    Get the threshold value for a metric based on a given percentiles.

    Parameters
    ----------
    results : list of dicts
        All data returned from the system simulation.
    tranmission_type : string
        The transmission type (SISO, MIMO etc.).
    parameters : dict
        Contains all necessary simulation parameters.
    confidence_intervals: list
        Integer confidence interval values. 

    Output
    ------
    percentile_site_results : list of dicts
        Contains the confidence interval values for each metric.

    """
    output = []

    path_loss_values = []
    received_power_values = []
    interference_values = []
    noise_values = []
    sinr_values = []
    spectral_efficiency_values = []
    estimated_capacity_values = []
    estimated_capacity_values_km2 = []

    for result in results:

        path_loss_values.append(result['path_loss'])

        received_power_values.append(result['received_power'])

        interference_values.append(result['interference'])

        noise_values.append(result['noise'])

        sinr = result['sinr']
        if sinr == None:
            sinr = 0
        else:
            sinr_values.append(sinr)

        spectral_efficiency = result['spectral_efficiency']
        if spectral_efficiency == None:
            spectral_efficiency = 0
        else:
            spectral_efficiency_values.append(spectral_efficiency)

        estimated_capacity = result['capacity_mbps']
        if estimated_capacity == None:
            estimated_capacity = 0
        else:
            estimated_capacity_values.append(estimated_capacity)

        estimated_capacity_km2 = result['capacity_mbps_km2']
        if estimated_capacity_km2 == None:
            estimated_capacity_km2 = 0
        else:
            estimated_capacity_values_km2.append(estimated_capacity_km2)

    for confidence_interval in confidence_intervals:

        output.append({
            'confidence_interval': confidence_interval,
            'tranmission_type': transmission_type,
            'path_loss': np.percentile(
                path_loss_values, confidence_interval #<- low path loss is better
            ),
            'received_power': np.percentile(
                received_power_values, 100 - confidence_interval
            ),
            'interference': np.percentile(
                interference_values, confidence_interval #<- low interference is better
            ),
            'noise': np.percentile(
                noise_values, confidence_interval #<- low interference is better
            ),
            'sinr': np.percentile(
                sinr_values, 100 - confidence_interval
            ),
            'spectral_efficiency': np.percentile(
                spectral_efficiency_values, 100 - confidence_interval
            ),
            'capacity_mbps': np.percentile(
                estimated_capacity_values, 100 - confidence_interval
            ),
            'capacity_mbps_km2': np.percentile(
                estimated_capacity_values_km2, 100 - confidence_interval
            )
        })

    return output


def obtain_threshold_values_choice(results, parameters):
    """

    Get the threshold capacity based on a given percentile.

    Parameters
    ----------
    results : list of dicts
        All data returned from the system simulation.
    parameters : dict
        Contains all necessary simulation parameters.

    Output
    ------
    matching_result : float
        Contains the chosen percentile value based on the input data.

    """
    sinr_values = []

    percentile = parameters['percentile']

    for result in results:

        sinr = result['sinr']

        if sinr == None:
            pass
        else:
            sinr_values.append(sinr)

    sinr = np.percentile(sinr_values, percentile, interpolation='nearest')

    matching_result = []

    for result in results:
        if float(result['sinr']) == float(sinr):
            matching_result.append(result)

    return float(choice(matching_result))


def convert_results_geojson(data):
    """
    Convert results to geojson format, for writing to shapefile.

    Parameters
    ----------
    data : list of dicts
        Contains all results ready to be written.

    Outputs
    -------
    output : list of dicts
        A list of geojson dictionaries ready for writing.

    """
    output = []

    for datum in data:
        output.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    datum['receiver_x'], datum['receiver_y']]
                },
            'properties': {
                'path_loss': float(datum['path_loss']),
                'received_power': float(datum['received_power']),
                'interference': float(datum['interference']),
                'noise': float(datum['noise']),
                'sinr': float(datum['sinr']),
                'spectral_efficiency': float(
                    datum['spectral_efficiency']
                ),
                'capacity_mbps': float(
                    datum['capacity_mbps']
                ),
                'capacity_mbps_km2': float(
                    datum['capacity_mbps_km2']
                ),
                },
            }
        )

    return output


def write_full_results(data, environment, site_radius, frequency,
    bandwidth, generation, ant_type, transmittion_type, directory,
    filename, parameters):
    """
    Write full results data to .csv.

    Parameters
    ----------
    data : list of dicts
        Contains all results ready to be written.
    environment : string
        Either urban, suburban or rural clutter type.
    site_radius : int
        Radius of site area in meters.
    frequency : float
        Spectral frequency of carrier band in GHz.
    bandwidth : int
        Channel bandwidth of carrier band in MHz.
    generation : string
        Either 4G or 5G depending on technology generation.
    ant_type : string
        The type of transmitter modelled (macro, micro etc.).
    tranmission_type : string
        The type of tranmission (SISO, MIMO 4x4, MIMO 8x8 etc.).
    directory : string
        Folder the data will be written to.
    filename : string
        Name of the .csv file.
    parameters : dict
        Contains all necessary simulation parameters.

    """
    sectors = parameters['sectorization']
    inter_site_distance = site_radius * 2
    site_area_km2 = (
        math.sqrt(3) / 2 * inter_site_distance ** 2 / 1e6
    )
    sites_per_km2 = 1 / site_area_km2

    if not os.path.exists(directory):
        os.makedirs(directory)

    full_path = os.path.join(directory, filename)

    results_file = open(full_path, 'w', newline='')
    results_writer = csv.writer(results_file)
    results_writer.writerow(
        (
            'environment',
            'inter_site_distance_m',
            'sites_per_km2',
            'frequency_GHz',
            'bandwidth_MHz',
            'number_of_sectors',
            'generation',
            'ant_type',
            'transmittion_type',
            'receiver_x',
            'receiver_y',
            'r_distance',
            'path_loss_dB',
            'r_model',
            'received_power_dB',
            'interference_dB',
            'i_model',
            'noise_dB',
            'sinr_dB',
            'spectral_efficiency_bps_hz',
            'capacity_mbps',
            'capacity_mbps_km2'
        )
    )

    for row in data:
        results_writer.writerow((
            environment,
            inter_site_distance,
            sites_per_km2,
            frequency,
            bandwidth,
            sectors,
            generation,
            ant_type,
            transmittion_type,
            row['receiver_x'],
            row['receiver_y'],
            row['distance'],
            row['path_loss'],
            row['r_model'],
            row['received_power'],
            row['interference'],
            row['i_model'],
            row['noise'],
            row['sinr'],
            row['spectral_efficiency'],
            row['capacity_mbps'],
            row['capacity_mbps_km2'],
            ))


def write_frequency_lookup_table(results, environment, site_radius,
    frequency, bandwidth, generation, ant_type, tranmission_type,
    directory, filename, parameters):
    """
    Write the main, comprehensive lookup table for all environments,
    site radii, frequencies etc.

    Parameters
    ----------
    results : list of dicts
        Contains all results ready to be written.
    environment : string
        Either urban, suburban or rural clutter type.
    site_radius : int
        Radius of site area in meters.
    frequency : float
        Spectral frequency of carrier band in GHz.
    bandwidth : int
        Channel bandwidth of carrier band in MHz.
    generation : string
        Either 4G or 5G depending on technology generation.
    ant_type : string
        Type of transmitters modelled.
    tranmission_type : string
        The transmission type (SISO, MIMO etc.).
    directory : string
        Folder the data will be written to.
    filename : string
        Name of the .csv file.
    parameters : dict
        Contains all necessary simulation parameters.

    """
    inter_site_distance = site_radius * 2
    site_area_km2 = math.sqrt(3) / 2 * inter_site_distance ** 2 / 1e6
    sites_per_km2 = 1 / site_area_km2

    sectors = parameters['sectorization']

    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = os.path.join(directory, filename)

    if not os.path.exists(directory):
        lut_file = open(directory, 'w', newline='')
        lut_writer = csv.writer(lut_file)
        lut_writer.writerow(
            (
                'confidence_interval',
                'environment',
                'inter_site_distance_m',
                'site_area_km2',
                'sites_per_km2',
                'frequency_GHz',
                'bandwidth_MHz',
                'number_of_sectors',
                'generation',
                'ant_type',
                'transmission_type',
                'path_loss_dB',
                'received_power_dBm',
                'interference_dBm',
                'noise_dB',
                'sinr_dB',
                'spectral_efficiency_bps_hz',
                'capacity_mbps',
                'capacity_mbps_km2',
            )
        )
    else:
        lut_file = open(directory, 'a', newline='')
        lut_writer = csv.writer(lut_file)

    for result in results:
        lut_writer.writerow(
            (
                result['confidence_interval'],
                environment,
                inter_site_distance,
                site_area_km2,
                sites_per_km2,
                frequency,
                bandwidth,
                sectors,
                generation,
                ant_type,
                tranmission_type,
                result['path_loss'],
                result['received_power'],
                result['interference'],
                result['noise'],
                result['sinr'],
                result['spectral_efficiency'],
                result['capacity_mbps'],
                result['capacity_mbps_km2'] * sectors,
            )
        )

    lut_file.close()


if __name__ == '__main__':

    PARAMETERS = {
        'seed_value2_4G': 4,
        'seed_value2_5G': 6,
        'seed_value2_free-space': 14,
        'los_breakpoint_m': 500,
        'tx_macro_baseline_height': 30,
        'tx_macro_power': 40,
        'tx_macro_gain': 16,
        'tx_macro_losses': 1,
        'rx_gain': 0,
        'rx_losses': 4,
        'rx_misc_losses': 4,
        'rx_height': 1.5,
        'network_load': 100,
        'sectorization': 3,
    }

    SPECTRUM_PORTFOLIO = [
        (0.7, 10, '5G', '4x4'),
        (0.8, 10, '4G', '2x2'),
        (1.8, 10, '4G', '2x2'),
        (2.5, 10, '4G', '2x2'),
        (3.5, 40, '5G', '4x4'),
    ]

    ANT_TYPES = [
        ('macro'),
    ]

    MODULATION_AND_CODING_LUT = {
        # ETSI. 2018. ‘5G; NR; Physical Layer Procedures for Data
        # (3GPP TS 38.214 Version 15.3.0 Release 15)’. Valbonne, France: ETSI.
        # Generation MIMO CQI Index	Modulation	Coding rate
        # Spectral efficiency (bps/Hz) SINR estimate (dB)
        '4G': [
            ('4G', '2x2', 1, 'QPSK', 78, 0.3, -6.7),
            ('4G', '2x2', 2, 'QPSK', 120, 0.46, -4.7),
            ('4G', '2x2', 3, 'QPSK', 193, 0.74, -2.3),
            ('4G', '2x2', 4, 'QPSK', 308, 1.2, 0.2),
            ('4G', '2x2', 5, 'QPSK', 449, 1.6, 2.4),
            ('4G', '2x2', 6, 'QPSK', 602, 2.2, 4.3),
            ('4G', '2x2', 7, '16QAM', 378, 2.8, 5.9),
            ('4G', '2x2', 8, '16QAM', 490, 3.8, 8.1),
            ('4G', '2x2', 9, '16QAM', 616, 4.8, 10.3),
            ('4G', '2x2', 10, '64QAM', 466, 5.4, 11.7),
            ('4G', '2x2', 11, '64QAM', 567, 6.6, 14.1),
            ('4G', '2x2', 12, '64QAM', 666, 7.8, 16.3),
            ('4G', '2x2', 13, '64QAM', 772, 9, 18.7),
            ('4G', '2x2', 14, '64QAM', 973, 10.2, 21),
            ('4G', '2x2', 15, '64QAM', 948, 11.4, 22.7),
        ],
        '5G': [
            ('5G', '4x4', 1, 'QPSK', 78, 0.15, -6.7),
            ('5G', '4x4', 2, 'QPSK', 193, 1.02, -4.7),
            ('5G', '4x4', 3, 'QPSK', 449, 2.21, -2.3),
            ('5G', '4x4', 4, '16QAM', 378, 3.20, 0.2),
            ('5G', '4x4', 5, '16QAM', 490, 4.00, 2.4),
            ('5G', '4x4', 6, '16QAM', 616, 5.41, 4.3),
            ('5G', '4x4', 7, '64QAM', 466, 6.20, 5.9),
            ('5G', '4x4', 8, '64QAM', 567, 8.00, 8.1),
            ('5G', '4x4', 9, '64QAM', 666, 9.50, 10.3),
            ('5G', '4x4', 10, '64QAM', 772, 11.00, 11.7),
            ('5G', '4x4', 11, '64QAM', 873, 14.00, 14.1),
            ('5G', '4x4', 12, '256QAM', 711, 16.00, 16.3),
            ('5G', '4x4', 13, '256QAM', 797, 19.00, 18.7),
            ('5G', '4x4', 14, '256QAM', 885, 22.00, 21),
            ('5G', '4x4', 15, '256QAM', 948, 25.00, 22.7),
        ]
    }

    CONFIDENCE_INTERVALS = [
        5,
        50,
        95,
    ]

    def generate_site_radii(min, max, increment):
        for n in range(min, max, increment):
            yield n

    INCREMENT_MA = (250, 40000, 250) #(400, 40400, 1000) #1000,125)#

    SITE_RADII = {
        'macro': {
            'free-space':
                generate_site_radii(INCREMENT_MA[0],INCREMENT_MA[1],INCREMENT_MA[2])
            },
        }

    unprojected_point = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': (0, 0),
            },
        'properties': {
            'site_id': 'Radio Tower'
            }
        }

    unprojected_crs = 'epsg:4326'
    projected_crs = 'epsg:3857'

    environments =[
        'free-space'
    ]

    for environment in environments:
        for ant_type in ANT_TYPES:
            site_radii_generator = SITE_RADII[ant_type]
            for site_radius in site_radii_generator[environment]:

                if environment == 'urban' and site_radius > 5000:
                    continue
                if environment == 'suburban' and site_radius > 15000:
                    continue

                print('--working on {}: {}'.format(environment, site_radius))

                transmitter, interfering_transmitters, site_area, int_site_areas = \
                    produce_sites_and_site_areas(
                        unprojected_point['geometry']['coordinates'],
                        site_radius,
                        unprojected_crs,
                        projected_crs
                        )

                receivers = generate_receivers(site_area, PARAMETERS, 1)

                for frequency, bandwidth, generation, transmission_type in SPECTRUM_PORTFOLIO:

                    print('{}, {}, {}, {}'.format(frequency, bandwidth, generation, transmission_type))

                    MANAGER = SimulationManager(
                        transmitter, interfering_transmitters, ant_type,
                        receivers, site_area, PARAMETERS
                        )

                    results = MANAGER.estimate_link_budget(
                        frequency,
                        bandwidth,
                        generation,
                        ant_type,
                        transmission_type,
                        environment,
                        MODULATION_AND_CODING_LUT,
                        PARAMETERS
                        )

                    folder = os.path.join(DATA_INTERMEDIATE, 'luts', 'full_tables')
                    filename = 'full_capacity_lut_{}_{}_{}_{}_{}_{}.csv'.format(
                        environment, site_radius, generation, frequency, ant_type, transmission_type)

                    write_full_results(results, environment, site_radius,
                        frequency, bandwidth, generation, ant_type, transmission_type,
                        folder, filename, PARAMETERS)

                    percentile_site_results = obtain_percentile_values(
                        results, transmission_type, PARAMETERS, CONFIDENCE_INTERVALS
                    )

                    results_directory = os.path.join(DATA_INTERMEDIATE, 'luts')
                    write_frequency_lookup_table(percentile_site_results, environment,
                        site_radius, frequency, bandwidth, generation,
                        ant_type, transmission_type, results_directory,
                        'capacity_lut_by_frequency.csv', PARAMETERS
                    )
