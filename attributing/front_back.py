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

def _get_front_back(contours):
    front_back_dict = {}
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
            front_back_dict['front'] = cand_1
            front_back_dict['back'] = cand_2
        else:
            front_back_dict['front'] = cand_2
            front_back_dict['back'] = cand_1
    return front_back_dict

def add_front_back(glyph):
    # name = at.name2dict(glyph.contours[0].points[0].name)
    # if name.get('double') is None:
    #     front_back = _get_front_back(glyph.contours)
    # else:
    #     candidates = [contour for contour in glyph.contours
    #                           if at.get_attr(contour.points[0], 'double') == 'left']
    #     front_back = _get_front_back(candidates)

    front_back = _get_front_back(glyph.contours)

    if front_back != {}:
        for point in front_back['front']:
            at.add_attr(point, 'stroke', 'begin')
        for point in front_back['back']:
            at.add_attr(point, 'stroke', 'end')

def is_front_back(glyph):
    if glyph.name.startswith('uni'):
        return False
    else:
        return True
    # name = at.name2dict(glyph.contours[0].points[0].name)
    # if name['sound'] == 'first' and name['char'] == '5':
    #     return True
    # elif name['sound'] == 'final' and int(name['char']) in range(8, 16):
    #     return True
    # else:
    #     return False

if __name__ == '__main__':
    # iterfont.glyph_generator(CurrentFont(), add_front_back, add_front_back=is_front_back)
    font = OpenFont('YullyeoM.ufo')
    iterfont.glyph_generator(font, add_front_back, add_front_back=is_front_back)
    font.close(save=True)