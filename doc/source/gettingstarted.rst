Getting started with AtraxiFlow
===============================

Installation
************

**Using pip (recommended)**
Install via the python package manager: ::

    python pip install atraxi-flow


**Downloading**
You can download the sources from the website. Please remember, that this will not provide all
dependencies like the Pillow imaging library needed for the Image-Nodes.

**Checkout from Github***
You can also clone the project from Github: ::

    git clone https://github.com/smertiens/AtraxiFlow


Contributors are always welcome!

Create your first workflow
**************************

To get you started we will write a small workflow that will do the following things:

1. Find all files in a given directory that are larger than 100 K
2. Put the files in a zip file
3. Write a friendly message for the user when the workflow is finished

.. todo:: Add small tutorial