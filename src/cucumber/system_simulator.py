"""
Taken from the India5G repository.

System simulator for 4G/5G

Author: Edward Oughton
Date: Adapted January 2022

"""
from shapely.geometry import shape, Point, LineString
import numpy as np
from itertools import tee
from collections import OrderedDict

from cucumber.path_loss import path_loss_calculator, lognormal_dist_values

np.random.seed(42)

class SimulationManager(object):
    """

    Meta-object for managing all transmitters and receivers.

    Parameters
    ----------
    transmitter : list of dicts
        Contains a geojson dict for the transmitter site.
    interfering_transmitters : list of dicts
        Contains dicts for each interfering transmitter site.
    receivers : list of dicts
        Contains a dict for each User Equipment (UE) receiver.
    site_area : list of dicts
        Contains geojson dict for the site area polygon.
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.

    """
    def __init__(self, transmitter, interfering_transmitters, ant_type,
        receivers, site_area, simulation_parameters):

        self.transmitter = Transmitter(transmitter[0], ant_type,
            simulation_parameters)
        self.interfering_transmitters = {}
        self.receivers = {}
        self.site_area = SiteArea(site_area[0])

        for interfering_transmitter in interfering_transmitters:
            site_id = interfering_transmitter['properties']["site_id"]
            site_object = InterferingTransmitter(
                interfering_transmitter, ant_type, simulation_parameters
                )
            self.interfering_transmitters[site_id] = site_object

        for receiver in receivers:
            receiver_id = receiver['properties']["ue_id"]
            receiver = Receiver(receiver, simulation_parameters)
            self.receivers[receiver_id] = receiver


    def estimate_link_budget(self, frequency, bandwidth,
        generation, ant_type, tranmission_type, environment,
        modulation_and_coding_lut, simulation_parameters):
        """

        Takes propagation parameters and calculates link budget capacity.

        Parameters
        ----------
        frequency : float
            The carrier frequency for the chosen spectrum band (GHz).
        bandwidth : int
            The bandwidth of the carrier frequency (MHz).
        generation : string
            The technology generation type.
        ant_type : str
            Type of antenna (macro, small etc.).
        tranmission_type : string
            Transmission type (SISO, MIMO etc.).
        environment : string
            Either urban, suburban or rural.
        modulation_and_coding_lut : list of tuples
            A lookup table containing modulation and coding rates,
            spectral efficiencies and SINR estimates.
        simulation_parameters : dict
            A dict containing all simulation parameters necessary.

        Returns
        -------
        results : List of dicts
            Each dict is an individual simulation result.

        """
        results = []

        random_variations = lognormal_dist_values(6, 3, 42, len(self.receivers))

        for index, receiver in enumerate(self.receivers.values()):

            random_variation = random_variations[index:index+1][0]

            path_loss, r_model, r_distance = self.estimate_path_loss(
                receiver, frequency, environment, simulation_parameters, 
                random_variation, generation
            )

            received_power = self.estimate_received_power(self.transmitter,
                receiver, path_loss
            )

            interference, i_model, ave_distance, ave_inf_pl = self.estimate_interference(
                receiver, frequency, environment, simulation_parameters, 
                random_variations[::-1], generation)

            noise = self.estimate_noise(
                bandwidth
            )

            f_received_power, f_interference, f_noise, i_plus_n, sinr = \
                self.estimate_sinr(received_power, interference, noise,
                simulation_parameters
                )

            spectral_efficiency = self.estimate_spectral_efficiency(
                sinr, generation, modulation_and_coding_lut
            )

            capacity_mbps, capacity_mbps_km2 = (
                self.estimate_average_capacity(
                bandwidth, spectral_efficiency)
            )

            results.append({
                'id': receiver.id,
                'path_loss': path_loss,
                'r_model': r_model,
                # 'type_of_sight': type_of_sight,
                'ave_inf_pl': ave_inf_pl,
                'received_power': f_received_power,
                'distance': r_distance,
                'interference': np.log10(f_interference),
                'i_model': i_model,
                'network_load': simulation_parameters['network_load'],
                'ave_distance': ave_distance,
                'noise': f_noise,
                'i_plus_n': np.log10(i_plus_n),
                'tranmission_type': tranmission_type,
                'sinr': sinr,
                'spectral_efficiency': spectral_efficiency,
                'capacity_mbps': capacity_mbps,
                'capacity_mbps_km2': capacity_mbps_km2,
                'receiver_x': receiver.coordinates[0],
                'receiver_y': receiver.coordinates[1],
                })

        return results


    def estimate_path_loss(self, receiver, frequency, environment,
        simulation_parameters, random_variation, generation):
        """

        Function to calculate the path loss between a transmitter
        and receiver.

        Parameters
        ----------
        receiver : object
            Receiving User Equipment (UE) item.
        frequency : float
            The carrier frequency for the chosen spectrum band (GHz).
        environment : string
            Either urban, suburban or rural.

        Returns
        -------
        path_loss : float
            Estimated path loss in decibels between the transmitter
            and receiver.
        model : string
            Specifies which propagation model was used.
        strt_distance : int
            States the straight line distance in meters between the
            transmitter and receiver.
        type_of_sight : string
            Either Line of Sight or None Line of Sight.

        """
        temp_line = LineString(
            [
                (receiver.coordinates[0],
                receiver.coordinates[1]),
                (self.transmitter.coordinates[0],
                self.transmitter.coordinates[1])
            ]
        )

        strt_distance = temp_line.length

        if strt_distance < 20:
            strt_distance = 20

        if strt_distance < simulation_parameters['los_breakpoint_m'] :
            type_of_sight = 'los'
        else:
            type_of_sight = 'nlos'
        
        seed_value = (simulation_parameters['seed_value2_{}'.format(generation)] +
            simulation_parameters['seed_value2_{}'.format(environment)]
        )
            
        path_loss, variation = path_loss_calculator(
            strt_distance,
            frequency,
            environment,
            simulation_parameters,
            random_variation
        )

        return path_loss, 'fspl', strt_distance#, type_of_sight


    def estimate_received_power(self, transmitter, receiver, path_loss):
        """

        Calculate received power based on transmitter and receiver
        characteristcs, and path loss.

        Equivalent Isotropically Radiated Power (EIRP) = (
            Power + Gain - Losses
        )

        Parameters
        ----------
        transmitter : object
            Radio transmitter.
        receiver : object
            Receiving User Equipment (UE) item.
        path_loss : float
            Estimated path loss in decibels between the transmitter
            and receiver.

        Returns
        -------
        received_power : float
            UE received power.

        """
        #calculate Equivalent Isotropically Radiated Power (EIRP)
        eirp = (
            float(self.transmitter.power) +
            float(self.transmitter.gain) -
            float(self.transmitter.losses)
        )

        received_power = (eirp -
            path_loss -
            receiver.misc_losses +
            receiver.gain -
            receiver.losses
        )

        return received_power


    def estimate_interference(self, receiver, frequency, environment,
        simulation_parameters, random_variation, generation):
        """
        Calculate interference from other sites.

        closest_sites contains all sites, ranked based
        on distance, meaning we need to select sites 1-3 (as site 0
        is the actual site in use)

        Parameters
        ----------
        receiver : object
            Receiving User Equipment (UE) item.
        frequency : float
            The carrier frequency for the chosen spectrum band (GHz).
        environment : string
            Either urban, suburban or rural.
        seed_value : int
            Set seed value for quasi-random number generator.
        iterations : int
            The number of stochastic iterations for the specific point.

        Returns
        -------
        interference : List
            Received interference power in decibels at the receiver.
        model : string
            Specifies which propagation model was used.
        ave_distance : float
            The average straight line distance in meters between the
            interfering transmitters and receiver.
        ave_pl : string
            The average path loss in decibels between the interfering
            transmitters and receiver.

        """
        interference = []

        ave_distance = 0
        ave_pl = 0

        for index, interfering_transmitter in enumerate(self.interfering_transmitters.values()):


            temp_line = LineString(
                [
                    (receiver.coordinates[0],
                    receiver.coordinates[1]),
                    (interfering_transmitter.coordinates[0],
                    interfering_transmitter.coordinates[1])
                ]
            )

            interference_strt_distance = temp_line.length
            if interference_strt_distance < 20:
                interference_strt_distance == 20

            ant_height = interfering_transmitter.ant_height
            ant_type =  interfering_transmitter.ant_type

            if interference_strt_distance < simulation_parameters['los_breakpoint_m']:
                type_of_sight = 'los'
            else:
                type_of_sight = 'nlos'

            seed_value = (simulation_parameters['seed_value2_{}'.format(generation)] +
                        simulation_parameters['seed_value2_{}'.format(environment)]
            )

            path_loss, variation = path_loss_calculator(
                interference_strt_distance, frequency, environment,
                simulation_parameters, random_variation[index:index+1][0])

            received_interference = self.estimate_received_power(
                interfering_transmitter,
                receiver,
                path_loss
            )

            ave_distance += interference_strt_distance
            ave_pl += path_loss

            interference.append(received_interference)

        ave_distance = (
            ave_distance / len(self.interfering_transmitters.values())
        )

        ave_pl = (
            ave_pl / len(self.interfering_transmitters.values())
        )

        return interference, 'fspl', ave_distance, ave_pl


    def estimate_noise(self, bandwidth):
        """
        Estimates the potential noise at the UE receiver.

        Terminal noise can be calculated as:

        “K (Boltzmann constant) x T (290K) x bandwidth”.

        The bandwidth depends on bit rate, which defines the number
        of resource blocks. We assume 50 resource blocks, equal 9 MHz,
        transmission for 1 Mbps downlink.

        Required SNR (dB)
        Detection bandwidth (BW) (Hz)
        k = Boltzmann constant
        T = Temperature (Kelvins) (290 Kelvin = ~16 degrees celcius)
        NF = Receiver noise figure (dB)

        NoiseFloor (dBm) = 10log10(k * T * 1000) + NF + 10log10(BW)

        NoiseFloor (dBm) = (
            10log10(1.38 x 10e-23 * 290 * 1x10e3) + 1.5 + 10log10(10 x 10e6)
        )

        Validated against the EverythingRF noise calculator:
        https://www.everythingrf.com/rf-calculators/noise-power-calculator

        Parameters
        ----------
        bandwidth : int
            The bandwidth of the carrier frequency (MHz).

        Returns
        -------
        noise : float
            Received noise at the UE receiver in decibels

        """
        k = 1.38e-23
        t = 290
        BW = bandwidth*1000000

        noise = 10 * np.log10(k * t * 1000) + 1.5 + 10 * np.log10(BW)

        return noise


    def estimate_sinr(self, received_power, interference, noise,
        simulation_parameters):
        """

        Calculate the Signal-to-Interference-plus-Noise-Ratio (SINR).

        Parameters
        ----------
        received_power : float
            UE received power in decibels.
        interference : List
            Received interference power in decibels at the receiver.
        noise : float
            Received noise at the UE receiver in decibels
        simulation_parameters : dict
            A dict containing all simulation parameters necessary.

        Returns
        -------
        received_power : float
            UE received power in decibels.
        raw_sum_of_interference : float
            Linear values of summed interference at the receiver in decibels.
        noise : float
            Received noise at the UE receiver in decibels.
        i_plus_n : float
            Linear sum of interference plus noise in decibels.
        sinr : float
            Signal-to-Interference-plus-Noise-Ratio (SINR) in decibels.

        """
        raw_received_power = 10**received_power
        # print('received power', raw_received_power, received_power)
        interference_list = []
        for value in interference:
            output_value = 10**value
            # print('received interference', output_value, value)
            interference_list.append(output_value)

        interference_list.sort(reverse=True)
        interference_list = interference_list[:3]

        network_load = simulation_parameters['network_load']
        i_summed = sum(interference_list)
        raw_sum_of_interference = i_summed * (network_load/100)

        raw_noise = 10**noise

        i_plus_n = (raw_sum_of_interference + raw_noise)

        sinr = round(np.log10(
            raw_received_power / i_plus_n
            ),2)

        return received_power, raw_sum_of_interference, noise, i_plus_n, sinr


    def estimate_spectral_efficiency(self, sinr, generation,
        modulation_and_coding_lut):
        """
        Uses the SINR to determine spectral efficiency given the relevant
        modulation and coding scheme.

        Parameters
        ----------
        sinr : float
            Signal-to-Interference-plus-Noise-Ratio (SINR) in decibels.
        generation : string
            Either 4G or 5G dependent on technology.
        modulation_and_coding_lut : list of tuples
            A lookup table containing modulation and coding rates,
            spectral efficiencies and SINR estimates.

        Returns
        -------
        spectral_efficiency : float
            Efficiency of information transfer in Bps/Hz

        """
        lookup = modulation_and_coding_lut[generation]

        spectral_efficiency = 0.1
        for lower, upper in pairwise(lookup):
            if lower[0] and upper[0] == generation:

                lower_sinr = lower[6]
                upper_sinr = upper[6]

                if sinr >= lower_sinr and sinr < upper_sinr:
                    spectral_efficiency = lower[5]
                    return spectral_efficiency

                highest_value = lookup[-1]

                if sinr >= highest_value[6]:
                    spectral_efficiency = highest_value[5]
                    return spectral_efficiency

                lowest_value = lookup[0]

                if sinr < lowest_value[5]:
                    spectral_efficiency = 0
                    return spectral_efficiency


    def estimate_average_capacity(self, bandwidth, spectral_efficiency):
        """
        Estimate link capacity based on bandwidth and received signal.

        Parameters
        ----------
        bandwidth : int
            Channel bandwidth in MHz
        spectral_efficiency : float
            Efficiency of information transfer in Bps/Hz

        Returns
        -------
        capacity_mbps : float
            Average link budget capacity in Mbps.
        capacity_mbps_km2 : float
            Average site area capacity in Mbps km^2.

        """
        bandwidth_in_hertz = bandwidth * 1e6 #MHz to Hz

        capacity_mbps = (
            (bandwidth_in_hertz * spectral_efficiency) / 1e6
        )

        capacity_mbps_km2 = (
            capacity_mbps / (self.site_area.area / 1e6)
        )

        return capacity_mbps, capacity_mbps_km2


    def receiver_density(self):
        """

        Calculate receiver density per square kilometer (km^2)

        Returns
        -------
        receiver_density : float
            Density of receivers per square kilometer (km^2).

        Notes
        -----
        Function returns `0` when no receivers are configered to the area.

        """
        if not self.receivers:
            return 0

        postcode_sector_area = (
            [round(a.area) for a in self.area.values()]
            )[0]

        receiver_density = (
            len(self.receivers) / (postcode_sector_area/1000000)
            )

        return receiver_density


class Transmitter(object):
    """

    Radio transmitter object.

    Parameters
    ----------
    data : dict
        Contains all object data parameters.
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.

    """
    def __init__(self, data, ant_type, simulation_parameters):

        self.id = data['properties']['site_id']
        self.coordinates = data['geometry']['coordinates']

        self.ant_type = ant_type

        if ant_type == 'macro':
            self.ant_height = simulation_parameters['tx_macro_baseline_height']
            self.power = simulation_parameters['tx_macro_power']
            self.gain = simulation_parameters['tx_macro_gain']
            self.losses = simulation_parameters['tx_macro_losses']

        if ant_type == 'micro':
            self.ant_height = simulation_parameters['tx_micro_baseline_height']
            self.power = simulation_parameters['tx_micro_power']
            self.gain = simulation_parameters['tx_micro_gain']
            self.losses = simulation_parameters['tx_micro_losses']


class InterferingTransmitter(object):
    """

    A site object is specific site.

    Parameters
    ----------
    data : dict
        Contains all object data parameters.
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.

    """
    def __init__(self, data, ant_type, simulation_parameters):

        self.id = data['properties']['site_id']
        self.coordinates = data['geometry']['coordinates']

        self.ant_type = ant_type

        if ant_type == 'macro':
            self.ant_height = simulation_parameters['tx_macro_baseline_height']
            self.power = simulation_parameters['tx_macro_power']
            self.gain = simulation_parameters['tx_macro_gain']
            self.losses = simulation_parameters['tx_macro_losses']

        if ant_type == 'micro':
            self.ant_height = simulation_parameters['tx_micro_baseline_height']
            self.power = simulation_parameters['tx_micro_power']
            self.gain = simulation_parameters['tx_micro_gain']
            self.losses = simulation_parameters['tx_micro_losses']


class Receiver(object):
    """

    Radio receiver object (UE).

    Parameters
    ----------
    data : dict
        Contains all object data parameters.
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.

    """
    def __init__(self, data, simulation_parameters):
        self.id = data['properties']['ue_id']
        self.coordinates = data['geometry']["coordinates"]

        self.ue_height = data['properties']['ue_height']
        self.gain = data['properties']['gain']
        self.losses = data['properties']['losses']
        self.misc_losses = data['properties']['misc_losses']
        self.indoor = data['properties']['indoor']


class SiteArea(object):
    """

    site area object.

    Parameters
    ----------
    data : dict
        Contains all object data parameters.

    """
    def __init__(self, data):
        self.id = data['properties']['site_id']
        self.geometry = data['geometry']
        self.coordinates = data['geometry']['coordinates']
        self.area = self._calculate_area(data)


    def _calculate_area(self, data):
        polygon = shape(data['geometry'])
        area = polygon.area
        return area


def pairwise(iterable):
    """

    Return iterable of 2-tuples in a sliding window

    Parameters
    ----------
    iterable: list
        Sliding window

    Returns
    -------
    list of tuple
        Iterable of 2-tuples

    Example
    -------
        >>> list(pairwise([1,2,3,4]))
            [(1,2),(2,3),(3,4)]

    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
