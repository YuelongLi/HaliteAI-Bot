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
def removeGeneWarning(list):
    return list[14:-2]

def toFloat(l):
    floatList = []
    for string in l:
        floatList.append(float(string))
    return floatList


with open('./bot-0.log','r') as log0:
    LineList = log0.readlines()
    gene1 = removeGeneWarning(LineList[-1])
    score1 = removeWarning(LineList[-2])
    scoreList1 = toFloat(score1.split(","))
    gene1 = toFloat(gene1.split(','))

with open('./bot-1.log','r') as log1:
    LineList = log1.readlines()
    gene2 = removeGeneWarning(LineList[-1])
    score2 = removeWarning(LineList[-2])
    scoreList2 = toFloat(score2.split(","))
    gene2 = toFloat(gene2.split(','))

def crossSingle(parent1, parent2, crosspoint):
    # crosspoint1 = random.randint(0,len(gene1)//2)
    # crosspoint2 = random.randint(len(gene1)//2
    gene1 = parent1[:crosspoint]
    gene2 = parent2[:crosspoint]
    gene1.append(parent2[crosspoint:])
    gene2.append(parent1[crosspoint:])
    return gene1, gene2

def cross(parent1, parent2, seed):
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
    print(parent)
    return parent

def mutate(parent):
    indeces = []
    for i in range(4):
        indeces.append(random.randint(0, len(parent)-1))
    newgene = copy.copy(parent)
    for i in range(4):
        mutateSingle(newgene,indeces[i])
    return newgene

def compare():
    totalScore1=0.2*scoreList1[0]+0.8*scoreList1[1]+0.0*scoreList1[2]
    totalScore2=0.2*scoreList2[0]+0.8*scoreList2[1]+0.0*scoreList2[2]
    if totalScore1>totalScore2:
        return (gene1,totalScore1)
    else:return (gene2,totalScore2)                

(winnerGene,winnerGeneScore) = compare() 
newgene = mutate(winnerGene)

def outPutCSV():
    with open('./versions.csv','a') as state:
        state.write(str(winnerGeneScore)+', '+str(winnerGene)[1: -1]+"\n")

def writeRunGame():
    with open('./compete.bat','w') as write_game:
        
        write_game.write(
            'halite.exe --replay-directory replays/ -v --no-logs --width 32 --height 32 "python GeneticBot2.py')
        for i in range (len(newgene)):
            write_game.write(" "+str(newgene[i]))
        write_game.write('" "python GeneticBot2.py')
        for j in range (len(winnerGene)):
            write_game.write(" "+str(winnerGene[j]))  
        write_game.write('"')


writeRunGame()
outPutCSV()

