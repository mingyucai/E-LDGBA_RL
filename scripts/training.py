import numpy as np
import random


# TODO: Define an abstract class for the MDP and ELDGBA
class LCRL:
    """
more details can be find in: https://arxiv.org/abs/2010.06797
    Attributes
    ----------
    MDP : an object from ./environments
        MDP object has to have the following properties
        (1) countably finite state and action spaces
        (2) a "step(action)" function describing the dynamics
        (3) a "state_label(state)" function that maps states to labels
        (4) a "reset()" function that resets the state to an initial state
        (5) current state of the MDP is "current_state"
        (6) action space is "action_space" and all actions are enabled in each state
    LDBA : an object from ./automata
        an automaton

    reward : array, shape=(n_pairs,n_qs,n_rows,n_cols)
        The reward function of the star-MDP. self.reward[state] = 1-discountB if 'state' belongs to B, 0 otherwise.

    discount : float
        The discount factor.

    discountB : float
        The discount factor applied to accepting states.

    """

    def __init__(
            self, MDP=None,
            LDBA=None,
            discount_factor=0.9,
            learning_rate=0.9,
            epsilon=0.15,
                ):
        if MDP is None:
            raise Exception("LCRL expects MDP as an input")
        self.MDP = MDP
        if LDBA is None:
            raise Exception("LCRL expects LDBA as an input")
        self.LDBA = LDBA
        self.epsilon_transitions_exists = 'epsilon' in self.LDBA.assignment.keys()
        #self.gamma = discount_factor
        self.discount = 0.99999
        self.discountB = 0.99
        self.alpha = learning_rate
        self.epsilon = epsilon
        self.path_length = []
        self.Q = {}
        self.Q_initial_value = 0
        # ##### testing area ##### #
        self.test = False

    def train_ql(
            self, number_of_episodes,
            iteration_threshold,
            Q_initial_value=0
                ):
        self.MDP.reset()
        self.LDBA.reset()
        self.Q_initial_value = Q_initial_value

        # product MDP: synchronise the MDP state with the automaton state
        current_state = self.MDP.current_state + [self.LDBA.automaton_state]
        product_MDP_action_space = self.MDP.action_space
        epsilon_transition_taken = False

        # check for epsilon-transitions at the current automaton state
        if self.epsilon_transitions_exists:
            product_MDP_action_space = self.action_space_augmentation()

        # initialise Q-value outside the main loop
        self.Q[str(current_state)] = {}
        for action_index in range(len(product_MDP_action_space)):
            self.Q[str(current_state)][product_MDP_action_space[action_index]] = Q_initial_value

        # main loop
        episode = 0
        self.path_length = [float("inf")]
        while episode < number_of_episodes:
            episode += 1
            self.MDP.reset()
            self.LDBA.reset()
            current_state = self.MDP.current_state + [self.LDBA.automaton_state]

            # check for epsilon-transitions at the current automaton state
            if self.epsilon_transitions_exists:
                product_MDP_action_space = self.action_space_augmentation()

            Q_at_initial_state = []
            for action_index in range(len(product_MDP_action_space)):
                Q_at_initial_state.append(self.Q[str(current_state)][product_MDP_action_space[action_index]])
            print('episode:' + str(episode) +
                  ', value function at s_0='+str(max(Q_at_initial_state)) +
                  ', trace length='+str(self.path_length[len(self.path_length)-1]))
            iteration = 0
            path = current_state
            reset_number = 0
            # each episode loop
            while iteration < iteration_threshold: #and \
                    #self.LDBA.automaton_state != -1: #and \
                    #self.LDBA.accepting_frontier_set:
                iteration += 1

                # find the action with max Q at the current state
                Qs = []
                for action_index in range(len(product_MDP_action_space)):
                    Qs.append(self.Q[str(current_state)][product_MDP_action_space[action_index]])
                maxQ_action_index = random.choice(np.where(Qs == np.max(Qs))[0])
                maxQ_action = product_MDP_action_space[maxQ_action_index]

                # check if an epsilon-transition is taken
                if self.epsilon_transitions_exists and \
                        maxQ_action_index > len(self.MDP.action_space)-1:
                    epsilon_transition_taken = True

                # product MDP modification (for more details refer to https://bit.ly/LCRL_CDC_2019)
                if epsilon_transition_taken:
                    next_MDP_state = self.MDP.current_state
                    next_automaton_state = self.LDBA.step(maxQ_action)
                else:
                    # epsilon-greedy policy
                    if random.random() < self.epsilon:
                        next_MDP_state = self.MDP.step(random.choice(self.MDP.action_space))
                    else:
                        next_MDP_state = self.MDP.step(maxQ_action)
                    next_automaton_state = self.LDBA.step(self.MDP.state_label(next_MDP_state))

                # product MDP: synchronise the automaton with MDP
                next_state = next_MDP_state + [next_automaton_state]
                if self.test:
                    print(str(maxQ_action)+' | '+str(next_state)+' | '+str(next_automaton_state))

                # check for epsilon-transitions at the next automaton state
                if self.epsilon_transitions_exists:
                    product_MDP_action_space = self.action_space_augmentation()

                # Q values of the next state
                Qs_prime = []
                if str(next_state) not in self.Q.keys():
                    self.Q[str(next_state)] = {}
                    for action_index in range(len(product_MDP_action_space)):
                        self.Q[str(next_state)][product_MDP_action_space[action_index]] = Q_initial_value
                        Qs_prime.append(Q_initial_value)
                else:
                    for action_index in range(len(product_MDP_action_space)):
                        Qs_prime.append(self.Q[str(next_state)][product_MDP_action_space[action_index]])

                # update the accepting frontier set
                if not epsilon_transition_taken:
                    reward_flag = self.LDBA.accepting_frontier_function(next_automaton_state)
                else:
                    reward_flag = 0
                    epsilon_transition_taken = False

                if not self.LDBA.accepting_frontier_set:
                    reset_number += 1


                # Q update
                R,  self.gamma = self.reward(reward_flag)
                self.Q[str(current_state)][maxQ_action] = \
                    (1 - self.alpha) * self.Q[str(current_state)][maxQ_action] + \
                    self.alpha * (R + self.gamma * np.max(Qs_prime))

                # update the state
                current_state = next_state
                path.append(current_state)

            if not self.LDBA.check_accepting_set:
                self.path_length.append(float("inf"))
            else:
                self.path_length.append(len(path))
                print('reset_number: ', reset_number)

# dependent reward and discount function
    def reward(self, reward_flag):
        if reward_flag > 0:
            R = 1-self.discountB
            gamma = self.discountB
            return R, gamma
        elif reward_flag < 0:
            gamma = self.discount
            return 0, gamma
        else:
            gamma = self.discount
            return 0, gamma

    def action_space_augmentation(self):
        if self.LDBA.automaton_state in self.LDBA.assignment['epsilon'].keys():
            product_MDP_action_space = self.MDP.action_space + \
                self.LDBA.assignment['epsilon'][self.LDBA.automaton_state]
        else:
            product_MDP_action_space = self.MDP.action_space
        return product_MDP_action_space
