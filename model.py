import os
from collections import OrderedDict
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
