import numpy as np
import bezier

class InputError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

def extend_curve(curve_x, curve_y, base_value, x_or_y):
    if len(curve_x) != 4 or len(curve_y) != 4:
        raise InputError('curve_x: ' + str(curve_x) + ", curve_y: " + str(curve_y), "Lack of Data")
    nodes = np.asfortranarray([list(map(float, [curve_x[0], curve_x[1], curve_x[2], curve_x[3]])), \
                               list(map(float, [curve_y[0], curve_y[1], curve_y[2], curve_y[3]]))])
    curve = bezier.Curve(nodes, degree=3)
    new_curve = curve.specialize(0, 2.5)
    if x_or_y == 'Y':
        nodes = np.asfortranarray([[0, 1000], [base_value, base_value]])
    elif x_or_y == 'X':
        nodes = np.asfortranarray([[base_value, base_value], [0, 1000]])
    else:
        raise InputError("x_or_y: " + x_or_y, "Put 'X' or 'Y'")
    line = bezier.Curve(nodes, degree=1)
    intersections = new_curve.intersect(line)
    s_vals = intersections[0, :]
    point = new_curve.evaluate(s_vals[0])
    rate = new_curve.locate(point)
    result_curve = new_curve.specialize(0, rate)

    return result_curve.nodes
