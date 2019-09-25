from itertools import chain
from . import attributetools as at

def _find_depend_target(point, penpair_dict, point_list):
    pair_points = penpair_dict[at.get_attr(point, 'penPair')[1:-1]]
    for target_point in point_list:
        target_pair_points = penpair_dict[at.get_attr(target_point, 'penPair')[1:-1]]
        if _is_between(pair_points, target_point) and \
                _is_diff_direction(pair_points, target_pair_points):
            return target_point
    return None

def distance(point_1, point_2):
    return ((point_1.x - point_2.x)**2 + (point_1.y - point_2.y)**2) ** 0.5

def _is_between(pair_points, target_point):
    if _is_linear(pair_points, target_point):
        return distance(pair_points[0], target_point) + distance(target_point, pair_points[1]) \
               == distance(*pair_points)
    else:
        return None

def _is_linear(pair_points, target_point):
    return _calculate_inclination(pair_points[0], target_point) == \
            _calculate_inclination(target_point, pair_points[1])

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

def _get_all_point(glyph):
    return set(chain.from_iterable([contour.points for contour in glyph.contours]))

def make_penpair_dict(all_points):
    penpair_dict = {}
    for point in all_points:
        penpair = at.get_attr(point, 'penPair')[1:-1]
        if penpair in penpair_dict:
            penpair_dict[penpair].append(point)
        else:
            penpair_dict[penpair] = [point]
    return penpair_dict

def add_depend_attribute(glyph):
    if glyph.name.find('V') != -1 or not glyph.hasOverlap():
        return None
    all_points = _get_all_point(glyph)
    penpair_dict = make_penpair_dict(all_points)
    for contour in glyph.contours:
        for i, current_point in enumerate(contour.points):
            previous_point = contour.points[i-1]
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
