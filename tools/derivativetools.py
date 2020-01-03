""" Font tools for calculating derivative and using it.

Last modified date: 2019/08/17

Created by Seongju Woo.
"""
import math
import numpy as np
import bezier
from fwig.tools import appendtools

def _calculate_distance(point_1, point_2):
    return math.sqrt(pow(point_1[0]-point_2[0], 2)
                     + pow(point_1[1]-point_2[1], 2))

def _is_curve_meet(curve_1, curve_2):
    if curve_2.intersect(curve_1)[0, :]:
        return True
    return False

def calculate_derivative(contour_points, target_index):
    """ Calculates derivative.

    Calculates the derivative of the current point(contour_points[target_index])
    and returned it.

    Args:
        contour_points:: [RPoint, RPoint, ...]
            RContour's points(RPoint objects) to be derivative.
        target_index:: int
            Index(at contour_points) of RPoint to be derivative.

    Returns:
        derivative value:: int
            The result of derivative calculating.
    """
    # Makes currrent point's bezier instance.
    nodes = np.asfortranarray([
        [float(contour_points[target_index+i].x) for i in range(-3, 1)],
        [float(contour_points[target_index+i].y) for i in range(-3, 1)]
        ])
    # Extends the curve for the derivative function.
    curve = bezier.Curve(nodes, degree=3).specialize(0, 1.5)

    # Calculates two x value for the derivative function.
    # These are the values from the original value plus and minus the very
    # small value(1e-4).
    current_x, _ = contour_points[target_index].position
    delta_x = 1e-4
    line_1 = bezier.Curve(np.asfortranarray([
        [current_x + delta_x, current_x + delta_x],
        [-1000, 1000]
        ]), degree=1)
    line_2 = bezier.Curve(np.asfortranarray([
        [current_x - delta_x, current_x - delta_x],
        [-1000, 1000]
        ]), degree=1)

    # Finds the y value that corresponds to the x value.
    prev_derivative = curve.evaluate(curve.intersect(line_1)[0, :][0])[1][0]
    next_derivative = curve.evaluate(curve.intersect(line_2)[0, :][0])[1][0]

    # Returns derivative function value.
    return (prev_derivative-next_derivative) / (2*delta_x)

def append_point_by_derivative(contour_points, target_index, target_contour):
    """ Appends point to opposite curve by using derivative.

    Appends point to opposite curve using line with gradient(by derivative)
    for pairing. It is recommended to use this function from inside(derivative)
    to outside(append point).

    Args:
        contour_points:: [RPoint, RPoint, ...]
            RContour's points(RPoint objects) to be derivative.
        target_index:: int
            Index(at contour_points) of RPoint to be derivative.
        target_contour: RContour
            RContour object which containing the opposite curve.

    Examples:
        from fontParts.world import CurrentGlyph
        glyph = CurrentGlyph()

        # RContour's list of RPoints which you want to derivative.
        contour_points = glyph.contours[0].points

        # Index(at contour_points) of RPoint to be derivative.
        target_index = 3

        # RContour object which you want to add a point.
        target_contour = glyph.contours[1]

        append_point_by_derivative(contour_points,target_index,target_contour)
    """
    target_contour_points = target_contour.points
    distance = 0xFFFFFF
    points_to_append, rate = None, 0
    x_value, y_value = contour_points[target_index].position

    try:
        # Calculates gradient by derivative.
        gradient = -1 / calculate_derivative(contour_points, target_index)
        # Line's equation.
        linear_function = lambda x: gradient*x + y_value - (x_value*gradient)
        # Extends 500 up and down from standard point.
        line = bezier.Curve(np.asfortranarray([
            [x_value+500, x_value-500],
            [linear_function(x_value+500), linear_function(x_value-500)]
            ]), degree=1)
    except ZeroDivisionError:
        line = bezier.Curve(np.asfortranarray([
            [x_value, x_value],
            [float(y_value+500), float(y_value-500)]
            ]), degree=1)

    # Finds what curve in target contour is meeted with line.
    for i, _ in enumerate(target_contour_points):
        if i == target_index and target_contour_points == contour_points:
            continue
        if target_contour_points[i].type != 'offcurve' \
                and target_contour_points[i-1].type == 'offcurve':
            nodes = np.asfortranarray([
                [float(target_contour_points[i+j].x) for j in range(-3, 1)],
                [float(target_contour_points[i+j].y) for j in range(-3, 1)]
                ])
            curve = bezier.Curve(nodes, degree=3)

            # If line meet curve.
            if _is_curve_meet(line, curve):
                meeting_object = curve.evaluate(curve.intersect(line)[0, :][0])
                meeting_point = tuple(meeting_object.flatten())
                new_distance = _calculate_distance( \
                        contour_points[target_index].position, meeting_point)
                # Finds nearest curve.
                if new_distance < distance:
                    distance = new_distance
                    points_to_append = [target_contour_points[i+j] \
                                        for j in range(-3, 1)]
                    rate = curve.locate(meeting_object)

    # Appends point at target curve.
    if points_to_append and rate:
        appendtools.append_point_rate(target_contour, points_to_append, rate)
