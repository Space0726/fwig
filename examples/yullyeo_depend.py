""" This is example of adding depend attribute using by Yullyeo font data.

Last modified date: 2019/12/14

Created by Seongju Woo.
"""
from fwig.tools import iterfont
from fwig.attributing.depend import add_depend_attr

def need_depend(glyph):
    """ Finds RGlyph object that needs depend attribute. """
    return not glyph.name.endswith('V') and glyph.hasOverlap()

if __name__ == '__main__':
    iterfont.glyph_generator(CurrentFont(), add_depend_attr, add_depend_attr=need_depend)
