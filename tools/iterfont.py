""" Calls functions with RFont object's children.

Calls functions with RFont object's children. RFont object's child is one of the
RGlyph, RContour and RPoint. This module helps you to iterate RFont object easily.

Last modified date: 2019/09/26

Created by Seongju Woo.
"""
from functools import wraps

def iter_with_func(iter_func):
    """ Decorator for iterating over font objects with functions.

    A decorator that iterate font objects with functions. Functions can
    be used with conditions. This conditions must be a predicate(functions
    that returns True or False).

    Examples:
        from fontParts.world import CurrentFont

        # For all glyph objects in current font.
        # If glyph's name starts with 'AB', print glyph's name.

        def print_glyph(glyph):
            print(glyph)

        def print_condition(glyph):
            return glyph.name.startswith('AB')

        @iter_with_func
        def generate_glyph(font, *functions, **conditions):
            return (font.getGlyph(key) for key in font.keys())

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
    """ Calls functions with RPoint objects in RFont object.

    Args:
        font:: RFont
        *functions:: (function object, ...)
            This functions must have only one parameter, which is an RPoint object.
        **conditions:: {str: function object, ...}
            The key of conditions is function name and the value is function object.
            This function object must be predicate and have only one parameter,
            which is an RPoint object. If this function object returns True, the key
            of conditions will be executed.

    Examples:
        from fontParts.world import CurrentFont

        def print_func(point):
            print(point)

        def print_condition(point):
            return point.index == 3

        point_generator(CurrentFont(), print_func, print_func=print_condition)
    """
    return (point for key in font.keys() \
                  for contour in font.getGlyph(key) \
                  for point in contour.points)

@iter_with_func
def contour_generator(font, *functions, **conditions):
    """ Calls functions with RContour objects in RFont object.

    Args:
        font:: RFont
        *functions:: (function object, ...)
            This functions must have only one parameter, which is an RContour object.
        **conditions:: {str: function object, ...}
            The key of conditions is function name and the value is function object.
            This function object must be predicate and have only one parameter,
            which is an RContour object. If this function object returns True, the key
            of conditions will be executed.

    Examples:
        from fontParts.world import CurrentFont

        def print_func(contour):
            print(contour)

        def print_condition(contour):
            return len(contour.points) == 3

        contour_generator(CurrentFont(), print_func, print_func=print_condition)
    """
    return (contour for key in font.keys() \
                    for contour in font.getGlyph(key))

@iter_with_func
def glyph_generator(font, *functions, **conditions):
    """ Calls functions with RGlyph objects in RFont object.

    Args:
        font:: RFont
        *functions:: (function object, ...)
            This functions must have only one parameter, which is an RGlyph object.
        **conditions:: {str: function object, ...}
            The key of conditions is function name and the value is function object.
            This function object must be predicate and have only one parameter,
            which is an RGlyph object. If this function object returns True, the key
            of conditions will be executed.

    Examples:
        from fontParts.world import CurrentFont

        def print_func(glyph):
            print(glyph.name)

        def print_condition(glyph):
            return glyph.name.startswith('uni')

        glyph_generator(CurrentFont(), print_func, print_func=print_condition)
    """
    return (font.getGlyph(key) for key in font.keys())
