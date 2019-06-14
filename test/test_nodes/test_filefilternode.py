#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest
import re
from atraxiflow.base.filesystem import FileFilterNode, LoadFilesNode
from atraxiflow.core import *

@pytest.fixture(scope="module")
def file_fixture(tmpdir_factory):
    testFiles = {
        "file_these_1": 2 * 1024 * 1024,  # M
        "file_are_21_end": 5 * 1024 * 1024,  # M
        "file_four_31_end": 578 * 1024,  # K
        "file_files_4": 10 * 1024,  # K
    }

    path = tmpdir_factory.mktemp('data')

    for name, size in testFiles.items():
        fp = open(str(path.join(name)), "wb")
        fp.seek(size - 1)
        fp.write(b"\0")
        fp.close()

    return path


def test_filter_size_single(file_fixture):
    fn = FileFilterNode({"filter": [
        ['file_size', '>', '120K']
    ]})

    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})
    assert Workflow.create([fin, fn]).run()

    assert len(fin.get_output().first().get_value()) == 4
    assert len(fn.get_output().items()) == 3


def test_filter_size_multiple(file_fixture):
    fn = FileFilterNode({
        'filter': [
            ['file_size', '>', '120K'],
            ['file_size', '<', '4M']
        ]
    })

    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})
    assert Workflow.create([fin, fn]).run()

    assert len(fin.get_output().first().get_value()) == 4
    assert len(fn.get_output().items()) == 2


def test_filter_filename_single_contains(file_fixture):
    fn = FileFilterNode({
        'filter': [
            ['filename', 'contains', '1']
        ]
    })

    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})
    assert Workflow.create([fin, fn]).run()

    assert len(fin.get_output().first().get_value()) == 4
    assert len(fn.get_output().items()) == 3


def test_filter_filename_single_matches(file_fixture):
    fn = FileFilterNode({
        'filter': [
            ['filename', 'matches', re.compile(r'file_\w+_\d+_end')]
        ]
    })

    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})
    assert Workflow.create([fin, fn]).run()

    assert len(fin.get_output().first().get_value()) == 4
    assert len(fn.get_output().items()) == 2



def test_filter_filename_single_contains_fail(file_fixture):
    fn = FileFilterNode({
        'filter': [
            ['filename', 'contains', 'hellowordl']
        ]
    })

    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})
    assert Workflow.create([fin, fn]).run()

    assert len(fin.get_output().first().get_value()) == 4
    assert len(fn.get_output().items()) == 0



def test_filter_filename_single_starts(file_fixture):
    fn = FileFilterNode({
        'filter': [
            ['filename', 'startswith', 'file_these']
        ]
    })

    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})
    assert Workflow.create([fin, fn]).run()

    assert len(fin.get_output().first().get_value()) == 4
    assert len(fn.get_output().items()) == 1


def test_filter_filename_single_ends(file_fixture):
    fn = FileFilterNode({
        'filter': [
            ['filename', 'endswith', '_end']
        ]
    })

    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})
    assert Workflow.create([fin, fn]).run()

    assert len(fin.get_output().first().get_value()) == 4
    assert len(fn.get_output().items()) == 2


def test_filter_filename_multiple(file_fixture):
    fn = FileFilterNode({
        'filter': [
            ['filename', 'endswith', '_end'],
            ['filename', 'contains', '21']
        ]
    })

    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})
    assert Workflow.create([fin, fn]).run()

    assert len(fin.get_output().first().get_value()) == 4
    assert len(fn.get_output().items()) == 1


def test_filter_filetype(file_fixture):
    file_fixture.mkdir('demo')

    fn = FileFilterNode({
        'filter': [
            ['type', '=', 'file']
        ]
    })

    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})
    assert Workflow.create([fin, fn]).run()

    assert len(fin.get_output().first().get_value()) == 5
    assert len(fn.get_output().items()) == 4

    # reset
    fin = LoadFilesNode({'path': str(file_fixture.join('*'))})

    # TODO: does not work -> reset state?
    fn.property("filter").set_value([
        ['type', '=', 'folder']
    ])

    fn = FileFilterNode({
        'filter': [
            ['type', '=', 'folder']
        ]
    })

    assert Workflow.create([fin, fn]).run()
    assert len(fn.get_output().items()) == 1
