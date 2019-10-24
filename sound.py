""" This is for adding sound attribute at points.

Last modified data: 2019/09/11

Created by Seongju Woo.
"""
import abc
from mojo.roboFont import RGlyph
from . import attributetools as at

class Sound:
    """ This class is for adding sound attribute at points.

    For adding appropriate sound attribute at points, you have to inherit
    this class and override calculate_sound method. This method is for
    deciding what contours in glyph are first, middle, or final sound
    respectively. Since the data are different in shape, you need to
    write an algorithm accordingly. Also, calculate_sound method must
    return an integer value of one of 0, 1, 2, or -1. To know that this
    return value means, see the docstring of calculate_sound method.

    Args:
        glyph:: RGlyph
            The RGlyph object that you want to add sound attribute.
    """
    __metaclass__ = abc.ABCMeta
    _SOUNDS = ("'first'", "'middle'", "'final'")

    def __init__(self, glyph):
        self.glyph = glyph

    @abc.abstractmethod
    def calculate_sound(self) -> int:
        """ If you want other criteria, you have to inherit this method.

        This method must return an integer value of one of -1, 0, 1, 2.
        0, 1 and 2 indicate the first, middle and final sound respectively.
        Returns -1 if none is applicable. You have to write your logic
        based on return values like this when you inherit this method.

        Returns:
            sound_identifier:: int
        """
        pass

    def add_sound_attribute(self, add_sound=True):
        """ Add sound attribute at first point of the glyph.

        Args:
            add_sound:: bool

        Returns:
            name_attribute:: str
        """
        name_attribute = "'sound':"
        glyph_sound = self.calculate_sound()
        if glyph_sound not in (-1, 0, 1, 2):
            raise ValueError("calculate_sound() must return one of 0, 1, 2, or -1.")
        elif glyph_sound == -1:
            return None
        else:
            name_attribute += Sound._SOUNDS[glyph_sound]

        if add_sound:
            for contour in self.glyph.contours:
                target_point = contour.points[0]
                attribute = at.Attribute(target_point)
                if target_point.name:
                    if "'sound':" in target_point.name and \
                            attribute.get_attr('sound') != Sound._SOUNDS[glyph_sound]:
                        attribute.set_attr('sound', Sound._SOUNDS[glyph_sound][1:-1])
                    else:
                        target_point.name += ',' + name_attribute
                else:
                    target_point.name = name_attribute

        return name_attribute
