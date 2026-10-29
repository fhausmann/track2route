"""Tests for track2route._base.convert_trackpoint_to_routepoint."""

from datetime import datetime, timezone

import gpxpy.gpx

from track2route._base import convert_trackpoint_to_routepoint


def make_full_trackpoint():
    """Create a GPXTrackPoint with every convertible attribute set."""
    trackpoint = gpxpy.gpx.GPXTrackPoint(
        latitude=1.23,
        longitude=4.56,
        elevation=78.9,
        time=datetime(2024, 5, 17, 12, 30, tzinfo=timezone.utc),
        name="Waypoint",
        symbol="Summit",
        comment="Some comment",
        horizontal_dilution=1.1,
        vertical_dilution=2.2,
        position_dilution=3.3,
    )
    # description and type are attributes of GPXTrackPoint, but not
    # constructor arguments.
    trackpoint.description = "A point of interest"
    trackpoint.type = "Waypoint"
    return trackpoint


def test_converts_into_new_routepoint():
    trackpoint = make_full_trackpoint()
    routepoint = convert_trackpoint_to_routepoint(trackpoint)
    assert isinstance(routepoint, gpxpy.gpx.GPXRoutePoint)
    assert routepoint is not trackpoint


def test_all_attributes_are_copied():
    trackpoint = make_full_trackpoint()
    routepoint = convert_trackpoint_to_routepoint(trackpoint)
    assert routepoint.latitude == 1.23
    assert routepoint.longitude == 4.56
    assert routepoint.elevation == 78.9
    assert routepoint.time == trackpoint.time
    assert routepoint.name == "Waypoint"
    assert routepoint.description == "A point of interest"
    assert routepoint.symbol == "Summit"
    assert routepoint.type == "Waypoint"
    assert routepoint.comment == "Some comment"
    assert routepoint.horizontal_dilution == 1.1
    assert routepoint.vertical_dilution == 2.2
    assert routepoint.position_dilution == 3.3


def test_missing_attributes_default_to_none():
    trackpoint = gpxpy.gpx.GPXTrackPoint(latitude=1.0, longitude=2.0)
    routepoint = convert_trackpoint_to_routepoint(trackpoint)
    assert (routepoint.latitude, routepoint.longitude) == (1.0, 2.0)
    assert routepoint.elevation is None
    assert routepoint.time is None
    assert routepoint.name is None
    assert routepoint.description is None
    assert routepoint.symbol is None
    assert routepoint.type is None
    assert routepoint.comment is None
    assert routepoint.horizontal_dilution is None
    assert routepoint.vertical_dilution is None
    assert routepoint.position_dilution is None


def test_modifying_the_copy_leaves_original_untouched():
    trackpoint = make_full_trackpoint()
    routepoint = convert_trackpoint_to_routepoint(trackpoint)
    routepoint.name = "Changed"
    assert trackpoint.name == "Waypoint"
