#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from atraxiflow.core import Resource, Container
from typing import List
import pytest

class DemoResource1(Resource):

    def __init__(self):
        self._value = 'Res1'
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)

class DemoResource2(Resource):

    def __init__(self):
        self._value = 'Res2'
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)

class DemoResource3(Resource):

    def __init__(self):
        self._value = 'Res3'
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)


def test_create_container():
    container = Container([DemoResource1(), DemoResource2()])
    assert isinstance(container, Container)


def test_find_nodes():
    test1 = DemoResource1()
    test2 = DemoResource2()
    test3 = DemoResource3()
    container = Container(test1, test2, test3)

    assert [test1, test2, test3] == container.find('*')
    assert [test1] == container.find('*Resource1')
    assert [test1, test2, test3] == container.find('{}.*'.format(DemoResource1.__module__))
    assert [test2] == container.find('{}.{}'.format(DemoResource2.__module__, DemoResource2.__name__))

    assert container.items() == [test1, test2, test3]


def test_add_nodes():
    container = Container()
    assert container.items() == []

    res = DemoResource1()
    container.add(res)
    assert container.items() == [res]
