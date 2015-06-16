from __future__ import division
from random import randint, choice
import numpy as np
import sys
from math import modf
import decimal

limit = 0.5

def coord(d):
    return float(np.random.uniform(0.05*d, 0.8*d))


def GetRAD(vector):
    RAD = []
    unique = list(set(vector))
    for val in unique:
        RAD.append(vector.count(val)) # the abundance of each species

    return RAD, unique # the rad and the species list


def get_color(ID, color_dict): # FUNCTION TO ASSIGN COLORS TO SPECIES

    r1 = lambda: randint(0,255)
    r2 = lambda: randint(0,255)
    r3 = lambda: randint(0,255)

    color = '#%02X%02X%02X' % (r1(),r2(),r3())
    color_dict[ID] = color

    return color_dict



def NewTracers(IDs, coords, TimeIn, width, height, length, u0, D):

    Xcoords, Ycoords, Zcoords = coords
    x = np.random.binomial(1, u0)

    if x == 1:
        TimeIn.append(0)

        y = coord(height)
        Ycoords.append(y)

        x = coord(width)
        Xcoords.append(x)

        IDs.append(0) # used to track the age of the tracer

        if D == 3:
            z = coord(length)
            Zcoords.append(z)

    coords = [Xcoords, Ycoords, Zcoords]
    return [IDs, TimeIn, coords]



def ResIn(Type, Vals, coords, ID, IDs, TimeIn, numr, rmax, nr, width, height, length, u0, D):

    Xcoords, Ycoords, Zcoords = coords
    for r in range(numr):
        x = np.random.binomial(1, u0)

        if x == 1:
            rval = int(np.random.random_integers(1, rmax, 1))
            rtype = int(np.random.random_integers(0, nr-1, 1))

            Vals.append(rval)
            IDs.append(ID)
            Type.append(rtype)
            TimeIn.append(0)
            ID += 1

            y = coord(height)
            Ycoords.append(y)

            x = coord(width)
            Xcoords.append(x)

            if D == 3:
                z = coord(length)
                Zcoords.append(z)

    coords = [Xcoords, Ycoords, Zcoords]
    return [Type, Vals, coords, IDs, ID, TimeIn]



def immigration(numin, Species, coords, width, height, length, MaintDict, GrowthDict, DispDict, color_dict, IDs, ID, TimeIn, Qs, ResUseDict, nr, u0, alpha, D):

    Xcoords, Ycoords, Zcoords = coords
    for m in range(numin):
        x = np.random.binomial(1, u0)

        if x == 1:
            prop = str(float(np.random.logseries(0.999, 1)))

            Species.append(prop)

            y = coord(height)
            Ycoords.append(y)

            x = coord(width)
            Xcoords.append(x)

            if D == 3:
                z = coord(length)
                Zcoords.append(z)

            IDs.append(ID)
            TimeIn.append(0)
            ID += 1
            Q = float(np.random.uniform(0.1, 1.0))
            Qs.append(Q)

            if prop not in color_dict:
                # species color
                color_dict = get_color(prop, color_dict)

                # species growth rate
                GrowthDict[prop] = np.random.uniform(0.1, 1.0)

                # species maintenance
                MaintDict[prop] = np.random.uniform(0.001, 0.01)

                # species active dispersal rate
                DispDict[prop] = np.random.uniform(0.0, 0.1)

                # species resource use efficiency
                ResUseDict[prop] = np.random.uniform(0.1, 1.0, nr)

    coords = [Xcoords, Ycoords, Zcoords]
    return [Species, coords, MaintDict, GrowthDict, DispDict, color_dict, IDs, ID, TimeIn, Qs, ResUseDict]


def fluid_movement(TypeOf, List, TimeIn, ExitAge, Xcoords, Ycoords, ux, uy, width, height, u0):

    Type, IDs, ID, Vals = [], [], int(), []

    if TypeOf == 'resource' or TypeOf == 'individual': Type, IDs, ID, Vals = List
    else: IDs = List

    if Xcoords == []:
        if TypeOf == 'resource' or TypeOf == 'individual':
            return [Type, Xcoords, Ycoords, ExitAge, IDs, ID, TimeIn, Vals]

        elif TypeOf == 'tracer':
            return [IDs, Xcoords, Ycoords, ExitAge, TimeIn]

    ux = np.reshape(ux, (width*height)) # ux is the macroscopic x velocity
    uy = np.reshape(uy, (width*height)) # uy is the macroscopic y velocity

    # dispersal inside the system
    for i, val in enumerate(Xcoords):

        X = int(round(Xcoords[i]))
        Y = int(round(Ycoords[i]))

        index =  int(round(X + Y * width))

        if index > len(ux) - 1: index = len(ux) - 1
        if index > len(uy) - 1: index = len(uy) - 1

        k = np.random.binomial(1, 1)
        if k == 1:
            Xcoords[i] += ux[index]
            Ycoords[i] += uy[index]

        y = Ycoords[i]
        if 0 > y: Ycoords[i] = 0
        elif y > height: Ycoords[i] = height

        TimeIn[i] += 1
        if Xcoords[i] >= width - limit:

            ExitAge.append(TimeIn[i])
            Xcoords.pop(i)
            Ycoords.pop(i)
            TimeIn.pop(i)
            IDs.pop(i)

            if TypeOf == 'resource' or TypeOf == 'individual':
                Type.pop(i)
                Vals.pop(i)

    ux = np.reshape(ux, (height, width))
    uy = np.reshape(uy, (height, width))

    listlengths = [len(Xcoords), len(Ycoords), len(IDs)]
    if TypeOf == 'tracer':
        return [IDs, Xcoords, Ycoords, ExitAge, TimeIn]

    elif TypeOf == 'resource' or TypeOf == 'individual':
        return [Type, Xcoords, Ycoords, ExitAge, IDs, ID, TimeIn, Vals]



def maintenance(SpeciesIDs, coords, ExitAge, color_dict, MaintDict, IDs, TimeIn, Qs, D):

    if SpeciesIDs == []:
        return [SpeciesIDs, coords, ExitAge, IDs, TimeIn, Qs]

    Xcoords, Ycoords, Zcoords = coords
    for i, val in enumerate(Qs):

        val -= MaintDict[SpeciesIDs[i]]  # maintanence influenced by species
        if val <= 0.0:   # starved

            Qs.pop(i)
            ExitAge.append(TimeIn[i])
            TimeIn.pop(i)
            SpeciesIDs.pop(i)
            IDs.pop(i)
            Xcoords.pop(i)
            Ycoords.pop(i)
            if D == 3: Zcoords.pop(i)

        else: Qs[i] = val

    coords = [Xcoords, Ycoords, Zcoords]
    return [SpeciesIDs, coords, ExitAge, IDs, TimeIn, Qs]



def predation(PredIDs, PredID, PredCoords, PredTimeIn, PredExitAge, SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndCoords, width, height, length, D):

    PredXcoords, PredYcoords, PredZcoords, IndXcoords, IndYcoords, IndZcoords, IndBoxes, PredBoxes = [[], [], [], [], [], [], [], []]
    PredXcoords, PredYcoords, PredYcoords = ResCoords
    IndXcoords, IndYcoords, IndZcoords = IndCoords

    if not len(PredTypes):
        PredLists = [PredTypes, PredVals, PredIDs, PredID, PredTimeIn, PredExitAge, PredXcoords, PredYcoords, PredZcoords]
        IndLists = [SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndXcoords, IndYcoords, IndZcoords]
        return [PredLists, IndLists]

    if D == 2:
        IndBoxes = [list([]) for _ in xrange(width*height)]
        PredBoxes = [list([]) for _ in xrange(width*height)]

    elif D == 3:
        IndBoxes = [list([]) for _ in xrange(width*height*length)]
        PredBoxes = [list([]) for _ in xrange(width*height*length)]

    index = 0
    for i, val in enumerate(IndIDs):
        roundedX = int(round(IndXcoords[i]))
        roundedY = int(round(IndYcoords[i]))

        if D == 2: index = int(round(roundedX + (roundedY * width)))

        elif D == 3:
            roundedZ = int(round(IndZcoords[i]))
            index = int(round((roundedY * length * width) + (roundedX * length) + roundedZ))

        if index > len(IndBoxes) - 1: index = len(IndBoxes) - 1
        elif index < 0: index = 0

        IndBoxes[index].append(val)

    index = 0
    for i, val in enumerate(PredIDs):
        roundedX = int(round(PredXcoords[i]))
        roundedY = int(round(PredYcoords[i]))

        if D == 2: index = int(round(roundedX + (roundedY * width)))

        elif D == 3:
            roundedZ = int(round(PredZcoords[i]))
            index = int(round((roundedY * length * width) + (roundedX * length) + roundedZ))

        if index > len(PredBoxes) - 1: index = len(PredBoxes) - 1
        elif index < 0: index = 0

        PredBoxes[index].append(val)


    for i, PredBox in enumerate(PredBoxes):
        if not len(PredBox): continue

        IndBox = IndBoxes[i]

        for pred in PredBox:
            if not len(IndBox): break

            # The predator
            PredBox.pop(0)

            # The prey
            IndID = choice(IndBox)
            index = IndBox.index(IndID)
            IndBox.pop(index)

            j = IndIDs.index(IndID)
            Qs.pop(j)
            IndExitAge.append(ResTimeIn[j])
            IndTimeIn.pop(j)
            SpeciesIDs.pop(j)
            IndIDs.pop(j)
            IndXcoords.pop(j)
            IndYcoords.pop(j)
            IndZcoords.pop(j)

    PredLists = PredIDs, PredID, PredXCoords, PredYCoords, PredZCoords, PredTimeIn, PredExitAge
    IndLists = SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndXCoords, IndYCoords, IndZCoords

    return [PredLists, IndLists]



def consume(ResTypes, ResVals, ResIDs, ResID, ResCoords, ResTimeIn, ResExitAge, SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndCoords, width, height, length, GrowthDict, ResUseDict, DispDict, D):

    IndBoxes, ResBoxes = [], []
    ResXcoords, ResYcoords, ResZcoords = ResCoords
    IndXcoords, IndYcoords, IndZcoords = IndCoords

    if not len(ResTypes) or not len(SpeciesIDs):
        ResLists = [ResTypes, ResVals, ResIDs, ResID, ResTimeIn, ResExitAge, ResXcoords, ResYcoords, ResZcoords]
        IndLists = [SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndXcoords, IndYcoords, IndZcoords]
        return [ResLists, IndLists]

    if D == 2:
        IndBoxes = [list([]) for _ in xrange(width*height)]
        ResBoxes = [list([]) for _ in xrange(width*height)]

    elif D == 3:
        IndBoxes = [list([]) for _ in xrange(width*height*length)]
        ResBoxes = [list([]) for _ in xrange(width*height*length)]

    index = 0
    for i, val in enumerate(IndIDs):
        roundedX = int(round(IndXcoords[i]))
        roundedY = int(round(IndYcoords[i]))

        if D == 2: index = int(round(roundedX + (roundedY * width)))

        elif D == 3:
            roundedZ = int(round(IndZcoords[i]))
            index = int(round((roundedY * length * width) + (roundedX * length) + roundedZ))

        if index > len(IndBoxes) - 1: index = len(IndBoxes) - 1
        elif index < 0: index = 0

        IndBoxes[index].append(val)

    index = 0
    for i, val in enumerate(ResIDs):
        roundedX = int(round(ResXcoords[i]))
        roundedY = int(round(ResYcoords[i]))

        if D == 2: index = int(round(roundedX + (roundedY * width)))

        elif D == 3:
            roundedZ = int(round(ResZcoords[i]))
            index = int(round((roundedY * length * width) + (roundedX * length) + roundedZ))

        if index > len(ResBoxes) - 1: index = len(ResBoxes) - 1
        elif index < 0: index = 0

        ResBoxes[index].append(val)


    for i, box in enumerate(IndBoxes):
        if not len(box): continue

        ResBox = ResBoxes[i]

        for ind in box: # The individuals
            if not len(ResBox): break

            resID = choice(ResBox)
            boxIndex = ResBox.index(resID)

            # The food
            j = ResIDs.index(resID)
            restype = ResTypes[j]
            resval = ResVals[j]

            # The Individual
            ID = IndIDs.index(ind)
            Q = Qs[ID]
            species = SpeciesIDs[ID]
            mu = GrowthDict[species]
            efficiency = ResUseDict[species][restype]
            mu = mu * efficiency

            if resval > (mu * Q): # Increase cell quota
                resval = resval - (mu * Q)
                Q = Q + (mu * Q)
                if Q > 1.0:
                    resval = Q - 1.0
                    Q = 1.0
                ResVals[j] = resval

            else:
                Q += resval
                resval = 0.0

            if resval == 0.0:
                ResBox.pop(boxIndex)
                ResVals.pop(j)
                ResExitAge.append(ResTimeIn[j])
                ResTimeIn.pop(j)
                ResTypes.pop(j)
                ResIDs.pop(j)
                ResXcoords.pop(j)
                ResYcoords.pop(j)
                if D == 3: ResZcoords.pop(j)

            Qs[ID] = Q

    ResLists = ResTypes, ResVals, ResIDs, ResID, ResTimeIn, ResExitAge, ResXcoords, ResYcoords, ResZcoords
    IndLists = SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndXcoords, IndYcoords, IndZcoords

    return [ResLists, IndLists]



def reproduce(reproduction, speciation, SpeciesIDs, Qs, IDs, ID, TimeIn, coords, width, height, length, GrowthDict, DispDict, color_dict, ResUseDict, MaintDict, D, nr):

    if SpeciesIDs == []:
        return [SpeciesIDs, coords, IDs, TimeIn, Qs]

    Xcoords, Ycoords, Zcoords = coords
    if reproduction == 'fission':
        for i, Q in enumerate(Qs):
            p = np.random.binomial(1, Q)
            if p == 1: # individual is large enough to reproduce
                Qs[i] = Q/2.0
                Qs.append(Q/2.0)
                ID += 1
                IDs.append(ID)
                TimeIn.append(TimeIn[i])
                spID = SpeciesIDs[i]

                if speciation == 'yes':
                    p = np.random.binomial(10**-4, 1)
                    if p == 1:

                        # speciate
                        frac, whole = spID.split('.')
                        frac = int(frac) + 1
                        spID = whole +'.'+ str(frac)

                        # new species color
                        color_dict = get_color(spID, color_dict)

                        # new species growth rate
                        p = np.random.binomial(0.25, 1)
                        GrowthDict[spID] = np.random.uniform(0.1, 1.0)

                        # new species maintenance
                        p = np.random.binomial(0.25, 1)
                        MaintDict[spID] = np.random.uniform(0.001, 0.01)

                        # new species active dispersal rate
                        p = np.random.binomial(0.25, 1)
                        DispDict[spID] = np.random.uniform(0.0, 0.1)

                        # new species resource use efficiencies
                        p = np.random.binomial(0.25, 1)
                        ResUseDict[spID] = np.random.uniform(0.1, 1.0, nr)


                SpeciesIDs.append(spID)
                direction = choice([-1,1])
                Xcoords.append(Xcoords[i] + direction*DispDict[SpeciesIDs[i]])
                direction = choice([-1,1])
                Ycoords.append(Ycoords[i] + direction*DispDict[SpeciesIDs[i]])

                if D == 3: Zcoords.append(Zcoords[ID])

    elif reproduction == 'sexual':

        indBoxes = []
        spBoxes = []

        if D == 2:
            indBoxes = [list([]) for _ in xrange(width*height)]
            spBoxes = [list([]) for _ in xrange(width*height)]
        elif D == 3:
            indBoxes = [list([]) for _ in xrange(width*height*length)]
            spBoxes = [list([]) for _ in xrange(width*height*length)]

        index = 0
        for i, indID in enumerate(IDs):

            spID = SpeciesIDs[i]
            roundedX = int(round(Xcoords[i]))
            roundedY = int(round(Ycoords[i]))

            if D == 2: index = int(round(roundedX + (roundedY * width)))
            elif D == 3:
                roundedZ = int(round(Zcoords[i]))
                index = int(round((roundedY * length * width) + (roundedX * length) + roundedZ))

            if index > len(indBoxes) - 1: index = len(indBoxes) - 1
            elif index < 0: index = 0

            indBoxes[index].append(indID)
            spBoxes[index].append(spID)

        for i, box in enumerate(indBoxes):
            if len(box) < 2: continue

            spbox = spBoxes[i]
            while len(box) > 1:
                i1 = choice(range(len(box))) # choose an individual at random
                ID1 = box.pop(i1) # remove the individual
                sp1 = spbox.pop(i1) # remove the species ID
                index1 = IDs.index(i1)
                q1 = Qs[index1]

                p1 = np.random.binomial(1, q1)
                if p1 == 0: continue # individual not large enough to reproduce

                # Find another of the same species
                if spbox.count(sp1) > 1:
                    i2 = spbox.index(sp1) # choose an individual of the same species
                    box.pop(i2) # remove the individual
                    spbox.pop(i2) # remove the species ID
                    index2 = IDs.index(i2)
                    q2 = Qs[index2]

                    p2 = np.random.binomial(1, q2)
                    if p2 == 0: continue # individual not large enough to reproduce

                    fq = choice([q1, q2])
                    Qs[i] = fq/2.0
                    Qs.append(fq/2.0)
                    ID += 1
                    IDs.append(ID)
                    TimeIn.append(TimeIn[i])

                    SpeciesIDs.append(SpeciesIDs[ID1])
                    direction = choice([-1,1])
                    Xcoords.append(Xcoords[ID] + direction*DispDict[SpeciesIDs[ID]])
                    direction = choice([-1,1])
                    Ycoords.append(Ycoords[ID] + direction*DispDict[SpeciesIDs[ID]])

    coords = Xcoords, Ycoords, Zcoords
    return [SpeciesIDs, Qs, IDs, ID, TimeIn, coords, width, height, length, GrowthDict, DispDict]



def nonfluid_movement(TypeOf, motion, Lists, ExitAge, TimeIn, coords, width, height, length, u0, D):

    limit = 0.5
    distance, direction, pop = 0, 0, 'no'
    X, Y, Z = 0, 0, 0
    IDs, Types, Vals = [], [], []
    DispDict = {}

    Xcoords, Ycoords, Zcoords = coords

    if TypeOf == 'tracer': IDs = Lists
    elif TypeOf == 'individual': Types, IDs, Vals, DispDict = Lists
    elif TypeOf == 'resource': Types, IDs, Vals = Lists

    for i, val in enumerate(IDs):

        # get distance
        if TypeOf == 'individual':
            distance = u0 * DispDict[Types[i]]
        else:
            distance = u0

        X, Y = Xcoords[i], Ycoords[i]

        if D == 3: Z = Zcoords[i]

        # go up or down
        #if TypeOf != 'resource':
        if motion == 'unidirectional': direction = np.random.uniform(-1, 1)
        if motion == 'random_walk': direction = np.random.uniform(-height, height)
        Y = Y + (direction * distance)

        # go forward or backward
        #if TypeOf != 'resource':
        if motion == 'unidirectional': direction = np.random.uniform(1, 1)
        if motion == 'random_walk': direction = np.random.uniform(-width, width)
        X = X + (direction * distance)

        if X > width - limit or X < limit: pop = 'yes'
        elif Y > height - limit or Y < limit: pop = 'yes'

        if D == 3:
            # go left or right
            if motion == 'unidirectional': direction = np.random.uniform(-0.5, 1.5)
            if motion == 'random_walk': direction = np.random.uniform(-length, length)
            Z = Z + (direction * distance)

            if Z > length - limit or Z < limit: pop = 'yes'

        if pop == 'no':
            Xcoords[i] = X
            Ycoords[i] = Y

            if D == 3: Zcoords[i] = Z

        elif pop == 'yes':
            IDs.pop(i)
            ExitAge.append(TimeIn[i])
            TimeIn.pop(i)
            Xcoords.pop(i)
            Ycoords.pop(i)

            if D == 3: Zcoords.pop(i)

            if TypeOf == 'individual' or TypeOf == 'resource':
                Vals.pop(i)
                Types.pop(i)

    coords = [Xcoords, Ycoords, Zcoords]
    if TypeOf == 'tracer': Lists = IDs
    if TypeOf == 'individual' or TypeOf == 'resource': Lists = [Types, IDs, Vals]

    return [Lists, ExitAge, TimeIn, coords]