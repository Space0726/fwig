import bezier
import numpy as np
from stemfont.tools import attributetools as at
from stemfont.tools import appendtools as apt
from stemfont.tools import extendtools as et

def _distance(point_1, point_2):
    return (point_1[0] - point_2[0])**2 + (point_2[1] - point_2[1])**2

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

def _get_penpair_lines(segment):
    penpair_line_dict = {}
    penpair_dict = _get_penpair_dict(segment)
    for point_1, point_2 in penpair_dict.values():
        if point_1.x == point_2.x:
            linear = et.get_linear_function(point_1.position, point_2.position, 'y')
            nodes = np.asfortranarray(
                [[float(linear(-1000)), float(linear(1000))], [-1000., 1000.]])
        else:
            linear = et.get_linear_function(point_1.position, point_2.position, 'x')
            nodes = np.asfortranarray(
                [[-1000., 1000.], [float(linear(-1000)), float(linear(1000))]])
        penpair_line_dict[bezier.Curve(nodes, degree=1)] = ((point_1.x + point_2.x)/2, ((point_1.y + point_2.y)/2))
    return penpair_line_dict

def _get_intersect_points(original, line_dict):
    intersect_dict = {}
    for idx, point in enumerate(original.points):
        if point.type == 'offcurve':
            continue
        elif point.type == 'curve':
            nodes = np.asfortranarray(
                [[float(original.points[idx+i].x) for i in range(0, -4, -1)],
                 [float(original.points[idx+i].y) for i in range(0, -4, -1)]])
            line_segment = bezier.Curve(nodes, degree=3)
        elif point.type == 'line':
            nodes = np.asfortranarray(
                [[float(point.x), float(original.points[idx-1].x)],
                 [float(point.y), float(original.points[idx-1].y)]])
            line_segment = bezier.Curve(nodes, degree=1)
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
    for i in range(start_idx+1, end_idx+1):
        if i >= points_len:
            i %= points_len
        if points[i].type == 'curve':
            curve_dict[i] = bezier.Curve(np.asfortranarray(
                [[float(points[i+idx].x) for idx in range(0, -4, -1)],
                 [float(points[i+idx].y) for idx in range(0, -4, -1)]]), degree=3)
        elif points[i].type == 'line':
            curves_dict[i] = bezier.Curve(np.asfortranarray(
                [[float(points[i+idx].x) for idx in range(0, -2, -1)],
                 [float(points[i+idx].y) for idx in range(0, -2, -1)]]), degree=1)
    return curve_dict

def _append_points(original, intersect_points):
    for intersects in intersect_points.values():
        for start_point, end_point, locate in intersects:
            curve_dict = _seg2curve(original.points, start_point.index, end_point.index)
            for idx, curve in curve_dict.items():
                if curve.degree == 1:
                    if curve.nodes[0][0] == curve.nodes[0][-1]:
                        intersect_marker = bezier.Curve(np.asfortranarray(
                                               [[locate[0][0]-2, locate[0][0]]+2,
                                                [locate[1][0], locate[1][0]]]), degree=1)
                        intersect = curve.intersect(intersect_marker)
                        if intersect.any():
                            curve_points = [original.points[idx+i] for i in range(0, -4, -1)]
                            apt.append_point_coordinate_line(original, curve_points, locate[1][0], True)
                            break
                    else:
                        intersect_marker = bezier.Curve(np.asfortranarray(
                                               [[locate[0][0], locate[0][0]],
                                                [locate[1][0]-2, locate[1][0]+2]]), degree=1)
                        intersect = curve.intersect(intersect_marker)
                        if intersect.any():
                            curve_points = [original.points[idx+i] for i in range(0, -4, -1)]
                            apt.append_point_coordinate_line(original, curve_points, locate[0][0], False)
                            break
                elif curve.degree == 3:
                    if curve.nodes[0][0] == curve.nodes[0][1] == curve.nodes[0][-2] == curve.nodes[0][-1]:
                        intersect_marker = bezier.Curve(np.asfortranarray(
                                               [[locate[0][0]-2, locate[0][0]]+2,
                                                [locate[1][0], locate[1][0]]]), degree=1)
                        intersect = curve.intersect(intersect_marker)
                        if intersect.any():
                            curve_points = [original.points[idx+i] for i in range(0, -4, -1)]
                            apt.append_point_coordinate(original, curve_points, locate[1][0], True)
                            break
                    else:
                        intersect_marker = bezier.Curve(np.asfortranarray(
                                               [[locate[0][0], locate[0][0]],
                                                [locate[1][0]-2, locate[1][0]+2]]), degree=1)
                        intersect = curve.intersect(intersect_marker)
                        if intersect.any():
                            curve_points = list(reversed([original.points[idx-i] for i in range(4)]))
                            apt.append_point_coordinate(original, curve_points, locate[0][0], False)
                            break

def _remove_points(original, remain_list=None):
    remove_list = []
    for point in original.points:
        if point not in remain_list:
            remove_list.append(point)
    for point in remove_list:
        original.removePoint(point, True)

def _find_point(contour, position):
    for point in contour.points:
        if point.position == position:
            return point.index
    return None

def _fit_bcps(original, segment):
    # print(segment.clockwise)
    # print(original.naked().clockwise)
    # segment.clockwise = False
    # segment.clockwise = original.naked().clockwise
    for idx, point in enumerate(segment.points):
        if segment.points[idx].type != 'offcurve' and segment.points[idx-1].type == 'offcurve':
            if segment.points[idx].smooth:
                segment.points[idx].smooth = False
            prev_point = segment.points[idx-3]
            original_idx = _find_point(original, point.position)
            if original_idx is not None:
                segment.points[idx-1].position = original.points[original_idx-1].position
                segment.points[idx-2].position = original.points[original_idx-2].position
    segment.setChanged()

def fit_curve(original, segment):
    """ Fit segment to curve.
        
    Examples:
        original = CurrentGlyph().contours[2]
        segment = CurrentGlyph().contours[3]
        fit_curve(original, segment)
    """
    penpair_lines = _get_penpair_lines(segment)
    intersect_points = _get_intersect_points(original, penpair_lines)
    _append_points(original, intersect_points)
    _fit_bcps(original, segment)
