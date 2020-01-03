from fwig.tools import attributetools as at, iterfont
from fontParts.world import CurrentFont

def is_serif_contour(glyph):
    return glyph.name.find('V') != -1

def is_vertical(contour):
    points = contour.points
    min_x = min(points, key=lambda a: a.x).x
    max_x = max(points, key=lambda a: a.x).x
    min_y = min(points, key=lambda a: a.y).y
    max_y = max(points, key=lambda a: a.y).y
    return abs(max_x - min_x) < abs(max_y - min_y)

def get_serif_point(contour):
    points = contour.points
    min_x = min(points, key=lambda a: a.x).x
    max_y = max(points, key=lambda a: a.y).y
    return [point for point in points if point.x == min_x and point.y == max_y][0]

def is_overlap_vertical_or_not_overlap(overlaps, contour):
    if overlaps is None:
        return True
    overlap_points = list(filter(contour.pointInside, overlaps))
    if overlap_points:
        return overlap_points[0][0] == overlap_points[1][0]
    else:
        return True

def get_serif_contour(glyph):
    overlaps = glyph.hasOverlap()
    serif_contours = []
    for contour in glyph.contours:
        if is_vertical(contour) and is_overlap_vertical_or_not_overlap(overlaps, contour):
            serif_contours.append(contour)
    return serif_contours

def add_serif_attr(glyph):
    serif_attr = 'serif'
    serif_contour = get_serif_contour(glyph)
    if serif_contour:
        serif_cnt = 1
        for contour in serif_contour:
            target_point = get_serif_point(contour)
            at.add_attr(target_point, 'serif', serif_cnt)
            serif_cnt += 1
            # for safety
            if serif_cnt > 2:
                break

if __name__ == '__main__':
    iterfont.glyph_generator(CurrentFont(), add_serif_attr, add_serif_attr=is_serif_contour)
