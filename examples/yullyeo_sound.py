""" This is example of adding sound attribute at points using by Yullyeo font data. 

Last modified date: 2019/09/11

Created by Seongju Woo.
"""
from fwig.attributing import sound
from fontParts.world import CurrentFont

class YullyeoSound(sound.Sound):
    def __init__(self, glyph):
        super().__init__(glyph)

    def calculate_sound(self):
        glyph_name = self.glyph.name
        sound_dict = {'C': 0, 'V': 1, 'F': 2}
        if glyph_name.endswith(tuple(sound_dict.keys())):
            return sound_dict[glyph_name[-1]]
        else:
            return -1


if __name__ == "__main__":
    font = CurrentFont()
    for o in font.glyphOrder:
        glyph = font.getGlyph(o)
        if glyph.name.find('uni') == -1:
            YullyeoSound(glyph).add_sound_attr()
