from stemfont.unicode import Uni2Kor
from stemfont import attributetools as at

class YullyeoTagger(Uni2Kor):
    def __init__(self, glyph):
        super().__init__(self.name2code(glyph.name))
        self.glyph = glyph
        self._init_char_tag()
        self._init_points_attr()
        self._init_char()
        self._init_is_double()

    def _init_points_attr(self):
        points = [contour.points[0] for contour in self.glyph.contours]
        self.points_attr = {point:at.Attribute(point) for point in points}

    def _init_is_double(self):
        double_chars = ('ㄲ', 'ㄸ')
        if self.char in double_chars or len(self.char) > 1:
            self.is_double = True
        else:
            self.is_double = False

    def _init_char(self):
        first_points = self.glyph.contours[0].points[0]
        self.char = Uni2Kor.get_sound(self.points_attr[first_points].get_attr('sound'), self.char_tag)

    def _init_char_tag(self):
        name = self.glyph.name
        if name.endswith('C'):
            self.char_tag = (self.code - 0xAC00) // 588
        elif name.endswith('V'):
            self.char_tag = (self.code - 0xAC00 - 588*((self.code-0xAC00) // 588)) // 28
        elif name.endswith('F'):
            self.char_tag = (self.code - 0xAC00) % 28

    def _calc_center(self, point):
        box = point.contour.box
        return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2

    def name2code(self, name):
        return int(name.split('_')[0], 16)

    # def add_tag(self):
    #     for point, attr in self.points_attr.items():
    #         if point.index == 0:
    #             attr.add_attr('char', self.char_tag)
    #             if self.is_double:
    #                 sound = attr.get_attr('sound')
    #                 center_x = self._calc_center(point)[0]
    #                 if (sound == 'final' and center_x < 290) or (sound == 'first' and center_x < 0):
    #                     attr.add_attr('double', 'left')
    #                 else:
    #                     attr.add_attr('double', 'right')


glyph = CurrentGlyph()
point = glyph.contours[0].points[0]
yt = YullyeoTagger(glyph)
print(yt.char_tag)
print(yt.char)
print(yt.is_double)
print(point.contour.box)
print(yt._calc_center(point))
