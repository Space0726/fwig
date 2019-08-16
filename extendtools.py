""" Font tools for extending line or curve object.

Last modified date: 2019/08/09

Created by Seongju Woo.
"""
import numpy as np
import bezier

class InputError(Exception):
    """ User exception class for input error.

    Args:
        expression:: str
            Expression of current state.
        message:: str
            Messages about error.
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def _get_linear_function(coordinates_1, coordinates_2, x_or_y):
    m_x, m_y = coordinates_1
    n_x, n_y = coordinates_2

    if (n_x == m_x and x_or_y == 'X') or (n_y == m_y and x_or_y == 'Y'):
        raise InputError(f"x_or_y: {x_or_y}, coordinates: {coordinates_1, coordinates_2}", \
                         "Not possible to get result because line is horizental or vertical")
    if x_or_y == 'X':
        linear_function = lambda x: (1 / (n_x-m_x))*((n_y - m_y)*x + (n_x*m_y - m_x*n_y))
    elif x_or_y == 'Y':
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
            If base_value is an x coordinate value, type 'x' or 'X'.
            If it is an y coordinate value,  type 'y' or 'Y'.
        apply_extend:: bool (default is True)
            If it is True, the change is applied. Input False if you
            do not want to apply the changes.

    Returns:
        extend_point:: (int, int)
            The coordinate value of the result of the extension.
    """
    if x_or_y.islower():
        x_or_y = x_or_y.upper()

    linear_function = _get_linear_function(start_point.position, end_point.position, x_or_y)
    if x_or_y == 'X':
        extend_point = (base_value, linear_function(base_value))
    elif x_or_y == 'Y':
        extend_point = (linear_function(base_value), base_value)
    else:
        raise InputError("x_or_y: " + x_or_y, "Put 'X' or 'Y'")

    if apply_extend:
        end_point.position = extend_point

    return extend_point

def extend_curve(curve_point_list, base_value, x_or_y, apply_extend=True):
    """ Extends the curve to the given value.

    Args:
        curve_point_list:: [RPoint, RPoint, RPoint, RPoint]
            4 RPoints forming a cubic bezier curve. The order is [(start point), 
            (control point1), (control point2), (end point)]. The extension 
            works from the end point.
        base_value:: int
            The coordinate value of how far you want to extend. The curve
            will extend to this value.
        x_or_y:: str
            If base_value is an x coordinate value, type 'x' or 'X'.
            If it is an y coordinate value,  type 'y' or 'Y'.
        apply_extend:: bool (default is True)
            If it is True, the change is applied. Input False if you
            do not want to apply the changes.

    Returns:
        nodes:: 2x4 numpy.ndarray (float)
            The coordinate values of the result of the extension. The rows
            represent the coordinates(x, y) and the columns represent 4 points 
            that form a cubic bezier curve. For example:
            
            [[(start_point_x, control_point_1_x, control_point_2_x, end_point_x]
             [(start_point_y, control_point_1_y, control_point_2_y, end_point_y]]
            
    """
    if len(curve_point_list) != 4:
        raise InputError('curve_point_list: ' + str(curve_point_list), \
                         "The number of data is not correct. Need 4 RPoint objects in the list")
        
    curve_x = [float(point.x) for point in curve_point_list]
    curve_y = [float(point.y) for point in curve_point_list]
    base_value = float(base_value)
    nodes = np.asfortranarray([curve_x, curve_y])
    curve = bezier.Curve(nodes, degree=3)
    new_curve = curve.specialize(0, 2.5)

    if x_or_y.islower():
        x_or_y = x_or_y.upper()
    if x_or_y == 'Y':
        nodes = np.asfortranarray([[0., 1000.], [base_value, base_value]])
    elif x_or_y == 'X':
        nodes = np.asfortranarray([[base_value, base_value], [0., 1000.]])
    else:
        raise InputError("x_or_y: " + x_or_y, "Put 'X' or 'Y'")

    line = bezier.Curve(nodes, degree=1)
    s_vals = new_curve.intersect(line)[0, :]
    point = new_curve.evaluate(s_vals[0])
    rate = new_curve.locate(point)
    result_curve = new_curve.specialize(0, rate)

    if apply_extend:
        for i in range(4):
            curve_point_list[i].position = (result_curve.nodes[0, i], result_curve.nodes[1, i])

    return result_curve.nodes
