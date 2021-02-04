"""Points and tracks used to convert to routes."""
import math
from typing import Any, Dict, Iterable, List, Optional

import gpxpy
import sortedcontainers
from geopy.distance import geodesic


class Point:
    """GPX point which can store the previous and next point as well.

    It also allows to calculate the angle between previous and next point
    and the distance to another point.
    """

    def __init__(
        self,
        point: gpxpy.gpx.GPXTrackPoint,
        next_point: Optional["Point"] = None,
        previous_point: Optional["Point"] = None,
    ):
        """Create GPX point.

        Args:
            point (gpxpy.gpx.GPXTrackPoint): GPXTrackPoint with the coordinates.
            next_point (Point, optional): Next point in the track. Defaults to None.
            previous_point (Point, optional): Previous point in the track. Defaults to None.
        """
        self._previous_point = previous_point
        self.point = point
        self._next_point = next_point
        self._angle = float("nan")

    def distance_to(self, other: Optional["Point"]) -> float:
        """Calculate distance to other Point instance.

        Args:
            other (Point): Other point for distance calculation.

        Returns:
            float: geodesic distance in metre between points.
                Can be nan if `other` is None.
        """
        if other is None:
            return float("nan")
        return (
            geodesic(
                (self.point.latitude, self.point.longitude),
                (other.point.latitude, other.point.longitude),
            ).km
            * 1000.0
        )

    @property
    def next_point(self) -> Optional["Point"]:
        """Next point in the track.

        Returns:
            Point: Next point in the track or None.
        """
        return self._next_point

    @next_point.setter
    def next_point(self, new_point):
        self._angle = float("nan")
        self._next_point = new_point

    @property
    def previous_point(self) -> Optional["Point"]:
        """Previous point in the track.

        Returns:
            Point: Previous point in the track or None.
        """
        return self._previous_point

    @previous_point.setter
    def previous_point(self, new_point):
        self._angle = float("nan")
        self._previous_point = new_point

    @property
    def distance_to_previous(self) -> float:
        """Get distance to previous point.

        Returns:
            float: Distance to previous point in metre.
        """
        return self.distance_to(self.previous_point)

    @property
    def distance_to_next(self) -> float:
        """Get distance to next point.

        Returns:
            float: Distance to next point in metre.
        """
        return self.distance_to(self.next_point)

    @property
    def angle(self) -> float:
        """Get Angle between previous, current and next point.

        Returns:
            float: Angle in degree.
        """
        if self.next_point is None or self.previous_point is None:
            return float("nan")
        if math.isnan(self._angle):
            distance_a = self.distance_to_previous
            distance_b = self.distance_to_next
            cos_gamma = (
                distance_a ** 2
                + distance_b ** 2
                - self.previous_point.distance_to(self.next_point) ** 2
            )
            try:
                cos_gamma /= 2 * distance_a * distance_b
            except ZeroDivisionError:
                self._angle = math.pi
            else:
                self._angle = math.acos(cos_gamma)
        return self._angle


def _sort_order(point):
    angle = point.angle
    return -1 if math.isnan(angle) else angle


class Track:
    """Track which can be converted to a route."""

    start_point: Point
    desc: Dict[str, Any]

    def __init__(self, points: Iterable[Point], **kwargs):
        """Store points and sort them by angle

        Args:
            points (Iterable[Point]): Points for the track.
            kwargs: Additional informations for the track.
        """
        self._points = list(points)
        self.start_point = self._points[0]
        self._points = sortedcontainers.SortedList(self._points, key=_sort_order)
        self.desc = kwargs

    def remove(self):
        """Remove the point with the biggest angle."""
        point_to_remove = self._points.pop(-1)
        self._points.discard(point_to_remove.next_point)
        self._points.discard(point_to_remove.previous_point)
        point_to_remove.previous_point.next_point = point_to_remove.next_point
        point_to_remove.next_point.previous_point = point_to_remove.previous_point
        self._points.add(point_to_remove.previous_point)
        self._points.add(point_to_remove.next_point)

    def remove_n(self, n_points: int):
        """Remove `n` points from the track.

        Total number of remaining points must stay greater 2.

        Args:
            n_points (int): Number of points to remove.

        """
        assert n_points <= len(self._points) - 2
        for _ in range(n_points):
            self.remove()

    @property
    def points(self) -> List[gpxpy.gpx.GPXTrackPoint]:
        """Points in correct order.

        Retursns:
            List[gpxpy.gpx.GPXTrackPoint]: List of points in track order.
        """
        points = []
        point: Optional[Point] = self.start_point
        while point is not None:
            points.append(point.point)
            point = point.next_point
        return points

    def __len__(self):
        return len(self._points)

    @classmethod
    def from_gpxtrack(cls, track: gpxpy.gpx.GPXTrack, **kwargs) -> "Track":
        """Create Track from GPXTrack.

        Returns:
            Track: Coverted GPXTrack
        """
        points = []
        for segment in track.segments:
            for point in segment.points:
                points.append(Point(point))

        assert len(points) >= 3

        points[0].next_point = points[1]
        points[-1].previous_point = points[-2]

        for i in range(1, len(points) - 1):
            points[i].previous_point = points[i - 1]
            points[i].next_point = points[i + 1]
        return cls(points=points, **kwargs)

    def to_route(self, n_points: int = -1) -> gpxpy.gpx.GPXRoute:
        """Convert Track to GPXRoute.

        Args:
            n_points (int, optional): Number of routing points. Defaults to all (-1).

        Returns:
            gpxpy.gpx.GPXRoute: The resulting GPXRoute.
        """
        route = gpxpy.gpx.GPXRoute(**self.desc)
        if n_points > 0:
            self.remove_n(len(self) - n_points)
        route.points = self.points
        return route
