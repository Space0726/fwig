""" This is for adding stroke attribute at points.

Last modified date: 2019/12/11

Created by Seongju Woo.
"""
from fwig.tools import attributetools as at

class _PairError(Exception):
    def __init__(self, e):
        super().__init__(e)

def _get_penpair_dict(contour):
    penpair_dict = {}
    for point in contour.points:
        if point.type == 'offcurve':
            continue
        penpair = at.get_attr(point, 'penPair')[1:-1]
        if penpair in penpair_dict:
            penpair_dict[penpair].append(point)
        else:
            penpair_dict[penpair] = [point]
    if not all(map(lambda x: len(x) == 2, penpair_dict.values())):
        raise _PairError('Pair is not exist.')
    return penpair_dict

def _get_stroke_dict(contours):
    stroke_dict = {'begin':[], 'end':[]}
    criteria_1 = lambda p: at.get_attr(p, 'dependX') is None and \
                           at.get_attr(p, 'dependY') is None
    criteria_2 = lambda p: any([contour.pointInside(p.position) for contour in contours
                                                                if not contour is p.contour])
    candidates = []
    for contour in contours:
        try:
            penpair_dict = _get_penpair_dict(contour)
        except _PairError:
            continue
        stroke_parts = []
        for penpair, points in penpair_dict.items():
            idx_diff = abs(points[0].index - points[1].index)
            if len(points) == 2 and (idx_diff == 1 or idx_diff == len(contour.points)-1):
                stroke_parts.append(points)
        if len(stroke_parts) == 2:
            candidates.append(stroke_parts)
    for candidate in candidates:
        cand_1, cand_2 = candidate
        if (cand_1[0].y + cand_1[1].y) / 2 > (cand_2[0].y + cand_2[1].y) / 2:
            if all(map(criteria_1, cand_1)) and not any(map(criteria_2, cand_1)):
                stroke_dict['begin'].extend(cand_1)
            if all(map(criteria_1, cand_2)) and not any(map(criteria_2, cand_2)):
                stroke_dict['end'].extend(cand_2)
        else:
            if all(map(criteria_1, cand_2)) and not any(map(criteria_2, cand_2)):
                stroke_dict['begin'].extend(cand_2)
            if all(map(criteria_1, cand_1)) and not any(map(criteria_2, cand_1)):
                stroke_dict['end'].extend(cand_1)
    return stroke_dict

def _classify_contours(glyph):
    classified_dict = {}
    for contour in glyph.contours:
        double = at.get_attr(contour.points[0], 'double')
        if double is not None:
            try:
                classified_dict[double].append(contour)
            except KeyError:
                classified_dict[double] = [contour]
    return tuple(classified_dict.values())

def add_stroke_attr(glyph):
    """ Adds stroke attribute at first point of the glyph.

    The stroke attribute indicates that the point is the start or end point
    when drawing the letter. The key of stroke attribute is 'stroke' and the
    value is 'begin' or 'end'. This attribute depends on 'double', 'char' and
    'sound' attribute so make sure that these attributes are already inside
    the glyph before calling this function.

    Args:
        glyph:: RGlyph
            The RGlyph object that you want to add stroke attribute.
    """
    repr_point = at.name2dict(glyph.contours[0].points[0].name)
    if repr_point.get('double') is not None:
        for contour in glyph.contours:
            attr = at.name2dict(contour.points[0].name)
            char = int(attr.get('char'))
            sound = attr.get('sound')
            if (sound == 'first' and (char == 1 or char == 4)) or \
                    (sound == 'final' and char in (2, 3, 5, 6, *range(9, 16), 18)):
                contour_set = _classify_contours(glyph)
                contour_set = [_get_stroke_dict(contours) for contours in contour_set]
            else:
                contour_set = [_get_stroke_dict(glyph.contours)]
    else:
        contour_set = [_get_stroke_dict(glyph.contours)]
    for stroke_dict in contour_set:
        if stroke_dict:
            for stroke, points in stroke_dict.items():
                for point in points:
                    at.add_attr(point, 'stroke', stroke)
