============================================================================
track2route - Command line tool to convert GPXTracks into a routeable format
============================================================================

Getting started
===============
Download `track2route` with:

    git clone https://github.com/fhausmann/track2route.git

    cd track2route

You can then install it either with pip (version >= 19.0):

    pip install .

or if you have `poetry`__:: installed:

    poetry install --no-dev

.. __: https://python-poetry.org/

To create an GPXRoute from a GPXTrack now run:

    track2route --simplify <inputfile.gpx>

For further options try:

    track2route --help

Tests
=====
Tests needs the developmental version of `track2route` which can be
installed with:

    poetry install

And then they can be run with:

    poetry run pytest

Docs
====
To build the docs you need the docs extra:

    poetry install -E docs

And then you can build the docs with:

    poetry run make -C docs/ html

They can be found afterwards add docs/_build/html

To get a different format try:

    poetry run make -C docs/ help
