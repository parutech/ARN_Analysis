import os
import re
import sys
import itertools
from matplotlib.cbook import strip_math
import matplotlib.pyplot as plt
import numpy as np
from anytree import Node, RenderTree
from anytree.exporter import DotExporter, JsonExporter
import pydot

"""
    Classe Loop correspondant à une boucle contenue au sein d'une molécule
    @attrs (entryPos) Position d'entrée de la boucle
           (exitPos) Position de sortie de la boucle
           (height) Hauteur de la boucle
           (childLoops) Liste des boucles enfant de la boucle en question
    @funcs (LoopType) "hairpin", "internal", "bulge", ou "multiloop", correspondant à un nombre de boucles enfants différent
                      0 boucles   1 (sym)    1 (asym)    > 1 boucle
           (summary) Renvoie un tuple contenant la position d'entrée, position de sortie, et hauteur de la boucle
           (structure) Renvoie la structure aplatie de la boucle et de ses boucles filles
           (sequence) Renvoie la liste des positions appartenant à la boucle
"""
class Loop:
    def __init__(self):
        self.childLoops = []

    def setEntryPos(self, entryPos):
        self.entryPos = entryPos

    def setExitPos(self, exitPos):
        self.exitPos = exitPos

    def setHeight(self, height):
        self.height = height

    def addChildLoops(self, loopList):
        for loop in loopList:
            self.childLoops.append(loop)

    def getHeight(self):
        return self.height

    def getEntryPos(self):
        return self.entryPos

    def getExitPos(self):
        return self.exitPos

    def getChildLoops(self):
        return self.childLoops

    def LoopType(self):
        if(len(self.childLoops) == 0):
            return "hairpin"
        elif(len(self.childLoops) == 1):
            child = self.childLoops[0]
            heightDif = child.getHeight() - self.height
            if(child.getEntryPos() - self.entryPos == heightDif) | (self.exitPos - child.getExitPos() == heightDif):
                return "bulge"
            return "internal"
        else:
            return "multiloop"

    def clear(self):
        self.entryPos = 0
        self.exitPos = 0
        self.height = 0

    def empty(self):
        self.childLoops = []

    def summary(self):
        return (self.getEntryPos(), self.getExitPos(), self.getHeight())

    def structure(self):
        structList = []
        if(self.LoopType() != "hairpin"):
            for child in self.childLoops:
                structList.append(child.structure())
        return structList

    def sequence(self):
        listPos = []
        if(self.LoopType() == "hairpin"):
            return listPos + range(self.entryPos+1, self.exitPos+1)
        else:
            startPos = self.entryPos
            stopPos = self.childLoops[0].getEntryPos() - (self.childLoops[0].getHeight() - self.height - 1)
            listPos.append(range(startPos, stopPos))
            for i in range(len(self.childLoops)):
                startPos = self.childLoops[i].getExitPos() + (self.childLoops[i].getHeight() - self.height)
                if(self.childLoops[i] == self.childLoops[-1]):
                    stopPos = self.exitPos
                else:
                    stopPos = self.childLoops[i+1].getEntryPos() - (self.childLoops[i+1].getHeight() - self.height - 1)
                listPos.append(range(startPos-1, stopPos))
        return listPos


"""
    Extraction des structures primaires des fichiers .dbn dans un fichier primStructList.txt
    @param X
    @returns X
"""
def ExtractPrimary():
    fileList = os.listdir(os.getcwd() + '\\dbnFiles')
    nbFiles = len(fileList)
    count = 0
    with open('primStructList.txt', 'w') as sf:
        for file in fileList:
            count += 1
            print(str(count) + '/' + str(nbFiles), end='\r')
            with open(os.getcwd() + '\\dbnFiles\\' + file, 'r') as f:
                lines = f.readlines()
                sf.write(file + '\n')
                sf.write(lines[3] + '\n')


"""
    Extraction des structures secondaires des fichiers .dbn dans un fichier primStructList.txt
    @param X
    @returns X
"""
def ExtractSecondary():
    fileList = os.listdir(os.getcwd() + '\\dbnFiles')
    nbFiles = len(fileList)
    count = 0
    with open('secStructList.txt', 'w') as sf:
        for file in fileList:
            count += 1
            print(str(count) + '/' + str(nbFiles), end='\r')
            with open(os.getcwd() + '\\dbnFiles\\' + file, 'r') as f:
                lines = f.readlines()
                sf.write(file + '\n')
                sf.write(lines[4] + '\n')


"""
    Génération de l'ensemble des mots de Motzkin valides de longueur inférieure ou égale à n
    @param (n) Longueur maximale des mots à générer
    @returns (R) Liste des mots de Motzkin valides de longueur <= n
"""
def GenTrueMotz(n):
    R = []
    if(n == 0):
        return [""]
    else:
        M = GenTrueMotz(n-1)
        for m in M:
            R.append('.'+m)
        for k in range(n-1):
            Mk = GenTrueMotz(k)
            Ml = GenTrueMotz(n-2-k)
            for m1 in Mk:
                for m2 in Ml:
                    R.append('('+m1+')'+m2)
        return R


"""
    Génération de l'ensemble des mots de Motzkin existants de longueur inférieure ou égale à n
    @param (n) Longueur maximale des mots à générer
    @returns (R) Liste des mots de Motzkin existants de longueur <= n
"""
def GenFullMotz(n):
    M = []
    for m in itertools.product(*(['.)('] * n)):
        M.append(''.join(m))
    return M


"""
    Crée une liste des hauteurs liées aux caractères de la structure secondaire
    @param (secStruct) Structure secondaire à analyser
           (startHeight) Hauteur de départ facultative
    @returns (heightTab) Liste des hauteurs liées à chaque caractère de la structure secondaire
"""
def GetSecondaryHeight(secStruct, startHeight=0):
    heightTab = []
    height = startHeight
    for sym in secStruct:
        if(sym == "("):
            heightTab.append(height)
            height += 1
        elif(sym == ")"):
            height -= 1
            heightTab.append(height)
        else:
            heightTab.append(height)
    
    return heightTab


"""
    Affiche le graphique des hauteurs des caractères de la structure secondaire
    @param (secStruct) Structure secondaire à analyser
    @returns X
"""
def ShowSecondaryHeight(secStruct):
    plt.plot(GetSecondaryHeight(secStruct))
    plt.show()


"""
    Vérifie si la structure secondaire donnée est une structure secondaire valide
    @param (secStruct) Structure secondaire à analyser
    @returns Booléen
"""
def IsValidSecondary(secStruct):
    return (-1 not in GetSecondaryHeight(secStruct))


"""
    Vérifie si la structure secondaire donnée est une structure secondaire englobée (une seule boucle racine)
    @param (secStruct) Structure secondaire à analyser
    @returns Booléen
"""
def IsEncompassed(secStruct):
    secStruct = secStruct.strip(".")
    CSecHeight = GetSecondaryHeight(secStruct)[1:-1]

    return (0 not in CSecHeight)


"""
    Récupère l'ensemble des boucles présentes au sein de la molécule à analyser par récurrence
    @param (secStruct) Structure secondaire à analyser
           (secHeight) Liste des hauteurs associées à la structure secondaire
           (positionsList) Liste des positions associées aux bases de la molécule
    @returns (loopList) Liste des boucles racinaires de la molécule, contenant chacune la liste de ses enfants, etc...
"""
def GetLoops(secStruct, secHeight, positionsList):
    loopList = []
    loop = Loop()

    if("(" not in secStruct) & (")" not in secStruct):
        return []

    minHeight = secHeight[0]

    for i in range(len(positionsList)):
        if(secStruct[i] == "(") & (secHeight[i] == minHeight):
            entryIndex = i
        elif(secStruct[i] == ")") & (secHeight[i] == minHeight):
            exitIndex = i

            # print(" "*(entryIndex)+"N"+" "*(exitIndex-entryIndex)+"X")
            # print(secStruct)
            # print(positionsList[entryIndex], positionsList[exitIndex])

            CSecStruct = secStruct[entryIndex:exitIndex+1]
            CSecHeight = secHeight[entryIndex:exitIndex+1]
            CPositionsList = positionsList[entryIndex:exitIndex+1]

            _secStructTemp = CSecStruct
            _secHeightTemp = CSecHeight
            _positionsListTemp = CPositionsList

            while(True):
                _secStructTemp = _secStructTemp[1:-1]
                _secHeightTemp = _secHeightTemp[1:-1]
                _positionsListTemp = _positionsListTemp[1:-1]

                if(IsValidSecondary(_secStructTemp)):
                    CSecStruct = _secStructTemp
                    CSecHeight = _secHeightTemp
                    CPositionsList = _positionsListTemp
                else:
                    break

                if(CSecStruct.startswith(('.', '[', '{'))) | (CSecStruct.endswith(('.', ']', '}'))) | (CSecStruct == ""):
                    break

            if(CSecStruct != ""):
                # print(CSecStruct, end="\n\n")

                loop.setHeight(CSecHeight[0])
                loop.setEntryPos(CPositionsList[0])
                loop.setExitPos(CPositionsList[-1]+2)

                loop.addChildLoops(GetLoops(CSecStruct, CSecHeight, CPositionsList))
                loopList.append(loop)
                loop = Loop()
    
    return loopList


"""
    Récupère l'ensemble des Nodes anytree associées aux boucles précédemment générées
    @param (rootLoop) Boucle racinaire de la molécule
           (rootNode) Node anytree correspondant à la boucle racinaire de la molécule
    @returns (nodeList) Liste de l'ensemble des Nodes anytree associées à la Node racinaire
"""
def GetLoopNodes(rootLoop, rootNode):
    nodeList = []
    childLoopList = rootLoop.getChildLoops()

    if(len(childLoopList) == 0):
        return []

    for loop in childLoopList:
        node = Node((loop.getEntryPos(), loop.getExitPos(), loop.getHeight()), parent=rootNode)
        nodeList.append(node)
        GetLoopNodes(loop, node)

    return nodeList


"""
    Affiche l'arbre de Nodes anytree associées à une boucle racinaire
    @param (rootLoop) Boucle racinaire de la molécule
    @returns X
"""
def GetTreeFromLoop(rootLoop):
    root = Node((rootLoop.getEntryPos(), rootLoop.getExitPos(), rootLoop.getHeight()), parent=None)
    nodeList = GetLoopNodes(rootLoop, root)

    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))


"""
    Enregistre l'arbre de Nodes généré à partir d'un fichier .dot sous forme d'une image .png
    @param (fileName) Fichier DOT à traiter
    @returns X
"""
def GetImageFromDot(fileName):
    (graph,) = pydot.graph_from_dot_file(os.getcwd() + "\\dotFiles\\" + fileName)
    graph.write_png(os.getcwd() + "\\pngFiles\\" + fileName.strip(".dot") + ".png")



"""
    Extrait l'ensemble des arbres associés à la liste des structures secondaires secStructList.txt sous forme de fichier JSON et DOT
    @param X
    @returns X
"""
def ExtractTrees():
    with open(os.getcwd() + "\\secStructList.txt", 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if(i%3 == 0):
                fileName = lines[i].strip()
                print('\r' + fileName, end=' ')
            if(i%3 == 1):
                secStructLine = lines[i].strip()

                if(not IsEncompassed(secStructLine)):
                    secStruct = '(' + secStructLine + ')'
                else:
                    secStruct = secStructLine

                secHeight = GetSecondaryHeight(secStruct)
                positionsList = range(len(secStruct))
                
                loopList = GetLoops(secStruct, secHeight, positionsList)

                if(len(loopList) == 0):
                    loopList.append(Loop())
                    loopList[0].clear()

                if(not IsEncompassed(secStructLine)):
                    loopList[0].clear()

                rootNode = Node((loopList[0].getEntryPos(), loopList[0].getExitPos(), loopList[0].getHeight()), parent=None)
                nodeList = GetLoopNodes(loopList[0], rootNode)

                DotExporter(rootNode).to_dotfile(os.getcwd() + "\\dotFiles\\" + fileName.strip(".dbn") + ".dot")
                with open(os.getcwd() + "\\jsonFiles\\" + fileName.strip(".dbn") + ".json", 'w') as j:
                    j.write(JsonExporter(indent=2, sort_keys=True).export((rootNode)))


if __name__ == "__main__" :
    secStruct = "...((((((((((..((((((.(((((((((....))))))))).[...{{.{{{{{(((((.(((.((......)))))......(((((((((((..........))))))..((((............))))...((.(((.....................................))).....((.((.........................................))...))))))))))))))...(((...........)))...(((((((...(........)...)))))))((((((..........))))))........)))))).(((...(.(......................).)...))).]....}}}}}}}....))))))))))..."
    secHeight = GetSecondaryHeight(secStruct)
    positionsList = range(len(secStruct))

    looplist = GetLoops(secStruct, secHeight, positionsList)

    print(looplist[0].structure())
    print(looplist[0].sequence())

    GetTreeFromLoop(looplist[0])

    # ExtractTrees()
    # GetImageFromDot("pRNA_CRW_2.dot")
    # sagemath
    pass