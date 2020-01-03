import numpy as np
import bezier

def point2nodes(points):
    return np.asfortranarray([[float(point.x) for point in points],
                              [float(point.y) for point in points]])

def make_linear_curve(coord_1, coord_2):
    nodes = np.asfortranarray([[float(coord_1[0]), float(coord_2[0])],
                               [float(coord_1[1]), float(coord_2[1])]])
    return bezier.Curve(nodes, degree=1)

# TODO: slope apply
def make_linear_segment(coord, range_, slope):
    nodes = np.asfortranarray([[float(coord[0]), float(coord[0])],
                               [float(coord[1]), float(coord[1])]])
    return bezier.Curve(nodes, degree=1)

class RCurve(bezier.Curve):
    """ Inherit bezier.Curve for using with RPoint object.

    Args:
        points:: RPoint
        degree:: int
        _copy:: bool

    Examples:
        from fontParts.world import CurrentGlyph

        glyph = CurrentGlyph()
        contour = glyph.contours[0]

        # if contour.points[3].type == 'curve' and
        # contour.points[2].type == contour.points[1].type == 'offcurve'
        curve = RCurve([contour.points[i] for i in range(4)], degree=3)
    """
    def __init__(self, points, degree, _copy=True):
        super().__init__(point2nodes(points), degree, _copy)
        self.points = points
