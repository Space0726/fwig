""" This is for handling stemfont attribute.

Last modified date: 2019/09/09

Created by Seongju Woo.
"""
import os
import json
from mojo.roboFont import RPoint
from xml.etree import ElementTree as et

def name2attr(path):
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
                attr =[]
                for a in point.attrib:
                    if a == 'x' or a == 'y' or a == 'type' or a == 'smooth':
                        continue
                    if not data:
                        data += ","
                    data += "'" + a + "':'" + point.get(a) + "'" 
                    attr.append(a)
                for x in attr:
                    point.attrib.pop(x)
                if not data:
                    point.set("name",data)

        tree.write(path + "/" + file, encoding="UTF-8", xml_declaration=True)

def name2dict(name) -> dict:
    if name is None:
        return {}
    name = '{' + name.replace("'", '"') + '}'
    name_dict = json.loads(name)

    return name_dict

def dict2name(dict_attributes) -> str:
    return ','.join([f"'{k}':'{v}'" for k, v in dict_attributes.items()])

def get_attr(point, attribute):
    attributes = name2dict(point.name)
    return attributes.get(attribute)

def set_attr(point, attribute, value):
    attributes = name2dict(point.name)
    if attribute in attributes:
        attributes[attribute] = value
        point.name = dict2name(attributes)

def add_attr(point, attribute, value):
    attributes = name2dict(point.name)
    if attribute not in attributes:
        attributes[attribute] = value
        point.name = dict2name(attributes)

def del_attr(point, attribute):
    attributes = name2dict(point.name)
    try:
        del(attributes[attribute])
    except KeyError:
        return None
    else:
        point.name = dict2name(attributes)

def get_all_points(glyph, offcurve=False):
    if not offcurve:
        return set([point for contour in glyph.contours \
                          for point in contour.points \
                          if point.type != 'offcurve'])
    else:
        return set([point for contour in glyph.contours \
                          for point in contour.points])

def get_penpair_dict(glyph):
    penpair_dict = {}
    all_points = get_all_points(glyph)
    for point in all_points:
        penpair = get_attr(point, 'penPair')[1:-1]
        if penpair in penpair_dict:
            penpair_dict[penpair].append(point)
        else:
            penpair_dict[penpair] = [point]
    return penpair_dict


class Attribute:
    def __init__(self, point):
        self.point = point
        if point.name:
            self.attribute = name2dict(point.name)
        else:
            self.attribute = {}

    def _update_attr(self):
        self.point.name = dict2name(self.attribute)

    def get_attr(self, attribute):
        return self.attribute.get(attribute)

    def set_attr(self, attribute, value):
        if attribute in self.attribute:
            self.attribute[attribute] = value
            self._update_attr()

    def add_attr(self, attribute, value):
        if attribute not in self.attribute:
            self.attribute[attribute] = value
            self._update_attr()

    def del_attr(self, attribute):
        try:
            del(self.attribute[attribute])
        except KeyError:
            return None
        else:
            self._update_attr()
