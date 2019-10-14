""" Call functions with RFont object's children.

Call functions with RFont object's children. RFont object's child is one of the
RGlyph, RContour and RPoint. This module helps you to iterate RFont object easily.

Last modified date: 2019/09/26

Created by Seongju Woo.
"""
from functools import wraps
from mojo.roboFont import RFont, CurrentFont

def iter_with_func(iter_func):
    """ Decorator for iterating over font objects with functions.

    A decorator that iterate font objects with functions. Functions can
    be used with conditions. This conditions must be a predicate(functions
    that return True or False).

    Examples:
        # For all glyph objects in current font.
        # If glyph's name starts with 'AB', print glyph's name.

        def print_glyph(glyph):
            print(glyph)

        def print_condition(glyph):
            return glyph.name.startswith('AB')

        @iter_with_func
        def generate_glyph(font, *functions, **conditions):
            return (font.getGlyph(order) for order in font.glyphOrder)

        generate_glyph(CurrentFont(), print_glyph, print_glyph=print_condition)
    """
    @wraps(iter_func)
    def call_func_with_cond(data, *args, **kwargs):
        objects = iter_func(data, *args, **kwargs)
        for object_ in objects:
            for function in args:
                condition = kwargs.get(function.__name__)
                if condition is None:
                    function(object_)
                else:
                    if condition(object_):
                        function(object_)
    return call_func_with_cond

@iter_with_func
def point_generator(font, *functions, **conditions):
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

        point_generator(CurrentFont(), print_func, print_func=print_condition)
    """
    return (point for order in font.glyphOrder \
                  for contour in font.getGlyph(order) \
                  for point in contour.points)

@iter_with_func
def contour_generator(font, *functions, **conditions):
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

        contour_generator(CurrentFont(), print_func, print_func=print_condition)
    """
    return (contour for order in font.glyphOrder \
                    for contour in font.getGlyph(order))

@iter_with_func
def glyph_generator(font, *functions, **conditions):
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

        glyph_generator(CurrentFont(), print_func, print_func=print_condition)
    """
    return (font.getGlyph(order) for order in font.glyphOrder)
