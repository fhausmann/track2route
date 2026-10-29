"""Tests for track2route._base.Track."""

import gpxpy.gpx
import pytest

from track2route import Track

# An L-shaped track: east along the equator, then north along a meridian.
# The second and fourth point are bent by 0.0001 degrees (about 11 m) so
# they are not perfectly straight.
TRACK_COORDS = [
    (0.0, 0.0),
    (0.0001, 1.0),
    (0.0, 2.0),
    (1.0, 2.0001),
    (2.0, 2.0),
]


def coords_of(points):
    """Extract (latitude, longitude) tuples from GPX points."""
    return [(point.latitude, point.longitude) for point in points]


def test_points_are_linked_in_track_order(make_track):
    track = make_track(TRACK_COORDS)
    walked = []
    point = track.start_point
    while point is not None:
        walked.append((point.point.latitude, point.point.longitude))
        point = point.next_point
    assert walked == TRACK_COORDS
    assert track.start_point.previous_point is None


def test_len_returns_number_of_points(make_track):
    assert len(make_track(TRACK_COORDS)) == 5


def test_points_property_returns_gpxtrackpoints_in_order(make_track):
    points = make_track(TRACK_COORDS).points
    assert all(isinstance(point, gpxpy.gpx.GPXTrackPoint) for point in points)
    assert coords_of(points) == TRACK_COORDS


def test_segments_are_flattened_into_one_chain(make_gpx_track):
    track = Track.from_gpxtrack(make_gpx_track(TRACK_COORDS[:3], TRACK_COORDS[3:]))
    assert coords_of(track.points) == TRACK_COORDS


def test_from_gpxtrack_requires_three_points(make_gpx_track):
    two_points = make_gpx_track([(0.0, 0.0), (0.0, 1.0)])
    with pytest.raises(AssertionError):
        Track.from_gpxtrack(two_points)


def test_extra_kwargs_are_stored_as_description(make_track):
    track = make_track(TRACK_COORDS, name="Tour", description="A test tour")
    assert track.desc == {"name": "Tour", "description": "A test tour"}


def test_remove_drops_the_straightest_point(make_track):
    track = make_track(TRACK_COORDS[:4])
    track.remove()
    assert len(track) == 3
    assert coords_of(track.points) == [
        (0.0, 0.0),
        (0.0, 2.0),
        (1.0, 2.0001),
    ]


def test_remove_n_drops_the_straightest_points(make_track):
    track = make_track(TRACK_COORDS)
    track.remove_n(2)
    assert coords_of(track.points) == [
        (0.0, 0.0),
        (0.0, 2.0),
        (2.0, 2.0),
    ]


def test_remove_n_can_reduce_to_two_points(make_track):
    track = make_track(TRACK_COORDS)
    track.remove_n(3)
    assert len(track) == 2
    assert coords_of(track.points) == [(0.0, 0.0), (2.0, 2.0)]


def test_remove_n_rejects_removing_too_many_points(make_track):
    track = make_track(TRACK_COORDS)
    with pytest.raises(AssertionError):
        track.remove_n(4)


def test_to_route_returns_all_points_by_default(make_track):
    route = make_track(TRACK_COORDS).to_route()
    assert isinstance(route, gpxpy.gpx.GPXRoute)
    assert coords_of(route.points) == TRACK_COORDS


def test_to_route_creates_new_routepoints(make_track):
    track = make_track(TRACK_COORDS)
    route = track.to_route()
    for route_point, track_point in zip(route.points, track.points):
        assert isinstance(route_point, gpxpy.gpx.GPXRoutePoint)
        assert route_point is not track_point
        assert route_point.latitude == track_point.latitude
        assert route_point.longitude == track_point.longitude


def test_to_route_uses_kwargs_as_route_metadata(make_track):
    route = make_track(TRACK_COORDS, name="Tour", description="A test tour").to_route()
    assert route.name == "Tour"
    assert route.description == "A test tour"


def test_to_route_with_limited_point_count(make_track):
    route = make_track(TRACK_COORDS).to_route(3)
    assert coords_of(route.points) == [
        (0.0, 0.0),
        (0.0, 2.0),
        (2.0, 2.0),
    ]


def test_to_route_with_two_points_keeps_the_endpoints(make_track):
    route = make_track(TRACK_COORDS).to_route(2)
    assert coords_of(route.points) == [(0.0, 0.0), (2.0, 2.0)]


def test_to_route_with_more_points_than_available(make_track):
    """A point count above the track length keeps every point."""
    route = make_track(TRACK_COORDS).to_route(100)
    assert coords_of(route.points) == TRACK_COORDS
