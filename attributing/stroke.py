from stemfont.tools import attributetools as at, iterfont

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
    return penpair_dict

def _get_stroke_dict(contours):
    stroke_dict = {}
    criteria_1 = lambda p: at.get_attr(p, 'dependX') is None and \
                           at.get_attr(p, 'dependY') is None
    criteria_2 = lambda p: any([contour.pointInside(p.position) for contour in contours
                                                                if not contour is p.contour])
    candidates = []
    for contour in contours:
        penpair_dict = _get_penpair_dict(contour)
        for penpair, points in penpair_dict.items():
            # TODO: Modify criteria - cri1 or cri2 => pass
            if len(points) == 2 and abs(points[0].index - points[1].index) == 1 and \
                    all(map(criteria_1, points)) and not any(map(criteria_2, points)):
                candidates.append(points)
    if len(candidates) == 2:
        cand_1, cand_2 = candidates
        if (cand_1[0].y + cand_1[1].y) / 2 > (cand_2[0].y + cand_2[1].y) / 2:
            stroke_dict['begin'] = cand_1
            stroke_dict['end'] = cand_2
        else:
            stroke_dict['begin'] = cand_2
            stroke_dict['end'] = cand_1
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
    repr_point = at.name2dict(glyph.contours[0].points[0].name)
    if repr_point.get('double') is not None:
        for contour in glyph.contours:
            attr = at.name2dict(contour.points[0].name)
            char = int(attr.get('char'))
            if (attr.get('sound') == 'first' and (char == 1 or char == 4)) or \
                    (attr.get('sound') == 'final' and char in (2, 3, 5, 6, *range(9, 16), 18)):
                contour_set = _classify_contours(glyph)
                contour_set = [_get_stroke_dict(contours) for contours in contour_set]
            else:
                contour_set = [_get_stroke_dict(glyph.contours)]
    else:
        contour_set = [_get_stroke_dict(glyph.contours)]
    for stroke_dict in contour_set:
        if stroke_dict:
            for point in stroke_dict['begin']:
                at.add_attr(point, 'stroke', 'begin')
            for point in stroke_dict['end']:
                at.add_attr(point, 'stroke', 'end')

def need_stroke(glyph):
    if glyph.name.startswith('uni'):
        return False
    else:
        return True

if __name__ == '__main__':
    # iterfont.glyph_generator(CurrentFont(), add_stroke_attr, add_stroke_attr=need_stroke)
    add_stroke_attr(CurrentGlyph())
