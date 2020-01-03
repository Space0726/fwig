from fwig.tools import attributetools as at, iterfont
from fontParts.world import CurrentFont

def _is_inside_point(point, glyph, self_check=False, position=None):
    if position is None:
        position = point.position
    for contour in glyph.contours:
        if not self_check and contour == point.contour:
            continue
        if contour.pointInside(position):
            return True
    return False

def rect_check(point, glyph):
    """ Flip N shape check """
    pos = point.position
    positions = [(pos[0] + 2.5 * ((-1)**(i < 2)), pos[1] + 2.5 * ((-1)**i)) for i in range(4)]
    return sum(map(lambda x: _is_inside_point(point, glyph, True, x), positions))

@iterfont.iter_with_func
def get_round_points(glyph, *functions, **conditions):
    # if point is outter and point is not overlap its contour(other contour doesn't matter):
    #     add point at result
    penpair_dict = at.get_penpair_dict(glyph)
    round_points = set()
    for point_1, point_2 in penpair_dict.values():
        index_diff = abs(point_1.index - point_2.index)
        if index_diff == 1 or index_diff \
                              == len(point_1.contour.points)-1 \
                              == len(point_2.contour.points)-1:
            if not _is_inside_point(point_1, glyph):
                round_points.add(point_1)
            if not _is_inside_point(point_2, glyph):
                round_points.add(point_2)
        else:
            rect_checks = (rect_check(point_1, glyph), rect_check(point_2, glyph))
            if rect_checks == (3, 1) or rect_checks == (1, 3):
                round_points.add(point_1 if rect_checks[0] == 1 else point_2)
    return round_points

def add_round_attr(point):
    at.add_attr(point, "round", 1)

if __name__ == "__main__":
    font = CurrentFont()
    for o in font.glyphOrder:
        glyph = font.getGlyph(o)
        if not glyph.name.startswith('uni'):
            get_round_points(glyph, add_round_attr)
