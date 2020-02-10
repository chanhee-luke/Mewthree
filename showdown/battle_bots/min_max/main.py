import constants

from showdown.battle import Battle
from copy import deepcopy

from data.parse_smogon_stats import MOVES_STRING
from data.helpers import get_pokemon_sets

from ..helpers import format_decision
from data.helpers import get_all_likely_moves
from showdown.engine.damage_calculator import _calculate_damage

from .tree import Tree

from config import logger

def switchTreeTraversalDFS(root):
    highest = None
    check = []
    visited = set()
    check.append(root)

    while check:
        node = check.pop()
        if node in visited:
            continue
        visited.add(node)

        if node.maximinScore:
            logger.debug("Potential switch Pokemon: {} with worst damage score {}".format(node.data,node.maximinScore))
            if highest == None:
                highest = node
            if highest.maximinScore < node.maximinScore:
                highest = node
        for child in node.children:
            check.append(child)

    if highest == None:
        return None
    logger.info("Action:{}".format(highest.data))
    return highest.data

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_switch(self):
        #build tree
        switchRoot = Tree()

        # find worst case move used on each possible switched in Pokemon
        battle_copy = deepcopy(self)
        battle_copy.opponent.lock_moves()
        try:
            pokemon_sets = get_pokemon_sets(battle_copy.opponent.active.name)
        except KeyError:
            logger.warning("No set for {}".format(battle_copy.opponent.active.name))
            return
        opponent_possible_moves = sorted(pokemon_sets[MOVES_STRING], key=lambda x: x[1], reverse=True)

        for reservePkm in self.user.reserve:
            if reservePkm.hp == 0:
                continue
            worstCase = 0
            for move in opponent_possible_moves:
                if move[0].startswith("hiddenpower"):
                    continue
                selfCopy = deepcopy(self)
                selfCopy.user.active = reservePkm
                state = selfCopy.create_state()
                damageEstimate = _calculate_damage(state.opponent.active,state.self.active,move[0])
                if damageEstimate != None:
                    if damageEstimate[0] > worstCase:
                        worstCase = damageEstimate[0]
            switchNode = Tree()
            switchNode.data = "switch " + reservePkm.name
            switchNode.maximinScore = worstCase*-1
            switchRoot.children.append(switchNode)

        # traverse Tree with root switchRoot
        return switchTreeTraversalDFS(switchRoot)

    def find_best_move(self):
        bot_choice = self.find_best_switch()
        logger.debug("Switching: {}".format(bot_choice))
        return format_decision(self, bot_choice)
