import json
import random
import math
import copy

scoreList1 = None
gene1 = None
scoreList2 = None
gene2 = None
index = 0

def removeWarning(list):
    return list[13:-1]

def toFloat(l):
    floatList = []
    for string in l:
        floatList.append(float(string))
    return floatList


with open('./bot-0.log','r') as log0:
    LineList = log0.readlines()
    gene1 = removeWarning(LineList[-1])
    score1 = removeWarning(LineList[-2])
    scoreList1 = toFloat(score1.split(","))

with open('./bot-1.log','r') as log1:
    LineList = log1.readlines()
    gene2 = removeWarning(LineList[-1])
    score2 = removeWarning(LineList[-2])
    scoreList2 = toFloat(score2.split(","))

def crossSingle(parent1, parent2, crosspoint):
    # crosspoint1 = random.randint(0,len(gene1)//2)
    # crosspoint2 = random.randint(len(gene1)//2
    gene1 = parent1[:crosspoint]
    gene2 = parent2[:crosspoint]
    gene1.append(parent2[crosspoint:])
    gene2.append(parent1[crosspoint:])
    return gene1, gene2

def cross(parent1, parent2, seed):
    random.seed(seed)
    crosspoints = []
    for i in range(4):
        crosspoints.append(random.randint(1, len(parent1)))
    child1, child2 = crossSingle(parent1, parent2, crosspoints[0])
    child1, child2 = crossSingle(child1, child2, crosspoints[1])
    child1, child2 = crossSingle(child1, child2, crosspoints[2])
    child1, child2 = crossSingle(child1, child2, crosspoints[3])
    return child1, child2
    

geneRanges = [[1, 10], [0.1, 10], [0.1, 10], [0.1, 10], [0, 100], [0.1, 10], [
    0, 1000], [0, 1000], [0.5, 1], [1, 30], [-100, 100]]

def deform(i):
    return math.asin(2*i-1)**3/(3.876*2)
    
def mutateSingle(parent, mutationIndex):
    distance = geneRanges[mutationIndex][1]- geneRanges[mutationIndex][0]
    newMutant = deform(random.random())*distance+parent[mutationIndex]
    parent[mutationIndex] = newMutant
    return parent


def mutate(parent):
    indeces = []
    for i in range(4):
        indeces.append(random.randint(1, len(parent)))
    newgene = copy.copy(parent)
    for i in range(4):
        mutateSingle(newgene,indeces[i])
    return newgene
                                        
def compare():
    totalScore1=0.1*scoreList1[0]+0.8*scoreList1[1]+0.3*scoreList1[2]
    totalScore2=0.1*scoreList2[0]+0.8*scoreList2[1]+0.3*scoreList2[2]
    if totalScore1>totalScore2:
        return (gene1,scoreList1)
    else:return (gene2,scoreList2)                

(winnerGene,winnerGeneScore) = compare() 
newgene = mutate(winnerGene)
def outPutCSV():
    with open('./optimization/versions.csv','a') as states:
        states.write("gene:" + str(winnerGene) + ", score:" +str(winnerGeneScore)+"\n")

def writeRunGame():
    with open('./optimization/run_game.bat','r') as run_game:
        runGame = run_game.read()
        stringList = run_game.read().split()
    with open('./optimization/run_game.bat','w') as write_game:
