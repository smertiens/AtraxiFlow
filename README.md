# AtraxiFlow
The python workflow framework

[![Build Status](https://travis-ci.org/smertiens/AtraxiFlow.svg?branch=master)](https://travis-ci.org/smertiens/AtraxiFlow)
[![Documentation Status](https://readthedocs.org/projects/atraxiflow/badge/?version=latest)](https://atraxiflow.readthedocs.io/en/latest/?badge=latest)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/smertiens/AtraxiFlow.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/smertiens/AtraxiFlow/context:python)
[![PyPI version](https://badge.fury.io/py/atraxi-flow.svg)](https://badge.fury.io/py/atraxi-flow)

* Create easy-to-read automation scripts in minutes - work with files, folders, images or anything else 
* Add your own logic as AtraxiFlow node and share it with others
* Use a console for in- and output or add one of the UI nodes to show graphical messages and input forms 
built with Qt5

## Learn

* See what you can do and check out the [examples](https://github.com/smertiens/AtraxiExamples)
* Get started with the [user manual](https://atraxiflow.readthedocs.io/en/latest/manual)
* Learn how to write your own nodes in minutes with the [developer manual](https://atraxiflow.readthedocs.io/en/latest/dev)

## Install
```
pip install atraxi-flow
```

## Requirements

* Python 3.5 or higher
* If you want to use the UI nodes and functions, you will need to install [Pyside2](https://pypi.org/project/PySide2/) (optional)


## Project goal
The goal is to create a framework that abstracts data (as resources) and business logic (as nodes) so they can be put 
together easily. This level of abstraction also allows for a visual approach on designing workflows, since nodes explain 
their structure and function to the user (using the  hint property) and to an editor application 
(using property definitions).

The source code of a resulting script should be as short as possible, easily readable and self explanatory.
Non-core nodes should be self contained (as a python module or package). 

**Using AtraxiFlow and AtraxiCreator should be fun** and focus on creativity and intuitiveness instead of technical aspects.
