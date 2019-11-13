# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction
from hlt.positionals import Position

# This library allows you to self.generate random numbers.
import random

import math

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

# Load self.gene from batch
import sys

debug = False
evolving = False

# This game object contains the initial game state.
game = hlt.Game()

# Needs 10% extra time to finish up
gene =[]
if evolving:
    arg = sys.argv
    for i in range(1,len(arg)):
        gene.append(float(arg[i]))
else:
    gene1 = [2.970838236686183, -6.746584856642684, 2.4833735462091395, 17.275122838579534, 8.825670658073955, 
            8.169974645647523, 803.5886853089133, 1769.9866582466768, 1.2373187373456498, 5.031640706232297, 130.44046747203575]
    gene2 = [1.694752105506565, 1.624583421625449, 0.5415420046116491, 1.9320045218797257, 96.16863790117458, 9.124600792523578, 917.7969162817453, 1050.1316618481346, 1.223971819209685, 18.4823494060523, 119.85035763626794]
    gene3 = [2.821805380092722, 0.6689916583576001, 1.645514405944587, 2.5185937510136296, 0.3284861497574507,
            0.9264364963052442, 414.5769621092161, 574.9294964238056, 1.0312179260695655, 12.952772984776137, 36.155014379716874]
    gene = [2.7782890222560783, 2.6934447704787488, 2.50834047292879, 2.28435598829312, 4.807194634240073,
            1.199855833665504, 296.46895148237587, 1031.7829682921465, 0.9689523610945215, 8.692940267670076, 30.4090328922088]

# Game stats for genetic training
crash = 0
haliteInMap = 0
haliteOnBoard = 0
haliteInMe = 0

map = game.game_map
me = game.me
max_turn = constants.MAX_TURNS
shipList = None
# Cost of halites along the path between two points
def H(a=Position(0, 0), b=Position(0, 0)):
    return map.calculate_distance(a, b)


# A register of all the ships modelled
geneticShips = {}
# A list of all existing targets
targetList = []

class GeneticShip:
    def __init__(self, ship, gene=[]):
        self.gene = gene
        self.ship = ship
        self.position = ship.position
        self.target = None
        self.target_score = -sys.maxsize

    def findTarget(self):
        if(not self.target is None):
            self.target_score = self.getScore(self.target)
        best_score = self.target_score
        best_pos = self.target
        radius = int(self.gene[0])
        posx = self.ship.position.x
        posy = self.ship.position.y
        for i in range(-radius, radius+1):
            for j in range(-radius, radius+1):
                target_cell = map[Position(posx+i, posy+j)]
                target_score = self.getScore(target_cell)
                if target_score > best_score:# and (target_cell not in targetList):
                    best_pos = target_cell
                    best_score = target_score
        if(debug):
            self.getScore(best_pos, True)
        if(self.ship.halite_amount == constants.MAX_HALITE):
            pos = me.shipyard.position
            px = pos.x
            py = pos.y
            x = self.position.x
            y = self.position.y
            ofx = 0 if(px-x == 0) else (px-x)/abs(px-x)
            ofy = 0 if(py-y == 0) else (py-y)/abs(py-y)
            self.target = map[Position(px+ofx, py+ofy)]
            self.target_score *= 3
        return (best_pos, best_score)
    # tc = target cell

    def getScore(self, tc=map[Position(0, 0)], show_score=False):
        s = self.f1(tc)+self.f2(tc)+self.f3(tc)+self.f4(tc)
        if(show_score):
            logging.info("score of "+str(tc)+": "+str(s))
            logging.info(" f1: "+str(self.f1(tc))+" f2: "+str(self.f2(tc, True)) +
                         " f3: "+str(self.f3(tc))+" f4: "+str(self.f4(tc)))
        return s

    def f1(self, tc=map[Position(0, 0)]):
        hc = tc.halite_amount
        d = map.calculate_distance(self.ship.position, tc.position)
        return hc-self.gene[1]*H(self.ship.position, tc.position)

    def f2(self, tc, show_score=False):
        h = self.ship.halite_amount
        yard = me.shipyard
        d = map.calculate_distance(tc.position, yard.position)
        if(show_score):
            logging.info("e2: "+str(self.e2()))
        return self.gene[2]*(h-self.e2())/d if d != 0 else self.gene[2]*(h-self.e2())/0.1

    def e2(self):
        return self.gene[6]*(1-game.turn_number/(max_turn*self.gene[8]))

    def f3(self, tc):
        h = self.ship.halite_amount
        total = 0
        for dropoff in me.get_dropoffs():
            d = map.calculate_distance(tc.position, dropoff.position)
            if(d != 0):
                total += self.gene[3]*(h-self.e3())/d
            else:
                total += self.gene[3]*(h-self.e3())/0.1
        return total

    def e3(self):
        return self.gene[7]*(1-game.turn_number/max_turn)

    def f4(self, tc):
        if not evolving:
            total = 0
            for player_id in game.players:
                player = game.players[player_id]
                for ship in player.get_ships():
                    if ship != self.ship:
                        d = map.calculate_distance(tc.position, ship.position)
                        # d doesn't have special case here since no two ships can occupy the same place
                        total -= (self.gene[4] if (ship in  shipList) else self.gene[10])/(0.1 if d == 0 else d)
                return total
        else:
            total = self.safetyScore(tc, map)
            if tc.is_occupied: total-= (self.gene[4]/0.1 if(tc.ship in shipList) else self.gene[10]/0.1)
            return total

    def t(self, s1, s2):
        if(s2 is None):
            return true
        return (s2-s1)/(s1 if(s1 > 0) else 1) > self.gene[5]

    def get_move(self):
        move = Direction.Still
        move = map.naive_navigate(self.ship, self.target.position)
        # If the ship is stuck
        if(move==Direction.Still):
            return map.naive_navigate(self.ship, Position(random.randint(0, constants.WIDTH-1), random.randint(0,constants.HEIGHT-1)))
        return move

    def safetyScore(self, ship, game_map):
        total = 0
        for d in [Direction.North, Direction.South, Direction.West, Direction.East]:
            targetCell = game_map[ship.position.directional_offset(d)]
            if  targetCell.is_occupied:
                if not targetCell.ship in shipList:
                    total -= self.gene[10]
                else:
                    total -= self.gene[4]
        return total

def navigateCheap(ship, destination):
    """
    Returns a singular safe move towards the destination.

    :param ship: The ship to move.
    :param destination: Ending position
    :return: A direction.
    """
    bestd = Direction.Still
    leastHalite = constants.MAX_HALITE
    # No need to normalize destination, since get_unsafe_moves
    # does that
    for direction in map.get_unsafe_moves(ship.position, destination):
        target_pos = ship.position.directional_offset(direction)
        if map[target_pos].halite_amount<=leastHalite:
            leastHalite=map[target_pos].halite_amount
            bestd = direction
    return bestd

# turnNumberToStop and maxShipAmount are potentially genes
maxShipAmount = gene[9]*constants.WIDTH/32
turnNumberToStop = max_turn*gene[8]

def shouldProduce():
    return (me.halite_amount > constants.SHIP_COST and len(shipList) < maxShipAmount and
            game.turn_number < turnNumberToStop and game.turn_number % 2 == 0 and not map[me.shipyard.position].is_occupied)

def normalize_position(ship, game_map):
    x = ship.position[0]
    y = ship.position[1]
    if (x < 0 and x > game_map.width and y < 0 and y > game_map.height):
        ship.position = game_map.normalize(ship.position)


game.ready("Pinecone bot")

if(evolving):
    for i in range(0,constants.WIDTH):
        for j in range(0,constants.HEIGHT):
            haliteInMap += map[Position(i, j)].halite_amount

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    shipList = me.get_ships()
    # A command queue holds all the commands you will run this turn.
    command_queue = []
    for ship in shipList:
        if(debug):
            logging.info("Ship {} has {} halite.".format(
                ship, ship.halite_amount))
        if(not ship.id in geneticShips):
            ngs = GeneticShip(ship, gene)
            geneticShips[ship.id] = ngs
            (ngs.target, ngs.target_score) = ngs.findTarget()
            #targetList.append(ngs.target)

    deathlist = []
    for key in geneticShips:
        gs = geneticShips[key]
        ship = None
        if(not gs.ship in shipList):
            crash+=1
            deathlist.append(gs)
            continue
        else:
            ship = gs.ship
        if(debug):
            logging.info("score of current target "+str(gs.target) +
                         ": "+str(gs.getScore(gs.target)))
        if(ship.position != me.shipyard.position):
            if(ship.position == gs.target.position):
                command_queue.append(ship.stay_still())
            else:
                command_queue.append(ship.move(gs.get_move()))
        (newTarget, newTargetScore) = gs.findTarget()
        #Decide whether a new target should be chosen
        if(gs.t(gs.target_score, newTargetScore)):
            # if(gs.target in targetList):
            #     targetList.remove(gs.target)
            gs.target = newTarget
            # targetList.append(newTarget)
            if(debug):
                logging.info("Updated target to:"+str(gs.target.position))
        # Avoid staying at the shipyard by forcing a target switch
        if(ship.position == me.shipyard.position):
            command_queue.append(ship.move(gs.get_move()))
            (newTarget, newTargetScore) = gs.findTarget()
            if(gs.t(gs.target_score, newTargetScore)):
                # if(gs.target in targetList):
                #     targetList.remove(gs.target)
                gs.target = newTarget
                # targetList.append(newTarget)
                if(debug):
                    logging.info("Updated target to:"+str(gs.target.position))
        # See google sheets for algorithm

        #Compute number of halites left in the ship if it is the last round and the model is being trained
        if(evolving and game.turn_number==constants.MAX_TURNS):
            if(ship.position!=me.shipyard.position): haliteOnBoard+=ship.halite_amount
            else: haliteInMe+=ship.halite_amount

    # Delete all the genetic models of crashed ships
    for crashed in deathlist:
        geneticShips.pop(crashed.ship.id)
    #Spawn ship if there is enough resource, right timming, and no ship on the yard
    if shouldProduce():
        command_queue.append(game.me.shipyard.spawn())
    
    if(evolving and game.turn_number == constants.MAX_TURNS):
        haliteInMe = me.halite_amount
        logging.warn(str(crash)+","+str(haliteInMap)+','+str(haliteOnBoard)+','+str(haliteInMe))
        logging.warn(str(math.exp(-2*crash/maxShipAmount))+','+str(haliteInMe/haliteInMap*30)+','+str(haliteInMe/(haliteInMe+haliteOnBoard)))
        logging.warn(str(gene))
    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

# gene 0: Search radius [1, map size]
# gene 1: Distance cost factor [0.1, 10]
# gene 2: Shipyard force factor [0.1, 10]
# gene 3: Dropoff point force factor [0.1, 10]
# gene 4: Friendly Ship-ship repulsion factor [0, 100]
# gene 5: Strategic threshold [0.1, 10]
#   (determines whether target should be switched)
# gene 6: Initial ship yard retreat threshold [0, max ship cargo]
#   (determines how much cargo a ship has to carry in order to retreat)
# gene 7: Initial dropoff threshold [0, max ship cargo]
#   (determines how much cargo a ship must carry in order to be pulled to dropoff points)
# gene 8: Wrap-up threshold: [0.5, 1]
#   (once this portion of the game has passed, the program takes a series of actions including
#   stop producing ships, exerting a stronger pull on each ship to get them deliver their cargos)
# gene 9: Max-number of ships to produce per 32 sidelength of game map [1, 30]
# gene 10: Competitive ship-ship repulsion factor [-100, 100]
