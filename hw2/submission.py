import random, util
from game import Agent
import numpy as np
import time
# this is OK according to staff
from ghostAgents import GhostAgent, RandomGhost, DirectionalGhost

#     ********* Reflex agent- sections a and b *********
class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.
  """
  def __init__(self):
    self.lastPositions = []
    self.dc = None
    self.time_total_actions = 0
    self.num_actions = 0

  def getAction(self, gameState):
    """
    getAction chooses among the best options according to the evaluation function.

    getAction takes a GameState and returns some Directions.X for some X in the set {North, South, West, East, Stop}
    ------------------------------------------------------------------------------
    """

    start = time.time()

    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    end = time.time()

    # update meta data
    self.time_total_actions += (end-start)
    self.num_actions += 1

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    The evaluation function takes in the current GameState (pacman.py) and the proposed action
    and returns a number, where higher numbers are better.
    """
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    # FIXME: make sure it is on betterEvaluationFunciton
    #return scoreEvaluationFunction(successorGameState)
    return betterEvaluationFunction(successorGameState)


#     ********* Evaluation functions *********

def scoreEvaluationFunction(gameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.
  """
  return gameState.getScore()

######################################################################################
# b: implementing a better heuristic function

def isTerminalState(gameState):

    #  getLegalPacmanActions() return [] if the state isWin or isLose so we
    #  don't need to check it separetly.
    return len(gameState.getLegalPacmanActions()) == 0

def betterEvaluationFunction(gameState):
  """

  The betterEvaluationFunction takes in a GameState (pacman.py) and should return a number, where higher numbers are better.

  A GameState specifies the full game state, including the food, capsules, agent configurations and more.
  Following are a few of the helper methods that you can use to query a GameState object to gather information about
  the present state of Pac-Man, the ghosts and the maze:

  gameState.getLegalActions():
  gameState.getPacmanState():
  gameState.getGhostStates():
  gameState.getNumAgents():
  gameState.getScore():
  The GameState class is defined in pacman.py and you might want to look into that for other helper methods.
  """
  return betterEvaluationFunction_bestButSlower(gameState)
  #return betterEvaluationFunction_notBestButFaster(gameState)


def betterEvaluationFunction_bestButSlower(gameState):

    # return the utility function values on terminal states
    if isTerminalState(gameState):
        return gameState.getScore()

    pacman_position = gameState.getPacmanPosition()

    # compute the manhatan distance to the closest piece of food
    min_food_dist = np.inf
    for food_position in gameState.getFood().asList():
        dist = util.manhattanDistance(food_position, pacman_position)
        min_food_dist = min(min_food_dist, dist)

    # compute the manhatan distance to the closest capsule
    min_capsule_dist = np.inf
    for capsule_position in gameState.getCapsules():
        dist = util.manhattanDistance(capsule_position, pacman_position)
        min_capsule_dist = min(min_capsule_dist, dist)

    # compute the manhatan distance to the closest ghost
    min_ghost_dist = np.inf
    index = 0
    for ghost_position in gameState.getGhostPositions():
        dist = util.manhattanDistance(ghost_position, pacman_position)
        if (dist < min_ghost_dist):
            min_ghost_dist = dist
            min_ghost_id = index
        index += 1
    # prevent dividing by 0
    if (min_ghost_dist == 0):
        min_ghost_dist = 1

    # check if we wan't to get closer to the closes ghost
    num_ghosts = len(gameState.getGhostStates())
    if num_ghosts > 0:
        is_closes_ghost_vulnerable = gameState.getGhostState(index).scaredTimer > 0
        if is_closes_ghost_vulnerable:
            ghost_factor = 30
        else:
            ghost_factor = -30
    else:
        ghost_factor = 0

    # FIXME: remove the randomness? I think we want the heuristic to be
    # deterimistic and let the search algorithm to do the randomness
    # Combination of the above calculated metrics.
    return gameState.getScore() + \
            (1/float(min_food_dist)) + \
            (1/float(min_capsule_dist)) + \
            ghost_factor * (1/float(min_ghost_dist)) + \
            np.random.choice([0, 1], p=[0.85, 0.15])


#FIXME: remove when done if not used
def betterEvaluationFunction_notBestButFaster(gameState):

    # return the utility function values on terminal states
    if isTerminalState(gameState):
        return gameState.getScore()

    pacman_position = gameState.getPacmanPosition()

    # compute the manhatan distance to the closest piece of food
    min_food_dist = np.inf
    for food_position in gameState.getFood().asList():
        dist = util.manhattanDistance(food_position, pacman_position)
        min_food_dist = min(min_food_dist, dist)

    # compute the manhatan distance to the closest capsule
    min_capsule_dist = np.inf
    for capsule_position in gameState.getCapsules():
        dist = util.manhattanDistance(capsule_position, pacman_position)
        min_capsule_dist = min(min_capsule_dist, dist)

    # compute the manhatan distance to each ghost
    ghost_all_dists = []
    for ghost_position in gameState.getGhostPositions():
        dist = util.manhattanDistance(ghost_position, pacman_position)
        # prevent dividing by 0
        if (dist == 0):
            dist = 1
        ghost_all_dists.append(dist)

    # check if we wan't to get closer to each ghost
    ghost_all_vulnerabilities = []
    for ghost_state in gameState.getGhostStates():
        if ghost_state.scaredTimer > 0:
            ghost_all_vulnerabilities.append(20)
        else:
            ghost_all_vulnerabilities.append(-20)

    # compute the total bonus for ghosts closnes
    ghosts_score = 0
    for i in range(len(ghost_all_dists)):
        ghosts_score += 1/float(ghost_all_dists[i]*ghost_all_vulnerabilities[i])

    # Combination of the above calculated metrics.
    return gameState.getScore() + \
            (1/float(min_food_dist)) + \
            (1/float(min_capsule_dist)) + \
            ghosts_score + \
            np.random.choice([0, 1], p=[0.85, 0.15])


#     ********* MultiAgent Search Agents- sections c,d,e,f*********

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxAgent, AlphaBetaAgent & both ExpectimaxAgents.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'betterEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)
    self.time_total_actions = 0
    self.num_actions = 0

######################################################################################
# c: implementing minimax

#FIXME: use multiproccessing if i have time for competition
class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent
    """

    def rbMinimax(self, gameState, agent, depth):

        # for terminal state or depth reached we will return the huristic estimation
        if isTerminalState(gameState) or depth == 0:
            return self.evaluationFunction(gameState)

        # get all successor states
        legal_action = gameState.getLegalActions(agent)
        childrens = [gameState.generateSuccessor(agent, action) for action in legal_action]

        # find the next agent modulo the number of agents
        next_agent = (agent + 1) % gameState.getNumAgents()

        # update the depth if we finished a full round of turns
        # pacmang, ..., last ghost
        if next_agent == 0:
            next_depth = depth - 1
        else:
            next_depth = depth

        # pacman turn
        if agent == 0:
            cur_max = -np.inf
            for c in childrens:
                v = self.rbMinimax(c, next_agent, next_depth)
                cur_max = max(cur_max, v)
            return cur_max

        # ghost turn
        else:
            cur_min = np.inf
            for c in childrens:
                v = self.rbMinimax(c, next_agent, next_depth)
                cur_min = min(cur_min, v)
            return cur_min


    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction. Terminal states can be found by one of the following:
          pacman won, pacman lost or there are no legal moves.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          Directions.STOP:
            The stop direction

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game

          gameState.getScore():
            Returns the score corresponding to the current state of the game

          gameState.isWin():
            Returns True if it's a winning state

          gameState.isLose():
            Returns True if it's a losing state

          self.depth:
            The depth to which search should continue

        """

        # BEGIN_YOUR_CODE

        start = time.time()

        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # find the next agent modulo the number of agents
        next_agent = 1 % gameState.getNumAgents()

        # update the depth if we finished a full round of turns
        # pacmang, ..., last ghost
        if next_agent == 0:
            next_depth = self.depth - 1
        else:
            next_depth = self.depth
        # according to staff we can assume that the game won't be launched with
        # 0 ghosts and with depth=0 therefor next_depth >= 0

        # Choose one of the best actions
        scores = [self.rbMinimax(gameState.generatePacmanSuccessor(action), \
                next_agent, next_depth) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        end = time.time()

        # update meta data
        self.time_total_actions += (end-start)
        self.num_actions += 1

        return legalMoves[chosenIndex]

      # END_YOUR_CODE


######################################################################################
# d: implementing alpha-beta

#FIXME: use multiproccessing if i have time for competition
class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning
    """

    def rbAlphaBeta(self, gameState, agent, depth, alpha, beta):

        # for terminal state or depth reached we will return the huristic estimation
        if isTerminalState(gameState) or depth == 0:
            return self.evaluationFunction(gameState)

        #FIXME: improvment - if there is only one possible acction return it,
        # don't need to genereate successor or to compute minmax value
        # get all successor states
        legal_action = gameState.getLegalActions(agent)
        #FIXME: sort children according to heuristic value for the competition
        childrens = [gameState.generateSuccessor(agent, action) for action in legal_action]

        # find the next agent modulo the number of agents
        next_agent = (agent + 1) % gameState.getNumAgents()

        # update the depth if we finished a full round of turns
        # pacmang, ..., last ghost
        if next_agent == 0:
            next_depth = depth - 1
        else:
            next_depth = depth

        # pacman turn
        if agent == 0:
            cur_max = -np.inf
            for c in childrens:
                v = self.rbAlphaBeta(c, next_agent, next_depth, alpha, beta)
                cur_max = max(cur_max, v)
                alpha = max(alpha, cur_max)
                if cur_max >= beta:
                    return np.inf
            return cur_max

        # ghost turn
        else:
            cur_min = np.inf
            for c in childrens:
                v = self.rbAlphaBeta(c, next_agent, next_depth, alpha, beta)
                cur_min = min(cur_min, v)
                beta = min(beta, cur_min)
                if cur_min <= alpha:
                    return -np.inf
            return cur_min

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """

        # BEGIN_YOUR_CODE

        start = time.time()

        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # find the next agent modulo the number of agents
        next_agent = 1 % gameState.getNumAgents()

        # update the depth if we finished a full round of turns
        # pacmang, ..., last ghost
        if next_agent == 0:
            next_depth = self.depth - 1
        else:
            next_depth = self.depth
        # according to staff we can assume that the game won't be launched with
        # 0 ghosts and with depth=0 therefor next_depth >= 0

        alpha = -np.inf

        #FIXME: sort children according to heuristic value for the competition
        # Choose one of the best actions
        scores = []
        for action in legalMoves:
            c = gameState.generatePacmanSuccessor(action)
            v = self.rbAlphaBeta(c, next_agent, next_depth, alpha, np.inf)
            scores.append(v)
            alpha = max(alpha, v)
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        end = time.time()

        # update meta data
        self.time_total_actions += (end-start)
        self.num_actions += 1

        return legalMoves[chosenIndex]

        # END_YOUR_CODE

######################################################################################
# e: implementing random expectimax

def rbExpectimax(gameState, agent, depth, multiAgent, ghostType):

    assert(ghostType == 'random_ghost' or ghostType == 'directional_ghost')

    # for terminal state or depth reached we will return the huristic estimation
    if isTerminalState(gameState) or depth == 0:
        return multiAgent.evaluationFunction(gameState)

    # find the next agent modulo the number of agents
    next_agent = (agent + 1) % gameState.getNumAgents()

    # update the depth if we finished a full round of turns
    # pacmang, ..., last ghost
    if next_agent == 0:
        next_depth = depth - 1
    else:
        next_depth = depth

    # create a ghost agent to access its distribution
    if ghostType == 'random_ghost':
        ghostAgent = RandomGhost(agent)
    else:
        ghostAgent = DirectionalGhost(agent)

    # pacman - maximinzing
    if agent == 0:
        cur_max = -np.inf
        legal_action = gameState.getLegalActions(agent)
        for action in legal_action:
            c = gameState.generateSuccessor(agent, action)
            v = rbExpectimax(c, next_agent, next_depth, multiAgent, ghostType)
            cur_max = max(cur_max, v)
        return cur_max

    # ghost - tohelet
    else:
        tohelet = 0
        dist = ghostAgent.getDistribution(gameState)
        for action, prob in dist.items():
            c = gameState.generateSuccessor(agent, action)
            v = rbExpectimax(c, next_agent, next_depth, multiAgent, ghostType)
            tohelet += v * prob
        return tohelet


class RandomExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction
          All ghosts should be modeled as choosing uniformly at random from their legal moves.
        """

        # BEGIN_YOUR_CODE

        start = time.time()

        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # find the next agent modulo the number of agents
        next_agent = 1 % gameState.getNumAgents()

        # update the depth if we finished a full round of turns
        # pacmang, ..., last ghost
        if next_agent == 0:
            next_depth = self.depth - 1
        else:
            next_depth = self.depth
        # according to staff we can assume that the game won't be launched with
        # 0 ghosts and with depth=0 therefor next_depth >= 0

        # Choose one of the best actions
        scores = [rbExpectimax(gameState.generatePacmanSuccessor(action), \
                next_agent, next_depth, self, 'random_ghost') for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        end = time.time()

        # update meta data
        self.time_total_actions += (end-start)
        self.num_actions += 1

        return legalMoves[chosenIndex]

        # END_YOUR_CODE

######################################################################################
# f: implementing directional expectimax

class DirectionalExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction
          All ghosts should be modeled as using the DirectionalGhost distribution
          to choose from their legal moves.
        """

        # BEGIN_YOUR_CODE

        start = time.time()

        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # find the next agent modulo the number of agents
        next_agent = 1 % gameState.getNumAgents()

        # update the depth if we finished a full round of turns
        # pacmang, ..., last ghost
        if next_agent == 0:
            next_depth = self.depth - 1
        else:
            next_depth = self.depth
        # according to staff we can assume that the game won't be launched with
        # 0 ghosts and with depth=0 therefor next_depth >= 0

        # Choose one of the best actions
        scores = [rbExpectimax(gameState.generatePacmanSuccessor(action), \
                next_agent, next_depth, self, 'directional_ghost') for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        end = time.time()

        # update meta data
        self.time_total_actions += (end-start)
        self.num_actions += 1

        return legalMoves[chosenIndex]

        # END_YOUR_CODE


######################################################################################
# I: implementing competition agent

class CompetitionAgent(MultiAgentSearchAgent):
  """
    Your competition agent
  """

  def getAction(self, gameState):
    """
      Returns the action using self.depth and self.evaluationFunction

    """

    # BEGIN_YOUR_CODE
    raise Exception("Not implemented yet")
    # END_YOUR_CODE



