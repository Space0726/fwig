""" This is for adding depend attribute at points.

Last modified date: 2019/12/14

Created by Seongju Woo.
"""
from itertools import chain
from fwig.tools import attributetools as at

def _find_depend_target(point, penpair_dict, point_list):
    pair_points = penpair_dict[at.get_attr(point, 'penPair')[1:-1]]
    for target_point in point_list:
        target_pair_points = penpair_dict[at.get_attr(target_point, 'penPair')[1:-1]]
        if _is_between(pair_points, target_point) and \
                _is_diff_direction(pair_points, target_pair_points):
            return target_point
    return None

def _distance(point_1, point_2):
    return ((point_1.x - point_2.x)**2 + (point_1.y - point_2.y)**2) ** 0.5

def _is_between(pair_points, target_point):
    if _is_linear(pair_points, target_point):
        return _distance(pair_points[0], target_point) + _distance(target_point, pair_points[1]) \
               == _distance(*pair_points)
    else:
        return None

def _is_linear(pair_points, target_point):
    return _calculate_inclination(pair_points[0], target_point) \
           == _calculate_inclination(target_point, pair_points[1])

def _is_diff_direction(pair_points_1, pair_points_2):
    inclination_1 = _calculate_inclination(*pair_points_1)
    inclination_2 = _calculate_inclination(*pair_points_2)
    diff_value = inclination_1 * inclination_2
    return diff_value == -1 or diff_value != diff_value

def _calculate_inclination(point_1, point_2):
    try:
        return (point_2.y - point_1.y) / (point_2.x - point_1.x)
    except ZeroDivisionError:
        return float('inf')

def add_depend_attr(glyph):
    """ Adds depend attribute at points of the glyph.

    The depend attribute indicates that certain points move in dependence on
    other points to maintain their shape while the letter is transformed.
    The key of depend attribute is 'dependX' or 'dependY' and the value is
    penPair attribute value(ex.'z1r'). The points with the depend attribute
    move as the dependent values move.

    Args:
        glyph:: RGlyph
            The RGlyph object that you want to add depend attribute.
    Raises:
        type of variable error:: TypeError
            If TypeError occurred, passes that case.
    """
    penpair_dict = at.get_penpair_dict(glyph)
    all_points = chain(*penpair_dict.values())
    for contour in glyph.contours:
        for i, current_point in enumerate(contour.points):
            previous_point = contour.points[i-1]
            try:
                if previous_point not in penpair_dict[at.get_attr(current_point, 'penPair')[1:-1]]:
                    continue
                target_point = _find_depend_target(current_point, penpair_dict, all_points)
                if target_point:
                    attribute_name = ""
                    if abs(current_point.x - previous_point.x) < 5:
                        attribute_name = 'dependX'
                    elif abs(current_point.y - previous_point.y) < 5:
                        attribute_name = 'dependY'
                    if attribute_name:
                        at.add_attr(current_point, attribute_name, at.get_attr(target_point, 'penPair'))
                        at.add_attr(previous_point, attribute_name, at.get_attr(target_point, 'penPair'))
                        glyph.setChanged()
            except TypeError:
                continue
