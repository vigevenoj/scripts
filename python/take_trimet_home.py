#! /usr/bin/env python

#    Copyright 2012 Paul Munday
#    PO Box 28228, Portland, OR, USA 97228
#    paul at gatheringstorms.org

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    or <http://www.gatheringstorms.org/code/gpl.txt>.

# I used wnb as a starting point for this script, so I'm including the
# license used in wnb.

import requests
import yaml
import sys
import xml.etree.ElementTree as ET
import time
import StringIO

# url base is https://developer.trimet.org/ws/V1/arrivals/

# stop IDs:
# 8333 (Library/SW 9th, for Red/Blue)
# 7787 (SW 6th & Pine, for Green)
# 7782 (SW 6th & Oak, for 12)
# 8402 (NW Everett & Park, for 77)
# 2562 (SE 79th & Harold)
# 1818 (SE Foster & 82nd)
stopList = [8333, 7787, 7782, 8402]

# stop IDs can be comma-separated list (up to 10)
# ie, 8333,7787,7782,8402 for all four of the stops close to work
# Green line is route 200
# Red line is route 90
# Blue line is route 100
# bus routes are their respective numbers (12, 77)
routeList = [12, 77, 90, 100, 200]

# appID is required by trimet
appID = "091253C02A8A508C8B7B9779E"

class TriMet():
    def __init__(self, cfg = 'trimet.yaml'):
        try:
            with open(cfg, 'r') as fptr:
                configs = yaml.load(fptr.read())
        except IOError as e:
            print 'Check your permissions on {}, unable to load configuration.'.format(cfg)
            sys.exit(1)
        self.stops = map(str, configs['stops'])
        self.routes = map(str, configs['routes'])
        self.appID = configs['appID']

    def get_arrivals(self):
        url = 'http://developer.trimet.org/ws/V1/arrivals/locIDs/{0}/appID/{1}'
        url = url.format(','.join(self.stops), appID)
        try:
            data = requests.get(url)
        except Exception as e:
            print 'Unable to request from url "{0}" because: {1}"'.format(url, e)
            sys.exit(1)
        if data.status_code / 100 != 2:
            print '{0} response: "{1}"'.format(data.status_code, data.text)
            sys.exit(2)
        return data.text


    def conv_time(self, time_in):
        '''converts from milliseconds, returns formatted local time'''
        time_out = time.strftime("%I:%M %p",(time.localtime(time_in / 1000)))
        return time_out

    def find_bus(self):
        data = self.get_arrivals()

        arrivals_tree = ET.parse(StringIO.StringIO(data))
        prefix = '{urn:trimet:arrivals}'
        fp = './/' + prefix


        # should figure out a way to do human-readable location like in wnb
        # but we have multiple stops to find and only care about certain routes
        for node in arrivals_tree.findall(fp + 'location'):
            if node.attrib['locid'] in self.stops:
                print (node.attrib['locid'] + ' is in stops ')
                stop_location = node.attrib['desc']
                stop_direction = node.attrib['dir']
            else:
                # should probably notify the user if they're asking for stuff
                # and we don't have it
                print (node.attrib['locid'] + ' is NOT in stops ')

        try:
            print 'The next arrivals due at our stops ({0}) are:'.format(','.join(self.stops))
        except NameErorr:
            print 'Invalid stop IDs'
            sys.exit(3)

        isabus = None

        for node in arrivals_tree.findall(fp + 'arrival'):
            if node.attrib['route'] in self.routes:
                print node.attrib['fullSign']
                verb = node.attrib['status']
                try:
                    time = self.conv_time(int(node.attrib[verb]))
                    msg = '{0} arrival time: {1}'.format(verb, time)
                except KeyError as e:
                    bad_responses = {'delayed': 'This vehicle is delayed, arrival time is uncertain',
                                     'cancelled': 'This service has been cancelled'}
                    msg = bad_responses[verb]
                print msg
                isabus = True
                if node.attrib['detour'] == 'true':
                    print 'Detours in effect on route ' + node.attrib['route']

                # report on route status/inclement weather effects
                for node in arrivals_tree.findall(fp + 'routeStatus'):
                    print 'Route: {0}'.format(node.attrib['route'])
                    if node.attrib['status'] == 'estimatedOnly':
                        print 'Arrivals are only being reported if they can be estimated in the next hour due to inclement weather conditions'
                    elif node.attrib['status'] == 'off':
                        print 'No arrivals are being reported for this route because conditions such as snow and ice make prediction impossible. Hope you don\'t get too cold. Snowpocalypse strikes again!'

                # found stop but not a bus
                if not isabus:
                    print 'Oops! There does not appear to be a bus scheduled at this stop any time soon, you might consider walking.'

if __name__ == '__main__':
    trimet = TriMet()
    trimet.find_bus()
