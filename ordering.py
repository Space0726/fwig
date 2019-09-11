""" This is for setting attribute values in order.

Last modified date: 2019/09/11

Created by Seongju Woo.
"""
import abc
import itertools as it
from mojo.roboFont import RGlyph
from . import attributetools as at

def _get_penpair_values(contour):
    return [int(at.get_attr(point, 'penPair')[1:-1]) for point in contour.points \
                                                     if point.type != 'offcurve']

def get_max_penpair(glyph):
    """ Get the maximum value of penPair attributes from glyph.

    Args:
        glyph:: RGlyph
            The RGlyph object that you want to know.
    """
    return max(it.chain(*[_get_penpair_values(contour) for contour in glyph.contours]))

def get_min_penpair(glyph):
    """ Get the minimum value of penPair attributes from glyph.

    Args:
        glyph:: RGlyph
            The RGlyph object that you want to know.
    """
    return min(it.chain(*[_get_penpair_values(contour) for contour in glyph.contours]))


class Ordering:
    """ This is for setting attribute values in order.

    Args:
        glyph:: RGlyph
        *attributes:: *str
        padding:: int (default is 0)
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, glyph, *attributes, padding=0):
        self.glyph = glyph
        self.attributes = attributes
        self.padding = padding
        self.calculate_padding()

    @abc.abstractmethod
    def calculate_padding(self):
        pass

    def attributes_ordering(self):
        """ Set attribute values in order. """
        if not self.padding:
            return None
        for contour in self.glyph.contours:
            for point in contour.points:
                if point.type == 'offcurve':
                    continue
                point_attr = at.Attribute(point)
                for attribute in self.attributes:
                    attr_value = point_attr.get_attr(attribute)
                    new_attr_value = attr_value[0] \
                                     + str(int(attr_value[1:-1]) + self.padding) \
                                     + attr_value[-1]
                    point_attr.set_attr(attribute, new_attr_value)
        self.glyph.setChanged()
