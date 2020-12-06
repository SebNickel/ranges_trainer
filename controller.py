import os
from PySide2.QtWidgets import QInputDialog, QFileDialog, QLineEdit
from PySide2.QtCore import QUrl
import pickle

from model import Model
from view import View, to_list_index


class Controller:

    def __init__(self, model: Model, view: View):

        self.model = model
        self.view = view

        for row_i in range(13):
            for col_i in range(13):
                hand_button_id = to_list_index(row_i, col_i)
                hand_button = self.view.hand_grid_button_group.button(hand_button_id)
                button_function = self.__create_hand_button_function(hand_button, row_i, col_i)
                hand_button.toggled.connect(button_function)

        for range_dict_dict in self.model.range_dict_list:
            self.view.range_dict_list_widget.addItem(range_dict_dict['Name'])
        self.view.range_dict_list_widget.currentIndexChanged.connect(self.range_dict_list_index_change_callback)
        self.view.save_range_dict_button.setEnabled(False)
        self.view.copy_range_button.setEnabled(False)
        self.view.paste_range_button.setEnabled(False)
        self.view.new_range_dict_button.clicked.connect(self.new_range_dict_button_callback)
        self.view.edit_range_dict_button.toggled.connect(self.edit_range_dict_button_toggled_callback)
        self.view.save_range_dict_button.clicked.connect(self.save_button_callback)
        self.view.copy_range_button.clicked.connect(self.copy_range_button_callback)
        self.view.paste_range_button.clicked.connect(self.paste_range_button_callback)

        for button_id in range(len(self.model.position_labels)):

            hero_pos_button = self.view.hero_pos_button_group.button(button_id)
            villain_pos_button = self.view.villain_pos_button_group.button(button_id)

            hero_pos_button.toggled.connect(self.radio_button_callback)
            villain_pos_button.toggled.connect(self.radio_button_callback)

        for button_id in range(len(self.model.action_labels)):

            action_button = self.view.action_button_group.button(button_id)
            action_button.toggled.connect(self.radio_button_callback)

        self.view.hero_pos_button_group.button(0).setChecked(True)
        self.view.action_button_group.button(0).setChecked(True)

        self.view.check_button.clicked.connect(self.check)
        self.view.reset_button.clicked.connect(self.reset)

    def __create_hand_button_function(self, button, button_row, button_col):

        def function():
            self.model.range_entered[button_row][button_col] ^= True
            if self.model.editing_mode:
                self.view.set_editing_mode_color(button)
                self.model.reference_range[button_row][button_col] = button.isChecked()

        return function

    def uncheck_all_hand_buttons(self):

        for id in range(13 * 13):
            button = self.view.hand_grid_button_group.button(id)
            button.setChecked(False)

    def update_model_on_radio_buttons(self):

        hero_pos_id = self.view.hero_pos_button_group.checkedId()
        action_id = self.view.action_button_group.checkedId()
        villain_pos_id = self.view.villain_pos_button_group.checkedId()

        self.model.set_hero_position_by_index(hero_pos_id)
        self.model.set_action_by_index(action_id)
        self.model.set_villain_position_by_index(villain_pos_id)

    # def enable_all_radio_buttons(self):
    #
    #     self.view.villain_pos_label.setEnabled(True)
    #
    #     for id in range(9):
    #
    #         hero_pos_button = self.view.hero_pos_button_group.button(id)
    #         action_button = self.view.action_button_group.button(id)
    #         villain_pos_button = self.view.villain_pos_button_group.button(id)
    #
    #         hero_pos_button.setEnabled(True)
    #         action_button.setEnabled(True)
    #         villain_pos_button.setEnabled(True)

    # def disable_inapplicable_radio_buttons(self):
    #
    #     inapplicable_dict = self.model.inapplicable_radio_buttons
    #
    #     for pos_label in inapplicable_dict['hero_position']:
    #         button_id = self.model.position_labels.index(pos_label)
    #         button = self.view.hero_pos_button_group.button(button_id)
    #         button.setEnabled(False)
    #     for action_label in inapplicable_dict['action']:
    #         button_id = self.model.action_labels.index(action_label)
    #         button = self.view.action_button_group.button(button_id)
    #         button.setEnabled(False)
    #     for pos_label in inapplicable_dict['villain_position']:
    #         button_id = self.model.position_labels.index(pos_label)
    #         button = self.view.villain_pos_button_group.button(button_id)
    #         button.setEnabled(False)
    #     if len(inapplicable_dict['villain_position']) == len(self.model.position_labels):
    #         self.view.villain_pos_label.setEnabled(False)

        # if self.view.hero_pos_buttongroup.checkedId() == -1:
        #     enabled_pos_indices = [i for i in range(len(self.model.position_labels))
        #                            if self.model.position_labels[i] not in inapplicable_dict['Position']]
        #     if len(enabled_pos_indices) > 0:
        #         button_id = enabled_pos_indices[0]
        #         self.view.hero_pos_button_group.button(button_id).setChecked(True)
        # if self.view.action_button_group.checkedId() == -1:
        #     enabled_action_indices = [i for i in range(len(self.model.action_labels))
        #                            if self.model.action_labels[i] not in inapplicable_dict['Action']]
        #     if len(enabled_action_indices) > 0:
        #         button_id = enabled_action_indices[0]
        #         self.view.action_button_group.button(button_id).setChecked(True)
        # if self.view.villain_pos_button_group.checkedId() == -1:
        #     enabled_pos_indices = [i for i in range(len(self.model.position_labels))
        #                            if self.model.position_labels[i] not in inapplicable_dict['VS']]
        #     if len(enabled_pos_indices) > 0:
        #         button_id = enabled_pos_indices[0]
        #         self.view.villain_pos_button_group.button(button_id).setChecked(True)

    def disable_all_radio_buttons(self):

        self.view.villain_pos_label.setEnabled(False)

        for id in range(len(self.model.position_labels)):

            hero_pos_button = self.view.hero_pos_button_group.button(id)
            villain_pos_button = self.view.villain_pos_button_group.button(id)

            hero_pos_button.setEnabled(False)
            villain_pos_button.setEnabled(False)

        for id in range(len(self.model.action_labels)):

            action_button = self.view.action_button_group.button(id)
            action_button.setEnabled(False)

    def enable_applicable_radio_buttons(self):

        applicable_dict = self.model.applicable_radio_buttons

        for pos_label in applicable_dict['hero_position']:
            button_id = self.model.position_labels.index(pos_label)
            button = self.view.hero_pos_button_group.button(button_id)
            button.setEnabled(True)
        for action_label in applicable_dict['action']:
            button_id = self.model.action_labels.index(action_label)
            button = self.view.action_button_group.button(button_id)
            button.setEnabled(True)
        for pos_label in applicable_dict['villain_position']:
            button_id = self.model.position_labels.index(pos_label)
            button = self.view.villain_pos_button_group.button(button_id)
            button.setEnabled(True)
        if len(applicable_dict['villain_position']) > 0:
            self.view.villain_pos_label.setEnabled(True)

        if (self.view.hero_pos_button_group.checkedButton() is None) \
                or (not self.view.hero_pos_button_group.checkedButton().isEnabled()):
            if len(applicable_dict['hero_position']) > 0:
                hero_pos_label = applicable_dict['hero_position'][0]
                hero_pos_id = self.model.position_labels.index(hero_pos_label)
                self.view.hero_pos_button_group.button(hero_pos_id).setChecked(True)
        if (self.view.action_button_group.checkedButton() is None) \
                or (not self.view.action_button_group.checkedButton().isEnabled()):
            if len(applicable_dict['action']) > 0:
                action_label = applicable_dict['action'][0]
                action_id = self.model.position_labels.index(action_label)
                self.view.action_button_group.button(action_id).setChecked(True)
        if (self.view.villain_pos_button_group.checkedButton()) is None \
                or (not self.view.villain_pos_button_group.checkedButton().isEnabled()):
            if len(applicable_dict['villain_position']) > 0:
                villain_pos_label = applicable_dict['villain_position'][0]
                villain_pos_id = self.model.position_labels.index(villain_pos_label)
                self.view.villain_pos_button_group.button(villain_pos_id).setChecked(True)

    def range_dict_list_index_change_callback(self, index):

        self.model.current_range_dict_list_index = index
        self.model.load_range_dict()

    def new_range_dict_button_callback(self):

        new_range_dict_name, clicked_ok = QInputDialog().getText(self.view.window,
                                                                 self.view.new_range_dict_dialog_title,
                                                                 self.view.new_range_dict_dialog_label,
                                                                 QLineEdit.Normal)

        if clicked_ok:
            new_range_dict_list_item = {'Name': new_range_dict_name, 'Filepath': None}
            self.model.range_dict_list.append(new_range_dict_list_item)
            self.view.range_dict_list_widget.addItem(new_range_dict_name)
            self.view.range_dict_list_widget.setCurrentIndex(len(self.model.range_dict_list) - 1)
            self.view.edit_range_dict_button.setChecked(True)

    def edit_range_dict_button_toggled_callback(self):

        if self.view.edit_range_dict_button.isChecked():
            self.edit_range_dict_button_checked_callback()
        else:
            self.edit_range_dict_button_unchecked_callback()

    def edit_range_dict_button_checked_callback(self):

        self.model.editing_mode = True
        self.view.check_button.setEnabled(False)
        self.view.save_range_dict_button.setEnabled(True)
        self.view.copy_range_button.setEnabled(True)
        self.view.set_editing_mode_colors()
        for row_i in range(13):
            for col_i in range(13):
                hand_button_id = to_list_index(row_i, col_i)
                hand_button = self.view.hand_grid_button_group.button(hand_button_id)
                hand_button.setChecked(self.model.reference_range[row_i][col_i])

    def edit_range_dict_button_unchecked_callback(self):

        self.model.editing_mode = False
        self.view.check_button.setEnabled(True)
        self.view.save_range_dict_button.setEnabled(False)
        self.view.copy_range_button.setEnabled(False)
        self.view.paste_range_button.setEnabled(False)
        self.view.reset_colors()

    def save_button_callback(self):

        range_dict_name = self.view.range_dict_list_widget.currentText()
        default_url = QUrl(os.path.join(os.getcwd(), 'range_dicts', '{}{}'.format(range_dict_name, '.pkl')))
        url, clicked_save = QFileDialog.getSaveFileUrl(self.view.window,
                                                       'Save range dict',
                                                       default_url,
                                                       'Pickle files (*.pkl)')
        if clicked_save:
            if len(url.path()) < 4 or url.path()[-4:] != '.pkl':
                target_path = '{}{}'.format(url.path(), '.pkl')
            else:
                target_path = url.path()
            self.model.range_dict_list[self.model.current_range_dict_list_index]['Filepath'] = target_path
            self.model.save_range_dict(target_path)
            self.model.save_range_dict_list()

    def copy_range_button_callback(self):

        self.model.copied_range = self.model.reference_range
        self.view.paste_range_button.setEnabled(True)

    def paste_range_button_callback(self):

        for row_i in range(13):
            for col_i in range(13):
                hand_button_id = to_list_index(row_i, col_i)
                hand_button = self.view.hand_grid_button_group.button(hand_button_id)
                hand_button.setChecked(self.model.copied_range[row_i][col_i])

    def radio_button_callback(self):

        self.update_model_on_radio_buttons()
        #self.enable_all_radio_buttons()
        #self.disable_inapplicable_radio_buttons()
        self.disable_all_radio_buttons()
        self.enable_applicable_radio_buttons()
        if self.model.editing_mode:
            for row_i in range(13):
                for col_i in range(13):
                    hand_button_id = to_list_index(row_i, col_i)
                    hand_button = self.view.hand_grid_button_group.button(hand_button_id)
                    hand_button.setChecked(self.model.reference_range[row_i][col_i])

    def check(self):

        self.update_model_on_radio_buttons()
        comparison_array = self.model.range_entered.astype(int) - self.model.reference_range.astype(int)
        self.model.incorrectly_checked = comparison_array == 1
        self.model.incorrectly_left_unchecked = comparison_array == -1
        self.model.correctly_checked = self.model.range_entered & self.model.reference_range
        self.view.display_feedback()

    def reset(self):

        self.uncheck_all_hand_buttons()
        self.view.reset_colors()
