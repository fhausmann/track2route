"""Tests for the track2route command line interface."""

import sys

import gpxpy
import gpxpy.gpx

from track2route.__main__ import main

# An L-shaped track: east along the equator, then north along a meridian.
TRACK_COORDS = [
    (0.0, 0.0),
    (0.0001, 1.0),
    (0.0, 2.0),
    (1.0, 2.0001),
    (2.0, 2.0),
]


def write_gpx_file(path, tracks):
    """Write a GPX file containing the given tracks."""
    gpx = gpxpy.gpx.GPX()
    gpx.tracks.extend(tracks)
    path.write_text(gpx.to_xml())
    return path


def run_cli(monkeypatch, *argv):
    """Run main() with a patched command line."""
    monkeypatch.setattr(sys, "argv", ["track2route", *(str(arg) for arg in argv)])
    main()


def test_writes_one_route_per_track(tmp_path, monkeypatch, make_gpx_track):
    infile = write_gpx_file(
        tmp_path / "input.gpx",
        [
            make_gpx_track(TRACK_COORDS, name="Tour", description="A test tour"),
            make_gpx_track([(0.0, 0.0), (0.0001, 1.0), (0.0, 2.0)], name="Second"),
        ],
    )
    outfile = tmp_path / "output.gpx"

    run_cli(monkeypatch, infile, "-o", outfile, "-n", "3")

    result = gpxpy.parse(outfile.read_text())
    assert len(result.routes) == 2
    first, second = result.routes
    assert first.name == "Tour"
    assert first.description == "A test tour"
    assert [(p.latitude, p.longitude) for p in first.points] == [
        (0.0, 0.0),
        (0.0, 2.0),
        (2.0, 2.0),
    ]
    assert second.name == "Second"
    assert len(second.points) == 3


def test_writes_output_gpx_by_default(tmp_path, monkeypatch, make_gpx_track):
    monkeypatch.chdir(tmp_path)
    infile = write_gpx_file(tmp_path / "input.gpx", [make_gpx_track(TRACK_COORDS)])

    run_cli(monkeypatch, infile)

    result = gpxpy.parse((tmp_path / "output.gpx").read_text())
    assert len(result.routes) == 1
    assert len(result.routes[0].points) == 5


def test_simplify_removes_collinear_points(tmp_path, monkeypatch, make_gpx_track):
    coords = [(0.0, float(lon)) for lon in range(5)] + [(1.0, 4.0)]
    infile = write_gpx_file(tmp_path / "input.gpx", [make_gpx_track(coords)])
    outfile = tmp_path / "output.gpx"

    run_cli(monkeypatch, infile, "-o", outfile, "--simplify")

    result = gpxpy.parse(outfile.read_text())
    assert len(result.routes) == 1
    assert [(p.latitude, p.longitude) for p in result.routes[0].points] == [
        (0.0, 0.0),
        (0.0, 4.0),
        (1.0, 4.0),
    ]
