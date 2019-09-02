import os
import json
from xml.etree import ElementTree as et

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
					name_dict = parse_name(name)
					for attr in list(name_dict.items()):
						point.attrib[attr[0]] = attr[1]

					try:
						del point.attrib['name']
					except:
						pass

					tree.write(path + "/" + file, encoding="UTF-8", xml_declaration=True)

def parse_name(name) -> dict:
	name = '{' + name.replace("'", '"') + '}'
    name_dict = json.loads(name)

    return name_dict

def get_attr(attribute):
	1

def set_attr(attribute, value):
    1

def add_attr(attribute, value):
    1

def del_attr(attribute):
    1
