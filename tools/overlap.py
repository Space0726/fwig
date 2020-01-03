""" This is for finding contours that overlap with others.

Last modified date: 2019/09/09

Created by Seongju Woo.
"""
from fontParts.world import CurrentFont

def _is_overlap_other_contour(contours, target_contour):
    for contour in contours:
        if contour == target_contour:
            continue
        overlap_count = 0
        points = contour.points
        target_points = target_contour.points
        position_list = [point.position for point in target_points]
        for point in points:
            if point.position in position_list:
                overlap_count += 1
            if overlap_count > 1:
                return True
    return False

def find_overlap_contour_current_font():
    """ Finds overlapping contours in the current font.

    Returns:
        overlap_set:: set
            A set of overlapping RContour objects in the current font.
    """
    font = CurrentFont()
    overlap_set = set()
    for o in font.glyphOrder:
        glyph = font.getGlyph(o)
        for contour in glyph.contours:
            if _is_overlap_other_contour(glyph.contours, contour):
                overlap_set.add((contour, contour.index))

    return overlap_set
