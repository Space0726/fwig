import numpy as np
import bezier

class InputError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        
def makeExtendLine(curveX, curveY, baseValue, XorY):
    if len(curveX) != 4 or len(curveY) != 4:
        raise InputError('curveX: ' + str(curveX) + ", curveY: " + str(curveY), "Lack of Data")
    nodes = np.asfortranarray([list(map(float, [curveX[0], curveX[1], curveX[2], curveX[3]])), list(map(float, [curveY[0], curveY[1], curveY[2], curveY[3]]))])
    curve = bezier.Curve(nodes, degree = 3)
    newCurve = curve.specialize(0, 2.5)
    if XorY == 'Y':
        nodes = np.asfortranarray([[0, 1000], [baseValue, baseValue]])
    elif XorY == 'X':
        nodes = np.asfortranarray([[baseValue, baseValue], [0, 1000]])
    else:
        raise InputError("XorY: " + XorY, "Put X or Y")
    line = bezier.Curve(nodes, degree = 1)
    intersections = newCurve.intersect(line)
    s_vals = intersections[0, :]
    P = newCurve.evaluate(s_vals[0])
    R = newCurve.locate(P)
    resultCurve = newCurve.specialize(0, R)
    return resultCurve.nodes