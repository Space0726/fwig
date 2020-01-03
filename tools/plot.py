from xml.etree import ElementTree as et
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()
import bezier

def plot_line(subplot, line_points, show_points):
    """ Plotting lines.

    Args:
        subplot:: matplotlib.axes._subplots.AxesSubplot
        line_points:: list
        show_points:: bool
    """
    nodes = np.asfortranarray([
        [float(p.x) for p in line_points],
        [float(p.y) for p in line_points]])
    subplot.plot(nodes[0, :], nodes[1, :], color=sns.xkcd_rgb['denim blue'])
    if show_points:
        subplot.plot(nodes[0, 0], nodes[1, 0], marker='s', linestyle='None', \
                     color=sns.xkcd_rgb['pale red'])

def plot_curve(subplot, curve_points, show_points):
    """ Plotting bezier curves.

    Args:
        subplot:: matplotlib.axes._subplots.AxesSubplot
        curve_points:: list
        show_points:: bool
    """
    nodes = np.asfortranarray([
        [float(p.x) for p in curve_points],
        [float(p.y) for p in curve_points]])
    if show_points:
        subplot.plot(nodes[0, :2], nodes[1, :2], color=sns.xkcd_rgb['medium green'])
        subplot.plot(nodes[0, 2:], nodes[1, 2:], color=sns.xkcd_rgb['medium green'])
    _ = bezier.Curve(nodes, degree=3).plot(100, ax=subplot, color=sns.xkcd_rgb['denim blue']) # TODO: width
    if show_points:
        subplot.plot(nodes[0, 0], nodes[1, 0], marker='s', linestyle='None', \
                     color=sns.xkcd_rgb['pale red'])
        subplot.plot(nodes[0, 1:-1], nodes[1, 1:-1], marker='.', linestyle='None', \
                     color=sns.xkcd_rgb['pale red'])

def plot_rglyph(rglyph, show_points=True):
    """ Plotting RGlyph object.

    Args:
        rglyph:: RGlyph
    """
    subplot = plt.subplot(xlim=(0, glyph.width), ylim=(0, 1000)) # TODO: Needs modify
    for contour in glyph.contours:
        points = contour.points
        # TODO: Needs plot clockwise
        for idx, point in enumerate(points):
            if point.type == 'line':
                plot_line(subplot, [points[idx+i] for i in range(-1, 1)], show_points)
            elif point.type == 'curve':
                plot_curve(subplot, [points[idx+i] for i in range(-3, 1)], show_points)
            else:
                continue
    plt.show()

def plot_glif(xml_glyph, show_points=True):
    """ Plotting .glif XML format file in UFO font data.

    Args:
        xml_glyph:: xml.etree.ElementTree.Element
    """
    class _Point:
        def __init__(self, x, y, type_):
            self.x = x
            self.y = y
            self.type = type_
    # subplot = plt.subplot(xlim=(0, xml_glyph.find('advance').attrib['width']), 
                          # ylim=(0, 1000)) # TODO: Needs modify
    contours = xml_glyph.find('outline').getchildren()
    curve_points = [_Point(p.attrib['x'], p.attrib['y'], p.attrib.get('type')) \
               for p in contours[0].getchildren()[:4]]
    nodes = np.asfortranarray([
        [float(p.x) for p in curve_points],
        [float(p.y) for p in curve_points]])
    subplot = bezier.Curve(nodes, degree=3).plot(100) # TODO: width
    for contour in contours:
        points = [_Point(p.attrib['x'], p.attrib['y'], p.attrib.get('type')) \
                  for p in contour.getchildren()]
        for idx, point in enumerate(points):
            if point.type == 'line':
                plot_line(subplot, [points[idx+i] for i in range(-1, 1)], show_points)
            elif point.type == 'curve':
                plot_curve(subplot, [points[idx+i] for i in range(-3, 1)], show_points)
            else:
                continue
    plt.show()

if __name__ == '__main__':
    plot_glif(et.parse('./test.xml').getroot(), False)
