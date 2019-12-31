""" Makes component of glyphs.

Last modified date: 2019/12/14

Created by Jeongjae Suk.
Modified by Seongju Woo.
"""
from fontParts.world import CurrentFont

def make_component_current_font():
    """ Makes component of glyphs in current font. """
    f = CurrentFont()
    keys = f.keys()

    for key in keys:
        name = 'uni%x' %f[key].unicode
        f.newGlyph(name)
        f[name].appendComponent(key)
        f[name].width = f[key].width
        f[name].leftMargin = f[key].leftMargin
        f[name].rightMargin = f[key].rightMargin
        f[name].unicodes = f[key].unicodes

