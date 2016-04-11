"""Script to parse GPS location and time out of photos and return the data as json"""
import argparse
import sys
import os
import exifread
import imghdr
from fractions import Fraction
from collections import defaultdict
import json

def main():
    """Main entry point for script"""
    parser = argparse.ArgumentParser(description="Script to parse gps location and time from a directory of photos")
    parser.add_argument("source")
    args = parser.parse_args()

    gps_info_for_files = []
    #file_list = get_file_list(args.source)
    files = []
    if os.path.isdir(args.source):
        for(dirpath, dirnames, filenames) in os.walk(args.source):
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() in ('.jpg', '.jpeg', '.png'):
                    latitude, longitude = read_gps_data(os.path.join(dirpath,filename))
                    if latitude and longitude:
                        this_image = { 'filename': filename, 'latitude': latitude, 'longitude': longitude }
                        gps_info_for_files.append(this_image)
            break
    else:
        sys.exit(path + " is not a directory")

    info = json.dumps(gps_info_for_files)
    print info

def read_gps_data(photofile):
    """Read exif gps data from a single image file"""
    # Reminder: the values in the exif tags dict are not strings
    latitude = None
    longitude = None
    f = open(photofile, 'rb')
    tags = exifread.process_file(f)
    for key in tags.keys():
        if str(key) == "GPS GPSLongitude":
            longitude = _convert_to_degrees(_get_if_exist(tags, key))
        if str(key) == "GPS GPSLatitude":
            latitude = _convert_to_degrees(_get_if_exist(tags, key))
    gps_latitude_ref = str(_get_if_exist(tags, "GPS GPSLatitudeRef"))
    gps_longitude_ref = str(_get_if_exist(tags, "GPS GPSLongitudeRef"))

    if latitude and gps_latitude_ref and longitude and gps_longitude_ref:
        if gps_latitude_ref != "N": # if not north, negative latitude (south of equator)
            latitude = 0 - latitude
        if gps_longitude_ref != "E": # if not east, negative longitude (west of prime meridian)
            longitude = 0 - longitude
    return latitude, longitude
    

def get_timestamp(exif_data):
    """Extract gps timestamp from exif data"""
    dt = None
    utc = pytz.utc
    if "GPSInfo" in exif_data:
        gps_time_stamp = exif_data["GPS GPSTimeStamp"]
        if 'GPSDateStamp' in exif_data:
            gps_date = [int(i) for i in exif_data["GPS GPSTimeStamp"].split(':')]


def _convert_to_degrees(value):
    degrees = float(Fraction(str(value.values[0])))
    minutes = float(Fraction(str(value.values[1])))
    seconds = float(Fraction(str(value.values[2])))
    
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

def _get_if_exist(data, key):
    if key in data:
        return data[key]
		
    return None

if __name__ == '__main__':
    sys.exit(main())
