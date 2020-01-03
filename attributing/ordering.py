""" This is for setting attribute values in order.

Last modified date: 2019/09/11

Created by Seongju Woo.
"""
import abc
import itertools as it
from fwig.tools import attributetools as at

def _get_penpair_values(contour):
    return [int(at.get_attr(point, 'penPair')[1:-1]) for point in contour.points \
                                                     if point.type != 'offcurve']

def get_max_penpair(glyph):
    """ Gets the maximum value of penPair attributes from glyph.

    Args:
        glyph:: RGlyph
            The RGlyph object that you want to know.

    Returns:
        maximum value of penPair:: str
    """
    return max(it.chain(*[_get_penpair_values(contour) for contour in glyph.contours]))

def get_min_penpair(glyph):
    """ Gets the minimum value of penPair attributes from glyph.

    Args:
        glyph:: RGlyph
            The RGlyph object that you want to know.

    Returns:
        minimum value of penPair:: str
    """
    return min(it.chain(*[_get_penpair_values(contour) for contour in glyph.contours]))


class Ordering:
    """ This is for setting penPair attribute values in order.

    Args:
        glyph:: RGlyph
            The RGlyph object that you want to set attribute values.
        *attributes:: str
            Attributes that you want to set in order.
        padding:: int (default is 0)
            The offset from current value. The penPair attributes are calculated
            after adding this value. For example, if padding=3, penPair 'z3l'
            is calculated as 'z6l'.

    Examples:
        class OrderingExample(Ordering):
            def __init__(self, glyph, *attributes, padding=0):
                super().__init__(glyph, *attributes, padding=padding)

            # To add 3 at penPair, dependX and dependY if glyph name contains 'ABCD'
            def calculate_padding(self):
                if 'ABCD' in self.glyph.name:
                    self.padding += 3


        od = OrderingExample(CurrentGlyph(), 'penPair', 'dependX', 'dependY')
        od.attributes_ordering()
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, glyph, *attributes, padding=0):
        self.glyph = glyph
        self.attributes = attributes
        self.padding = padding
        self.calculate_padding()

    @abc.abstractmethod
    def calculate_padding(self):
        """ Set the value of the penPair attribute according to your own criteria. """
        pass

    def attributes_ordering(self):
        """ Sets attribute values in order. """
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
