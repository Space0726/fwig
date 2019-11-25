from stemfont.tools import attributetools as at
from stemfont.tools import iterfont
from fontParts.world import OpenFont

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

def _get_begin_end(contours):
    begin_end_dict = {}
    criteria_1 = lambda p: at.get_attr(p, 'dependX') is None and \
                           at.get_attr(p, 'dependY') is None
    criteria_2 = lambda p: any([contour.pointInside(p.position) for contour in contours
                                                                if not contour is p.contour])
    candidates = []
    for contour in contours:
        penpair_dict = _get_penpair_dict(contour)
        for penpair, points in penpair_dict.items():
            if len(points) == 2 and abs(points[0].index - points[1].index) == 1 and \
                    all(map(criteria_1, points)) and not any(map(criteria_2, points)):
                candidates.append(points)
    if len(candidates) == 2:
        cand_1, cand_2 = candidates
        if (cand_1[0].y + cand_1[1].y) / 2 > (cand_2[0].y + cand_2[1].y) / 2:
            begin_end_dict['front'] = cand_1
            begin_end_dict['back'] = cand_2
        else:
            begin_end_dict['front'] = cand_2
            begin_end_dict['back'] = cand_1
    return begin_end_dict

def add_stroke_attr(glyph):
    begin_end = _get_begin_end(glyph.contours)
    if begin_end:
        for point in begin_end['front']:
            at.add_attr(point, 'stroke', 'begin')
        for point in begin_end['back']:
            at.add_attr(point, 'stroke', 'end')

def need_stroke(glyph):
    if glyph.name.startswith('uni'):
        return False
    else:
        return True

if __name__ == '__main__':
    iterfont.glyph_generator(CurrentFont(), add_stroke_attr, add_stroke_attr=need_stroke)
