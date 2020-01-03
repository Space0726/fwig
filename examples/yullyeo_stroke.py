from fwig.attributing.stroke import add_stroke_attr
from fwig.tools import iterfont
from fontParts.world import CurrentFont

def need_stroke(glyph):
    return not glyph.name.startswith('uni')

if __name__ == '__main__':
    iterfont.glyph_generator(CurrentFont(), add_stroke_attr, add_stroke_attr=need_stroke)
