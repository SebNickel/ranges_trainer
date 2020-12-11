import os
from collections import OrderedDict
import itertools
import functools
import numpy as np
import pickle
import json


class Model:

    def __init__(self, range_dict_list_filepath=os.path.join(os.getcwd(), 'range_dicts', 'range_dict_list.json')):

        self.range_dict_list_filepath = range_dict_list_filepath
        with open(self.range_dict_list_filepath, 'r') as f:
            self.range_dict_list = json.load(f)
        self.current_range_dict_list_index = 0
        self.load_range_dict()
        self.editing_mode = False

        self.check_default_radio_buttons()

        self.range_entered = np.zeros((13, 13), dtype=bool)
        self.incorrectly_checked = np.zeros((13, 13), dtype=bool)
        self.incorrectly_left_unchecked = np.zeros((13, 13), dtype=bool)
        self.correctly_checked = np.zeros((13, 13), dtype=bool)
        self.copied_range = None

        self.card_ranks = 'AKQJT98765432'

        # Hand quiz stuff
        self.randomize_range_in_hand_quiz = False
        self.hand_quiz_marginal_hands_only = True
        self.hand_quiz_hand_indices = (0, 0)
        # TODO: Hardwired dicts for testing. Make flexible.
        self.hand_quiz_answer_dict = answers_dict
        self.prior_action_dict = create_prior_action_dict()
        self.alternative_actions_dict = alternatives_dict
        self.action_to_quiz_option_dict = action_to_quiz_option_dict

    @property
    def reference_range(self):

        range_dict = self.__reference_range_dict
        for label in self.range_dict_schema.keys():
            key = self.current_radio_button_setting[label]
            if type(range_dict[key]) is dict:
                range_dict = range_dict[key]
            else:
                return range_dict[key]

    def set_radio_button_setting(self, label_index_dict):

        self.current_radio_button_setting = {label: self.range_dict_schema[label][index]
                                             for label, index in label_index_dict.items()}

    @property
    def applicable_radio_buttons(self):

        applicable_dict = {label: [] for label in self.range_dict_schema.keys()}

        range_dict = self.__reference_range_dict
        for i, label in enumerate(self.range_dict_schema.keys()):
            if i == 0:
                applicable_dict[label] = self.range_dict_schema[label]
            else:
                applicable_dict[label] = list(range_dict.keys())
            key = self.current_radio_button_setting[label]
            if key not in list(range_dict.keys()):
                key = list(range_dict.keys())[0]
            if type(range_dict[key]) is dict:
                range_dict = range_dict[key]
            else:
                break

        return applicable_dict

    def check_default_radio_buttons(self):

        self.current_radio_button_setting = OrderedDict([(label, self.range_dict_schema[label][0])
                                                         for label in self.range_dict_schema.keys()])

    # TODO: This will need to change
    # def create_new_empty_reference_range_dict(self):
    #
    #     self.__reference_range_dict = {}
    #     for hero_pos_label in self.position_labels:
    #         self.__reference_range_dict[hero_pos_label] = {}
    #         for action_label in self.action_labels:
    #             if action_label in {'RFI', 'Limp-fold', 'Limp-call', 'Limp-3bet'}:
    #                 self.__reference_range_dict[hero_pos_label][action_label] = np.zeros((13, 13), dtype=bool)
    #             else:
    #                 self.__reference_range_dict[hero_pos_label][action_label] = {}
    #                 for villain_pos_label in self.position_labels:
    #                     self.__reference_range_dict[hero_pos_label][action_label][villain_pos_label] = \
    #                         np.zeros((13, 13), dtype=bool)

    def load_range_dict(self):

        range_dict_descriptor = self.range_dict_list[self.current_range_dict_list_index]
        if range_dict_descriptor['Filepath'] is not None:
            with open(range_dict_descriptor['Filepath'], 'rb') as f:
                self.__top_level_dict = pickle.load(f)
            self.range_dict_schema = self.__top_level_dict['schema']
            self.__reference_range_dict = self.__top_level_dict['contents']
        else:
            # TODO
            pass
            # self.create_new_empty_reference_range_dict()

    def save_range_dict(self, target_path):

        with open(target_path, 'wb') as f:
            pickle.dump(self.__top_level_dict, f)

    def save_range_dict_list(self):

        with open(self.range_dict_list_filepath, 'w') as f:
            json.dump(self.range_dict_list, f, indent=4)

    def alternative_action_range(self, alternative_action):

        current_hero_pos_setting = self.current_radio_button_setting['Position']
        current_villain_pos_setting = self.current_radio_button_setting['VS']

        hero_pos_action = self.__reference_range_dict[current_hero_pos_setting][alternative_action]
        if type(hero_pos_action) is not dict:
            return hero_pos_action
        else:
            return hero_pos_action[current_villain_pos_setting]

    def range_of_quiz_answer(self, selected_option):

        if selected_option in {'Fold', 'Check'}:
            return ValueError('"{}" is not handled by this method.'.format(selected_option))

        current_action_setting = self.current_radio_button_setting['Action']

        if selected_option in {'3bet', '4bet', 'Limp/fold', 'Limp/call', 'Limp/3bet'}:
            return self.alternative_action_range(selected_option)
        elif selected_option == 'Raise':
            assert current_action_setting in {'RFI', 'Raise vs limp'}
            return self.reference_range
        elif selected_option == 'Call':
            if current_action_setting == '3bet':
                return self.alternative_action_range('Call RFI')
            elif current_action_setting == '4bet':
                return self.alternative_action_range('Call 3bet')

    @property
    def hand_quiz_correct_action(self):

        current_action_setting = self.current_radio_button_setting['Action']

        if self.reference_range[self.hand_quiz_hand_indices]:
            return current_action_setting

        alternative_actions = self.alternative_actions_dict[current_action_setting]
        for alternative_action in alternative_actions:
            alternative_action_range = self.alternative_action_range(alternative_action)
            if alternative_action_range[self.hand_quiz_hand_indices]:
                return alternative_action

        if current_action_setting == 'Raise vs limp':
            return 'Check'
        else:
            return 'Fold'

    def translate_quiz_answer(self, selected_option):

        if selected_option in self.range_dict_schema['Action']:
            return selected_option

        if selected_option in {'Fold', 'Check'}:
            return selected_option

        current_action_setting = self.current_radio_button_setting['Action']

        if selected_option == 'Call':
            if current_action_setting in {'Call RFI', '3bet'}:
                return 'Call RFI'
            elif current_action_setting in {'Call 3bet', '4bet'}:
                return 'Call 3bet'

        if selected_option == 'Raise':
            if current_action_setting == 'RFI':
                return 'RFI'
            elif current_action_setting == 'Raise vs limp':
                return 'Raise vs limp'

        raise ValueError("I'm not programmed for this :(")

    def hand_quiz_answer_is_correct(self, selected_option: str):
        # TODO: Must be made more flexible.
        selected_action = self.translate_quiz_answer(selected_option)

        current_action_setting = self.current_radio_button_setting['Action']

        if selected_action == current_action_setting:
            return self.reference_range[self.hand_quiz_hand_indices]
        elif selected_action not in {'Fold', 'Check'}:
            range_of_selected_action = self.alternative_action_range(selected_action)
            return range_of_selected_action[self.hand_quiz_hand_indices]
        elif selected_action == 'Check':
            return not self.reference_range[self.hand_quiz_hand_indices]
        else:
            assert selected_action == 'Fold'
            return not self.combined_alternatives_range[self.hand_quiz_hand_indices]

    @property
    def combined_alternatives_range(self):

        current_action_setting = self.current_radio_button_setting['Action']
        alternative_actions = self.alternative_actions_dict[current_action_setting]

        if len(alternative_actions) == 0:
            return self.reference_range

        applicable_actions = alternative_actions + [current_action_setting]
        alternative_ranges = [self.alternative_action_range(applicable_action)
                              for applicable_action in applicable_actions]

        return functools.reduce(np.logical_or, alternative_ranges)

    def quiz_feedback_range(self, selected_option):

        if selected_option not in {'Fold', 'Check'}:
            return self.range_of_quiz_answer(selected_option)
        elif selected_option == 'Check':
            return self.reference_range
        else:
            return self.combined_alternatives_range

    @property
    def marginal_index_pairs(self):

        current_hero_pos_setting = self.current_radio_button_setting['Position']
        current_action_setting = self.current_radio_button_setting['Action']
        current_villain_pos_setting = self.current_radio_button_setting['VS']

        if current_action_setting in {'RFI', 'Raise vs limp'}:
            return marginal_index_pairs(self.reference_range)
        elif current_action_setting in {'Call RFI', '3bet'}:
            calling_range = self.__reference_range_dict[current_hero_pos_setting]['Call RFI'][current_villain_pos_setting]
            three_betting_range = self.__reference_range_dict[current_hero_pos_setting]['3bet'][current_villain_pos_setting]
            calling_range_marginal = marginal_index_pairs(calling_range)
            three_betting_range_marginal = marginal_index_pairs(three_betting_range)
            return list(set(calling_range_marginal + three_betting_range_marginal))
        elif current_action_setting in {'Call 3bet', '4bet'}:
            calling_range = self.__reference_range_dict[current_hero_pos_setting]['Call 3bet'][current_villain_pos_setting]
            four_betting_range = self.__reference_range_dict[current_hero_pos_setting]['4bet'][current_villain_pos_setting]
            calling_range_marginal = marginal_index_pairs(calling_range)
            four_betting_range_marginal = marginal_index_pairs(four_betting_range)
            return list(set(calling_range_marginal + four_betting_range_marginal))
        elif current_action_setting in {'Limp/fold', 'Limp/call', 'Limp/3bet'}:
            lf_range = self.__reference_range_dict[current_hero_pos_setting]['Limp/fold'][current_villain_pos_setting]
            lc_range = self.__reference_range_dict[current_hero_pos_setting]['Limp/call'][current_villain_pos_setting]
            l3_range = self.__reference_range_dict[current_hero_pos_setting]['Limp/3bet'][current_villain_pos_setting]
            lf_range_marginal = marginal_index_pairs(lf_range)
            lc_range_marginal = marginal_index_pairs(lc_range)
            l3_range_marginal = marginal_index_pairs(l3_range)
            return list(set(lf_range_marginal + lc_range_marginal + l3_range_marginal))
        else:
            raise ValueError("I'm not programmed for this :(")


def marginal_index_pairs(hand_range: np.ndarray):

    index_pairs = []

    for i in range(13):
        for j in range(13):

            value = hand_range[i, j]

            adjacent_row_indices = []
            adjacent_column_indices = []
            if i > 0:
                adjacent_row_indices.append(i - 1)
            if i < 12:
                adjacent_row_indices.append(i + 1)
            if j > 0:
                adjacent_column_indices.append(j - 1)
            if j < 12:
                adjacent_column_indices.append(j + 1)
            neighbors = itertools.product(adjacent_row_indices, adjacent_column_indices)

            is_marginal = False
            for neighbor in neighbors:
                if hand_range[neighbor] != value:
                    is_marginal = True
                    break

            if is_marginal:
                index_pairs.append((i, j))

    return index_pairs


# TODO: Here's a hardwired dict that assigns "Prior action" strings to radio button settings. Add non-hardwired
# implementation. THIS ONE IS STRICTLY FOR 6MAX.
def create_prior_action_dict():

    pa_dict = {'UTG_RFI': 'None (First to act)',
               'RFI': 'Folded down.',
               'Call RFI': {},
               '3bet': {},
               'Call 3bet': {},
               '4bet': {},
               'Limp/fold': 'Folded down.',
               'Limp/call': 'Folded down.',
               'Limp/3bet': 'Folded down.',
               'Raise vs limp': 'SB limps.'}

    positions = ['UTG', 'HJ', 'CO', 'BN', 'SB', 'BB']
    for villain_pos in positions:
        if villain_pos != 'BB':
            pa_dict['Call RFI'][villain_pos] = '{} opens.'.format(villain_pos)
            pa_dict['3bet'][villain_pos] = '{} opens.'.format(villain_pos)
        if villain_pos != 'UTG':
            pa_dict['Call 3bet'][villain_pos] = 'Hero opens. {} 3bets.'.format(villain_pos)
            pa_dict['4bet'][villain_pos] = 'Hero opens. {} 3bets.'.format(villain_pos)

    return pa_dict


# Nother temporary hardwired dict:
options_dict = {
    'RFI': ['Raise', 'Fold'],
    'Call RFI': ['Call', '3bet', 'Fold'],
    '3bet': ['Call', '3bet', 'Fold'],
    'Limp/fold': ['Limp/fold', 'Limp/call', 'Limp/3bet', 'Fold'],
    'Limp/call': ['Limp/fold', 'Limp/call', 'Limp/3bet', 'Fold'],
    'Limp/3bet': ['Limp/fold', 'Limp/call', 'Limp/3bet', 'Fold'],
    'Raise vs limp': ['Raise', 'Check'],
    '4bet': ['4bet', 'Fold']  # There's no "Call" option here because I'm testing this with a somewhat incomplete range_dict.
}

correct_options_if_in_range_dict = {
    'RFI': 'Raise',
    'Call RFI': 'Call',
    '3bet': '3bet',
    'Limp/fold': 'Limp/fold',
    'Limp/call': 'Limp/call',
    'Limp/3bet': 'Limp/3bet',
    'Raise vs limp': 'Raise',
    '4bet': '4bet'
}


answers_dict = {'options': options_dict,
                'correct_option_if_in_range': correct_options_if_in_range_dict}

#Nother one
alternatives_dict = {
    'RFI': [],
    'Call RFI': ['3bet'],
    '3bet': ['Call RFI'],
    'Call 3bet': ['4bet'],
    '4bet': ['Call 3bet'],
    'Limp/fold': ['RFI', 'Limp/call', 'Limp/3bet'],
    'Limp/call': ['RFI', 'Limp/fold', 'Limp/3bet'],
    'Limp/3bet': ['RFI', 'Limp/fold', 'Limp/call'],
    'Raise vs limp': []
}


#Nother one
action_to_quiz_option_dict = {
    'RFI': 'Raise',
    'Call RFI': 'Call',
    'Call 3bet': 'Call',
    'Raise vs limp': 'Raise',
    'Fold': 'Fold',
    'Check': 'Check'
}