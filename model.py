import os
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

        self.position_labels = self.__range_dict_schema['hero_position']
        self.action_labels = self.__range_dict_schema['action']
        self.__hero_position = self.position_labels[0]
        self.__action = self.action_labels[0]
        self.__villain_position = self.position_labels[0]

        self.range_entered = np.zeros((13, 13), dtype=bool)
        self.incorrectly_checked = np.zeros((13, 13), dtype=bool)
        self.incorrectly_left_unchecked = np.zeros((13, 13), dtype=bool)
        self.correctly_checked = np.zeros((13, 13), dtype=bool)
        self.copied_range = None

        self.card_ranks = 'AKQJT98765432'

    @property
    def reference_range(self):

        hero_pos_action = self.__reference_range_dict[self.hero_position][self.action]

        if type(hero_pos_action) is not dict:
            return hero_pos_action
        else:
            return hero_pos_action[self.villain_position]

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
    def applicable_radio_buttons(self):

        applicable_dict = {'hero_position': self.position_labels, 'action': [], 'villain_position': []}

        hero_pos_action = self.__reference_range_dict[self.hero_position][self.action]
        if type(hero_pos_action) is dict:
            applicable_dict['villain_position'] = list(hero_pos_action.keys())

        for action_label in self.action_labels:
            if action_label in self.__reference_range_dict[self.hero_position].keys():
                applicable_dict['action'].append(action_label)
                # hero_pos_action = self.__reference_range_dict[self.hero_position][action_label]
                # if (type(hero_pos_action) is not dict or self.villain_position in hero_pos_action.keys()):
                #     applicable_dict['action'].append(action_label)

        # for hero_position_label in self.position_labels:
        #     if self.action in self.__reference_range_dict[hero_position_label].keys():
        #         hero_pos_action = self.__reference_range_dict[hero_position_label][self.action]
        #         if ((type(hero_pos_action) is not dict)
        #             or (self.villain_position in hero_pos_action.keys())):
        #             applicable_dict['hero_position'].append(hero_position_label)

        return applicable_dict

    # TODO: This will need to change
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
                self.__top_level_dict = pickle.load(f)
            self.__range_dict_schema = self.__top_level_dict['schema']
            self.__reference_range_dict = self.__top_level_dict['contents']
        else:
            # TODO
            self.create_new_empty_reference_range_dict()

    def save_range_dict(self, target_path):

        with open(target_path, 'wb') as f:
            pickle.dump(self.__top_level_dict, f)

    def save_range_dict_list(self):

        with open(self.range_dict_list_filepath, 'w') as f:
            json.dump(self.range_dict_list, f, indent=4)
