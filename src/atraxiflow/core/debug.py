#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.stream import *


class Debug:
    '''
    A collection of tools that help with debugging.
    '''

    @staticmethod
    def print_resources(stream, query):
        '''
        Print all resources from stream

        :param stream: Stream to print resources from
        :type stream: Stream
        :param query: A resource query
        :type query: str
        :return: None
        '''

        def print_resource_data(data):
            name = ''
            if '__class__' in dir(data):
                name = data.__class__.__name__
            else:
                name = type(data)

            print('\t{0}: {1}'.format(name, str(data)))

        resources = stream.get_resources(query)

        if not isinstance(resources, dict) and not isinstance(resources, list):
            resources = [resources]
        
        x = 1
        for res in resources:
            print("{0}. {2} ({1}) -> data:".format(x, res.get_name(), res.__class__.__name__))

            if isinstance(res.get_data(), dict) or isinstance(res.get_data(), list):
                for data in res.get_data():
                    print_resource_data(data)
            else:
                print_resource_data(res.get_data())
            x += 1

