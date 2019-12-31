import os.path
from xml.dom import minidom
import sys
import math
from fontParts.world import *
from fontParts.base import BaseGlyph
from stemfont.tools.attributetools import *

# confirm file is gilf
def _is_glif(file_name):
    tokens = file_name.split('.')
    if len(tokens) != 2:
        return False
    return tokens[-1] == 'glif'

# convert UFO to METAFONT
def ufo2mf(destPath, ufoPath=None):
    if ufoPath is None:
        font = CurrentFont()
    else:
        font = OpenFont(os.path.abspath(ufoPath), showInterface=False)

    DIR_UFO = os.path.join(font.path, "glyphs")

    destPath = os.path.abspath(destPath)
    DIR_METAFONT_RADICAL = os.path.join(destPath, "radical.mf")
    DIR_METAFONT_COMBINATION = os.path.join(destPath, "combination.mf")

    print("Target:", DIR_UFO)
    print("Destination Path:", destPath)
    # Remove exist Metafont file for renew
    try:
        os.remove(DIR_METAFONT_RADICAL)
        os.remove(DIR_METAFONT_COMBINATION)
    except:
        nothing = 0

    # Get glyphs from UFO and Convert to Metafont
    glyphs = [font for font in os.listdir(DIR_UFO) if _is_glif(font)]
    font_width = get_font_width(DIR_UFO, glyphs)
    for glyph in glyphs:
        glyph2mf(glyph, DIR_UFO, DIR_METAFONT_RADICAL, DIR_METAFONT_COMBINATION, font_width, font)
    return None

# point class for point data of font
class Point:
    def __init__(self):
        self.name = ""
        self.idx = ""
        self.type = ""
        self.x = ""
        self.y = ""
        self.controlPoints = []
        self.dependX = ""
        self.dependY = ""
        self.penWidth = ""
        self.penHeight = ""
        self.startP = ""
        self.endP = ""
        self.serif = ""
        self.roundA = ""
        self.sound = ""
        self.char = ""
        self.double = ""
        self.formType = ""
        self.stroke = ""
        self.customer = ""

# get value of some attribute
def _get_value_by_node(tag, attribute):
    node = xmlData.getElementsByTagName(tag)
    try:
        return node[0].attributes[attribute].value
    except:
        return None

# convert float to string
def _float2str(value, decimal=4):
    str_val = str(float(value))
    return str_val[:str_val.find('.') + decimal]

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

# convert glyph of UFO to METAFONT
def glyph2mf(glyphName, dirUFO, dirRadical, dirCombination, fontWidth, rfont):
    global xmlData

    totalNum = 400
    # Initialize points
    points = []
    for i in range(0, totalNum):
        points.append(Point())
        points[i].controlPoints = []

    # Get glyph's UFO file
    dirGlyph = os.path.join(dirUFO, glyphName)
    xmlData = minidom.parse(dirGlyph)

    # If combination file, create characters for using glyph
    components = xmlData.getElementsByTagName('component')

    # get glyph object
    rglyph = getglyphobject(glyphName, rfont)
    print(rglyph.name)

    ####################################################################################################################
    # convert component of UFO to combination of METAFONT
    if len(components) != 0:
        fp = open(dirCombination, "a")
        # Write beginchar
        # glyphName = getValueByNode('glyph', 'name')

        unicodeList = xmlData.getElementsByTagName("unicode")
        if len(unicodeList) == 1:  # Need Change if unicode is more than 1
            code = str(int(unicodeList[0].getAttribute('hex'), 16))
        # fp.write('\nbeginchar('  + code + ', Width#, Height#, 0);\n') #!!!!!!!!!!!!!!!
        fp.write(
            '\nbeginchar(' + code + ', max(firstWidth#, middleWidth#, finalWidth#), max(firstHeight#, middleHeight#, finalHeight#), 0);\n\n')
        # fp.write('\nbeginchar('  + glyphName + ', Width#, Height#, 0);\n')
        # fp.write("    currenttransform := identity slanted slant;\n\n") #!!!!!!!!!!!!!!!

        # Write componenet (changed)
        # cnt = 0
        for component in components:
            name = component.attributes['base'].value
            # *** Changed *** #
            # fp.write("    " + _num2char(name)) #!!!!!!!!!!!!!!!
            # Apply each parameter
            # if cnt == 0:
            #   fp.write("(firstMoveSizeOfH, firstMoveSizeOfV)\n")
            # elif cnt == 1:
            #   fp.write("(middleMoveSizeOfH, middleMoveSizeOfV)\n")
            # if cnt == 2:
            #   fp.write("(finalMoveSizeOfH, finalMoveSizeOfV)\n")
            # cnt = cnt + 1
            if name[-1] == 'C':
                fp.write("  currenttransform := identity slanted firstSlant;\n")
                fp.write("  " + _num2char(name))
                fp.write(
                    "(firstWidth, firstHeight, firstMoveSizeOfH, firstMoveSizeOfV, firstPenWidthRate, firstPenHeightRate, firstCurveRate, firstSerifRate, firstBranchRate, firstUnfillRate, false, firstOpenUnfill)\n")
                fp.write("  if firstUnfillRate > 0.0:\n")
                fp.write("    " + _num2char(name))
                fp.write(
                    "(firstWidth, firstHeight, firstMoveSizeOfH, firstMoveSizeOfV, firstPenWidthRate * firstUnfillRate, firstPenHeightRate * firstUnfillRate, firstCurveRate, firstSerifRate, firstBranchRate, firstUnfillRate, true, firstOpenUnfill)\n")
                fp.write("  fi\n\n")
            elif name[-1] == 'V':
                fp.write("  currenttransform := identity slanted middleSlant;\n")
                fp.write("  " + _num2char(name))
                fp.write(
                    "(middleWidth, middleHeight, middleMoveSizeOfH, middleMoveSizeOfV, middlePenWidthRate, middlePenHeightRate, middleCurveRate, middleSerifRate, middleBranchRate, middleUnfillRate, false, middleOpenUnfill)\n")
                fp.write("  if middleUnfillRate > 0.0:\n")
                fp.write("    " + _num2char(name))
                fp.write(
                    "(middleWidth, middleHeight, middleMoveSizeOfH, middleMoveSizeOfV, middlePenWidthRate * middleUnfillRate, middlePenHeightRate * middleUnfillRate, middleCurveRate, middleSerifRate, middleBranchRate, middleUnfillRate, true, middleOpenUnfill)\n")
                fp.write("  fi\n\n")
            elif name[-1] == 'F':
                fp.write("  currenttransform := identity slanted finalSlant;\n")
                fp.write("  " + _num2char(name))
                fp.write(
                    "(finalWidth, finalHeight, finalMoveSizeOfH, finalMoveSizeOfV, finalPenWidthRate, finalPenHeightRate, finalCurveRate, finalSerifRate, finalBranchRate, finalUnfillRate, false, finalOpenUnfill)\n")
                fp.write("  if finalUnfillRate > 0.0:\n")
                fp.write("    " + _num2char(name))
                fp.write(
                    "(finalWidth, finalHeight, finalMoveSizeOfH, finalMoveSizeOfV, finalPenWidthRate * finalUnfillRate, finalPenHeightRate * finalUnfillRate, finalCurveRate, finalSerifRate, finalBranchRate, finalUnfillRate, true, finalOpenUnfill)\n")
                fp.write("  fi\n\n")

        # Write end
        fp.write("endchar;\n");
        fp.close()
    ####################################################################################################################


    ####################################################################################################################
    # convert glyph of UFO to radical of METAFONT
    else:  # If glyph file
        fp = open(dirRadical, "a")

        glyphName = _get_value_by_node('glyph', 'name')
        fp.write("% File parsed with MetaUFO %\n")
        # *** Changed *** #
        # fp.write('def ' + _num2char(glyphName) + '(expr moveSizeOfH, moveSizeOfV) =\n') #!!!!!!!!!!!!!!!
        fp.write('def ' + _num2char(
            glyphName) + '(expr Width, Height, moveSizeOfH, moveSizeOfV, penWidthRate, penHeightRate, curveRate, serifRate, branchRate, unfillRate, isUnfill, openUnfill) =\n')

        # Get UFO data by xml parser
        # UNDEFINED = 9999
        # leftP = [[UNDEFINED for col in range(2)] for row in range(totalNum)]
        # rightP = [[UNDEFINED for col in range(2)] for row in range(totalNum)]
        # diffP = [[0 for col in range(2)] for row in range(totalNum)]
        # dependLX = [0 for i in range(totalNum)]
        # dependRX = [0 for i in range(totalNum)]
        # dependLY = [0 for i in range(totalNum)]
        # dependRY = [0 for i in range(totalNum)]
        penWidth = [-1 for i in range(totalNum)]
        penHeight = [-1 for i in range(totalNum)]
        # cp = []
        # cpX = []
        # cpY = []
        # type = []
        pointOrder = []
        pointCnt = 0
        # cpCnt = 0
        existRound = False

        ################################################################################################################
        # Get point's tag information
        node = xmlData.getElementsByTagName('point')

        rpoints = []
        for rcontour in rglyph:
            rpoints += rcontour.points
        rpointsattr = []
        for rpoint in rpoints:
            rpointsattr.append(name2dict(rpoint.name))

        for i in range(len(node)):
            # if have a penPair attribute
            try:
                # name = node[i].attributes['penPair'].value
                name = rpointsattr[i]['penPair']
                # Get pointNumber and Store point order
                pointNumber = int(name[1:-1])
                if name.find('l') != -1:
                    idx = pointNumber * 2 - 1
                elif name.find('r') != -1:
                    idx = pointNumber * 2
                else:
                    print('Error : penPair attribute have a incorrect format value (' + name + ')')
                    return

                pointOrder.append(idx)

                # Store basic information of point having a penPair attribute
                # print("length:", len(points), ", idx:", idx)
                points[idx].name = name
                points[idx].type = node[i].attributes['type'].value
                points[idx].x = str(float(node[i].attributes['x'].value) / fontWidth)
                points[idx].y = str(float(node[i].attributes['y'].value) / fontWidth)
                points[idx].idx = pointCnt
                pointCnt = pointCnt + 1

                # If point have a special attributes, stroe it
                try:
                    # points[idx].dependX = node[i].attributes['dependX'].value
                    points[idx].dependX = rpointsattr[i]['dependX']
                except:
                    notting = 0

                try:
                    # points[idx].dependY = node[i].attributes['dependY'].value
                    points[idx].dependY = rpointsattr[i]['dependY']
                except:
                    notting = 0

                try:
                    # points[idx].startP = node[i].attributes['innerType'].value
                    points[idx].startP = rpointsattr[i]['innerType']
                    if len(pointOrder) > 1:
                        points[pointOrder[-2]].endP = 'end'
                    firstIdx = idx
                except:
                    notting = 0

                try:
                    # points[idx].serif = node[i].attributes['serif'].value
                    points[idx].serif = rpointsattr[i]['serif']
                except:
                    notting = 0

                try:
                    # points[idx].roundA = node[i].attributes['round'].value  # add round attribute
                    points[idx].roundA = rpointsattr[i]['round']
                    existRound = True
                except:
                    notting = 0

                try:
                    # points[idx].char = node[i].attribute['char'].value
                    points[idx].char = rpointsattr[i]['char']
                except:
                    notting = 0

                try:
                    # points[idx].sound = node[i].attribute['sound'].value
                    points[idx].sound = rpointsattr[i]['sound']
                except:
                    notting = 0

                try:
                    # points[idx].formType = node[i].attribute['formType'].value
                    points[idx].formType = rpointsattr[i]['formType']
                except:
                    notting = 0

                try:
                    # points[idx].double = node[i].attribute['double'].value
                    points[idx].double = rpointsattr[i]['double']
                except:
                    notting = 0

                try:
                    points[idx].stroke = rpointsattr[i]['stroke']
                except:
                    notting = 0

                try:
                    # points[idx].customer = node[i].attributes['customer'].value
                    points[idx].customer = rpointsattr[i]['customer']
                except:
                    notting = 0

            # if not have penPair attribute, it is control point
            except:
                # print(glyphName)
                idx = pointOrder[-1]
                xValue = node[i].attributes['x'].value
                yValue = node[i].attributes['y'].value
                points[idx].controlPoints.append([xValue, yValue])

        points[pointOrder[-1]].endP = 'end'
        ################################################################################################################

        ################################################################################################################
        # get data from fontParts

        # scaling
        for rcontour in rglyph:
            for rpoint in rcontour.points:
                rpoint.x /= fontWidth
                rpoint.y /= fontWidth

        # get siot, jieut contours
        siotcontours = []
        jiotcontours = []
        siotnums = {'first': ['9', '10'], 'final': ['3', '12', '18', '19', '20']}
        jiotnums = {'first': ['12', '13', '14'], 'final': ['5', '22', '23']}
        firstattr = Attribute(rglyph[0].points[0])
        if firstattr.get_attr('sound') == 'first':
            if firstattr.get_attr('char') in siotnums['first']:
                for rcontour in rglyph:
                    siotcontours.append(rcontour)
            elif firstattr.get_attr('char') in jiotnums['first']:
                for rcontour in rglyph:
                    if rcontour.bounds[1] == rglyph.bounds[1]:
                        jiotcontours.append(rcontour)
        elif firstattr.get_attr('sound') == 'final':
            if firstattr.get_attr('char') in siotnums['final']:
                if firstattr.get_attr('double') is None:
                    for rcontour in rglyph:
                        siotcontours.append(rcontour)
                else:
                    for rcontour in rglyph:
                        attr = Attribute(rcontour.points[0])
                        if attr.get_attr('double') == 'right':
                            siotcontours.append(rcontour)
            elif firstattr.get_attr('char') in jiotnums['final']:
                if firstattr.get_attr('double') is None:
                    for rcontour in rglyph:
                        if rcontour.bounds[1] == rglyph.bounds[1]:
                            jiotcontours.append(rcontour)
                else:
                    for rcontour in rglyph:
                        attr = Attribute(rcontour.points[0])
                        if attr.get_attr('double') == 'right' and rcontour.bounds[1] == rglyph.bounds[1]:
                            jiotcontours.append(rcontour)

        # get siot, jieut pairdict
        siotpairdict = getpairdict(siotcontours)
        siotorder = sorted(siotpairdict,
                           key=lambda pair: siotpairdict[pair]['l'].x if siotpairdict[pair]['l'].y > siotpairdict[pair][
                               'r'].y else siotpairdict[pair]['r'].x)
        jiotpairdict = getpairdict(jiotcontours)
        jiotorder = sorted(jiotpairdict,
                           key=lambda pair: jiotpairdict[pair]['l'].x if jiotpairdict[pair]['l'].y > jiotpairdict[pair][
                               'r'].y else jiotpairdict[pair]['r'].x)
        pairdict = getpairdict(rglyph)

        # get standard points
        gbounds = rglyph.bounds
        upformtype = ['3', '4', '5', '6']
        downformtype = ['2', '4', '6']
        standardpoints = {}

        if firstattr.get_attr('sound') == 'first' and firstattr.get_attr('formType') in upformtype:
            if firstattr.get_attr('double') is None:
                standardpoints['h'] = [findpoint(rglyph, (None, gbounds[1]))]
                standardpoints['w'] = [None]
            else:
                leftcontours = [rcontour for rcontour in rglyph if get_attr(rcontour.points[0], 'double') == 'left']
                rightcontours = [rcontour for rcontour in rglyph if
                                 get_attr(rcontour.points[0], 'double') == 'right']

                lgbounds = getbounds(leftcontours)
                rgbounds = getbounds(rightcontours)

                standardpoints['h'] = [findpoint(leftcontours, (None, lgbounds[1])),
                                       findpoint(rightcontours, (None, rgbounds[1]))]
                standardpoints['w'] = [findpoint(leftcontours, (lgbounds[2], None)),
                                       findpoint(rightcontours, (rgbounds[0], None))]
        elif firstattr.get_attr('sound') == 'final' and firstattr.get_attr('formType') in downformtype:
            if firstattr.get_attr('double') is None:
                standardpoints['h'] = [findpoint(rglyph, (None, gbounds[3]))]
                standardpoints['w'] = [None]
            else:
                leftcontours = [rcontour for rcontour in rglyph if get_attr(rcontour.points[0], 'double') == 'left']
                rightcontours = [rcontour for rcontour in rglyph if
                                 get_attr(rcontour.points[0], 'double') == 'right']

                lgbounds = getbounds(leftcontours)
                rgbounds = getbounds(rightcontours)

                standardpoints['h'] = [findpoint(leftcontours, (None, lgbounds[3])),
                                       findpoint(rightcontours, (None, rgbounds[3]))]
                standardpoints['w'] = [findpoint(leftcontours, (lgbounds[2], None)),
                                       findpoint(rightcontours, (rgbounds[0], None))]
        else:
            if firstattr.get_attr('double') is None:
                standardpoints['h'] = [None]
                standardpoints['w'] = [None]
            else:
                standardpoints['h'] = [None, None]
                standardpoints['w'] = [None, None]

        # get original point for siot
        originlist = []
        for standardpoint in standardpoints['h']:
            if standardpoint is None:
                continue
            attr = Attribute(standardpoint)
            pair = attr.get_attr('penPair')[1: -1]
            if pair in siotorder[1: -1]:
                index = siotorder.index(pair)
                for i in range(index - 1, index + 2):
                    originlist.append(siotorder[i])

        ################################################################################################################

        ################################################################################################################
        # convert pens

        fp.write("\n% pen parameter \n")
        # for i in range(1, int(totalNum / 2)):
        #     l = i * 2 - 1
        #     r = i * 2
        #
        #     if points[l].name == "" or points[r].name == "":
        #         continue
        #     elif str(i) in siotpairdict.keys():
        #         continue
        #
        #     penWidth[i] = float(points[l].x) - float(points[r].x)
        #     penHeight[i] = float(points[l].y) - float(points[r].y)
        #
        #     # *** Changed *** #
        #     fp.write("penWidth_" + str(i) + " := (((penWidthRate - 1) * "
        #         + _float2str(penWidth[i]) + ") / 2) * Width;\n")
        #     # *** Changed *** #
        #     fp.write("penHeight_" + str(i) + " := (((penHeightRate - 1) * "
        #         + _float2str(penHeight[i]) + ") / 2) * Height;\n")

        penform = 'pen{HW}_{num}{opt} := ((pen{HWR}Rate - 1) * {diff:0.3f}) / 2;\n'
        for pair in pairdict.keys():
            penpair = pairdict[pair]
            lattr = Attribute(penpair['l'])
            rattr = Attribute(penpair['r'])

            if len(penpair) != 2:
                continue

            penWidth[int(pair)] = float(penpair['l'].x) - float(penpair['r'].x)
            penHeight[int(pair)] = float(penpair['l'].y) - float(penpair['r'].y)

            penstrs = []
            edgepenstrs = []

            # siot case of pen
            if pair in siotpairdict.keys():
                if pair == siotorder[0]:
                    penstrs.append(penform.format(HW='Width', num=pair, HWR='Height', diff=penWidth[int(pair)], opt=''))
                    penstrs.append(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt=''))
                elif pair == siotorder[-1]:
                    penstrs.append(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt=''))
                    penstrs.append(penform.format(HW='Height', num=pair, HWR='Width', diff=penHeight[int(pair)], opt=''))
                else:
                    penstrs.append(penform.format(HW='Width', num=pair, HWR='Height', diff=penWidth[int(pair)], opt='_h'))
                    penstrs.append(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt='_h'))
                    penstrs.append(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt='_w'))
                    penstrs.append(penform.format(HW='Height', num=pair, HWR='Width', diff=penHeight[int(pair)], opt='_w'))

            # jieut case of pen
            elif pair in jiotpairdict.keys():
                if jiotorder.index(pair) in [0, 1, 4]:
                    penstrs.append(penform.format(HW='Width', num=pair, HWR='Height', diff=penWidth[int(pair)], opt=''))
                    penstrs.append(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt=''))
                elif jiotorder.index(pair) in [2, 5, 6] or (jiotorder.index(pair) == 3 and jiotorder[-1] == pair):
                    penstrs.append(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt=''))
                    penstrs.append(penform.format(HW='Height', num=pair, HWR='Width', diff=penHeight[int(pair)], opt=''))
                else:
                    penstrs.append(penform.format(HW='Width', num=pair, HWR='Height', diff=penWidth[int(pair)], opt='_h'))
                    penstrs.append(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt='_h'))
                    penstrs.append(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt='_w'))
                    penstrs.append(penform.format(HW='Height', num=pair, HWR='Width', diff=penHeight[int(pair)], opt='_w'))

            else:
                penstrs.append(penform.format(HW='Width', num=pair, HWR='Width', diff=penWidth[int(pair)], opt=''))
                penstrs.append(penform.format(HW='Height', num=pair, HWR='Height', diff=penHeight[int(pair)], opt=''))

            # edge pen
            if lattr.get_attr('stroke') is not None and rattr.get_attr('stroke') is not None:
                rpoints = penpair['l'].contour.points
                edgepoint = penpair['l'] if rpoints[penpair['l'].index - 1] != penpair['r'] else penpair['r']
                prepoint = rpoints[edgepoint.index - 1]
                vector = (edgepoint.x - prepoint.x, edgepoint.y - prepoint.y)
                diffw = penHeight[int(pair)]
                diffh = penWidth[int(pair)]

                if vector[0] < 0:
                    diffw = diffw if diffw < 0 else -diffw
                else:
                    diffw = -diffw if diffw < 0 else diffw
                if vector[1] < 0:
                    diffh = diffh if diffh < 0 else -diffh
                else:
                    diffh = -diffh if diffh < 0 else diffh

                # siot case of edge pen
                if pair in siotpairdict.keys():
                    if pair == siotorder[0]:
                        edgepenstrs.append(penform.format(HW='Width', num=pair, HWR='Width', diff=diffw, opt='_e'))
                        edgepenstrs.append(penform.format(HW='Height', num=pair, HWR='Width', diff=diffh, opt='_e'))
                    else:
                        edgepenstrs.append(penform.format(HW='Width', num=pair, HWR='Height', diff=diffw, opt='_e'))
                        edgepenstrs.append(penform.format(HW='Height', num=pair, HWR='Height', diff=diffh, opt='_e'))

                # jieut case of edge pen
                elif pair in jiotpairdict.keys():
                    if pair == jiotorder[0]:
                        edgepenstrs.append(penform.format(HW='Width', num=pair, HWR='Width', diff=diffw, opt='_e'))
                        edgepenstrs.append(penform.format(HW='Height', num=pair, HWR='Width', diff=diffh, opt='_e'))
                    else:
                        edgepenstrs.append(penform.format(HW='Width', num=pair, HWR='Height', diff=diffw, opt='_e'))
                        edgepenstrs.append(penform.format(HW='Height', num=pair, HWR='Height', diff=diffh, opt='_e'))

                else:
                    edgepenstrs.append(penform.format(HW='Width', num=pair, HWR='Width', diff=diffw, opt='_e'))
                    edgepenstrs.append(penform.format(HW='Height', num=pair, HWR='Height', diff=diffh, opt='_e'))

            # write pens on radical of METAFONT
            oripenstrs = []
            for penstr in penstrs:
                fp.write(penstr)
            for edgepenstr in edgepenstrs:
                fp.write(edgepenstr)
            # edge pen for open unfill
            if len(edgepenstrs) != 0:
                fp.write('if (openUnfill = 1) and (isUnfill):\n')
                for edgepenstr in edgepenstrs:
                    curpen = edgepenstr[: edgepenstr.find(' :=')]
                    edgepenstr = edgepenstr.replace(' := ', '_o := ')
                    edgepenstr = edgepenstr.replace('Rate', 'Rate / unfillRate')
                    edgepenstr = edgepenstr.replace(';', ' - ' + curpen + ';')
                    fp.write('\t' + edgepenstr)
                fp.write('fi\n')
            # original pen for siot
            if pair in originlist:
                for penstr in penstrs:
                    oripenstrs.append(penstr.replace('Rate', 'Rate / unfillRate').replace(' :=', '_ori :='))
                for edgepenstr in edgepenstrs:
                    oripenstrs.append(edgepenstr.replace('Rate', 'Rate / unfillRate').replace(' :=', '_ori :='))
                fp.write('if isUnfill:\n')
                for oripenstr in oripenstrs:
                    fp.write('\t' + oripenstr)
                fp.write('fi\n')

        ################################################################################################################

        ################################################################################################################
        # convert points

        fp.write("\n% point coordinates \n")
        for i in range(len(pointOrder)):
            idx = pointOrder[i]
            name = points[idx].name[1:]
            curpoint = points[idx]

            if curpoint.startP != '':
                startpoint = curpoint

            # convert siot, jieut separately
            if len(siotorder) > 0 and name[: -1] in siotorder[1: -1]:
                continue
            elif len(jiotorder) > 0 and name[: -1] in jiotorder[1: -1]:
                continue

            if name.find("l") != -1:
                op = "+"
            else:
                op = "-"

            # if startpoint.double != '':
            #     double = startpoint.double[0]
            # else:
            #     double = ''

            pointstrs = []
            oripointstrs = []

            # x of points
            pointstr = "x" + name + " := " + _float2str(float(points[idx].x))
            oripointstr = pointstr.replace(' :=', '_ori :=')
            # if points[idx].customer != "":
            #     pointstr += " + " + points[idx].customer
            if points[idx].dependX != "":
                dependXValue = points[idx].dependX
                if dependXValue.find("l") != -1:
                    pointstr += "+ penWidth_" + dependXValue[1:-1]
                    oripointstr += "+ penWidth_" + dependXValue[1:-1] + '_ori'
                else:
                    pointstr += "- penWidth_" + dependXValue[1:-1]
                    oripointstr += "- penWidth_" + dependXValue[1:-1] + '_ori'
            elif penWidth[int(name[0:-1])] != -1:
                pointstr += op + " penWidth_" + name[0:-1]
                oripointstr += op + " penWidth_" + name[0:-1] + '_ori'
            if points[idx].stroke != '':
                pointstr += ' + penWidth_' + name[: -1] + '_e'
                oripointstr += ' + penWidth_' + name[: -1] + '_e_ori'
            pointstr += ";\n"
            oripointstr += ";\n"
            pointstrs.append(pointstr)
            oripointstrs.append(oripointstr)

            # y of points
            pointstr = "y" + name + " := " + _float2str(float(points[idx].y))
            oripointstr = pointstr.replace(' :=', '_ori :=')
            if points[idx].dependY != "":
                dependYValue = points[idx].dependY
                if dependYValue.find("l") != -1:
                    pointstr += "+ penHeight_" + dependYValue[1:-1]
                    oripointstr += "+ penHeight_" + dependYValue[1:-1] + '_ori'
                else:
                    pointstr += "- penHeight_" + dependYValue[1:-1]
                    oripointstr += "- penHeight_" + dependYValue[1:-1] + '_ori'
            elif penHeight[int(name[0:-1])] != -1:
                pointstr += op + " penHeight_" + name[0:-1]
                oripointstr += op + " penHeight_" + name[0:-1] + '_ori'
            if points[idx].stroke != '':
                pointstr += ' + penHeight_' + name[: -1] + '_e'
                oripointstr += ' + penHeight_' + name[: -1] + '_e_ori'
            pointstr += ";\n"
            oripointstr += ";\n"
            pointstrs.append(pointstr)
            oripointstrs.append(oripointstr)

            # write points on radical of METAFONT
            for pointstr in pointstrs:
                fp.write(pointstr)
            if name[: -1] in originlist:
                fp.write('if isUnfill:\n')
                for oripointstr in oripointstrs:
                    fp.write('\t' + oripointstr)
                fp.write('fi\n')
        ################################################################################################################

        ################################################################################################################
        # siot, jieut case of points

        pointform = '{xy}{pair}{opt1}{opt2}{lr} := {coord:0.3f} {op} pen{hw}_{pair}{opt1};\n'
        for pair in pairdict.keys():
            penpair = pairdict[pair]

            if len(siotorder) > 0 and pair in siotorder[1: -1]:
                pass
            elif len(jiotorder) > 0 and pair in jiotorder[1: -1]:
                pass
            else:
                continue

            pointstrs = []
            if pair in jiotorder[1: -1] and jiotorder.index(pair) % 3 != 0:
                for lr in penpair.keys():
                    if lr == 'l':
                        op = '+'
                    else:
                        op = '-'
                    pointstrs.append(
                        pointform.format(xy='x', pair=pair, lr=lr, coord=penpair[lr].x, hw='Width', op=op,
                                         opt1='', opt2='_'))
                    pointstrs.append(
                        pointform.format(xy='y', pair=pair, lr=lr, coord=penpair[lr].y, hw='Height', op=op,
                                         opt1='', opt2='_'))
            else:
                for lr in penpair.keys():
                    if lr == 'l':
                        op = '+'
                    else:
                        op = '-'
                    pointstrs.append(
                        pointform.format(xy='x', pair=pair, lr=lr, coord=penpair[lr].x, hw='Width', op=op,
                                         opt1='_h', opt2=''))
                    pointstrs.append(
                        pointform.format(xy='y', pair=pair, lr=lr, coord=penpair[lr].y, hw='Height', op=op,
                                         opt1='_h', opt2=''))
                    pointstrs.append(
                        pointform.format(xy='x', pair=pair, lr=lr, coord=penpair[lr].x, hw='Width', op=op,
                                         opt1='_w', opt2=''))
                    pointstrs.append(
                        pointform.format(xy='y', pair=pair, lr=lr, coord=penpair[lr].y, hw='Height', op=op,
                                         opt1='_w', opt2=''))

            oripointstrs = []
            for pointstr in pointstrs:
                fp.write(pointstr)
            if pair in originlist:
                for pointstr in pointstrs:
                    oripointstrs.append(pointstr.replace(' :=', '_ori :=').replace(';', '_ori;'))
                fp.write('if isUnfill:\n')
                for oripointstr in oripointstrs:
                    fp.write('\t' + oripointstr)
                fp.write('fi\n')

        # intersection points for transforming weight of siot, jieut
        lineform = 'z{start} -- 2[z{start}, z{end}]'
        vlineform = '0.5[z{start}l, z{start}r] -- 0.5[z{end}l, z{end}r]'
        insecform = '{xy}part (({lineform1}) intersectionpoint ({lineform2}))'
        insecpointform = '{xy}{pair}{lr} := {insecform};\n'
        ifinsecform = 'if {insecform} > ypart (0.5[z{start}l, z{start}r]):\n'
        ifinsecform += '\t{vinsecpointformx}\t{vinsecpointformy}'
        ifinsecform += 'else:\n\t{insecpointformx}\t{insecpointformy}fi\n'

        # siot case of intersection points
        for i in range(1, len(siotorder) - 1):
            pairlist = siotorder[i - 1: i + 2]
            upside = ['l' if pairdict[pair]['l'].y > pairdict[pair]['r'].y else 'r' for pair in pairlist]
            downside = ['l' if side == 'r' else 'r' for side in upside]

            if i % 2 != 0:
                opt = ['_h', '_w']
            else:
                opt = ['_w', '_h']

            insecpoints = []
            oriinsecpoints = []
            for side in [upside, downside]:
                start = [pairlist[0] + (opt[0] if pairlist[0] != siotorder[0] else '') + side[0],
                         pairlist[2] + (opt[1] if pairlist[2] != siotorder[-1] else '') + side[2]]
                end = [pairlist[1] + opt[0] + side[1], pairlist[1] + opt[1] + side[1]]
                line = [lineform.format(start=start[num], end=end[num]) for num in range(len(start))]
                oriline = [lineform.format(start=start[num] + '_ori', end=end[num] + '_ori') for num in range(len(start))]
                for xy in ['x', 'y']:
                    insec = insecform.format(xy=xy, lineform1=line[0], lineform2=line[1])
                    insecpoint = insecpointform.format(xy=xy, pair=pairlist[1], lr=side[1], insecform=insec)
                    insecpoints.append(insecpoint)
                    oriinsec = insecform.format(xy=xy, lineform1=oriline[0], lineform2=oriline[1])
                    oriinsecpoint = insecpointform.format(xy=xy, pair=pairlist[1], lr=side[1] + '_ori', insecform=oriinsec)
                    oriinsecpoints.append(oriinsecpoint)

            for insecpoint in insecpoints:
                fp.write(insecpoint)
            if originlist == pairlist:
                fp.write('if isUnfill:\n')
                for oriinsecpoint in oriinsecpoints:
                    fp.write('\t' + oriinsecpoint)
                fp.write('fi\n')

        # jieut case of intersection points
        for i in range(1, len(jiotorder) - 1):
            curpair = jiotorder[i]
            if i % 3 == 1:
                pairlist = jiotorder[i - 1: i + 3]
            elif i % 3 == 2:
                pairlist = jiotorder[i - 2: i + 2]
            else:
                pairlist = jiotorder[i - 1: i + 2]

            upside = ['l' if pairdict[pair]['l'].y > pairdict[pair]['r'].y else 'r' for pair in pairlist]
            downside = ['l' if side == 'r' else 'r' for side in upside]

            if i % 3 != 0:
                for rcontour in rglyph:
                    point = jiotpairdict[pairlist[1]][upside[1]]
                    if rcontour.pointInside((point.x, point.y)):
                        hatcontour = rcontour
                hatpairdict = getpairdict([hatcontour])
                hatpairlist = list(hatpairdict.keys())

                opt = []
                for pair in pairlist:
                    if pair in [jiotorder[0], jiotorder[-1]]:
                        opt.append('')
                    elif jiotorder.index(pair) % 3 in [1, 2]:
                        opt.append('_')
                    else:
                        if pair == pairlist[0]:
                            opt.append('_h')
                        elif pair == pairlist[-1]:
                            opt.append('_w')

                start = [pairlist[0] + opt[0] + upside[0], pairlist[3] + opt[3] + upside[3]]
                end = [pairlist[1] + opt[1] + upside[1], pairlist[2] + opt[2] + upside[2]]
                line = [lineform.format(start=start[num], end=end[num]) for num in range(len(start))]
                vline = vlineform.format(start=hatpairlist[0], end=hatpairlist[1])
                insec = {}
                vinsec = {}
                insecpoint = {}
                vinsecpoint = {}
                for xy in ['x', 'y']:
                    insec[xy] = insecform.format(xy=xy, lineform1=line[0], lineform2=line[1])
                    vinsec[xy] = insecform.format(xy=xy, lineform1=vline, lineform2=line[i % 3 - 1])
                    insecpoint[xy] = insecpointform.format(xy=xy, pair=curpair, lr=upside[pairlist.index(curpair)],
                                                           insecform=insec[xy])
                    vinsecpoint[xy] = insecpointform.format(xy=xy, pair=curpair, lr=upside[pairlist.index(curpair)],
                                                            insecform=vinsec[xy])
                ifinsec = ifinsecform.format(insecform=insec['y'], start=hatpairlist[0],
                                             vinsecpointformx=vinsecpoint['x'], vinsecpointformy=vinsecpoint['y'],
                                             insecpointformx=insecpoint['x'], insecpointformy=insecpoint['y'])
                fp.write(ifinsec)

                start = [pairlist[0] + opt[0] + downside[0], pairlist[3] + opt[3] + downside[3]]
                end = [pairlist[1] + opt[1] + downside[1], pairlist[2] + opt[2] + downside[2]]
                line = [lineform.format(start=start[num], end=end[num]) for num in range(len(start))]
                downinsecpoints = []
                for xy in ['x', 'y']:
                    insec = insecform.format(xy=xy, lineform1=line[0], lineform2=line[1])
                    insecpoint = insecpointform.format(xy=xy, pair=curpair, lr=downside[pairlist.index(curpair)],
                                                       insecform=insec)
                    downinsecpoints.append(insecpoint)
                for insecpoint in downinsecpoints:
                    fp.write(insecpoint)
            else:
                opt = ['_w', '_h']

                insecpoints = []
                for side in [upside, downside]:
                    start = [pairlist[0] + '_' + side[0], pairlist[2] + '_' + side[2]]
                    end = [pairlist[1] + opt[0] + side[1], pairlist[1] + opt[1] + side[1]]
                    line = [lineform.format(start=start[num], end=end[num]) for num in range(len(start))]
                    for xy in ['x', 'y']:
                        insec = insecform.format(xy=xy, lineform1=line[0], lineform2=line[1])
                        insecpoint = insecpointform.format(xy=xy, pair=pairlist[1], lr=side[1], insecform=insec)
                        insecpoints.append(insecpoint)

                for insecpoint in insecpoints:
                    fp.write(insecpoint)

        # for open unfill
        openform = '{xy}{point} := {xy}{point} + {open};\n'
        openstrs = []
        for pair in pairdict.keys():
            for lr, point in pairdict[pair].items():
                attr = Attribute(point)
                if attr.get_attr('stroke') is not None:
                    name = attr.get_attr('penPair')
                    openstrs.append(openform.format(xy='x', point=name[1:], open='penWidth_' + name[1: -1] + '_e_o'))
                    openstrs.append(openform.format(xy='y', point=name[1:], open='penHeight_' + name[1: -1] + '_e_o'))

        fp.write('if (openUnfill = 1) and (isUnfill):\n')
        for openstr in openstrs:
            fp.write('\t' + openstr)
        fp.write('fi\n')

        ################################################################################################################

        """
        ##############################################################################
        # Set dependency
        fp.write("\n% dependency\n")
        for i in range(len(pointOrder)):
            idx = pointOrder[i]
            name = points[idx].name[1:]

            if points[idx].dependX != "":
                dependIdx = points[idx].dependX[1:-1]
                if points[idx].dependX.find("r") > -1 :
                    fp.write("x" + name + " := x" + name + " - penWidth_" + dependIdx + ";\n")
                else:
                    fp.write("x" + name + " := x" + name + " + penWidth_" + dependIdx + ";\n")
            if points[idx].dependY != "":
                dependIdx = points[idx].dependY[1:-1]
                if points[idx].dependY.find("r") > -1 :
                    fp.write("y" + name + " := y" + name + " - penHeight_" + dependIdx + ";\n")
                else:
                    fp.write("y" + name + " := y" + name + " + penHeight_" + dependIdx + ";\n")
        """

        ################################################################################################################
        # convert bezier control points (bcp)

        fp.write("\n% control point\n")
        circlepoints = []
        # if (points[pointOrder[0]].sound == 'first' and (
        #         points[pointOrder[0]].char == '11' or (points[pointOrder[0]].char == '18'))) or (
        #         points[pointOrder[0]].sound == 'final' and (
        #         points[pointOrder[0]].char == '21' or (points[pointOrder[0]].char == '27'))):
        #     for i in range(len(pointOrder)):
        #         curIdx = pointOrder[i]
        #         if points[curIdx].startP != '':
        #             firstOI = i
        #             iscurve = 1
        #             isright = 1
        #             isleft = 1
        #
        #         if points[curIdx].type != 'curve':
        #             iscurve *= 0
        #         if points[curIdx].name[-1] == 'l':
        #             isright *= 0
        #         else:
        #             isleft *= 0
        #
        #         if points[curIdx].endP != '':
        #             if iscurve == 1 and (isright != isleft):
        #                 circlepoints += range(firstOI, i + 1)

        # get ieung points
        if (firstattr.get_attr('sound') == 'first' and firstattr.get_attr('char') in ['11', '18']) or \
                (firstattr.get_attr('sound') == 'final' and firstattr.get_attr('char') in ['6', '15', '21', '27']):
            for rcontour in rglyph:
                if len(rcontour.points) == len(rcontour) * 3:
                    for point in rcontour.points:
                        if point.type == 'curve':
                            name = get_attr(point, 'penPair')
                            circlepoints.append(name[1: -1])
            circlepoints = list(set(circlepoints))

        for i in range(0, len(pointOrder)):
            # convert ieung separately
            if points[pointOrder[i]].name[1: -1] in circlepoints:
                continue

            if points[pointOrder[i]].startP != "":
                firstIdx = pointOrder[i]

            if i == len(pointOrder) - 1 or points[pointOrder[i + 1]].startP != "":
                curIdx = pointOrder[i]
                nextIdx = firstIdx
            else:
                curIdx = pointOrder[i]
                nextIdx = pointOrder[i + 1]

            if points[nextIdx].name == "" or points[nextIdx].type == "line":
                continue

            name = points[curIdx].name[1:-1]
            nextName = points[nextIdx].name[1:-1]
            way = points[curIdx].name[-1]

            if points[curIdx].name.find("l") != -1:
                curOp = "+"
            else:
                curOp = "-"

            if points[nextIdx].name.find("l") != -1:
                nextOp = "+"
            else:
                nextOp = "-"

            curPenWidthIdx = int(name)
            curPenHeightIdx = int(name)
            nextPenWidthIdx = int(nextName)
            nextPenHeightIdx = int(nextName)

            # x of first bcp
            dependXValue = points[curIdx].dependX
            if dependXValue != "":
                if dependXValue.find("l") != -1:
                    curPenW = "+ penWidth_" + dependXValue[1:-1]
                else:
                    curPenW = "- penWidth_" + dependXValue[1:-1]
                curPenWidthIdx = int(dependXValue[1:-1])
            elif penWidth[int(name)] != -1:
                curPenW = curOp + " penWidth_" + name
            else:
                curPenW = ""

            # y of first bcp
            dependYValue = points[curIdx].dependY
            if dependYValue != "":
                if dependYValue.find("l") != -1:
                    curPenH = "+ penHeight_" + dependYValue[1:-1]
                else:
                    curPenH = "- penHeight_" + dependYValue[1:-1]
                curPenHeightIdx = int(dependYValue[1:-1])
            elif penHeight[int(name)] != -1:
                curPenH = curOp + " penHeight_" + name
            else:
                curPenH = ""

            # x of second bcp
            dependXValue = points[nextIdx].dependX
            if dependXValue != "":
                if dependXValue.find("l") != -1:
                    nextPenW = "+ penWidth_" + dependXValue[1:-1]
                else:
                    nextPenW = "- penWidth_" + dependXValue[1:-1]
                nextPenWidthIdx = int(dependXValue[1:-1])
            elif penWidth[int(nextName)] != -1:
                nextPenW = nextOp + " penWidth_" + nextName
            else:
                nextPenW = ""

            # y of second bcp
            dependYValue = points[nextIdx].dependY
            if dependYValue != "":
                if dependYValue.find("l") != -1:
                    nextPenH = "+ penHeight_" + dependYValue[1:-1]
                else:
                    nextPenH = "- penHeight_" + dependYValue[1:-1]
                nextPenHeightIdx = int(dependYValue[1:-1])
            elif penHeight[int(nextName)] != -1:
                nextPenH = nextOp + " penHeight_" + nextName
            else:
                nextPenH = ""

            if points[curIdx].customer != "":
                curCustomer = points[curIdx].customer
            else:
                curCustomer = ""

            if points[nextIdx].customer != "":
                nextCustomer = points[nextIdx].customer
            else:
                nextCustomer = ""

            # write bcp on radical of METAFONT
            pointName = points[curIdx].name[1:]
            # *** Changed float -> _float2str() *** #
            if points[nextIdx].type == "curve":
                fp.write("x" + pointName + "1 := (" + _float2str(float(points[curIdx].controlPoints[0][
                                                                                  0]) / fontWidth) + " + " + curCustomer + " + moveSizeOfH) * Width " + curPenW + ";\n")
                fp.write("y" + pointName + "1 := (" + _float2str(float(
                    points[curIdx].controlPoints[0][1]) / fontWidth) + " + moveSizeOfV) * Height " + curPenH + ";\n")
                #   fp.write("x" + pointName + "1 := x" + pointName + "1 - (1 - curveRate)*(" + "x" + pointName + "1 - x" + pointName + "); ")
                #   fp.write("y" + pointName + "1 := y" + pointName + "1 - (1 - curveRate)*(" + "y" + pointName + "1 - y" + pointName + ");\n")
                fp.write("x" + pointName + "2 := (" + _float2str(float(points[curIdx].controlPoints[1][
                                                                                  0]) / fontWidth) + " + " + nextCustomer + " + moveSizeOfH) * Width " + nextPenW + ";\n")
                fp.write("y" + pointName + "2 := (" + _float2str(float(
                    points[curIdx].controlPoints[1][1]) / fontWidth) + " + moveSizeOfV) * Height " + nextPenH + ";\n")
            #   fp.write("x" + pointName + "2 := x" + pointName + "2 - (1 - curveRate)*(" + "x" + pointName + "2 - x" + pointName + "); ")
            #   fp.write("y" + pointName + "2 := y" + pointName + "2 - (1 - curveRate)*(" + "y" + pointName + "2 - y" + pointName + ");\n")
            elif points[nextIdx].type == "qcurve":
                size = len(points[curIdx].controlPoints)
                for j in range(0, size):
                    if size % 2 == 1 and j == size / 2:
                        if penWidth[curPenWidthIdx] > penWidth[nextPenWidthIdx]:
                            fp.write("x" + pointName + str(j + 1) + " := (" + _float2str(float(
                                points[curIdx].controlPoints[j][
                                    0]) / fontWidth) + " + " + curCustomer + " + moveSizeOfH) * Width " + curPenW + ";\n")
                        else:
                            fp.write("x" + pointName + str(j + 1) + " := (" + _float2str(float(
                                points[curIdx].controlPoints[j][
                                    0]) / fontWidth) + " + " + nextCustomer + " + moveSizeOfH) * Width " + nextPenW + ";\n")

                        if penHeight[curPenHeightIdx] > penHeight[nextPenHeightIdx]:
                            fp.write("y" + pointName + str(j + 1) + " := (" + _float2str(float(
                                points[curIdx].controlPoints[j][
                                    1]) / fontWidth) + " + moveSizeOfV) * Height " + curPenH + ";\n")
                        else:
                            fp.write("y" + pointName + str(j + 1) + " := (" + _float2str(float(
                                points[curIdx].controlPoints[j][
                                    1]) / fontWidth) + " + moveSizeOfV) * Height " + nextPenH + ";\n")

                    elif j < size / 2:
                        fp.write("x" + pointName + str(j + 1) + " := (" + _float2str(float(
                            points[curIdx].controlPoints[j][
                                0]) / fontWidth) + " + " + curCustomer + " + moveSizeOfH) * Width " + curPenW + ";\n")
                        fp.write("y" + pointName + str(j + 1) + " := (" + _float2str(float(
                            points[curIdx].controlPoints[j][
                                1]) / fontWidth) + " + moveSizeOfV) * Height " + curPenH + ";\n")
                    else:
                        fp.write("x" + pointName + str(j + 1) + " := (" + _float2str(float(
                            points[curIdx].controlPoints[j][
                                0]) / fontWidth) + " + " + nextCustomer + " + moveSizeOfH) * Width " + nextPenW + ";\n")
                        fp.write("y" + pointName + str(j + 1) + " := (" + _float2str(float(
                            points[curIdx].controlPoints[j][
                                1]) / fontWidth) + " + moveSizeOfV) * Height " + nextPenH + ";\n")

            #       fp.write("x" + pointName + str(j+1) + " := x" + pointName + str(j+1) + " - (1 - curveRate) * (" + "x" + pointName + str(j+1) + " - x" + pointName + "); ")
            #       fp.write("y" + pointName + str(j+1) + " := y" + pointName + str(j+1) + " - (1 - curveRate) * (" + "y" + pointName + str(j+1) + " - y" + pointName + ");\n")

        ################################################################################################################

        ################################################################################################################
        # ieung case of bcp

        if len(circlepoints) != 0:
            radiusform = '(({anchor} {op} {anchorpen} - ({revname} {op} {revpen})) / 2)'
            bcpform = '{bcpname}{num} := {anchor} * {coordrate} {op} {pen} / {radius} * (1 - {coordrate}) * {anchor};\n'
            for rcontour in rglyph:
                if len(rcontour.points) != len(rcontour) * 3:
                    continue

                cboundx = [rcontour.bounds[0], rcontour.bounds[2]]
                cboundy = [rcontour.bounds[1], rcontour.bounds[3]]

                for cursegidx in range(len(rcontour)):
                    curseg = rcontour[cursegidx]
                    preseg = rcontour[cursegidx - 1]
                    revsegs = [rcontour[cursegidx - 1 - len(rcontour) // 2], rcontour[cursegidx - len(rcontour) // 2]]

                    curpoint = curseg.onCurve
                    prepoint = preseg.onCurve
                    revpoints = [seg.onCurve for seg in revsegs]
                    bcpoint = curseg.offCurve

                    curattr = Attribute(curpoint)
                    preattr = Attribute(prepoint)
                    revattrs = [Attribute(revpoint) for revpoint in revpoints]

                    revnames = [revattr.get_attr('penPair')[1:] for revattr in revattrs]
                    anchor = [preattr.get_attr('penPair')[1:], curattr.get_attr('penPair')[1:]]
                    bcpname = anchor[0]
                    coordratex = ['%0.3f / %0.3f' % (bcpoint[0].x, prepoint.x),
                                  '%0.3f / %0.3f' % (bcpoint[1].x, curpoint.x)]
                    coordratey = ['%0.3f / %0.3f' % (bcpoint[0].y, prepoint.y),
                                  '%0.3f / %0.3f' % (bcpoint[1].y, curpoint.y)]
                    penx = ['penHeight_%s' % (x[:-1]) for x in anchor]
                    peny = ['penWidth_%s' % (x[:-1]) for x in anchor]

                    radius = []
                    op = '-' if bcpname[-1] == 'l' else '+'
                    if prepoint.x in cboundx:
                        pen = 'penWidth_'
                        radius.append(radiusform.format(anchor='x' + anchor[0], anchorpen=pen + anchor[0][:-1],
                                                        revname='x' + revnames[0], revpen=pen + revnames[0][:-1], op=op))
                    elif prepoint.y in cboundy:
                        pen = 'penHeight_'
                        radius.append(radiusform.format(anchor='y' + anchor[0], anchorpen=pen + anchor[0][:-1],
                                                        revname='y' + revnames[0], revpen=pen + revnames[0][:-1], op=op))
                    if curpoint.x in cboundx:
                        pen = 'penWidth_'
                        radius.append(radiusform.format(anchor='x' + anchor[1], anchorpen=pen + anchor[1][:-1],
                                                        revname='x' + revnames[1], revpen=pen + revnames[1][:-1], op=op))
                    elif curpoint.y in cboundy:
                        pen = 'penHeight_'
                        radius.append(radiusform.format(anchor='y' + anchor[1], anchorpen=pen + anchor[1][:-1],
                                                        revname='y' + revnames[1], revpen=pen + revnames[1][:-1], op=op))

                    for num in range(2):
                        fp.write(bcpform.format(bcpname='x' + bcpname, num=num + 1, anchor='x' + anchor[num],
                                                coordrate=coordratex[num], pen=penx[num], radius=radius[num], op=op))
                        fp.write(bcpform.format(bcpname='y' + bcpname, num=num + 1, anchor='y' + anchor[num],
                                                coordrate=coordratey[num], pen=peny[num], radius=radius[num], op=op))

        ################################################################################################################

        ################################################################################################################
        # convert moveSize

        moveform = 'moveSizeOf{hv}{opt} := moveSizeOf{hv}{dist};\n'
        distform = ' + ({end} - {start}{pen}{unfill}{epen}{eunfill})'
        unfillform = ' / (pen{hw}Rate - 1) * (pen{hw}Rate / unfillRate - 1)'
        ifmoveform = 'if isUnfill:\n{moveunfill}\nelse:\n{move}\nfi\n\n'
        moves = ''
        moveunfills = ''

        for key in standardpoints.keys():
            hw = 'Height' if key == 'h' else 'Width'
            hv = 'V' if key == 'h' else 'H'
            xy = 'y' if key == 'h' else 'x'
            dists = []
            distsunfill = []
            unfill = unfillform.format(hw=hw)

            for point in standardpoints.get(key):
                if point is None:
                    continue

                attr = Attribute(point)
                name = xy + attr.get_attr('penPair')[1:]

                if hw == 'Height':
                    depend = attr.get_attr('dependY')
                else:
                    depend = attr.get_attr('dependX')

                if name[1: -1] in siotorder[1: -1]:
                    pen = ' + ('
                    if depend is not None:
                        if depend[-1] == 'l':
                            pen += '- pen' + hw + '_' + depend[1: -1]
                        else:
                            pen += 'pen' + hw + '_' + depend[1: -1]
                    else:
                        if name[-1] == 'l':
                            pen += '- pen' + hw + '_' + name[1: -1]
                        else:
                            pen += 'pen' + hw + '_' + name[1: -1]
                    pen += '_' + key + ')'
                    if attr.get_attr('stroke') is not None:
                        epen = ' + (- pen' + hw + '_' + name[1: -1] + '_e)'
                    else:
                        epen = ''
                    dists.append(distform.format(end=name[: -1] + '_' + key + name[-1], start=name, pen=pen, unfill='', epen=epen, eunfill=''))
                    distsunfill.append(distform.format(end=name[: -1] + '_' + key + name[-1], start=name + '_ori', pen=pen, unfill='', epen=epen, eunfill=''))
                else:
                    pen = ' + ('
                    if depend is not None:
                        if depend[-1] == 'l':
                            pen += '- pen' + hw + '_' + depend[1: -1]
                        else:
                            pen += 'pen' + hw + '_' + depend[1: -1]
                    else:
                        if name[-1] == 'l':
                            pen += '- pen' + hw + '_' + name[1: -1]
                        else:
                            pen += 'pen' + hw + '_' + name[1: -1]
                    pen += ')'
                    if attr.get_attr('stroke') is not None:
                        epen = ' + (- pen' + hw + '_' + name[1: -1] + '_e)'
                        eunfill = unfill
                    else:
                        epen = ''
                        eunfill = ''
                    if name[1: -1] in siotorder or name[1: -1] in jiotorder:
                        unfill = unfillform.format(hw='Height')
                    dists.append(distform.format(end=name, start=name, pen=pen, unfill='', epen=epen, eunfill=''))
                    distsunfill.append(distform.format(end=name, start=name, pen=pen, unfill=unfill, epen=epen, eunfill=eunfill))

            if len(dists) == 0:
                if len(standardpoints[key]) == 1:
                    moves += '\t' + moveform.format(hv=hv, opt='_', dist='')
                    moveunfills += '\t' + moveform.format(hv=hv, opt='_', dist='')
                else:
                    opt = ['_l', '_r']
                    for i in range(2):
                        moves += '\t' + moveform.format(hv=hv, opt=opt[i], dist='')
                        moveunfills += '\t' + moveform.format(hv=hv, opt=opt[i], dist='')
            elif len(dists) == 1:
                moves += '\t' + moveform.format(hv=hv, opt='_', dist=dists[0])
                moveunfills += '\t' + moveform.format(hv=hv, opt='_', dist=distsunfill[0])
            else:
                opt = ['_l', '_r']
                for i in range(2):
                    moves += '\t' + moveform.format(hv=hv, opt=opt[i], dist=dists[i])
                    moveunfills += '\t' + moveform.format(hv=hv, opt=opt[i], dist=distsunfill[i])

        fp.write(ifmoveform.format(moveunfill=moveunfills, move=moves))

        ################################################################################################################

        ################################################################################################################
        # moveSize for branch contours

        branchs = []
        stems = []
        for rcontour in rglyph:
            point = rcontour.points[0]
            attr = Attribute(point)
            if attr.get_attr('sound') == 'middle' and attr.get_attr('elem') == 'branch':
                branchs.append(rcontour)
            elif attr.get_attr('sound') == 'middle' and attr.get_attr('elem') == 'stem':
                stems.append(rcontour)

        branchdict = {}
        for branch in branchs:
            branchpairdict = getpairdict([branch])
            for pair in branchpairdict.keys():
                pairpoints = branchpairdict[pair]
                leftpoint = pairpoints['l']
                rightpoint = pairpoints['r']
                for stem in stems:
                    if stem.pointInside((leftpoint.x, leftpoint.y)) and stem.pointInside((rightpoint.x, rightpoint.y)):
                        if branch in branchdict:
                            branchdict[branch]['stem'].append(stem)
                        else:
                            branchdict[branch] = {'stem': [stem]}
            if branchdict.get(branch) is not None:
                branchdict[branch]['stem'].sort(key=lambda x: x.index)


        if len(branchdict) == 2:
            keys = list(branchdict.keys())
            values = list(branchdict.values())
            if values[0]['stem'] == values[1]['stem']:
                branchdict[keys[0]]['double'] = keys[1]
                branchdict[keys[1]]['double'] = keys[0]

        branchdistform = '({xy}{stem} - {xy}{branch})'
        branchform = 'moveSizeOf{hv}_b := {dist}'
        branchifform = 'if {maxdist} < moveSizeOf{hv}_b:\n\t{maxbranch};\nelseif {mindist} > moveSizeOf{hv}_b:\n\t{minbranch};\nfi\n\n'

        for branch, values in branchdict.items():
            stem = values.get('stem')
            double = values.get('double')
            if double is not None:
                if list(branchdict.keys()).index(double) != 0:
                    continue
                branch = [branch, double]
            else:
                branch = [branch]

            branchpairdict = getpairdict([branch[0]])
            branchpairs = list(branchpairdict.items())
            direction = getdirection([branchpairs[0][1], branchpairs[1][1]])
            branchbounds = getbounds(branch)
            stembounds = [getbounds([contour]) for contour in stem]
            stemvector = [getvector([bounds[: 2], bounds[2:]]) for bounds in stembounds]

            if abs(direction[0]) < abs(direction[1]):
                hv = 'H'
                xy = 'x'
                branchlimitpoints = [findpoint(branch, (branchbounds[0], None)), findpoint(branch, (branchbounds[2], None))]
                if len(stem) == 2:
                    stemindex = 0 if abs(stemvector[0][0]) > abs(stemvector[1][0]) else 1
                    stemlimitpoints = [findpoint(stem[stemindex], (stembounds[stemindex][0], None)), findpoint(stem[stemindex], (stembounds[stemindex][2], None))]
                else:
                    stembounds = stembounds[0]
                    stemlimitpoints = [findpoint(stem, (stembounds[0], None)), findpoint(stem, (stembounds[2], None))]
                limitvectors = [getvector([(stemlimitpoints[i].x, stemlimitpoints[i].y), (branchlimitpoints[i].x, branchlimitpoints[i].y)]) for i in range(len(stemlimitpoints))]
                limitindex = limitvectors.index(max(limitvectors, key=lambda x: abs(x[0])))
            else:
                hv = 'V'
                xy = 'y'
                branchlimitpoints = [findpoint(branch, (None, branchbounds[1])), findpoint(branch, (None, branchbounds[3]))]
                if len(stem) == 2:
                    stemindex = 0 if abs(stemvector[0][1]) > abs(stemvector[1][1]) else 1
                    stemlimitpoints = [findpoint(stem[stemindex], (None, stembounds[stemindex][1])), findpoint(stem[stemindex], (None, stembounds[stemindex][3]))]
                else:
                    stembounds = stembounds[0]
                    stemlimitpoints = [findpoint(stem, (None, stembounds[1])), findpoint(stem, (None, stembounds[3]))]
                limitvectors = [getvector([(stemlimitpoints[i].x, stemlimitpoints[i].y), (branchlimitpoints[i].x, branchlimitpoints[i].y)]) for i in range(len(stemlimitpoints))]
                limitindex = limitvectors.index(max(limitvectors, key=lambda x: abs(x[1])))

            stemlimitnames = [get_attr(stemlimitpoints[i], 'penPair') for i in range(len(stemlimitpoints))]
            branchlimitnames = [get_attr(branchlimitpoints[i], 'penPair') for i in range(len(branchlimitpoints))]
            branchdiststrs = [branchdistform.format(xy=xy, stem=stemlimitnames[i][1:], branch=branchlimitnames[i][1:]) for i in range(len(branchlimitnames))]
            branchdistopenstrs = [branchdistform.format(xy=xy,
                                                        stem=stemlimitnames[i][1:] + (' - penWidth_' if xy == 'x' else ' - penHeight_') + stemlimitnames[i][1: -1] + '_e_o',
                                                        branch=branchlimitnames[i][1:])
                                  for i in range(len(branchlimitnames))]
            branchstrs = [branchform.format(hv=hv, dist=branchdiststrs[i]) for i in range(len(branchdiststrs))]
            branchopenstrs = [branchform.format(hv=hv, dist=branchdistopenstrs[i]) for i in range(len(branchdistopenstrs))]
            branchifstr = branchifform.format(hv=hv, maxdist=branchdiststrs[1], maxbranch=branchstrs[1], mindist=branchdiststrs[0], minbranch=branchstrs[0])
            branchifopenstr = branchifform.format(hv=hv, maxdist=branchdistopenstrs[1], maxbranch=branchopenstrs[1], mindist=branchdistopenstrs[0], minbranch=branchopenstrs[0])

            if limitindex == 1:
                op = ''
            else:
                op = '-'

            fp.write('if (openUnfill = 1) and (isUnfill):\n')
            fp.write('\t' + branchopenstrs[limitindex].replace(':= ', ':= ' + op) + ' * branchRate;\n')
            fp.write('\t' + branchifopenstr)
            fp.write('else:\n')
            fp.write('\t' + branchstrs[limitindex].replace(':= ', ':= ' + op) + ' * branchRate;\n')
            fp.write('\t' + branchifstr)
            fp.write('fi\n')

        ################################################################################################################

        ################################################################################################################
        # shift points so moveSize

        movesize_form = "{xy}{pair}{lr}{curve_} := {xy}{pair}{lr}{curve_} + moveSizeOf{hv}_{double}{branchmove};{end}"
        fp.write('\n% Move points\n')
        for pair, pair_points in pairdict.items():
            for lr in pair_points.keys():
                curpoint = pair_points[lr]
                curcontour = curpoint.contour
                curpoints = curcontour.points
                double = get_attr(curpoints[0], 'double')
                double = double[0] if double is not None else ''

                branchh = ''
                branchv = ''
                if get_attr(curpoints[0], 'elem') == 'branch':
                    branchpairdict = getpairdict([curcontour])
                    branchpairs = list(branchpairdict.items())
                    direction = getdirection([branchpairs[0][1], branchpairs[1][1]])
                    if abs(direction[0]) < abs(direction[1]):
                        branchh = ' + moveSizeOfH_b'
                    else:
                        branchv = ' + moveSizeOfV_b'

                if curpoint.type == 'curve':
                    prepoint = curpoints[curpoint.index - 3]
                    prepair = get_attr(prepoint, 'penPair')[1: -1]
                    for num in range(1, 3):
                        fp.write(movesize_form.format(xy='x', pair=prepair, lr=lr, hv='H', end=' ', curve_=num, double=double, branchmove=branchh))
                        fp.write(movesize_form.format(xy='y', pair=prepair, lr=lr, hv='V', end='\n', curve_=num, double=double, branchmove=branchv))
                fp.write(movesize_form.format(xy='x', pair=pair, lr=lr, hv='H', end=' ', curve_='', double=double, branchmove=branchh))
                fp.write(movesize_form.format(xy='y', pair=pair, lr=lr, hv='V', end='\n', curve_='', double=double, branchmove=branchv))

        ################################################################################################################

        ################################################################################################################
        # convert round points

        if existRound:
            fp.write('\n% round point\n')
            fp.write('if curveRate > 0.0:\n')

            numPoints = len(pointOrder)
            startIdx = 0
            endIdx = 0
            for i in range(numPoints):
                curIdx = pointOrder[i]
                curPoint = points[curIdx]

                if curPoint.startP != '':
                    startIdx = curIdx
                    for j in range(i + 1, numPoints):
                        if points[pointOrder[j]].endP != '':
                            endIdx = pointOrder[j]
                            break

                if curPoint.roundA == "":
                    continue

                preIdx = pointOrder[(i - 1 + numPoints) % numPoints]
                nextIdx = pointOrder[(i + 1) % numPoints]

                if curIdx == startIdx:
                    preIdx = endIdx
                elif curIdx == endIdx:
                    nextIdx = startIdx

                prePoint = points[preIdx]
                nextPoint = points[nextIdx]

                if curIdx % 2 == 0:
                    pairIdx = curIdx - 1
                    pairPoint = points[pairIdx]
                else:
                    pairIdx = curIdx + 1
                    pairPoint = points[pairIdx]

                dists = []
                dists.append(float(prePoint.x) - float(curPoint.x))
                dists.append(float(prePoint.y) - float(curPoint.y))
                dists.append(float(nextPoint.x) - float(curPoint.x))
                dists.append(float(nextPoint.y) - float(curPoint.y))

                op = []
                zeroDist = []
                for j in range(len(dists)):
                    if dists[j] < 0:
                        op.append('-')
                    else:
                        op.append('+')
                    zeroDist.append(math.isclose(dists[j], 0))

                # if float(prePoint.x) - float(curPoint.x) < 0:
                #   op.append('-')
                # else:
                #   op.append('+')
                # if float(prePoint.y) - float(curPoint.y) < 0:
                #   op.append('-')
                # else:
                #   op.append('+')
                # if float(nextPoint.x) - float(curPoint.x) < 0:
                #   op.append('-')
                # else:
                #   op.append('+')
                # if float(nextPoint.y) - float(curPoint.y) < 0:
                #   op.append('-')
                # else:
                #   op.append('+')

                pointName = curPoint.name[1:]
                nameForm = '%s' + pointName[:-1] + '_R%d' + pointName[-1] + ' := %s' + pointName
                distForm1 = 'abs(%s' + pointName[:-1] + 'l - %s' + pointName[:-1] + 'r)'
                distForm2 = 'max(' + distForm1 % ('x', 'x') + ', ' + distForm1 % ('y', 'y') + ")"
                curveRate = '/ 2 * curveRate'
                bcpRate = '* 0.45'
                distParam = [None for i in range(4)]
                roundP = []
                roundBcp = []

                if pairIdx == preIdx:
                    distParam[0] = distParam[3] = ('x', 'x')
                    distParam[1] = distParam[2] = ('y', 'y')
                    for j in range(4):
                        roundP.append(' ' + op[j] + ' ' + distForm1 % distParam[j] + ' ' + curveRate)
                        roundBcp.append(roundP[-1] + ' ' + bcpRate)
                elif pairIdx == nextIdx:
                    distParam[0] = distParam[3] = ('y', 'y')
                    distParam[1] = distParam[2] = ('x', 'x')
                    for j in range(4):
                        roundP.append(' ' + op[j] + ' ' + distForm1 % distParam[j] + ' ' + curveRate)
                        roundBcp.append(roundP[-1] + ' ' + bcpRate)
                else:
                    for j in range(4):
                        if zeroDist[j]:
                            roundP.append('')
                            roundBcp.append('')
                        else:
                            roundP.append(' ' + op[j] + ' ' + distForm2 + ' ' + curveRate)
                            roundBcp.append(roundP[-1] + ' ' + bcpRate)

                fp.write(
                    '\t' + nameForm % ('x', 0, 'x') + roundP[0] + ';\n\t' + nameForm % ('y', 0, 'y') + roundP[
                        1] + ';\n')
                fp.write(
                    '\t' + nameForm % ('x', 1, 'x') + roundBcp[0] + ';\n\t' + nameForm % ('y', 1, 'y') + roundBcp[
                        1] + ';\n')
                fp.write(
                    '\t' + nameForm % ('x', 2, 'x') + roundBcp[2] + ';\n\t' + nameForm % ('y', 2, 'y') + roundBcp[
                        3] + ';\n')
                fp.write(
                    '\t' + nameForm % ('x', 3, 'x') + roundP[2] + ';\n\t' + nameForm % ('y', 3, 'y') + roundP[
                        3] + ';\n')

            fp.write('fi\n')

        ################################################################################################################

        ################################################################################################################
        # scale points

        wh_form = "{xy}{pair}{round_}{lr}{curve_} := {xy}{pair}{round_}{lr}{curve_} * {hw};{end}"
        fp.write("\n% Resize glyph\n")
        for pair, pair_points in pairdict.items():
            for lr in pair_points.keys():
                curpoint = pair_points[lr]
                if curpoint.type == 'curve':
                    curpoints = curpoint.contour.points
                    prepoint = curpoints[curpoint.index - 3]
                    prepair = get_attr(prepoint, 'penPair')[1: -1]
                    for num in range(1, 3):
                        fp.write(wh_form.format(xy='x', round_='', pair=prepair, lr=lr, hw='Width', end='', curve_=num))
                        fp.write(wh_form.format(xy='y', round_='', pair=prepair, lr=lr, hw='Height', end='\n', curve_=num))
                fp.write(wh_form.format(xy='x', round_='', pair=pair, lr=lr, hw='Width', end=' ', curve_=''))
                fp.write(wh_form.format(xy='y', round_='', pair=pair, lr=lr, hw='Height', end='\n', curve_=''))

        # For round points
        fp.write('\nif curveRate > 0.0:\n')
        for rcontour in rglyph.contours:
            for rpoint in rcontour.points:
                if rpoint.type == 'offcurve':
                    continue
                attr_dict = name2dict(rpoint.name)
                if attr_dict.get('round') is not None:
                    penpair = attr_dict.get('penPair')
                    pair = penpair[1:-1]
                    lr = penpair[-1]
                    for i in range(4):
                        round_ = '_R' + str(i)
                        fp.write('\t' + wh_form.format(
                            xy='x', round_=round_, pair=pair, lr=lr, hw='Width', end='', curve_=''))
                        fp.write(wh_form.format(
                            xy='y', round_=round_, pair=pair, lr=lr, hw='Height', end='\n', curve_=''))
        fp.write('fi\n')

        ################################################################################################################

        #####################################################################################################################################
        # convert path of points to METAFONT

        fp.write("\n% Get draw \n");
        fp.write("if isUnfill:\n");
        fp.write("\tindex := 2;\n");
        fp.write("else:\n");
        fp.write("\tindex := 0;\n");
        fp.write("fi\n");

        source = ""
        sourceR = ""
        dash = ""
        startIdx = 0
        serifList = []
        for i in range(0, len(pointOrder)):
            # source += '\t'
            # sourceR += '\t'

            idx = pointOrder[i]

            if i + 1 != len(pointOrder) and points[pointOrder[i + 1]].startP == "":
                nextIdx = pointOrder[i + 1]
            else:
                nextIdx = startIdx

            if idx % 2 == 0:
                pairIdx = idx - 1
            else:
                pairIdx = idx + 1

            if points[idx].startP != "":
                startIdx = idx
                if points[idx].startP == "fill":
                    source = 'if isUnfill:\n\tunfill\nelse:\n\tfill\nfi\n'
                    sourceR = 'if isUnfill:\n\tunfill\nelse:\n\tfill\nfi\n'
                else:
                    source = 'if isUnfill:\n\tfill\nelse:\n\tunfill\nfi\n'
                    sourceR = 'if isUnfill:\n\tfill\nelse:\n\tunfill\nfi\n'
            # else:
            #   source = ""

            # source += points[pointOrder[i]].name
            dash = " .. "

            if points[idx].roundA != '':
                if points[idx].serif == '1' or points[idx].serif == '2':
                    serifList.append(idx)
                    sourceR += 'if serifRate > 0.0:\n'
                    sourceR += '\t' + points[idx].name + '\n'
                    sourceR += 'else:\n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R0' + points[idx].name[-1] + ' .. controls (' + points[
                                                                                                                    idx].name[
                                                                                                                :-1] + '_R1' + \
                               points[idx].name[-1] + ') and (' + points[idx].name[:-1] + '_R2' + points[idx].name[
                                   -1] + ') .. \n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R3' + points[idx].name[-1] + '\n'
                    sourceR += 'fi\n'
                    source += points[idx].name
                elif points[pairIdx].serif == '1' or points[pairIdx].serif == '2':
                    sourceR += 'if serifRate > 0.0:\n'
                    sourceR += '\tz%d_R0r .. controls (z%d_R1r) and (z%d_R2r) ..\n\tz%d_R3r --\n' % (
                    int(points[pairIdx].serif) * 10 + 191, int(points[pairIdx].serif) * 10 + 191,
                    int(points[pairIdx].serif) * 10 + 191, int(points[pairIdx].serif) * 10 + 191)
                    sourceR += '\tz%d_R0r .. controls (z%d_R1r) and (z%d_R2r) ..\n\tz%d_R3r --\n' % (
                    int(points[pairIdx].serif) * 10 + 192, int(points[pairIdx].serif) * 10 + 192,
                    int(points[pairIdx].serif) * 10 + 192, int(points[pairIdx].serif) * 10 + 192)
                    sourceR += '\tz%d_R0l .. controls (z%d_R1l) and (z%d_R2l) ..\n\tz%d_R3l\n' % (
                    int(points[pairIdx].serif) * 10 + 192, int(points[pairIdx].serif) * 10 + 192,
                    int(points[pairIdx].serif) * 10 + 192, int(points[pairIdx].serif) * 10 + 192)
                    sourceR += 'else:\n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R0' + points[idx].name[-1] + ' .. controls ('\
                               + points[idx].name[:-1] + '_R1' + points[idx].name[-1] + ') and ('\
                               + points[idx].name[:-1] + '_R2' + points[idx].name[-1] + ') .. \n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R3' + points[idx].name[-1] + '\n'
                    sourceR += 'fi\n'
                    source += 'if serifRate > 0.0:\n\tz%dr --\n\tz%dr --\n\tz%dl\n' % (
                    int(points[pairIdx].serif) * 10 + 191, int(points[pairIdx].serif) * 10 + 192,
                    int(points[pairIdx].serif) * 10 + 192)
                    source += 'else:\n\t' + points[idx].name + '\nfi\n'
                else:
                    sourceR += points[idx].name[:-1] + '_R0' + points[idx].name[-1] + ' .. controls ('\
                               + points[idx].name[:-1] + '_R1' + points[idx].name[-1] + ') and ('\
                               + points[idx].name[:-1] + '_R2' + points[idx].name[-1] + ') .. \n'
                    sourceR += '\t' + points[idx].name[:-1] + '_R3' + points[idx].name[-1]
                    source += points[idx].name
            else:
                if points[idx].serif == '1' or points[idx].serif == '2':
                    serifList.append(idx)
                    sourceR += 'if serifRate > 0.0:\n'
                    sourceR += '\t' + points[idx].name + '\n'
                    sourceR += 'else:\n'
                    sourceR += '\t' + points[idx].name + '\n'
                    sourceR += 'fi\n'
                    source += points[idx].name
                elif points[pairIdx].serif == '1' or points[pairIdx].serif == '2':
                    sourceR += 'if serifRate > 0.0:\n'
                    sourceR += '\tz%d_R0r .. controls (z%d_R1r) and (z%d_R2r) ..\n\tz%d_R3r --\n' % (
                    int(points[pairIdx].serif) * 10 + 191, int(points[pairIdx].serif) * 10 + 191,
                    int(points[pairIdx].serif) * 10 + 191, int(points[pairIdx].serif) * 10 + 191)
                    sourceR += '\tz%d_R0r .. controls (z%d_R1r) and (z%d_R2r) ..\n\tz%d_R3r --\n' % (
                    int(points[pairIdx].serif) * 10 + 192, int(points[pairIdx].serif) * 10 + 192,
                    int(points[pairIdx].serif) * 10 + 192, int(points[pairIdx].serif) * 10 + 192)
                    sourceR += '\tz%d_R0l .. controls (z%d_R1l) and (z%d_R2l) ..\n\tz%d_R3l\n' % (
                    int(points[pairIdx].serif) * 10 + 192, int(points[pairIdx].serif) * 10 + 192,
                    int(points[pairIdx].serif) * 10 + 192, int(points[pairIdx].serif) * 10 + 192)
                    sourceR += 'else:\n'
                    sourceR += '\t' + points[idx].name + '\n'
                    sourceR += 'fi\n'
                    source += 'if serifRate > 0.0:\n\tz%dr --\n\tz%dr --\n\tz%dl\n' % (
                    int(points[pairIdx].serif) * 10 + 191, int(points[pairIdx].serif) * 10 + 192,
                    int(points[pairIdx].serif) * 10 + 192)
                    source += 'else:\n\t' + points[idx].name + '\nfi\n'
                else:
                    sourceR += points[idx].name
                    source += points[idx].name

            if points[nextIdx].type == "line":
                dash = " -- "
            elif points[nextIdx].type == "None":
                dash = " .. "
            elif points[nextIdx].type == "curve":
                dash = " .. "
                dash = dash + "controls (z" + points[idx].name[1:] + "1) and (z" + points[idx].name[1:] + "2) .. "
            elif points[nextIdx].type == "qcurve":
                dash = " .. "
                controlPoints = points[idx].controlPoints
                for j in range(0, len(controlPoints)):
                    if j == 0:
                        QP0 = points[idx].name
                    else:
                        QP0 = QP2

                    QP1 = points[idx].name + str(j + 1)
                    if j != len(controlPoints) - 1:
                        newX = "(x" + points[idx].name[1:] + str(j + 1) + " + x" + points[idx].name[1:] + str(
                            j + 2) + ") / 2"
                        newY = "(y" + points[idx].name[1:] + str(j + 1) + " + y" + points[idx].name[1:] + str(
                            j + 2) + ") / 2"
                        QP2 = "(" + newX + ", " + newY + ")"
                    else:
                        QP2 = points[nextIdx].name

                    CP1 = QP0 + " + 2 / 3 * (" + QP1 + " - " + QP0 + ")"
                    CP2 = QP2 + " + 2 / 3 * (" + QP1 + " - " + QP2 + ")"
                    dash = dash + "controls (" + CP1 + ") and (" + CP2 + ") .. "

                    if j != len(controlPoints) - 1:
                        dash = dash + QP2 + " .. "

            source = source + dash + '\n'
            sourceR = sourceR + dash + '\n'

            if points[idx].endP != "":
                source += "cycle;\n"
                sourceR += "cycle;\n"
                serifStr = ''
                if len(serifList) > 0:
                    serifStr += 'if serifRate > 0.0:\n'
                    for serifIdx in serifList:
                        if serifIdx % 2 != 0:
                            serifpairIdx = serifIdx + 1
                        else:
                            serifpairIdx = serifIdx - 1
                        lserifpoint = points[serifIdx] if float(points[serifIdx].x) < float(points[serifpairIdx].x) else points[serifpairIdx]
                        rserifpoint = points[serifIdx] if float(points[serifIdx].x) >= float(points[serifpairIdx].x) else points[serifpairIdx]
                        serifStr += '\tserif_'
                        for serifNum in range(int(points[serifIdx].serif)):
                            serifStr += 'i'
                        serifStr += '(%0.3f, %0.3f, ' %(float(lserifpoint.x), float(lserifpoint.y))
                        serifStr += '%0.3f, %0.3f, ' %(float(rserifpoint.x), float(rserifpoint.y))
                        serifStr += 'Width, Height, moveSizeOfH, moveSizeOfV, penWidthRate, penHeightRate, curveRate, serifRate, branchRate, unfillRate, isUnfill, openUnfill);\n'
                        serifStr += '\ty' + points[serifIdx].name[1:] + ' := y%dl;\n' % (
                                    int(points[serifIdx].serif) * 10 + 192)
                    serifStr += 'fi\n'
                forStr = 'for x = 0 upto index:\n'
                if existRound:
                    forStr += '\tif curveRate > 0.0:\n'
                    forStr += '\t\t' + sourceR.replace('\n', '\n\t\t')[: -2]
                    forStr += '\telse:\n'
                    forStr += '\t\t' + source.replace('\n', '\n\t\t')[: -2]
                    forStr += '\tfi\n'
                else:
                    forStr += '\t' + source.replace('\n', '\n\t\t')[: -2]
                forStr += 'endfor\n'
                fp.write(serifStr)
                fp.write(forStr)
                serifList = []
            # fp.write(source + "\n")
        # source += '\tcycle;\n'
        # sourceR += '\tcycle;\n'

        # ifIsUnfill_unfill = "\t\tif isUnfill:\n\t\t\tunfill\n\t\telse:\n\t\t\tfill\n\t\tfi\n"
        # ifIsUnfill_fill = "\t\tif isUnfill:\n\t\t\tfill\n\t\telse:\n\t\t\tunfill\n\t\tfi\n"

        # fp.write("for x = 0 upto index:\n")
        # if existRound:
        #     fp.write('\tif curveRate > 0.0:\n')
        #     for line in sourceR.split('\n'):
        #         if line.strip().split(' ')[0] == "fill":
        #             fp.write(ifIsUnfill_unfill)
        #             fp.write('\t\t' + line.replace("fill", "") + '\n')
        #         elif line.strip().split(' ')[0] == "unfill":
        #             fp.write(ifIsUnfill_fill)
        #             fp.write('\t\t' + line.replace("unfill", "") + '\n')
        #         else:
        #             fp.write('\t\t' + line.strip() + '\n')
        #     #fp.write(sourceR)

        #     fp.write('\telse:\n')
        #     for line in source.split('\n'):
        #         if line.strip().split(' ')[0] == "fill":
        #             fp.write(ifIsUnfill_unfill)
        #             fp.write('\t\t' + line.replace("fill", "") + '\n')
        #         elif line.strip().split(' ')[0] == "unfill":
        #             fp.write(ifIsUnfill_fill)
        #             fp.write('\t\t' + line.replace("unfill", "") + '\n')
        #         else:
        #             fp.write('\t\t' + line.strip() + '\n')
        #     #fp.write(source)
        #     fp.write('\tfi\n')
        # else:
        #     fp.write(source)
        # fp.write("endfor\n")

        ################################################################################################################

        ################################################################################################################
        # Set serif attribute (current no use)

        for i in range(0, len(points)):
            if points[i].serif == "1":  # !!!!!!!!!!!!!!!
                idx = points[i].name[1:-1]
                # fp.write('if serifRate > 0.0:\n')
                # fp.write("\tserif_i(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, serifRate, penHeightRate / penWidthRate, curveRate, unfillRate, isUnfill);\n")
                # fp.write('fi\n')
            elif points[i].serif == "2":
                idx = points[i].name[1:-1]
                # fp.write('if serifRate > 0.0:\n')
                # fp.write("\tserif_ii(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, serifRate, penHeightRate / penWidthRate, curveRate, unfillRate, isUnfill);\n")
                # fp.write('fi\n')
            # end serif test by ghj (1710A) /w glyphs.mf UFO2mf.py  xmltomf.py
            elif points[i].serif == "3":
                idx = points[i].name[1:-1]
                fp.write('if serifRate > 0.0:\n')
                fp.write("\tserif_iii(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, curveRate);\n")
                fp.write('fi\n')
            # end serif test by ghj (1710A) /w glyphs.mf UFO2mf.py  xmltomf.py
            elif points[i].serif == "4":
                idx = points[i].name[1:-1]
                fp.write('if serifRate > 0.0:\n')
                fp.write("\tserif_iv(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, curveRate);\n")
                fp.write('fi\n')
            elif points[i].serif == "5":
                idx = points[i].name[1:-1]
                fp.write('if serifRate > 0.0:\n')
                fp.write("\tserif_v(x" + idx + "l, y" + idx + "l, x" + idx + "r, y" + idx + "r, curveRate);\n")
                fp.write('fi\n')

        ##########################################################################################################
        # last

        fp.write("\n% pen labels\n");
        fp.write("penlabels(range 1 thru %d);\n" % totalNum);
        fp.write("enddef;\n\n");

        fp.close()

    ####################################################################################################################
    return None

# get width of font
def get_font_width(DIR_UFO, glifs):
    width_dict = {}

    for glif in glifs:
        glif = os.path.join(DIR_UFO, glif)
        glif_data = minidom.parse(glif)
        components = glif_data.getElementsByTagName('component')

        if len(components) != 0:
            advance = glif_data.getElementsByTagName('advance')
            width = advance[0].getAttribute('width')
            if width in width_dict:
                width_dict[width] += 1
            else:
                width_dict[width] = 1

    font_width = max(width_dict.keys(), key=(lambda k: width_dict[k]))

    return float(font_width)

# get font object of fontParts
def getfontobject(DIR_UFO):
    return OpenFont(DIR_UFO)

# get glyph object in font object of fontParts
def getglyphobject(glyph, rfont):
    glyph = os.path.splitext(glyph)[0]
    return rfont[glyph]

# get pair dictionary from contour objects of fontParts
def getpairdict(rcontours):
    pairdict = {}

    for rcontour in rcontours:
        for rseg in rcontour:
            point = rseg.onCurve
            attr = Attribute(point)
            penpair = attr.get_attr('penPair')

            if not penpair[1: -1] in pairdict:
                pairdict[penpair[1: -1]] = {}
            pairdict[penpair[1: -1]][penpair[-1]] = point

    return pairdict

# find point object being some coordinates from contour objects of fontParts
def findpoint(rcontours, coord):
    point = None
    x = coord[0]
    y = coord[1]

    for rcontour in rcontours:
        for rpoint in rcontour.points:
            if rpoint.type == 'offcurve':
                continue
            if x is not None and y is not None:
                if rpoint.x == x and rpoint.y == y:
                    point = rpoint
            elif x is not None:
                if rpoint.x == x:
                    point = rpoint
            elif y is not None:
                if rpoint.y == y:
                    point = rpoint

    return point

# get bounds from contour objects of fontParts
def getbounds(rcontours):
    newglyph = rcontours[0].glyph.copy()
    newglyph.clearContours()
    for rcontour in rcontours:
        newglyph.appendContour(rcontour)

    return newglyph.bounds

# get middle point coordinates of 2 points
def getmidcoord(points):
    dist = getvector(points)
    mid = (points[0][0] + dist[0] / 2, points[0][1] + dist[1] / 2)
    return mid

# get vector of 2 points
def getvector(points, reverse=False):
    vector = (points[0][0] - points[1][0], points[0][1] - points[1][1])
    return (-vector[0], -vector[1]) if reverse else vector

# get direction of stroke
def getdirection(pairs):
    mids = []
    for pair in pairs:
        mids.append(getmidcoord([(pair['l'].x, pair['l'].y), (pair['r'].x, pair['r'].y)]))

    return getvector(mids)

if __name__ == '__main__':
    ufo2mf('../../..', 'YullyeoM.ufo')
