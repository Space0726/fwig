""" Font tools for extending line or curve object.

Last modified date: 2019/08/09

Created by Seongju Woo.
"""
import numpy as np
import bezier

class _InputError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def _make_lower_string(string):
    if string.upper():
        return string.lower()
    return string

def get_linear_function(coordinates_1, coordinates_2, x_or_y):
    """ Returns a linear function created from coordinates.

    Creates a linear function using the two coordinates you entered.
    Type 'x' at x_or_y if you want to create a function for x
    or Type 'y' at x_or_y if you want to create a function for y.

    Args:
        coordinates_1:: (int, int)
            First coordinate value.
        coordinates_2:: (int, int)
            Second coordinate value.
        x_or_y:: str
            Type 'x' to create a function for x.
            Or type 'y' to create a function for y.

    Examples:
        coor_1 = (10, 20)
        coor_2 = (30, 50)

        # Case 1: function for x
        linear_function = get_linear_function(coor_1, coor_2, 'x')
        x_value = 100
        y_value = linear_function(x_value)

        # Case 2: function for y
        linear_function = get_linear_function(coor_1, coor_2, 'y')
        y_value = 200
        x_value = linear_function(y_value)

    Returns:
        linear_function:: function
            Linear function created from coordinates.
    """
    m_x, m_y = coordinates_1
    n_x, n_y = coordinates_2

    x_or_y = _make_lower_string(x_or_y)
    if (n_x == m_x and x_or_y == 'x') or (n_y == m_y and x_or_y == 'y'):
        raise _InputError(f"x_or_y: {x_or_y}, coordinates: {coordinates_1, coordinates_2}", \
                         "Not possible to get result because line is horizental or vertical")
    if x_or_y == 'x':
        linear_function = lambda x: (1 / (n_x-m_x))*((n_y - m_y)*x + (n_x*m_y - m_x*n_y))
    elif x_or_y == 'y':
        linear_function = lambda y: (1 / (n_y-m_y))*((n_x - m_x)*y - (n_x*m_y - m_x*n_y))

    return linear_function

def extend_line(start_point, end_point, base_value, x_or_y, apply_extend=True):
    """ Extends the line to the given value.

    Args:
        start_point:: RPoint
            RPoint object of start point.
        end_point:: RPoint
            RPoint object of end point. The line extends from this point.
        base_value:: int
            The coordinate value of how far you want to extend. The line
            will extend to this value.
        x_or_y:: str
            If base_value is an x coordinate value, type 'x'.
            If it is an y coordinate value,  type 'y'.
        apply_extend:: bool (default is True)
            If it is True, the change is applied. Input False if you
            do not want to apply the changes.

    Returns:
        extend_point:: (int, int)
            The coordinate value of the result of the extension.
    """
    x_or_y = _make_lower_string(x_or_y)

    linear_function = get_linear_function(start_point.position, end_point.position, x_or_y)
    if x_or_y == 'x':
        extend_point = (base_value, linear_function(base_value))
    elif x_or_y == 'y':
        extend_point = (linear_function(base_value), base_value)
    else:
        raise _InputError("x_or_y: " + x_or_y, "Put 'x' or 'y'")

    if apply_extend:
        end_point.position = extend_point

    return extend_point

def extend_curve(curve_point_list, base_value, x_or_y, apply_extend=True):
    """ Extends the curve to the given value.

    Args:
        curve_point_list:: [RPoint, RPoint, RPoint, RPoint]
            4 RPoint objects forming a cubic bezier curve. The order is
            [(start point), (control point1), (control point2), (end point)].
            The extension works from the end point.
        base_value:: int
            The coordinate value of how far you want to extend. The curve
            will extend to this value.
        x_or_y:: str
            If base_value is an x coordinate value, type 'x'.
            If it is an y coordinate value,  type 'y'.
        apply_extend:: bool (default is True)
            If it is True, the change is applied. Input False if you
            do not want to apply the changes.

    Returns:
        nodes:: 2x4 numpy.ndarray (float)
            The coordinate values of the result of the extension. The rows
            represent the coordinates(x, y) and the columns represent 4 points
            that form a cubic bezier curve. For example:

            [[start_point_x, control_point_1_x, control_point_2_x, end_point_x]
             [start_point_y, control_point_1_y, control_point_2_y, end_point_y]]

    """
    if len(curve_point_list) != 4:
        raise _InputError('curve_point_list: ' + str(curve_point_list), \
                         "The number of data is not correct. Need 4 RPoint objects in the list")

    curve_x = [float(point.x) for point in curve_point_list]
    curve_y = [float(point.y) for point in curve_point_list]
    base_value = float(base_value)
    nodes = np.asfortranarray([curve_x, curve_y])
    curve = bezier.Curve(nodes, degree=3)
    new_curve = curve.specialize(0, 2.5)

    x_or_y = _make_lower_string(x_or_y)
    if x_or_y == 'y':
        nodes = np.asfortranarray([[0., 1000.], [base_value, base_value]])
    elif x_or_y == 'x':
        nodes = np.asfortranarray([[base_value, base_value], [0., 1000.]])
    else:
        raise _InputError("x_or_y: " + x_or_y, "Put 'x' or 'y'")

    line = bezier.Curve(nodes, degree=1)
    s_vals = new_curve.intersect(line)[0, :]
    point = new_curve.evaluate(s_vals[0])
    rate = new_curve.locate(point)
    result_curve = new_curve.specialize(0, rate)

    if apply_extend:
        for i in range(4):
            curve_point_list[i].position = (result_curve.nodes[0, i], result_curve.nodes[1, i])

    return result_curve.nodes
