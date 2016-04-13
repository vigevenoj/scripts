"""Script to parse GPS location and time out of photos and return the data as json"""
import argparse
import sys
import os
import exifread
import imghdr
import fractions
import collections
import json

PIC_EXTS = ['.jpg', '.jpeg', '.png']

class GPS(object):
    def __init__(self, tags):
        self._refs = {'latitude':
                        1 if tags['GPS GPSLatitudeRef'] == 'N' else -1,
                      'longitude':
                        1 if tags['GPS GPSLongitudeRef'] == 'E' else -1}
        self._rawlatitude = tags['GPS GPSLatitude']
        self._rawlongitude = tags['GPS GPSLongitude']
        self._latlong = collections.defaultdict(lambda: None)
    @property
    def longitude(self):
        if self._latlong['longitude']:
            return self._latlong['longitude']
        self._compute()
        return self._latlong['longitude']
    @property
    def latitude(self):
        if self._latlong['latitude']:
            return self._latlong['latitude']
        self._compute()
        return self._latlong['latitude']
    def _compute(self):
        for i, j in {'latitude': self._rawlatitude,
                     'longitude': self._rawlongitude}.items():
            degs, mins, secs = ([float(fractions.Fraction(str(x)))
                                  for x in j.values[0:3]])
            sign = self._refs[i]
            self._latlong[i] = sign*(degs+(mins/60.0)+(secs/3600.0))

class PhotoGPS(object):
    ''' Class for finding and presenting GPS data in photos
    '''
    def __init__(self, path):
        self._path = path
        self._dict = {}
        self._gps = None
        self._tags = None
    @property
    def tags(self):
        if self._tags:
            return self._tags
        with open(self._path, 'r') as photo:
            self._tags = exifread.process_file(photo)
        return self._tags
    @property
    def dict(self):
        if self._dict:
            return self._dict
        try:
            self._dict =  {'filename': self._path,
                           'latitude': self.latitude,
                           'longitude': self.longitude}
        except (IOError, KeyError):
            print 'Unable to determine gps data for %s' % self._path
            return None
        return self._dict
    @property
    def latitude(self):
        if self._gps:
            return self._gps.latitude
        self._gps = GPS(self.tags)
        return self._gps.latitude
    @property
    def longitude(self):
        if self._gps:
            return self._gps.longitude
        self._gps = GPS(self.tags)
        return self._gps.longitude

def main():
    """Main entry point for script"""
    parser = (argparse
              .ArgumentParser(
                  description="Script to parse gps location and time from a \
                          directory of photos"))
    parser.add_argument("source",
                        help="Directory in which to search for photos.",
                        type=str)
    args = parser.parse_args()

    gps_info_for_files = []
    files = []
    if not os.path.isdir(args.source):
        sys.exit(path + " is not a directory")
    for(dirpath, dirnames, filenames) in os.walk(args.source):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext in PIC_EXTS:
                abspath = os.path.join(dirpath, filename)
            else:
                continue
            gpsdata = PhotoGPS(abspath)
            (gps_info_for_files.append(gpsdata.dict)
                if gpsdata.dict
                else False)
    print json.dumps(gps_info_for_files)

if __name__ == '__main__':
    sys.exit(main())
