from fwig.tools.unicodetools import Uni2Kor
from fwig.tools import attributetools as at, iterfont
from fontParts.world import CurrentFont

class YullyeoTagger(Uni2Kor):
    def __init__(self, glyph):
        super().__init__(self.name2code(glyph.name))
        self.glyph = glyph
        self._init_char_tag()
        self._init_points_attr()
        self._init_char()
        self._init_form_type()
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
        initial_point = self.glyph.contours[0].points[0]
        self.char = Uni2Kor.get_sound(
            self.points_attr[initial_point].get_attr('sound'), 
            self.char_tag
        )

    def _init_char_tag(self):
        name = self.glyph.name
        code = Uni2Kor.parse_unicode(self.code)
        if name.endswith('C'):
            self.char_tag = code[0]
        elif name.endswith('V'):
            self.char_tag = code[1]
        elif name.endswith('F'):
            self.char_tag = code[2]

    def _init_form_type(self):
        code = int(self.glyph.name.split('_')[0], 16)
        self.form_type = Uni2Kor.get_form_type(code)

    def _separate_contours(self):
        centers = {contour:_calc_center(contour.points[0])[0] for contour in self.glyph.contours}
        separated_dict = {}
        center_len = len(centers)
        if center_len == 2 or center_len == 4:
            contours = sorted(centers.items(), key=lambda x: x[1])
            separated_dict['left'] = [contour[0] for i, contour in enumerate(contours)
                                                 if i < center_len / 2]
            separated_dict['right'] = [contour[0] for i, contour in enumerate(contours)
                                                  if i >= center_len / 2]
        if separated_dict:
            for attr, contours in separated_dict.items():
                for contour in contours:
                    self.points_attr[contour.points[0]].add_attr('double', attr)

    def name2code(self, name):
        return int(name.split('_')[0], 16)

    def add_tags(self):
        if self.is_double and (self.char == 'ㄲ' or self.char == 'ㄸ'):
            self._separate_contours()
        for point, attr in self.points_attr.items():
            attr.add_attr('char', self.char_tag)
            attr.add_attr('formType', self.form_type)
            if self.is_double and attr.get_attr('double') is None:
                sound = attr.get_attr('sound') center_x = _calc_center(point)[0]
                if sound == 'final':
                    if center_x < 311:
                        attr.add_attr('double', 'left')
                    else:
                        attr.add_attr('double', 'right')


def _calc_center(point):
    box = point.contour.box
    return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2


if __name__ == "__main__":
    def add_tags(glyph):
        YullyeoTagger(glyph).add_tags()

    def tag_cond(glyph):
        return not glyph.name.startswith("uni")

    iterfont.glyph_generator(CurrentFont(), add_tags, add_tags=tag_cond)
