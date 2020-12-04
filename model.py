import os
import numpy as np
import pickle
import json


class Model:

    def __init__(self, reference_range_dict):

        self.range_dict_list_filepath = os.path.join(os.getcwd(), 'range_dicts', 'range_dict_list.json')
        with open(self.range_dict_list_filepath, 'r') as f:
            self.range_dict_list = json.load(f)
        self.current_range_dict_list_index = 0
        with open(self.range_dict_list[self.current_range_dict_list_index]['Filepath'], 'rb') as f:
            self.__reference_range_dict = pickle.load(f)
        self.editing_mode = False

        self.__hero_position = 'UTG'
        self.__action = 'RFI'
        self.__villain_position = 'BB'

        self.range_entered = np.zeros((13, 13), dtype=bool)
        self.incorrectly_checked = np.zeros((13, 13), dtype=bool)
        self.incorrectly_left_unchecked = np.zeros((13, 13), dtype=bool)
        self.correctly_checked = np.zeros((13, 13), dtype=bool)

        self.card_ranks = 'AKQJT98765432'
        self.position_labels = ['UTG', 'UTG+1', 'UTG+2', 'LJ', 'HJ', 'CO', 'BN', 'SB', 'BB']
        self.action_labels = \
            ['RFI', 'Call RFI', '3bet', 'Call 3bet', '4bet', 'Call 4bet', '5bet shove', 'Limp-fold', 'Limp-call', 'Limp-3bet']

    @property
    def reference_range(self):

        if self.action in ['RFI', 'Limp-fold', 'Limp-call', 'Limp-3bet']:
            return self.__reference_range_dict[self.hero_position][self.action]
        else:
            return self.__reference_range_dict[self.hero_position][self.action][self.villain_position]

    @property
    def hero_position(self):

        return self.__hero_position

    def set_hero_position_by_index(self, pos_index):

        self.__hero_position = self.position_labels[pos_index]

    @property
    def action(self):

        return self.__action

    def set_action_by_index(self, action_index):

        self.__action = self.action_labels[action_index]

    @property
    def villain_position(self):

        return self.__villain_position

    def set_villain_position_by_index(self, pos_index):

        self.__villain_position = self.position_labels[pos_index]

    @property
    def inapplicable_options(self):

        option_dict = {'Position': [], 'Action': [], 'VS': []}
        if self.hero_position == 'UTG':
            option_dict['Action'].append('Call RFI')
        elif self.hero_position == 'BB':
            option_dict['Action'] += ['RFI', 'Limp-fold', 'Limp-call', 'Limp-3bet']
        if self.action in ['RFI', 'Limp-fold', 'Limp-call', 'Limp-3bet']:
            option_dict['VS'] = self.position_labels
            option_dict['Position'].append('BB')
        elif self.action == 'Call RFI':
            option_dict['Position'].append('UTG')
            hero_position_index = self.position_labels.index(self.hero_position)
            option_dict['VS'] = self.position_labels[hero_position_index:]

        return option_dict

    def create_new_empty_reference_range_dict(self):

        self.__reference_range_dict = {}
        for hero_pos_label in self.position_labels:
            self.__reference_range_dict[hero_pos_label] = {}
            for action_label in self.action_labels:
                if action_label in {'RFI', 'Limp-fold', 'Limp-call', 'Limp-3bet'}:
                    self.__reference_range_dict[hero_pos_label][action_label] = np.zeros((13, 13), dtype=bool)
                else:
                    self.__reference_range_dict[hero_pos_label][action_label] = {}
                    for villain_pos_label in self.position_labels:
                        self.__reference_range_dict[hero_pos_label][action_label][villain_pos_label] = \
                            np.zeros((13, 13), dtype=bool)

    def load_range_dict(self):

        range_dict_descriptor = self.range_dict_list[self.current_range_dict_list_index]
        if range_dict_descriptor['Filepath'] is not None:
            with open(range_dict_descriptor['Filepath'], 'rb') as f:
                self.__reference_range_dict = pickle.load(f)
        else:
            self.create_new_empty_reference_range_dict()

    def save_range_dict(self, target_path):

        with open(target_path, 'wb') as f:
            pickle.dump(self.__reference_range_dict, f)

    def save_range_dict_list(self):

        with open(self.range_dict_list_filepath, 'w') as f:
            json.dump(self.range_dict_list, f, indent=4)
