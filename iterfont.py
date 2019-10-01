""" Call functions with RFont object's children.

Call functions with RFont object's children. RFont object's child is one of the
RGlyph, RContour and RPoint. This module helps you to iterate RFont object easily.

Last modified date: 2019/09/26

Created by Seongju Woo.
"""
from functools import wraps
from mojo.roboFont import RFont, CurrentFont

def _call_func_with_condition(func):
    @wraps(func)
    def call_func_with_condition(data, *args, **kwargs):
        objects = func(data, *args, **kwargs)
        for object_ in objects:
            for function in args:
                condition = kwargs.get(function.__name__)
                if condition is None:
                    function(object_)
                else:
                    if condition(object_):
                        function(object_)
    return call_func_with_condition

@_call_func_with_condition
def point_iterator(font, *functions, **conditions):
    """ Call functions with RPoint objects in RFont object.

    Args:
        font:: RFont
        *functions:: (function object, ...)
        **conditions:: {str: function object, ...}
            The key of conditions is function name and the value is function object.

    Examples:
        def print_func(data):
            print(data)

        def print_condition(data):
            return isinstance(data, str)

        point_iterator(CurrentFont(), print_func, print_func=print_condition)
    """
    return (point for order in font.glyphOrder \
                  for contour in font.getGlyph(order) \
                  for point in contour.points)

@_call_func_with_condition
def contour_iterator(font, *functions, **conditions):
    """ Call functions with RContour objects in RFont object.

    Args:
        font:: RFont
        *functions:: (function object, ...)
        **conditions:: {str: function object, ...}
            The key of conditions is function name and the value is function object.

    Examples:
        def print_func(data):
            print(data)

        def print_condition(data):
            return isinstance(data, str)

        point_iterator(CurrentFont(), print_func, print_func=print_condition)
    """
    return (contour for order in font.glyphOrder \
                    for contour in font.getGlyph(order))

@_call_func_with_condition
def glyph_iterator(font, *functions, **conditions):
    """ Call functions with RGlyph objects in RFont object.

    Args:
        font:: RFont
        *functions:: (function object, ...)
        **conditions:: {str: function object, ...}
            The key of conditions is function name and the value is function object.

    Examples:
        def print_func(data):
            print(data)

        def print_condition(data):
            return isinstance(data, str)

        point_iterator(CurrentFont(), print_func, print_func=print_condition)
    """
    return (font.getGlyph(order) for order in font.glyphOrder)
