#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

class FlinnEngdahl(object):
    """
    Load data from asc files and allow to resolve coordinates
    to Flinn Engdahl region names.
    """

    data_directory = os.path.join(os.path.dirname(__file__), 'data')

    names_file = os.path.join(data_directory, 'names.asc')
    quadsindex_file = os.path.join(data_directory, 'quadsidx.asc')
    sect_files = (
        os.path.join(data_directory, 'nesect.asc'),
        os.path.join(data_directory, 'nwsect.asc'),
        os.path.join(data_directory, 'sesect.asc'),
        os.path.join(data_directory, 'swsect.asc')
    )
    quads_order = ('ne', 'nw', 'se', 'sw')

    def __init__(self):
        self.quads_index = []

        directory =  os.path.dirname(__file__)

        with open(self.names_file, 'r') as fh:
            self.names = [ name.strip() for name in fh ]

        with open(self.quadsindex_file, 'r') as fh:
            indexes = []
            for index in fh:
                indexes += [ n.strip() for n in index.split(' ') if n != '' ]

        self.lons_per_lat = dict(zip(
            self.quads_order,
            [indexes[x:x+91] for x in xrange(0, len(indexes), 91)]
        ))

        self.lat_begins = {}

        for quad, index in self.lons_per_lat.items():
            begin = 0
            end = -1
            begins = []
            n = 0

            for item in index:
                n += 1
                begin = end + 1
                begins.append(begin)
                end += int(item)

            self.lat_begins[quad] = begins

        self.lons = {}
        self.fenums = {}
        for quad, sect_file in zip(self.quads_order, self.sect_files):
            sect = []
            with open(sect_file, 'r') as fh:
                for line in fh:
                    sect += [ int(v) for v in line.strip().split(' ') if v != '' ]

            lons = []
            fenums = []
            n = 0
            for item in sect:
                n += 1
                if n % 2:
                    lons.append(item)
                else:
                    fenums.append(item)

            self.lons[quad] = lons
            self.fenums[quad] = fenums

    def get_quadrant(self, longitude, latitude):
        """
        Return quadrat from given coordinate

        :param longitude: WGS84 longitude
        :type longitude: int or float
        :param latitude: WGS84 latitude
        :type latitude: int or float
        :rtype: string
        :return: Quadrant name (ne, nw, se and sw)
        """
        if longitude >= 0 and latitude >= 0: return 'ne'
        if longitude <  0 and latitude >= 0: return 'nw'
        if longitude >= 0 and latitude <  0: return 'se'
        if longitude <  0 and latitude <  0: return 'sw'

    def get_region(self, longitude, latitude):
        """
        Return region from given coordinate

        :param longitude: WGS84 longitude
        :type longitude: int or float
        :param latitude: WGS84 latitude
        :type latitude: int or float
        :rtype: string
        :return: Flinn Engdahl region name
        """

        if longitude < -180 or longitude > 180: raise ValueError
        if latitude < -90 or latitude > 90: raise ValueError

        if longitude == -180: longitude = 180

        quad = self.get_quadrant(longitude, latitude)

        abs_longitude = int(abs(longitude))
        abs_latitude = int(abs(latitude))

        begin = self.lat_begins[quad][abs_latitude]
        num = int(self.lons_per_lat[quad][abs_latitude])

        my_lons = self.lons[quad][begin:begin+num]
        my_fenums = self.fenums[quad][begin:begin+num]

        n = 0
        for longitude in my_lons:
            if longitude > abs_longitude: break
            n += 1

        fe_index = n - 1
        fe_num = my_fenums[fe_index]
        fe_name = self.names[fe_num-1]

        return fe_name


if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
