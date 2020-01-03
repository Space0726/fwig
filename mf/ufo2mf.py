import os
from fontParts.world import OpenFont, CurrentFont
from fwig.tools import attributetools as at
from fwig.mf import constants as mfc

# convert number of unicode to alphabet
class Num2Char:
    n2c = {
        '1':'o',
        '2':'t',
        '3':'h',
        '4':'u',
        '5':'i',
        '6':'s',
        '7':'v',
        '8':'g',
        '9':'n',
        '0':'z',
        '_':'_'
    }

    @classmethod
    def get_char(cls, number):
        return cls.n2c[number]


def _num2char(name):
    return ''.join([w if w.isalpha() else Num2Char.get_char(w) for w in list(name)])

def _float2str(value, decimal=4):
    str_val = str(float(value))
    return str_val[:str_val.find('.') + decimal]

def ufo2mf(dest_path, ufo_path=None, logs=True):
    """ Converts UFO format to METAFONT format.

    Args:
        dest_path:: str
        ufo_path:: str (default is None)
        logs:: bool
    """
    if ufo_path is None:
        font = CurrentFont()
    else:
        font = OpenFont(os.path.abspath(ufo_path), showInterface=False)
    dest_path = os.path.abspath(dest_path)

    with open(os.path.join(dest_path, mfc.RADICAL)) as radical_mf, \
            open(os.path.join(dest_path, mfc.COMBINATION)) as combination_mf:
        if logs:
            print("====================== Start ufo2mf() ======================")
            # print("Date:")
            print("Target:", font.path)
            print("Destination Path:", dest_path)
            print("Radical Path:", radical_mf)
            print("Combination Path:", combination_mf)

        # Remove exist Metafont file for renew
        try:
            os.remove(radical_mf)
            os.remove(combination_mf)
        except:
            pass

        for key in font.keys:
            glyph = font.getGlyph(key)
            glyph2mf(glyph, radical_mf, combination_mf, logs)

    if logs:
        print("======================= End ufo2mf() =======================")

def _combination_builder(glyph, mf, logs):
    with mfc.BeginChar(mf, glyph.unicode, 100, 100, 0) as bc:
        bc.add_body()

def _radical_builder(glyph, mf, logs):
    1

def glyph2mf(glyph, radical_mf, combination_mf, logs):
    """ Converts RGlyph object to METAFONT format.
    
    Args:
        glyph:: RGlyph
        radical_mf:: file
        combination_mf:: file
        logs:: bool
    """
    if logs:
        print("--------------------- Start glyph2mf() ---------------------")
        print("Target glyph:", glyph)

    if glyph.component:
        if logs:
            print("Type of glyph: combination.mf")
        _combination_builder(glyph, combination_mf, logs)
    else:
        if logs:
            print("Type of glyph: radical.mf")
        _radical_builder(glyph, radical_mf, logs)

    if logs:
        print("---------------------- End glyph2mf() ----------------------")
