#! /usr/bin/env python3
"""
Script to parse GPS location and time out of photos and
return the data as json
"""
import argparse
import collections
import exifread
import folium
import fractions
import geojson
# import imghdr
# import json
import logging
import os
import sys

PIC_EXTS = ['.jpg', '.jpeg', '.png']

logger = logging.getLogger(__name__)
logging.getLogger(__name__).addHandler(logging.NullHandler())


class GPS(object):
    def __init__(self, tags):
        self._refs = {'latitude':
                      1 if str(tags['GPS GPSLatitudeRef']) == 'N' else -1,
                      'longitude':
                      1 if str(tags['GPS GPSLongitudeRef']) == 'E' else -1}
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
        with open(self._path, 'rb') as photo:
            self._tags = exifread.process_file(photo)
        return self._tags

    @property
    def dict(self):
        if self._dict:
            return self._dict
        try:
            self._dict = {'filename': self._path,
                          'latitude': self.latitude,
                          'longitude': self.longitude}
        except (IOError, KeyError):
            logger.error('Unable to determine gps data for %s' % self._path)
            return None
        return self._dict

    def as_geojson(self):
        """
        Return the photo as a geojson feature located at the GPS coordinates
        and with the filename and path as properties
        """
        point = geojson.Point((self.longitude, self.latitude))
        feature = geojson.Feature(geometry=point,
                                  properties={
                                      'filename': self._path.split('/')[-1],
                                      'path': self._path})
        return feature

    def datetimestamp(self):
        # date = self._tags['GPS GPSDate']
        # convert time from array of [hh, mm, ss] in
        # self._tags['GPS GPSTimeStamp'] # [hh, mm, ss] array
        pass

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

    collection = []
    if not os.path.isdir(args.source):
        sys.exit(args.source + " is not a directory")
    for(dirpath, dirnames, filenames) in os.walk(args.source):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.lower() in PIC_EXTS:
                abspath = os.path.join(dirpath, filename)
            else:
                continue
            gpsdata = PhotoGPS(abspath)
            if gpsdata.dict:
                collection.append(gpsdata.as_geojson())
    fc = geojson.FeatureCollection(collection)
    logger.warn(geojson.dumps(fc))

    # use the first point in the trip to center a map
    # geojson is [lng,lat] and folium is [lat,lng] so make sure to adjust
    m = folium.Map(
        location=[fc[0].geometry.coordinates[1], fc[0].geometry.coordinates[0]],
    )
    folium.GeoJson(fc).add_to(m)
    m.save('index.html')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    sys.exit(main())
