# -*- coding: utf-8 -*-
from fontTools.misc.bezierTools import splitCubic, splitCubicAtT, splitLine

# 곡선을 x 혹은 y 값을 기준으로 나누어 점을 추가하는 함수
# parameter
# contour - contour object (robofont에서 사용하는 contour object인 RContour)
# Rpoints - list of point object (robofont에서 사용하는 point object인 RPoint의 list
# [곡선의 시작점, 보조점, 보조점, 곡선의 끝점] 순으로 구성 필요, 곡선의 시작점은 contour의 방향상 가장 먼저 나오는 점)
# where - x or y coordinate (나눌 기준이 될 x 혹은 y 값)
# isHorizeontal - True or False (where이 x 값이면 False, y 값이면 True)
def appendPointCoordinate(contour, Rpoints, where, isHorizeontal):
	points = Rpoint2Tpoint(Rpoints)
	newCurve = splitCubic(points[0], points[1], points[2], points[3], where, isHorizeontal)

	if len(newCurve)<2:
		return -1

	if appendPointCurve(contour, Rpoints, newCurve):
		return -1

	return 1

# 곡선을 비율로 나누어 점을 추가하는 함수
# parameter
# contour - contour object (robofont에서 사용하는 contour object인 RContour)
# Rpoints - list of point object (robofont에서 사용하는 point object인 RPoint의 list
# [곡선의 시작점, 보조점, 보조점, 곡선의 끝점] 순으로 구성 필요, 곡선의 시작점은 contour의 방향상 가장 먼저 나오는 점)
# rate - 0.x (나눌 비율)
def appendPointRate(contour, Rpoints, rate):
	points = Rpoint2Tpoint(Rpoints)
	newCurve = splitCubicAtT(points[0], points[1], points[2], points[3], rate)

	if len(newCurve)<2:
		return -1

	if appendPointCurve(contour, Rpoints, newCurve)<0:
		return -1

	return 1

def appendPointCurve(contour, Rpoints, curve):
	segmentIndex = segmentIndexOf(contour, Rpoints[3])
	if segmentIndex<0:
		return -1

	changePoint(contour[segmentIndex].offCurve[0], curve[1][1])
	changePoint(contour[segmentIndex].offCurve[1], curve[1][2])

	contour.insertSegment(segmentIndex, 'curve', list(curve[0][1:]))

	contour.round()

	return 1

# 직선을 x 혹은 y 값을 기준으로 나누어 점을 추가하는 함수
# contour - contour object (robofont에서 사용하는 contour object인 RContour)
# Rpoints - list of point object (robofont에서 사용하는 point object인 RPoint의 list
# [직선의 시작점, 직선의 끝점] 순으로 구성 필요, 직선의 시작점은 contour의 방향상 가장 먼저 나오는 점)
# where - x or y coordinate (나눌 기준이 될 x 혹은 y 값)
# isHorizeontal - True or False (where이 x 값이면 False, y 값이면 True)
def appendPointLine(contour, Rpoints, where, isHorizeontal):
	points = Rpoint2Tpoint(Rpoints)
	newLine = splitLine(points[0], points[1], where, isHorizeontal)

	if len(newLine)<2:
		return -1

	segmentIndex = segmentIndexOf(contour, Rpoints[1])
	if segmentIndex<0:
		return -1

	contour.insertSegment(segmentIndex, 'line', [newLine[0][1]])

	contour.round()

	return 1

# 직선을 비율로 나누어 점을 추가하는 함수
# parameter
# contour - contour object (robofont에서 사용하는 contour object인 RContour)
# Rpoints - list of point object (robofont에서 사용하는 point object인 RPoint의 list
# [직선의 시작점, 직선의 끝점] 순으로 구성 필요, 직선의 시작점은 contour의 방향상 가장 먼저 나오는 점)
# rate - 0.x (나눌 비율)
def appendPointRateLine(contour, Rpoints, rate):
	if Rpoints[0].x == Rpoints[1].x:
		appendPointLine(contour, Rpoints, subdivide(Rpoints[0], Rpoints[1], rate)[1], True)
	elif Rpoints[0].y == Rpoints[1].y:
		appendPointLine(contour, Rpoints, subdivide(Rpoints[0], Rpoints[1], rate)[0], False)
	else:
		appendPointLine(contour, Rpoints, subdivide(Rpoints[0], Rpoints[1], rate)[1], True)

	return 1

# RPoint a, b를 rate의 비율로 내분해주는 함수
# 리턴 값은 리스트 형으로 된 내분점의 좌표 ex) [100, 200]
def subdivide(a, b, rate):
    s = 1 - rate
    return list(map(lambda x: int(round(x)), [b.x*rate + a.x*s, b.y*rate + a.y*s]))

def segmentIndexOf(contour, Rpoint):
	for index in range(0, len(contour)):
		if contour[index].onCurve.x==Rpoint.x and contour[index].onCurve.y==Rpoint.y:
			return index

	return -1

def changePoint(Rpoint, point):
	Rpoint.x = point[0]
	Rpoint.y = point[1]

	return

def Rpoint2Tpoint(points):
	Tpoint = []

	for point in points:
		Tpoint.append((point.x, point.y))

	return Tpoint