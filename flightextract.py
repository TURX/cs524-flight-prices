# import os
# os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data3"))

import glob
import json
import csv

import tqdm
import pandas as pd
import pyarrow
import pyarrow.parquet

filenames = glob.glob('*/*/*.json', recursive = True)

csv_header = None

csv_name = 'itineraries.csv'

with open(csv_name, 'w', newline = '') as csv_file:
    for iteration_number, file in enumerate(tqdm.tqdm(filenames)):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            continue
        try:
            assert len(data['legs']) == len(data['offers']), "legs and offers not same length"
        except KeyError:
            continue
        for flight_info, fare_info in zip(data['legs'], data['offers']):
            assert flight_info['legId'] == fare_info['legIds'][0], "legIds don't match"
            try:
                assert flight_info['totalTravelDistanceUnits'] == 'mi', "totalTravelDistanceUnits is not 'mi'"
            except KeyError:
                pass
            assert fare_info['currency'] == 'USD', "currency is not 'USD'"
            searchDate, flightDate, basename = file.split('/')
            startingAirport, _, destinationAirport = basename.split('.')[0].split('_')
            entry = {
                'legId': flight_info['legId'],
                'searchDate': searchDate,
                'flightDate': flightDate,
                'startingAirport': startingAirport,
                'destinationAirport': destinationAirport,
                'fareBasisCode': flight_info['fareBasisCode'],
                'travelDuration': flight_info['travelDuration'],
                'elapsedDays': flight_info['elapsedDays'],
                'isBasicEconomy': flight_info['isBasicEconomy'],
                'isRefundable': flight_info['isRefundable'],
                'isNonStop': flight_info['isNonStop'],
                'baseFare': fare_info['baseFare'],
                'totalFare': fare_info['totalFare'],
                'seatsRemaining': fare_info['seatsRemaining'],
            }
            try:
                entry['totalTravelDistance'] = flight_info['totalTravelDistance']
            except KeyError:
                entry['totalTravelDistance'] = None
            assert len(flight_info['segments']) == len(fare_info['segmentAttributes'][0]), "segments and segmentAttributes not same length"
            departureTimeEpochSeconds = []
            departureTimeRaw = []
            arrivalTimeEpochSeconds = []
            arrivalTimeRaw = []
            arrivalAirportCode = []
            departureAirportCode = []
            airlineName = []
            airlineCode = []
            flightNumber = []
            equipmentDescription = []
            durationInSeconds = []
            distance = []
            cabinCode = []
            meal = []
            for segment, segment_attributes in zip(flight_info['segments'], fare_info['segmentAttributes'][0]):
                departureTimeEpochSeconds.append(segment['departureTimeEpochSeconds'])
                departureTimeRaw.append(segment['departureTimeRaw'])
                arrivalTimeEpochSeconds.append(segment['arrivalTimeEpochSeconds'])
                arrivalTimeRaw.append(segment['arrivalTimeRaw'])
                arrivalAirportCode.append(segment['arrivalAirportCode'])
                departureAirportCode.append(segment['departureAirportCode'])
                airlineName.append(segment['airlineName'])
                airlineCode.append(segment['airlineCode'])
                flightNumber.append(segment['flightNumber'])
                equipmentDescription.append(segment['equipmentDescription'])
                durationInSeconds.append(segment['durationInSeconds'])
                try:
                    distance.append(segment['distance'])
                except KeyError:
                    distance.append(None)
                cabinCode.append(segment_attributes['cabinCode'])
                try:
                    meal.append(segment['meal'])
                except KeyError:
                    meal.append(None)
            entry['segmentsDepartureTimeEpochSeconds'] = '||'.join(map(str, departureTimeEpochSeconds))
            entry['segmentsDepartureTimeRaw'] = '||'.join(map(str, departureTimeRaw))
            entry['segmentsArrivalTimeEpochSeconds'] = '||'.join(map(str, arrivalTimeEpochSeconds))
            entry['segmentsArrivalTimeRaw'] = '||'.join(map(str, arrivalTimeRaw))
            entry['segmentsArrivalAirportCode'] = '||'.join(map(str, arrivalAirportCode))
            entry['segmentsDepartureAirportCode'] = '||'.join(map(str, departureAirportCode))
            entry['segmentsAirlineName'] = '||'.join(map(str, airlineName))
            entry['segmentsAirlineCode'] = '||'.join(map(str, airlineCode))
            entry['segmentsFlightNumber'] = '||'.join(map(str, flightNumber))
            entry['segmentsEquipmentDescription'] = '||'.join(map(str, equipmentDescription))
            entry['segmentsDurationInSeconds'] = '||'.join(map(str, durationInSeconds))
            entry['segmentsDistance'] = '||'.join(map(str, distance))
            entry['segmentsCabinCode'] = '||'.join(map(str, cabinCode))
            entry['segmentsMeal'] = '||'.join(map(str, meal))
            if csv_header is None:
                csv_header = list(entry.keys())
                csv_writer = csv.DictWriter(csv_file, csv_header)
                csv_writer.writeheader()
            else:
                csv_writer = csv.DictWriter(csv_file, csv_header)
            csv_writer.writerow(entry)
