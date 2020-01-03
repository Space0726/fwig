""" This is example of setting attribute values in order using by Yullyeo font data.

Last modified date: 2019/09/11

Created by Seongju Woo.
"""
from fwig.attributing import ordering as od
from fontParts.world import CurrentFont

class YullyeoOrdering(od.Ordering):
    def __init__(self, glyph, *attributes, padding=0):
        super().__init__(glyph, *attributes, padding=padding)

    def calculate_padding(self):
        font = self.glyph.font
        if self.glyph.name.endswith('C'):
            return None
        elif self.glyph.name.endswith('V'):
            padding_glyphs = font.getGlyph(self.glyph.name[:-1] + 'C')
        elif self.glyph.name.endswith('F'):
            padding_glyphs = font.getGlyph(self.glyph.name[:-1] + 'C'), \
                             font.getGlyph(self.glyph.name[:-1] + 'V')
        for padding_glyph in padding_glyphs:
            if od.get_min_penpair(padding_glyph) == 1:
                self.padding += od.get_max_penpair(padding_glyph)
            else:
                self.padding = od.get_max_penpair(padding_glyph)
                break


if __name__ == '__main__':
    font = CurrentFont()
    for order in font.glyphOrder:
        glyph = font.getGlyph(order)
        if glyph.name.find('uni') == -1:
            YullyeoOrdering(glyph, 'penPair').attributes_ordering()
