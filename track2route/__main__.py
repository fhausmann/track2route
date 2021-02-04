"""Main function."""
import argparse
import pathlib

import gpxpy

import track2route


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Tool to convert GPX Track to a routeable GPXRoute.",
        prog="track2route",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("infile", type=str, help="Input GPX file")
    parser.add_argument(
        "-n",
        "--routepoints",
        default=50,
        metavar="n-points",
        type=int,
        help="Number of points per route in the output.",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        metavar="outputfilename",
        default="output.gpx",
        type=str,
        help="Name of the output file.",
    )
    parser.add_argument(
        "--simplify",
        action="store_true",
        help="Simplify track beforehand using Ramer-Douglas-Peucker algorithm from gpxpy",
    )
    parser.add_argument(
        "--max_distance",
        metavar="distance",
        type=float,
        default=10.0,
        help="Maximum distance for simplification procedure. Only used together with --simplify.",
    )
    args = parser.parse_args()
    with pathlib.Path(args.infile).open("r") as file:
        gpxfile = gpxpy.parse(file)
    for track in gpxfile.tracks:
        if args.simplify:
            track.simplify(max_distance=args.max_distance)
        new_track = track2route.Track.from_gpxtrack(
            track, name=track.name, description=track.description
        )
        route = new_track.to_route(args.routepoints)
        gpxfile.routes.append(route)
    with pathlib.Path(args.outfile).open("w") as file:
        file.write(gpxfile.to_xml())


if __name__ == "__main__":
    main()
