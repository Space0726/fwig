""" This is for handling stemfont attributes.

Last modified date: 2019/09/09

Created by Seongju Woo.
"""
import os
import json
from xml.etree import ElementTree as et
from mojo.roboFont import *

def name2attr(path):
    """ Converts JSON format string to xml attributes.

    Args:
        path:: str
            A path of the UFO format font data.
    """
    path += '/glyphs'
    files = os.listdir(path)
    for file in files:
        tree = et.parse(path + "/" + file)
        glyph = tree.getroot()
        outline = glyph.find("outline")
        if outline is None:
            continue
        contours = outline.getchildren()
        for contour in contours:
            for point in contour.getchildren():
                name = (point.get("name"))
                if name is not None:
                    name_dict = name2dict(name)
                    for attr in list(name_dict.items()):
                        point.attrib[attr[0]] = attr[1]
                    try:
                        del point.attrib['name']
                    except:
                        pass

        tree.write(path + "/" + file, encoding="UTF-8", xml_declaration=True)

def attr2name(path):
    """ Converts xml attributes to JSON format string.

    Args:
        path:: str
            A path of the UFO format font data.
    """
    path += "/glyphs"
    files = os.listdir(path)
    for file in files:
        if file.find(".glif") == -1:
            continue
        tree = et.parse(path + "/" + file)
        glyph = tree.getroot()
        outline = glyph.find("outline")
        if outline is None:
            continue
        contours = outline.getchildren()
        for contour in contours:
            for point in contour.getchildren():
                if point.get("name") is not None:
                    continue
                data = ""
                attr = []
                for a in point.attrib:
                    if a == 'x' or a == 'y' or a == 'type' or a == 'smooth':
                        continue
                    if data:
                        data += ","
                    data += "'" + a + "':'" + point.get(a) + "'" 
                    attr.append(a)
                for x in attr:
                    point.attrib.pop(x)
                if data:
                    point.set("name",data)

        tree.write(path + "/" + file, encoding="UTF-8", xml_declaration=True)

def name2dict(name) -> dict:
    """ Converts JSON format string to dictionary.

    Args:
        name:: str
            A JSON format string. For example, "'penPair':'z1r'".

    Examples:
        >>> from fwig.tools import attributetools as at
        >>> name = "'penPair':'z1r','serif':'1'"
        >>> at.name2dict(name)
        {'penPair': 'z1r', 'serif': '1'}
    """
    if name is None:
        return {}
    name = '{' + name.replace("'", '"') + '}'
    name_dict = json.loads(name)

    return name_dict

def dict2name(dict_attributes) -> str:
    """ Converts attribute dictionary to JSON format string.

    Args:
        dict_attributes:: dict
            A dictionary of attributes.

    Examples:
        >>> from fwig.tools import attributetools as at
        >>> dict_ = {'penPair': 'z1r', 'serif': '1'}
        >>> at.dict2name(dict_)
        "'penPair':'z1r','serif':'1'"
    """
    return ','.join([f"'{k}':'{v}'" for k, v in dict_attributes.items()])

def get_attr(point, attribute):
    """ Gets attribute value from RPoint object.

    Args:
        point:: RPoint
            The RPoint object that you want to get attribute value.
        attribute:: str
            The key of attribute that you want to get value.

    Returns:
        attribute value:: str
            The value of attribute.
    """
    attributes = name2dict(point.name)
    return attributes.get(attribute)

def set_attr(point, attribute, value):
    """ Sets attribute to RPoint object.

    Args:
        point:: RPoint
            The RPoint object that you want to set attribute.
        attribute:: str
            The key of attribute that you want to set.
        value:: str
            The new value of attribute that you want to set.
    """
    attributes = name2dict(point.name)
    if attribute in attributes:
        attributes[attribute] = value
        point.name = dict2name(attributes)
        point.glyph.setChanged()

def add_attr(point, attribute, value):
    """ Adds attribute to RPoint object.

    Args:
        point:: RPoint
            The RPoint object that you want to add attribute.
        attribute:: str
            The key of attribute that you want to add.
        value:: str
            The value of attribute that you want to add.
    """
    attributes = name2dict(point.name)
    if attribute not in attributes:
        attributes[attribute] = value
        point.name = dict2name(attributes)
        point.glyph.setChanged()

def del_attr(point, attribute):
    """ Deletes attribute from RPoint object.

    Args:
        point:: RPoint
            The RPoint object that you want to delete attribute.
        attribute:: str
            The key of attribute that you want to delete.
    """
    attributes = name2dict(point.name)
    try:
        del(attributes[attribute])
        point.glyph.setChanged()
    except KeyError:
        return None
    else:
        point.name = dict2name(attributes)

def get_all_points(obj, offcurve=False):
    if isinstance(obj, RGlyph):
        glyph = obj
        if not offcurve:
            return set([point for contour in glyph.contours \
                              for point in contour.points \
                              if point.type != 'offcurve'])
        else:
            return set([point for contour in glyph.contours \
                              for point in contour.points])
    else:
        contour = obj
        if not offcurve:
            return set([point for point in contour.points \
                              if point.type != 'offcurve'])
        else:
            return set([point for point in contour.points])
            
def get_penpair_dict(glyph):
    """ Gets penPair attribute dictionary of RGlyph object.

    Args:
        glyph:: RGlyph
            The RGlyph object that you want to get penPair attribute dictionary.

    Returns:
        penpair_dict:: dict
            The penPair attribute dictionary of RGlyph object. If there is no
            penPair attribute in the RGlyph object, returns empty dictionary.
    """
    penpair_dict = {}
    all_points = get_all_points(glyph)
    for point in all_points:
        penpair = get_attr(point, 'penPair')[1:-1]
        if penpair is None:
            continue
        if penpair in penpair_dict:
            penpair_dict[penpair].append(point)
        else:
            penpair_dict[penpair] = [point]
    return penpair_dict


class Attribute:
    """ A class for keeping RPoint object's attributes.

    Args:
        point:: RPoint
            The RPoint object that you want to keep attributes.

    Examples:
        >>> from fontParts.world import CurrentGlyph
        >>> from fwig.tools import attributetools as at
        >>> glyph = CurrentGlyph()
        >>> point = glyph.contours[0].points[0]
        >>> point.name
        "'penPair':'z1r'"
        >>> point_attr = at.Attribute(point)
        >>> point_attr.get_attr('penPair')
        'z1r'
        >>> point_attr.add_attr('dependX', 'z2r')
        >>> point_attr.point.name
        "'penPair':'z1r','dependX':'z2r'"
        >>> point_attr.set_attr('dependX', 'z3l')
        >>> point_attr.point.name
        "'penPair':'z1r','dependX':'z3l'"
        >>> point_attr.del_attr('dependX')
        >>> point_attr.point.name
        "'penPair':'z1r'"
    """
    def __init__(self, point):
        self.point = point
        if point.name:
            self.attribute = name2dict(point.name)
        else:
            self.attribute = {}

    def _update_attr(self):
        self.point.name = dict2name(self.attribute)

    def get_attr(self, attribute):
        """ Gets attribute value from RPoint object.

        Args:
            attribute:: str
                The key of attribute that you want to get value.

        Returns:
            attribute value:: str
                The value of attribute.
        """
        return self.attribute.get(attribute)

    def set_attr(self, attribute, value):
        """ Sets attribute to RPoint object.

        Args:
            attribute:: str
                The key of attribute that you want to set.
            value:: str
                The new value of attribute that you want to set.
        """
        if attribute in self.attribute:
            self.attribute[attribute] = value
            self.point.glyph.setChanged()
            self._update_attr()

    def add_attr(self, attribute, value):
        """ Adds attribute to RPoint object.

        Args:
            attribute:: str
                The key of attribute that you want to add.
            value:: str
                The value of attribute that you want to add.
        """
        if attribute not in self.attribute:
            self.attribute[attribute] = value
            self.point.glyph.setChanged()
            self._update_attr()

    def del_attr(self, attribute):
        """ Deletes attribute from RPoint object.

        Args:
            attribute:: str
                The key of attribute that you want to delete.
        """
        try:
            del(self.attribute[attribute])
            self.point.glyph.setChanged()
        except KeyError:
            return None
        else:
            self._update_attr()
