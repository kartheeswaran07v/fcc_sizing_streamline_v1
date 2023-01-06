import math

ACCURACY = 0.001

Cv_1 = [0, 1688, 2531.3, 2742.188, 2847.656, 2953.125, 3375, 6750]
FL_1 = [0.85, 0.713, 0.645, 0.627, 0.619, 0.61, 0.576, 0.54]

# Cv1 = [0, 17.2, 50.2, 87.8, 146, 206, 285, 365, 465, 521, 1000]
# FL1 = [0.85, 0.85, 0.84, 0.79, 0.75, 0.71, 0.63, 0.58, 0.56, 0.54, 0.54]

Cv_globe_4 = [17, 24, 34, 47, 65, 88, 134, 166, 187, 201, 20000000]
Fl_globle_4 = [0.93, 0.9275, 0.92, 0.91, 0.905, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]

Cv_butterfly_6 = [56, 126, 204, 306, 425, 556, 671, 717, 698, 200000]
Fl_butterfly_6 = [0.97, 0.95, 0.92, 0.9, 0.88, 0.83, 0.79, 0.72, 0.7, 0.67]

Opening = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 100]

Cv1 = Cv_butterfly_6
FL1 = Fl_butterfly_6


def Sign(x):
    if x >= 0:
        return 1
    else:
        return -1


def getFL(C):
    a = 0
    while True:
        # print(f"Cv1, C: {Cv1[a], C}")
        if Cv1[a] == C:
            return FL1[a]
        elif Cv1[a] > C:
            break
        else:
            a += 1

    Fllll = FL1[a - 1] - (((Cv1[a - 1] - C) / (Cv1[a - 1] - Cv1[a])) * (FL1[a - 1] - FL1[a]))

    return round(Fllll, 3)


def getPercentageOpening(C):
    a = 0
    while True:
        if Cv1[a] == C:
            return Opening[a]
        elif Cv1[a] > C:
            break
        else:
            a += 1

    Fllll = Opening[a - 1] - (((Cv1[a - 1] - C) / (Cv1[a - 1] - Cv1[a])) * (Opening[a - 1] - Opening[a]))

    return round(Fllll, 3)


def etaB(valveDia, pipeDia):
    return 1 - ((valveDia / pipeDia) ** 4)


def eta1(valveDia, pipeDia):
    return 0.5 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)


def eta2(valveDia, pipeDia):
    return 1 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)


def sigmaEta(valveDia, inletDia, outletDia):
    return eta1(valveDia, inletDia) + eta2(valveDia, outletDia) + etaB(valveDia, inletDia) - etaB(valveDia, outletDia)


def fP(C, valveDia, inletDia, outletDia):
    a = (sigmaEta(valveDia, inletDia, outletDia) / 0.00214) * ((C / valveDia ** 2) ** 2)
    return 1 / math.sqrt(1 + a)


def fLP(C, valveDia, inletDia):
    FL_input = getFL(C)
    a = (FL_input * FL_input / 0.00214) * (eta1(valveDia, inletDia) + etaB(valveDia, inletDia)) * (
            (C / (valveDia * valveDia)) ** 2)
    return FL_input / (math.sqrt(1 + a))


def fF(vaporPressure, criticalPressure):
    return 0.96 - (0.28 * (math.sqrt(vaporPressure / criticalPressure)))


def chokedPressure(inletPressure, vaporPressure, criticalPressure, C, valveDia, inletDia, outletDia):
    return ((fLP(C, valveDia, inletDia) / fP(C, valveDia, inletDia, outletDia)) ** 2) * (
            inletPressure - fF(vaporPressure, criticalPressure) * vaporPressure)


def sizingP(inletPressure, outletPressure, vaporPressure, criticalPressure, C, valveDia, inletDia, outletDia):
    return min((inletPressure - outletPressure),
               chokedPressure(inletPressure, vaporPressure, criticalPressure, C, valveDia, inletDia, outletDia))


def cUpper(valveDia):
    return 0.075 * valveDia * valveDia * 1


def flowFunction(inletPressure, outletPressure, vaporPressure, criticalPressure, C, valveDia, inletDia, outletDia,
                 flowRate, specificGravity):
    return flowRate - C * 0.865 * fP(C, valveDia, inletDia, outletDia) * (math.sqrt(
        sizingP(inletPressure, outletPressure, vaporPressure, criticalPressure, C, valveDia, inletDia,
                outletDia) / specificGravity))


# print( flowFunction(inletPressure=6.7, outletPressure=6.676, vaporPressure=0.1, criticalPressure=100, C=6750,
# valveDia=200, inletDia=300, outletDia=275))


# final formulae

def findCv(dia):
    C_Upper = cUpper(dia)
    C_Lower = 0
    while True:

        FCUpper = flowFunction(inletPressure=3550, outletPressure=2240, vaporPressure=4, criticalPressure=22120,
                               C=C_Upper, valveDia=dia,
                               inletDia=154.1, outletDia=202.7, flowRate=400, specificGravity=0.780)
        FCLower = flowFunction(inletPressure=3550, outletPressure=2240, vaporPressure=4, criticalPressure=22120,
                               C=C_Lower, valveDia=dia,
                               inletDia=154.1, outletDia=202.7, flowRate=400, specificGravity=0.780)
        C_Mid = (C_Upper + C_Lower) / 2
        FCMid = flowFunction(inletPressure=3550, outletPressure=2240, vaporPressure=4, criticalPressure=22120,
                             C=C_Mid, valveDia=dia,
                             inletDia=154.1, outletDia=202.7, flowRate=400, specificGravity=0.780)
        if Sign(FCMid) != Sign(FCUpper):
            print(f"FCMid: {FCMid}, FCUpper: {FCUpper}, CUpper: {C_Upper}, CMid: {C_Mid}")
            if abs(C_Upper - C_Mid) <= ACCURACY:
                return C_Mid
            else:
                C_Lower = C_Mid
                C_Upper = C_Upper
        elif Sign(FCLower) != Sign(FCMid):
            print(f"FCMid: {FCMid}, FCLower: {FCLower}, CLower: {C_Lower}, CMid: {C_Mid}")
            if abs(C_Lower - C_Mid) <= ACCURACY:
                return C_Mid
            else:
                C_Upper = C_Mid
                C_Lower = C_Lower
        else:
            return "Wrong dia"
