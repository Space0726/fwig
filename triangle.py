""" Select points without pairs and make it into a triangle shape of two points.

Last modified date: 2019/08/28

Created by Seongju Woo.
"""
from mojo.roboFont import RContour
from stemfont import extendtools as et

class Triangle:
    """ Make an isolated point into a triangle shape of two points.

    This class is for selecting a points without pairs and making it into triangle shape
    of two points. This class can be used by inheritance. If you override three functions
    (_is_triangle(), _find_triangle_point(), _find_opposite_points()), you can decide
    what point should be selected using your own criteria.

    Args:
        contour:: RContour
            The RContour object that you want to make a triangle shape.

    Examples:
            .______.                .______,
            /      \                / ,__. \
           /   ??   \              /   \/   \
          /    /\    \     ->     /    /\    \
         /    /  \    \          /    /  \    \
        /    /    \    \        /    /    \    \

        from mojo.roboFont import CurrentFont

        f = CurrentFont()
        for o in f.glyphOrder:
            glyph = f.getGlyph(o)
            for contour in glyph.contours:
                Triangle(contour).make_triangle()
    """
    _CLOCKWISE_LOCATION = {0: ('right', 'left'), 1: ('left', 'right')}

    def __init__(self, contour: RContour):
        self.contour = contour
        self.points = contour.points

    def _update_points(self):
        self.points = self.contour.points

    def _is_triangle(self) -> bool:
        if len(self.points) % 2 or len(self.points) == 12:
            return True
        return False

    def _find_triangle_point(self) -> list:
        triangle_points = []
        for i, _ in enumerate(self.points):
            if self.points[i-1].y < self.points[i].y and \
                    self.points[i].y > self.points[(i+1) % len(self.points)].y:
                triangle_points.append(i)

        return triangle_points

    def _find_opposite_points(self, triangle_index: int) -> dict:
        standard_value = self.points[triangle_index].y
        opposite_points = []
        for point in self.points:
            if point.y > standard_value:
                opposite_points.append(point)
        opposite_points = sorted([point for point in opposite_points],
                                 key=lambda p: abs(self.points[triangle_index].x - p.x))[:2]

        return self._classify_right_and_left(tuple(opposite_points))

    def _get_max_penpair(self):
        max_penpair = 0
        for contour in self.contour.getParent().contours:
            for point in contour.points:
                if point.name and 'penPair' in point.name:
                    max_penpair = max(max_penpair, \
                                      int(point.name[point.name[:-1].rindex("'") + 2:-2]))
        return max_penpair

    def _classify_right_and_left(self, pair):
        classify_dict = dict()
        if all([isinstance(element, self.points[0].__class__) for element in pair]):
            if pair[0].x > pair[1].x:
                right_object = pair[0]
                left_object = pair[1]
            else:
                right_object = pair[1]
                left_object = pair[0]
        classify_dict['right'] = right_object
        classify_dict['left'] = left_object

        return classify_dict

    def _add_penpair_attribute(self, *pairs, start_pair_number=1, twist=False):
        attribute_template = "'penPair':'z"
        if twist:
            turning = True
        for index, pair in enumerate(pairs):
            classify_dict = self._classify_right_and_left(pair)
            classify_dict['right'].name = attribute_template + str(start_pair_number+index)
            classify_dict['left'].name = attribute_template + str(start_pair_number+index)
            if twist:
                if turning:
                    classify_dict['right'].name += "r'"
                    classify_dict['left'].name += "l'"
                else:
                    classify_dict['right'].name += "l'"
                    classify_dict['left'].name += "r'"
                turning = not turning
            else:
                classify_dict['right'].name += "r'"
                classify_dict['left'].name += "l'"

    def _get_number_of_all_points(self):
        return sum([len(contour.bPoints) for contour in self.contour.getParent().contours])

    def make_triangle(self, add_penpair=True):
        """ Make point into triangle shape of two points.

        Args:
            add_penpair:: bool (default is True)
                If it is True, penpair attributes are added. If you do not want to
                add penpair attribute, input False.
        """
        if not self._is_triangle():
            return
        triangle_indexes = self._find_triangle_point()
        if len(triangle_indexes) > 1 and triangle_indexes[0] < triangle_indexes[1]:
            triangle_indexes[1] += 1

        max_penpair = self._get_max_penpair()
        if max_penpair:
            start_pair_number = max_penpair + 1
        else:
            start_pair_number = (self._get_number_of_all_points() + len(triangle_indexes))//2 + 1 \
                                 - 2*len(triangle_indexes)
        for triangle_index in triangle_indexes:
            self.contour.insertPoint(index=triangle_index,
                                     type='line',
                                     point=self.points[triangle_index])
            self._update_points()
            opposite_points_dict = self._find_opposite_points(triangle_index)
            prev_func = et.get_linear_function(self.points[triangle_index-1].position,
                                               self.points[triangle_index].position, 'x')
            next_func = et.get_linear_function(self.points[triangle_index+1].position,
                                               self.points[(triangle_index+2) \
                                               % len(self.points)].position, 'x')
            prev_loc, next_loc = Triangle._CLOCKWISE_LOCATION[self.contour.clockwise]
            prev_x = opposite_points_dict[prev_loc].x
            next_x = opposite_points_dict[next_loc].x
            if add_penpair:
                self._add_penpair_attribute(
                    (opposite_points_dict[prev_loc], self.points[triangle_index+1]),
                    (opposite_points_dict[next_loc], self.points[triangle_index]),
                    start_pair_number=start_pair_number, twist=True)
            self.points[triangle_index].position = (prev_x, prev_func(prev_x))
            self.points[triangle_index+1].position = (next_x, next_func(next_x))
            start_pair_number += 2
