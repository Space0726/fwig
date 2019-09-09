""" This is for adding sound attribute at RPoints.

Last modified data: 2019/09/09

Created by Seongju Woo
"""
from stemfont import attributetools as at # change from . if input external packages.

class Sound:
    _SOUNDS = ("'first'", "'middle'", "'final'")

    def __init__(self, glyph):
        self.glyph = glyph

    def calculate_sound(self) -> int:
        """ If you want other criteria, you have to inherit this method.
        
        This method must return an integer value of one of -1, 0, 1, 2.
        0, 1 and 2 indicate the first, middle and final sound respectively.
        Returns -1 if none is applicable. You have to write your logic
        based on return values like this when you inherit this method.

        Returns:
            sound_identifier:: int
        """
        glyph_name = self.glyph.name
        sound_dict = {'C': 0, 'V': 1, 'F': 2}
        if glyph_name.endswith(tuple(sound_dict.keys())):
            return sound_dict[glyph_name[-1]]
        else:
            return -1

    def add_sound_attribute(self, add_sound=True):
        """ Add sound attribute at first point of the glyph.
        
        Args:
            add_sound:: bool

        Returns:
            name_attribute:: str
        """
        name_attribute = "'sound':"
        glyph_sound = self.calculate_sound()
        if glyph_sound != -1:
            name_attribute += Sound._SOUNDS[glyph_sound]
        else:
            return None

        if add_sound:
            target_point = self.glyph.contours[0].points[0]
            if target_point.name:
                if "'sound':" in target_point.name and \
                        at.get_attr('sound') != Sount._SOUNDS[glyph_sound]:
                    at.set_attr('sound', Sound._SOUNDS[glyph_sound])
                else:
                    target_point.name += ',' + name_attribute
            else:
                target_point.name = name_attribute

        return name_attribute
