""" Font tools for appending point at line or curve object.

Last modified date: 2020/01/02

Created by Jeongjae Suk.
Modified by Seongju Woo.
"""
from fontTools.misc.bezierTools import splitCubic, splitCubicAtT, splitLine

def append_point_coordinate(contour, rpoints, where, is_horizontal):
    """ Appends RPoint object to curve(RSegment object) by horizontal or vertical line.

    Args:
        contour:: RContour
            The RContour object that you want to add RPoint object.
        rpoints:: list
            A list of RPoint objects. It should be containing 4 RPoint objects like
            [startpoint, bcp(of startpoint), bcp(of endpoint), endpoint].
            The order of start and end follows a index of contour.points.
        where:: int or float
            The coordinate value of line(x value if uses vertical line otherwise y value).
        is_horizontal:: bool
            If this is True, uses horizontal line(coordinate value of y).
            Otherwise uses vertical line(coordinate value of x).

    Raises:
        arguments value error:: ValueError
            If not found target segment in contour, raises this error.
            This can be occured when the rpoints(RPoint objects) are not in the contour.points.
        splitting error:: AssertionError
            If function of splitting is not done properly, raises this error.
            For example, if it split one line(or curve) but result is also one line(or curve).
    """
    points = _r2t(rpoints)
    new_curve = splitCubic(points[0], points[1], points[2], points[3], where, is_horizontal)
    assert(len(new_curve) > 1)
    _append_point_curve(contour, rpoints, new_curve)

def append_point_rate(contour, rpoints, rate):
    """ Appends RPoint object to curve(RSegment object) by rate.

    Args:
        contour:: RContour
            The RContour object that you want to add RPoint object.
        rpoints:: list
            A list of RPoint objects. It should be containing 4 RPoint objects like
            [startpoint, bcp(of startpoint), bcp(of endpoint), endpoint].
            The order of start and end follows a index of contour.points.
        rate:: float
            A rate of location. It must be in [0, 1].

    Raises:
        arguments value error:: ValueError
            If not found target segment in contour, raises this error.
            This can be occured when the rpoints(RPoint objects) are not in the contour.points.
        splitting error:: AssertionError
            If function of splitting is not done properly, raises this error.
            For example, if it split one line(or curve) but result is also one line(or curve).
    """
    points = _r2t(rpoints)
    new_curve = splitCubicAtT(points[0], points[1], points[2], points[3], rate)
    assert(len(new_curve) > 1)
    _append_point_curve(contour, rpoints, new_curve)

def _append_point_curve(contour, rpoints, curve):
    segment_index = _segment_index_of(contour, rpoints[3])
    if segment_index is None:
        raise ValueError('Not found target segment in contour.')
    _change_point(contour[segment_index].offCurve[0], curve[1][1])
    _change_point(contour[segment_index].offCurve[1], curve[1][2])
    contour.insertSegment(segment_index, 'curve', list(curve[0][1:]))
    contour.round()

def append_point_coordinate_line(contour, rpoints, where, is_horizontal):
    """ Appends RPoint object to line(RSegment object) by horizontal or vertical line.

    Args:
        contour:: RContour
            The RContour object that you want to add RPoint object.
        rpoints:: list
            A list of RPoint objects. It should be containing startpoint and endpoint of line.
            The order of start and end follows a index of contour.points.
        where:: int or float
            The coordinate value of line(x value if uses vertical line otherwise y value).
        is_horizontal:: bool
            If this is True, uses horizontal line(coordinate value of y).
            Otherwise uses vertical line(coordinate value of x).

    Raises:
        arguments value error:: ValueError
            If not found target segment in contour, raises this error.
            This can be occured when the rpoints(RPoint objects) are not in the contour.points.
        splitting error:: AssertionError
            If function of splitting is not done properly, raises this error.
            For example, if it split one line(or curve) but result is also one line(or curve).
    """
    points = _r2t(rpoints)
    new_line = splitLine(points[0], points[1], where, is_horizontal)
    assert(len(new_line) > 1)
    segment_index = _segment_index_of(contour, rpoints[1])
    if segment_index is None:
        raise ValueError('Not found target segment in contour.')
    contour.insertSegment(segment_index, 'line', [new_line[0][1]])
    contour.round()

def append_point_rate_line(contour, rpoints, rate):
    """ Appends RPoint object to line(RSegment object) by rate.

    Args:
        contour:: RContour
            The RContour object that you want to add RPoint object.
        rpoints:: list
            A list of RPoint objects. It should be containing startpoint and endpoint of line.
            The order of start and end follows a index of contour.points.
        rate:: float
            A rate of location. It must be in [0, 1].

    Raises:
        arguments value error:: ValueError
            If contour or rpoints is None or rate is not in [0, 1], raises this error.
        splitting error:: AssertionError
            If function of splitting is not done properly, raises this error.
            For example, if it split one line(or curve) but result is also one line(or curve).
    """

    if not (contour and rpoints and 0 <= rate <= 1):
        raise ValueError('Arguments contour and rpoints must not be None and rate must be in [0, 1]')
    if rpoints[0].x == rpoints[1].x:
        append_point_coordinate_line(
            contour,
            rpoints,
            _internal_division(rpoints[0], rpoints[1], rate)[1],
            True
        )
    elif rpoints[0].y == rpoints[1].y:
        append_point_coordinate_line(
            contour,
            rpoints,
            _internal_division(rpoints[0], rpoints[1], rate)[0],
            False
        )
    else:
        append_point_coordinate_line(
            contour,
            rpoints,
            _internal_division(rpoints[0], rpoints[1], rate)[1],
            True
        )

def _internal_division(a, b, rate):
    s = 1 - rate
    return list(map(lambda x: int(round(x)), [b.x*rate + a.x*s, b.y*rate + a.y*s]))

def _segment_index_of(contour, rpoint):
    for index, segment in enumerate(contour):
        if segment.onCurve.x == rpoint.x and segment.onCurve.y == rpoint.y:
            return index
    return None

def _change_point(rpoint, point):
    rpoint.x = point[0]
    rpoint.y = point[1]

def _r2t(points):
    tpoint = []
    for point in points:
        tpoint.append((point.x, point.y))
    return tpoint
