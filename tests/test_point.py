"""Tests for track2route._base.Point."""

import math

import gpxpy.gpx
import pytest

from track2route import Point


def link(previous, current, next_point):
    """Link three points into a chain."""
    previous.next_point = current
    current.previous_point = previous
    current.next_point = next_point
    next_point.previous_point = current


def test_point_wraps_a_gpxtrackpoint(make_point):
    """A Point wraps a GPXTrackPoint and starts without neighbours."""
    point = make_point(1.0, 2.0)
    assert isinstance(point, Point)
    assert isinstance(point.point, gpxpy.gpx.GPXTrackPoint)
    assert (point.point.latitude, point.point.longitude) == (1.0, 2.0)
    assert point.next_point is None
    assert point.previous_point is None


def test_neighbour_setters_store_points(make_point):
    point = make_point(0.0, 0.0)
    other = make_point(0.0, 1.0)
    point.next_point = other
    point.previous_point = other
    assert point.next_point is other
    assert point.previous_point is other


def test_distance_to_other_point(make_point):
    """One degree of longitude at the equator is about 111.3 km."""
    a = make_point(0.0, 0.0)
    b = make_point(0.0, 1.0)
    assert a.distance_to(b) == pytest.approx(111_319.49, rel=1e-5)


def test_distance_to_none_is_nan(make_point):
    point = make_point(0.0, 0.0)
    assert math.isnan(point.distance_to(None))


def test_distance_is_symmetric(make_point):
    a = make_point(0.0, 0.0)
    b = make_point(1.0, 1.0)
    assert a.distance_to(b) == pytest.approx(b.distance_to(a))


def test_distance_scales_linearly_along_the_equator(make_point):
    """The equator is a geodesic, so distances along it scale linearly."""
    a = make_point(0.0, 0.0)
    b = make_point(0.0, 1.0)
    c = make_point(0.0, 2.0)
    assert a.distance_to(c) == pytest.approx(2 * a.distance_to(b))


def test_distance_to_previous_and_next(make_point):
    a = make_point(0.0, 0.0)
    b = make_point(0.0, 1.0)
    c = make_point(0.0, 2.0)
    link(a, b, c)
    expected = pytest.approx(111_319.49, rel=1e-5)
    assert b.distance_to_previous == expected
    assert b.distance_to_next == expected


def test_angle_is_nan_without_both_neighbours(make_point):
    a = make_point(0.0, 0.0)
    assert math.isnan(a.angle)
    b = make_point(0.0, 1.0)
    a.next_point = b
    assert math.isnan(a.angle)


def test_angle_of_nearly_straight_point(make_point):
    """A point on an almost straight line has an angle close to pi."""
    a = make_point(0.0, 0.0)
    b = make_point(0.0001, 1.0)
    c = make_point(0.0, 2.0)
    link(a, b, c)
    assert b.angle == pytest.approx(math.pi, abs=1e-3)


def test_angle_of_right_angle_corner(make_point):
    """A 90 degree turn between west and north yields roughly pi / 2."""
    a = make_point(0.0, 0.0)
    b = make_point(0.0, 1.0)
    c = make_point(1.0, 1.0)
    link(a, b, c)
    assert b.angle == pytest.approx(math.pi / 2, abs=0.05)


def test_angle_with_zero_length_leg(make_point):
    """A zero-length leg degenerates the law of cosines; result is pi."""
    a = make_point(0.0, 0.0)
    b = make_point(0.0, 0.0)
    c = make_point(0.0, 1.0)
    link(a, b, c)
    assert b.angle == pytest.approx(math.pi)


def test_angle_is_recomputed_after_relinking(make_point):
    """Changing a neighbour must invalidate the cached angle."""
    west = make_point(0.0, 0.0)
    middle = make_point(0.0001, 1.0)
    east = make_point(0.0, 2.0)
    north = make_point(1.0, 1.0)
    link(west, middle, east)
    assert middle.angle == pytest.approx(math.pi, abs=1e-3)
    middle.next_point = north
    north.previous_point = middle
    assert middle.angle == pytest.approx(math.pi / 2, abs=0.05)
