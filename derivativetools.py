import numpy as np
import bezier
import math
import appendTools

# # #
# Calculate the derivative of the current point(=points[pIndex]) and returned it
def getDerivative(points, pIndex):
    # Make currrent point's bezier instance #
    nodes = np.asfortranarray([
        [float(points[pIndex+i].x) for i in range(-3, 1)],
        [float(points[pIndex+i].y) for i in range(-3, 1)],
        ])
    # Extend the curve for the derivative function #
    curve = bezier.Curve(nodes, degree=3).specialize(0, 1.5)
    
    # Calculate two x value for the derivative function #
    # These are the values ​​from the original value plus and minus the very small value(1e-4) #
    cx, cy = points[pIndex].position
    line1 = bezier.Curve(np.asfortranarray([[cx + 1e-4, cx + 1e-4], [-1000, 1000],]), degree=1)
    line2 = bezier.Curve(np.asfortranarray([[cx - 1e-4, cx - 1e-4], [-1000, 1000],]), degree=1)
    
    # Find the y value that corresponds to the x value #
    dp = curve.evaluate(curve.intersect(line1)[0, :][0])[1][0]
    dn = curve.evaluate(curve.intersect(line2)[0, :][0])[1][0]
    
    # Return derivative function value #
    return (dp-dn) / (2*(1e-4))

# # #
# Determine if two curves are meeted
def isCurveMeet(curve1, curve2):
    if curve2.intersect(curve1)[0, :]:
        return True
    return False

# # #
# Append point to opposite curve using line with gradient(by derivative) for pairing
# *** It is recommended to use this function from inside(derivative) to outside(append point) ***
# Parameter - points: RContour's points of RPoint to be derivative
#           - pIndex: Index(at first parameter) of RPoint to be derivative
#           - target: RContour object which containing the opposite curve
# ex) g = CurrentGlyph()
#     appendPointByDerivative(g.contours[0].points, 3, g.contours[1])
def appendPointByDerivative(points, pIndex, target):
    tp = target.points
    dist = 0xFFFFFF
    targetPoints, rate = None, 0
    px, py = points[pIndex].position
    
    try:
        # Calculate gradient by derivative #
        gradient = -1 / float(getDerivative(points, pIndex))
        # line's equation #
        f = lambda x: gradient*x + py - (px*gradient)
        # Extend 500 up and down from standard point #
        line = bezier.Curve(np.asfortranarray([[px+500, px-500], [f(px+500), f(px-500)],]), degree=1)
    except ZeroDivisionError:
        line = bezier.Curve(np.asfortranarray([[px, px], [float(py+500), float(py-500)],]), degree=1)
    
    # Find what curve in target contour is meeted with line #
    for i in range(len(tp)):
        if i == pIndex and target.points == points:
            continue
        if tp[i].type != 'offcurve' and tp[i-1].type == 'offcurve':
            nodes = np.asfortranarray([
                [float(tp[i+j].x) for j in range(-3, 1)],
                [float(tp[i+j].y) for j in range(-3, 1)],
                ])
            curve = bezier.Curve(nodes, degree=3)
            
            # If line meet curve #
            if isCurveMeet(line, curve):
                mp = curve.evaluate(curve.intersect(line)[0, :][0])
                meetPoint = tuple(mp.flatten())
                newDist = distance(points[pIndex].position, meetPoint)
                # Find nearest curve #
                if newDist < dist:
                    dist = newDist
                    targetPoints = [tp[i+j] for j in range(-3, 1)]
                    rate = curve.locate(mp)

    # Append point at target curve #
    if targetPoints and rate:
        appendTools.appendPointRate(target, targetPoints, rate)

def distance(a, b):
    return math.sqrt(pow(a[0]-b[0], 2) + pow(a[1]-b[1], 2))

# # #
# How to use #
if __name__ == '__main__':
    g = CurrentGlyph()
    
    # RContour's RPoints that containing RPoint which you want to derivative #
    points = g.contours[0].points
    
    # Index of RPoint at points to be derivative #
    pIndex = 7
    
    # RContour object which you want to add a point #
    targetContour = g.contours[0]
    
    # Call appendPointByDerivative function #
    appendPointByDerivative(points, pIndex, targetContour)