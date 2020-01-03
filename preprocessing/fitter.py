import bezier
import numpy as np
from fwig.tools import attributetools as at, appendtools as apt, \
                           extendtools as et, beziertools as bt

def _distance(point_1, point_2):
    return (point_1[0] - point_2[0])**2 + (point_1[1] - point_2[1])**2

def _get_all_points(contour):
    return set([point for point in contour.points if point.type != 'offcurve'])

def _get_penpair_dict(contour):
    penpair_dict = {}
    all_points = _get_all_points(contour)
    for point in all_points:
        penpair = at.get_attr(point, 'penPair')[1:-1]
        if penpair in penpair_dict:
            penpair_dict[penpair].append(point)
        else:
            penpair_dict[penpair] = [point]
    return penpair_dict

def _get_penpair_lines(piece):
    penpair_line_dict = {}
    penpair_dict = _get_penpair_dict(piece)
    range_ = 1000
    for point_1, point_2 in penpair_dict.values():
        if point_1.x == point_2.x:
            linear = et.get_linear_function(point_1.position, point_2.position, 'y')
            linear_curve = bt.make_linear_curve((linear(-range_), -range_), (linear(range_), range_))
        else:
            linear = et.get_linear_function(point_1.position, point_2.position, 'x')
            linear_curve = bt.make_linear_curve((-range_, linear(-range_)), (range_, linear(range_))) 
        penpair_line_dict[linear_curve] = ((point_1.x + point_2.x)/2, ((point_1.y + point_2.y)/2))
    return penpair_line_dict

def _get_intersect_points(original, line_dict):
    intersect_dict = {}
    for idx, point in enumerate(original.points):
        if point.type == 'offcurve':
            continue
        elif point.type == 'curve':
            line_segment = bt.RCurve([original.points[idx+i] for i in range(-3, 1)], degree=3)
        elif point.type == 'line':
            line_segment = bt.RCurve([original.points[idx+i] for i in range(-1, 1)], degree=1)
        for line, criteria in line_dict.items():
            intersect = line_segment.intersect(line)
            if intersect.any():
                if line in intersect_dict:
                    if len(intersect_dict[line]) > 1:
                        new_intersect = intersect_dict[line][:]
                        new_intersect.append((original.points[idx-3], point, \
                                              line_segment.evaluate(intersect[0, 0])))
                        intersect_dict[line] = sorted(new_intersect, \
                                                      key=lambda x: _distance(x[2], criteria))[:2]
                    else:
                        intersect_dict[line].append((original.points[idx-3], point, \
                                                     line_segment.evaluate(intersect[0, 0])))
                else:
                    intersect_dict[line] = [(original.points[idx-3], point, \
                                             line_segment.evaluate(intersect[0, 0]))]
    return intersect_dict

def _seg2curve(points, start_idx, end_idx):
    curve_dict = {}
    points_len = len(points)
    if points[end_idx].type == 'offcurve':
        raise ValueError(f'The Point of end index {end_idx} must be curve of line.')
    if start_idx > end_idx:
        end_idx += points_len
    for idx in range(start_idx+1, end_idx+1):
        if idx >= points_len:
            idx %= points_len
        if points[idx].type == 'curve':
            curve_dict[idx] = bt.RCurve([points[idx+i] for i in range(-3, 1)], degree=3)
        elif points[idx].type == 'line':
            curve_dict[idx] = bt.RCurve([points[idx+i] for i in range(-1, 1)], degree=1)
    return curve_dict

def _append_points(original, intersect_points):
    for intersects in intersect_points.values():
        for start_point, end_point, locate in intersects:
            curve_dict = _seg2curve(original.points, start_point.index, end_point.index)
            for idx, curve in curve_dict.items():
                if curve.degree == 1:
                    if curve.nodes[0][0] == curve.nodes[0][-1]:
                        linear_curve = bt.make_linear_curve(
                                (locate[0][0]-2, locate[1][0]),
                                (locate[0][0]+2, locate[1][0]))
                        intersect = curve.intersect(linear_curve)
                        if intersect.any():
                            curve_points = [original.points[idx+i] for i in range(0, -4, -1)]
                            apt.append_point_coordinate_line(original, curve_points, locate[1][0], True)
                            break
                    else:
                        linear_curve = bt.make_linear_curve(
                                (locate[0][0], locate[1][0]-2),
                                (locate[0][0], locate[1][0]+2))
                        intersect = curve.intersect(linear_curve)
                        if intersect.any():
                            curve_points = [original.points[idx+i] for i in range(0, -4, -1)]
                            apt.append_point_coordinate_line(original, curve_points, locate[0][0], False)
                            break
                elif curve.degree == 3:
                    if curve.nodes[0][0] == curve.nodes[0][1] == curve.nodes[0][-2] == curve.nodes[0][-1]:
                        linear_curve = bt.make_linear_curve(
                                (locate[0][0]-2, locate[1][0]),
                                (locate[0][0]+2, locate[1][0]))
                        intersect = curve.intersect(linear_curve)
                        if intersect.any():
                            curve_points = [original.points[idx+i] for i in range(0, -4, -1)]
                            apt.append_point_coordinate(original, curve_points, locate[1][0], True)
                            break
                    else:
                        linear_curve = bt.make_linear_curve(
                                (locate[0][0], locate[1][0]-2),
                                (locate[0][0], locate[1][0]+2))
                        intersect = curve.intersect(linear_curve)
                        if intersect.any():
                            curve_points = list(reversed([original.points[idx-i] for i in range(4)]))
                            apt.append_point_coordinate(original, curve_points, locate[0][0], False)
                            break

def _find_remove_list(original, piece, penpair_lines) -> list:
    1

def _remove_points(original, remove_list):
    for point in remove_list:
        original.removePoint(point, True)

def _find_point(contour, position, strict=False):
    for point in contour.points:
        if strict:
            if _distance(point.position, position) < 9:
                return point.index
        else:
            if point.position == position:
                return point.index
    return None

def _fit_bcps(standard, target, fit_target=True):
    if standard.naked().clockwise != target.naked().clockwise:
        if fit_target:
            target.cockwise = standard.clockwise
        else:
            standard.cockwise = target.clockwise
    for idx, point in enumerate(target.points):
        if target.points[idx].type != 'offcurve' and target.points[idx-1].type == 'offcurve':
            original_idx = _find_point(standard, point.position)
            if original_idx is not None:
                if fit_target:
                    if target.points[idx].smooth:
                        target.points[idx].smooth = False
                    target.points[idx-1].position = standard.points[original_idx-1].position
                    target.points[idx-2].position = standard.points[original_idx-2].position
                    target.setChanged()
                else:
                    if standard.points[original_idx].smooth:
                        standard.points[original_idx].smooth = False
                    standard.points[original_idx-1].position = target.points[idx-1].position
                    standard.points[original_idx-2].position = target.points[idx-2].position
                    standard.setChanged()

def fit_contour(original, piece, fit_piece=True):
    """ Fit piece to curve.

    Args:
        original:: RContour
        piece:: RContour
        fit_piece:: bool

    Examples:
        original = CurrentGlyph().contours[2]
        piece = CurrentGlyph().contours[3]
        fit_contour(original, piece)
    """
    penpair_lines = _get_penpair_lines(piece)
    intersect_points = _get_intersect_points(original, penpair_lines)
    _append_points(original, intersect_points)
    remove_list = _find_remove_list(original, piece, penpair_lines)
    _remove_points(original, remove_list)
    _fit_bcps(original, piece, fit_piece)
