""" Call functions with RFont object's children.

Call functions with RFont object's children. RFont object's child is one of the
RGlyph, RContour and RPoint. This module helps you to iterate RFont object easily.

Last modified date: 2019/09/26

Created by Seongju Woo.
"""
from mojo.roboFont import RFont

def point_iterator(font, *functions, **conditions=None):
	""" Call functions with RPoint objects in RFont object.

	Args:
		font:: RFont
		*functions:: function objects
		**conditions:: str(name of function)=function object
	"""
	for order in font.glyphOrder:
		glyph = font.getGlyph(order)
		for contour in glyph.contours:
			for point in contour.points:
				if conditions is None:
					for function in functions:
						function(point)
				else:
					for function in functions:
						condition = conditions[function.__name__]
						if condition is not None and condition(point):
							function(point)

def contour_iterator(font, *functions):
	""" Call functions with RContour objects in RFont object.

	Args:
		font:: RFont
		*functions:: function objects
	"""
	for order in font.glyphOrder:
		glyph = font.getGlyph(order)
		for contour in glyph.contours:
			for function in functions:
				function(contour)

def glyph_iterator(font, *functions):
	""" Call functions with RGlyph objects in RFont object.

	Args:
		font:: RFont
		*functions:: function objects
	"""
	for order in font.glyphOrder:
		glyph = font.getGlyph(order)
		for function in functions:
			function(glyph)
