from pprint import pprint
import csv

from model_address import Address

addresses = []

with open('data_to_elas/data/provinces.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        print(row[0])
        print(row[1])
        print(row[2])
        temp_province = {
            'province_id': row[0],
            'province_name': row[1],
            'province_type': row[2]
        }

        addresses.append(temp_province)

with open('data_to_elas/data/districts.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        temp_district = {
            'district_id': row[0], 
            'district_name': row[1],
            'district_type': row[2],
            'district_location': row[3],
        }

        # -1 since list start from 0
        if 'districts' not in addresses[int(row[4])-1]:
            addresses[int(row[4])-1]['districts'] = []
        
        addresses[int(row[4])-1]['districts'].append(temp_district)

with open('data_to_elas/data/wards.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        temp_subdistrict = {
            'subdistrict_id': row[0], 
            'subdistrict_name': row[1],
            'subdistrict_type': row[2],
            'subdistrict_location': row[3],
        }

        # -1 since list start from 0
        districts = addresses[int(row[5])-1]['districts']
        for district in districts:
            if district['district_id'] == str(int(row[4])): 
                if 'subdistricts' not in district: 
                    district['subdistricts'] = []
                district['subdistricts'].append(temp_subdistrict)

def convert_dms_to_dd(degrees, minutes, seconds):
    return seconds/3600 + minutes/60 + degrees

def parse_location(location):
    if location:
        lat_dms, lon_dms = location.split(',')

        dms = lat_dms.split()
        if len(dms) == 3:
            lat = convert_dms_to_dd(int(dms[0]), int(dms[1]), int(dms[2][:-1]))
        else:
            return None

        dms = lon_dms.split()
        if len(dms) == 3:
            lon = convert_dms_to_dd(int(dms[0]), int(dms[1]), int(dms[2][:-1]))
        else:
            return None

        return {
            'lat': lat,
            'lon': lon
        }

# Format data for Elasticsearch
for province in addresses: 
    elas_address = {}
    elas_address['province_id'] = province['province_id']
    elas_address['province_name'] = province['province_name']
    elas_address['province_type'] = province['province_type']
    
    for district in province['districts']:
        elas_address['district_id'] = district['district_id']
        elas_address['district_name'] = district['district_name']
        elas_address['district_type'] = district['district_type']
        elas_address['district_location'] = district['district_location']
        if 'subdistricts' in district:
            for subdistrict in district['subdistricts']:
                
                elas_address['_id'] = subdistrict['subdistrict_id']
                elas_address['subdistrict_id'] = subdistrict['subdistrict_id']
                elas_address['subdistrict_name'] = subdistrict['subdistrict_name']
                elas_address['subdistrict_type'] = subdistrict['subdistrict_type']
                elas_address['subdistrict_location'] = subdistrict['subdistrict_location']
                locations = [location for location in [parse_location(elas_address['subdistrict_location']), 
                                parse_location(elas_address['district_location'])] if location]

                subdistricts = (
                    '{} {}'.format(elas_address['subdistrict_type'], elas_address['subdistrict_name']),
                    elas_address['subdistrict_name']
                )

                districts = (
                    '{} {}'.format(elas_address['district_type'], elas_address['district_name']),
                    elas_address['district_name']
                )

                suggestions = []

                for subdistrict in subdistricts:
                    for district in districts:
                        suggestions.append('{}, {}, {}'.format(
                            subdistrict, district, elas_address['province_name']))
                        suggestions.append('{}, {}, {}'.format(
                            district, subdistrict, elas_address['province_name']))

                elas_address['suggestions'] = {}
                elas_address['suggestions']['contexts'] = {}
                elas_address['suggestions']['contexts']['location'] = locations
                elas_address['suggestions']['input'] = suggestions

                full_address = (elas_address['subdistrict_type'] + ' ' + elas_address['subdistrict_name'] + ', '
                                + elas_address['district_type'] + ' ' + elas_address['district_name'] + ', '
                                + elas_address['province_type'] + ' ' + elas_address['province_name'])

                elas_address['full_address'] = full_address

                # Save to Elasticsearch 
                try: 
                    doc = Address(**elas_address)
                    doc.save()
                except: 
                    print(elas_address)