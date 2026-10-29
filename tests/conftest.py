"""Shared fixtures for the track2route test suite."""

import gpxpy.gpx
import pytest

from track2route import Point, Track


def _track_points(coords):
    """Create GPXTrackPoints from (latitude, longitude) tuples."""
    return [
        gpxpy.gpx.GPXTrackPoint(latitude=latitude, longitude=longitude)
        for latitude, longitude in coords
    ]


@pytest.fixture
def make_point():
    """Factory creating a single Point from a (latitude, longitude) tuple."""

    def _factory(latitude, longitude, **kwargs):
        return Point(
            gpxpy.gpx.GPXTrackPoint(latitude=latitude, longitude=longitude),
            **kwargs,
        )

    return _factory


@pytest.fixture
def make_gpx_track():
    """Factory creating a GPXTrack from one or more coordinate sequences.

    Each positional argument becomes one track segment.
    """

    def _factory(*segments, name=None, description=None):
        track = gpxpy.gpx.GPXTrack(name=name, description=description)
        for coords in segments:
            segment = gpxpy.gpx.GPXTrackSegment()
            segment.points.extend(_track_points(coords))
            track.segments.append(segment)
        return track

    return _factory


@pytest.fixture
def make_track(make_gpx_track):
    """Factory creating a track2route Track from one or more coordinate sequences."""

    def _factory(*segments, **kwargs):
        return Track.from_gpxtrack(make_gpx_track(*segments), **kwargs)

    return _factory
