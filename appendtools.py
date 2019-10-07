""" Font tools for appending point at line or curve object.

Last modified date: 2019/10/07

Created by Jeongjae Suk.
Modified by Seongju Woo.
"""
from fontTools.misc.bezierTools import splitCubic, splitCubicAtT, splitLine
from mojo.roboFont import RContour, RPoint

def append_point_coordinate(contour, rpoints, where, is_horizontal):
    """ 곡선을 x 혹은 y 값을 기준으로 나누어 점을 추가하는 함수.

    Args:
        contour:: RContour object
            robofont에서 사용하는 contour object인 RContour.
        rpoints:: [RPoint object, ...]
            robofont에서 사용하는 point object인 RPoint의 list[곡선의 시작점, 보조점, 보조점, 곡선의 끝점]
            순으로 구성 필요, 곡선의 시작점은 contour의 방향상 가장 먼저 나오는 점.
        where:: int or float
            나눌 기준이 될 x 혹은 y 값.
        is_horizontal:: bool
            where이 x 값이면 False, y 값이면 True.

    Returns:
        status flag:: int
            1이면 정상 종료, -1이면 에러 발생.
    """
    points = _r2t(rpoints)
    new_curve = splitCubic(points[0], points[1], points[2], points[3], where, is_horizontal)

    if len(new_curve) < 2:
        return -1

    if _append_point_curve(contour, rpoints, new_curve):
        return -1

    return 1

def append_point_rate(contour, rpoints, rate):
    """ 곡선을 비율로 나누어 점을 추가하는 함수.
    
    Args:
        contour:: RContour object
            robofont에서 사용하는 contour object인 RContour.
        rpoints:: [RPoint object, ...]
            robofont에서 사용하는 point object인 RPoint의 list[곡선의 시작점, 보조점, 보조점, 곡선의 끝점]
            순으로 구성 필요, 곡선의 시작점은 contour의 방향상 가장 먼저 나오는 점.
        rate:: float
            0 ~ 1 사이의 나눌 비율.

    Returns:
        status flag:: int
            1이면 정상 종료, -1이면 에러 발생.
    """
    points = _r2t(rpoints)
    new_curve = splitCubicAtT(points[0], points[1], points[2], points[3], rate)

    if len(new_curve) < 2:
        return -1

    if _append_point_curve(contour, rpoints, new_curve) < 0:
        return -1

    return 1

def _append_point_curve(contour, rpoints, curve):
    segment_index = _segment_index_of(contour, rpoints[3])
    if segment_index < 0:
        return -1

    _change_point(contour[segment_index].offCurve[0], curve[1][1])
    _change_point(contour[segment_index].offCurve[1], curve[1][2])

    contour.insertSegment(segment_index, 'curve', list(curve[0][1:]))

    contour.round()

    return 1

def append_point_coordinate_line(contour, rpoints, where, is_horizontal):
    """ 직선을 x 혹은 y 값을 기준으로 나누어 점을 추가하는 함수.

    Args:
        contour:: RContour object
            robofont에서 사용하는 contour object인 RContour.
        rpoints:: [RPoint object, ...]
            robofont에서 사용하는 point object인 RPoint의 list[직선의 시작점, 직선의 끝점]
            순으로 구성 필요, 직선의 시작점은 contour의 방향상 가장 먼저 나오는 점.
        where:: int or float
            나눌 기준이 될 x 혹은 y 값.
        is_horizontal:: bool
            where이 x 값이면 False, y 값이면 True.

    Returns:
        status flag:: int
            1이면 정상 종료, -1이면 에러 발생.
    """
    points = _r2t(rpoints)
    new_line = splitLine(points[0], points[1], where, is_horizontal)

    if len(new_line) < 2:
        return -1

    segment_index = _segment_index_of(contour, rpoints[1])
    if segment_index < 0:
        return -1

    contour.insertSegment(segment_index, 'line', [new_line[0][1]])

    contour.round()

    return 1

def append_point_rate_line(contour, rpoints, rate):
    """ 직선을 비율로 나누어 점을 추가하는 함수.

    Args:
        contour:: RContour object
            robofont에서 사용하는 contour object인 RContour.
        rpoints:: [RPoint object, ...]
            robofont에서 사용하는 point object인 RPoint의 list[직선의 시작점, 직선의 끝점]
            순으로 구성 필요, 직선의 시작점은 contour의 방향상 가장 먼저 나오는 점.
        rate:: float
            0 ~ 1 사이의 나눌 비율.

    Returns:
        status flag:: int
            1이면 정상 종료, -1이면 에러 발생.
    """

    if not (contour and rpoints and 0 <= rate <= 1):
        return -1

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

    return 1

def _internal_division(a, b, rate):
    s = 1 - rate
    return list(map(lambda x: int(round(x)), [b.x*rate + a.x*s, b.y*rate + a.y*s]))

def _segment_index_of(contour, rpoint):
    for index in range(0, len(contour)):
        if contour[index].onCurve.x == rpoint.x and contour[index].onCurve.y == rpoint.y:
            return index

    return -1

def _change_point(rpoint, point):
    rpoint.x = point[0]
    rpoint.y = point[1]

def _r2t(points):
    tpoint = []

    for point in points:
        tpoint.append((point.x, point.y))

    return tpoint
