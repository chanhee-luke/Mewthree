import constants

from showdown.battle import Battle
from copy import deepcopy

from data.parse_smogon_stats import MOVES_STRING
from data.helpers import get_pokemon_sets

from ..helpers import format_decision
from data.helpers import get_all_likely_moves
from showdown.engine.damage_calculator import _calculate_damage
from showdown.engine.damage_calculator import get_move

from .tree import Tree

from config import logger

from data import all_move_json

from showdown.engine.objects import StateMutator
from showdown.engine.select_best_move import get_payoff_matrix
from showdown.engine.select_best_move import remove_guaranteed_opponent_moves
from collections import defaultdict

def treeTraversalDFS(root):
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
            if highest == None:
                highest = node
            if highest.maximinScore < node.maximinScore:
                highest = node
        for child in node.children:
            check.append(child)

    if highest == None:
        return None
    return highest.data

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def attack_or_switch(self):
        if self.user.last_used_move[1].startswith("switch"):
            return "ATTACK"
        if self.user.active.hp == 0:
            return "SWITCH"
        waitingPkm = False;
        for pkm in self.user.reserve:
            if not pkm.fainted:
                waitingPkm = True
                break
        if not waitingPkm:
            return "ATTACK"
        battle_copy = deepcopy(self)
        battle_copy.opponent.lock_moves()
        try:
            pokemon_sets = get_pokemon_sets(battle_copy.opponent.active.name)
        except KeyError:
            logger.warning("No set for {}".format(battle_copy.opponent.active.name))
            return
        opponent_possible_moves = sorted(pokemon_sets[MOVES_STRING], key=lambda x: x[1], reverse=True)
        worstCaseDmgTaken = 0
        for move in opponent_possible_moves:
            if move[0].startswith("hiddenpower"):
                continue
            selfCopy = deepcopy(self)
            state = selfCopy.create_state()
            damageEstimate = _calculate_damage(state.opponent.active,state.self.active,move[0])
            if damageEstimate != None:
                if damageEstimate[0] > worstCaseDmgTaken:
                    worstCaseDmgTaken = damageEstimate[0]
        bestCaseDmgGiven = 0
        for move in self.user.active.moves:
            if move.name.startswith("hiddenpower"):
                continue
            selfCopy = deepcopy(self)
            state = selfCopy.create_state()
            attacking_move = deepcopy(all_move_json.get(move.name, None))

            attacking_type = attacking_move.get(constants.CATEGORY)
            if attacking_type == constants.STATUS:
                score = 40
            else:
                score = _calculate_damage(state.self.active,state.opponent.active,move.name)[0]
            if score != None:
                if score > bestCaseDmgGiven:
                    bestCaseDmgGiven = score
        if bestCaseDmgGiven >= worstCaseDmgTaken:
            return "ATTACK"
        else:
            return "SWITCH"



    def find_best_attack(self):
        #build tree
        attackRoot = Tree()
        # find worst case move used on each possible switched in Pokemon
        battle_copy = deepcopy(self)
        battle_copy.opponent.lock_moves()
        if self.user.active.hp == 0:
            return attackRoot
        for move in self.user.active.moves:
            if move.name.startswith("hiddenpower"):
                continue
            if move.current_pp == 0:
                continue
            selfCopy = deepcopy(self)
            state = selfCopy.create_state()
            attacking_move = deepcopy(all_move_json.get(move.name, None))

            attacking_type = attacking_move.get(constants.CATEGORY)
            if attacking_type == constants.STATUS:
                score = 25
            else:
                score = _calculate_damage(state.self.active,state.opponent.active,move.name)[0]
            switchNode = Tree()
            switchNode.data = move.name
            switchNode.maximinScore = score
            attackRoot.children.append(switchNode)
        return treeTraversalDFS(attackRoot)


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
            switchNode.maximinScore = worstCase*-0.667
            switchRoot.children.append(switchNode)

        # traverse Tree with root switchRoot
        return treeTraversalDFS(switchRoot)

    def find_best_move_milestone2(self):
        if self.attack_or_switch() is "ATTACK":
            print("ATTACK")
            bot_choice = self.find_best_attack()
        else:
            print("SWITCH")
            bot_choice = self.find_best_switch()
        logger.debug("Using: {}".format(bot_choice))
        return format_decision(self, bot_choice)
    
    def effi_move(battle, move, pokemon2, pokemon1, team):
        return None
        # to be further worked upon

    ################################################
    # Below is Milestone 3
    ################################################

    def pick_safest(self, score_lookup):
        # Helper function that gets rid of moves that have no option
        modified_score_lookup = remove_guaranteed_opponent_moves(score_lookup)
        if not modified_score_lookup:
            modified_score_lookup = score_lookup
        worst_case = defaultdict(lambda: (tuple(), float('inf')))

        # Simply selects the highest scoring move
        for move_pair, result in modified_score_lookup.items():
            if worst_case[move_pair[0]][1] > result:
                worst_case[move_pair[0]] = move_pair, result

        safest = max(worst_case, key=lambda x: worst_case[x][1])
        return worst_case[safest]


    def pick_bfs_safest_move(self, battle):

        state = battle.create_state()
        mutator = StateMutator(state)
        user_options, opponent_options = battle.get_all_options()
        logger.debug("Attempting to find best move from: {}".format(mutator.state))

        # Builds a tree to search for opponent's moves
        scores = get_payoff_matrix(mutator, user_options, opponent_options, depth=3, prune=True)

        logger.debug(f"Scores: {scores}")
        
        decision, payoff = self.pick_safest(scores)
        bot_choice = decision[0]
        logger.debug(f"Safest: {bot_choice}, {payoff}")
        return bot_choice
    

    def find_best_move(self):
        battles = self.prepare_battles(join_moves_together=True)
        bot_choice = self.pick_bfs_safest_move(battles[0])
        return format_decision(self, bot_choice)
    
    
    ################################################
    # Below is Milestone 4
    ################################################

    #helper function for calculating stats
    def stat_calculation(base, level, ev):
        # calculating stats from base stat, level, and ev
        return floor(((2 * base + 31 + floor(ev / 4)) * level) / 100 + 5)

    def pokemonEfficiency(battle, pokemon1, pokemon2, team):
        # comparing efficiency of user pokemon vs opponent pokemon
        # if efficiency of pokemon is greater than 150, the other pokemon's efficiency isn't taken
        # also note: pokemonEfficiency(a, b, team_a) = - pokemonEfficiency(b, a, team_b)
        efficiency1 = 0
        efficiency2 = 0

        pokemon1_stat = stat_calculation(pokemon1.stats["spe"], pokemon1.level, 252) * pokemon1.buff_affect("spe")
        pokemon2_stat = stat_calculation(pokemon2.stats["spe"], pokemon2.level, 252) * pokemon2.buff_affect("spe")

        for move in pokemon1.moves:
            dmg = effi_move(battle, move, pokemon1, pokemon2, team)
            if efficiency1 < dmg:
                efficiency1 = dmg

        if efficiency1 >= comparator_calculation(150, pokemon1, pokemon2) and pokemon1_stat > pokemon2_stat:
            return efficiency1

        for move in pokemon2.moves:
            dmg = effi_move(battle, move, pokemon2, pokemon1, team)
            if efficiency2 < dmg:
                efficiency2 = dmg

        if efficiency2 >= comparator_calculation(150, pokemon1, pokemon2) and pokemon2_stat > pokemon1_stat:
            return -efficiency2

        return efficiency1 - efficiency2

    def make_best_order(self, battle):
        #returns users list of pokemons sorted by efficiency

        team = battle.user
        opponent = battle.opponent

        orderedTeam = []

        for i, pokemon in enumerate(team.reserve):
            avgEfficiency = 0

            for enemy_pokemon in opponent.reserve:

                efficiency = -1024
                efficiency = pokemonEfficiency(battle, pokemon, enemy_pokemon, opponent)
                avgEfficiency += efficiency

            avgEfficiency /= 6
            orderedTeam.append([i + 1, avgEfficiency])
            orderedTeam.sort(key=lambda x: x[1], reverse=True)

        return orderedTeam
