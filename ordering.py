import abc
import itertools as it
from . import attributetools as at

def _get_penpair_values(contour):
    return [int(at.get_attr(point, 'penPair')[1:-1]) for point in contour.points \
                                                     if point.type != 'offcurve']

def get_max_penpair(glyph):
    return max(it.chain(*[_get_penpair_values(contour) for contour in glyph.contours]))

def get_min_penpair(glyph):
    return min(it.chain(*[_get_penpair_values(contour) for contour in glyph.contours]))


class Ordering:
    __metaclass__ = abc.ABCMeta

    def __init__(self, glyph, *attributes, padding):
        self.glyph = glyph
        self.attributes = attributes
        self.padding = padding
        self.calculate_padding()

    @abc.abstractmethod
    def calculate_padding(self):
        pass

    def attributes_ordering(self):
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
