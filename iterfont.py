""" Call functions with RFont object's children.

Call functions with RFont object's children. RFont object's child is one of the
RGlyph, RContour and RPoint. This module helps you to iterate RFont object easily.

Last modified date: 2019/09/26

Created by Seongju Woo.
"""
from mojo.roboFont import RFont, CurrentFont

def _call_func_by_condition(func):
	def call_func_by_condition(data, *args, **kwargs):
		objects, functions, conditions = func(data, *args, **kwargs)
		for object_ in objects:
			for function in functions:
				condition = conditions.get(function.__name__)
				if condition is None:
					function(object_)
				else:
					if condition[object_]:
						function(object_)
	return call_func_by_condition

@_call_func_by_condition
def point_iterator(font, *functions, **conditions=None):
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
				  for point in contour.points), functions, conditions

@_call_func_by_condition
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
					for contour in font.getGlyph(order)), functions, conditions

@_call_func_by_condition
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
	return (font.getGlyph(order) for order in font.glyphOrder), functions, conditions
