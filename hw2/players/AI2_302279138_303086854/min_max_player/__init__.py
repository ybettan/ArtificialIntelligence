
#===============================================================================
# Imports
#===============================================================================

import abstract
from utils import INFINITY, run_with_limited_time, ExceededTimeError, \
        MiniMaxAlgorithm
from Reversi.consts import EM, OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS
import time
import copy
from collections import defaultdict
import sys

#===============================================================================
# Player
#===============================================================================

class Player(abstract.AbstractPlayer):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, \
                time_per_k_turns, k)
        self.clock = time.time()

        # We are simply providing (remaining time / remaining turns) for each \
        #       turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / \
                self.turns_remaining_in_round - 0.05

    def get_move(self, game_state, possible_moves):
        self.clock = time.time()
        self.time_for_current_move = self.time_remaining_in_round / \
                self.turns_remaining_in_round - 0.05

        #FIXME:remove
        assert(possible_moves)
        print("possible_moves =", possible_moves)

        if len(possible_moves) == 1:
            return possible_moves[0]

        curr_depth = 1
        mini_max = MiniMaxAlgorithm(self.utility, self.color, \
                self.no_more_time, None)

        # compute upper bound for the number of steps left
        max_steps_left = 0
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if game_state.board[x][y] == EM:
                    max_steps_left += 1

        # there is maximum max_steps_left steps in the game
        while curr_depth < max_steps_left:
            try:
                _, last_minimax_move = mini_max.search(game_state, \
                        curr_depth, True)
                #FIXME: remove
                print(last_minimax_move, "depth =", curr_depth, "val =", _)
                curr_depth += 1
            except ExceededTimeError:
                break

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.time() - self.clock)

        return last_minimax_move

    def utility(self, state):
        if len(state.get_possible_moves()) == 0:
            #FIXME:remove
            print("we shouldn't arrive here")
            sys.exit(1)
            return INFINITY if state.curr_player != self.color else -INFINITY

        my_u = 0
        op_u = 0
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if state.board[x][y] == self.color:
                    my_u += 1
                if state.board[x][y] == OPPONENT_COLOR[self.color]:
                    op_u += 1

        if my_u == 0:
            # I have no tools left
            return -INFINITY
        elif op_u == 0:
            # The opponent has no tools left
            return INFINITY
        else:
            return my_u - op_u
        
    def selective_deepening_criterion(self, state):
        # Simple player does not selectively deepen into certain nodes.
        return False

    def no_more_time(self):
        return (time.time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'min_max')

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player