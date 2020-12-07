import os
from collections import OrderedDict
from PySide2.QtCore import QUrl
from PySide2.QtWidgets import QInputDialog, QFileDialog, QLineEdit

from model import Model
from view import View, to_list_index


class Controller:

    def __init__(self, model: Model, view: View):

        self.model = model
        self.view = view

        self.view.window.shift_key_pressed.connect(self.shift_key_pressed_slot)
        self.view.window.shift_key_released.connect(self.shift_key_released_slot)

        for row_i in range(13):
            for col_i in range(13):
                hand_button_id = to_list_index(row_i, col_i)
                hand_button = self.view.hand_grid_button_group.button(hand_button_id)
                button_function = self.__create_hand_button_function(hand_button, row_i, col_i)
                hand_button.toggled.connect(button_function)

        for range_dict_dict in self.model.range_dict_list:
            self.view.range_dict_list_widget.addItem(range_dict_dict['Name'])
        self.view.range_dict_list_widget.currentIndexChanged.connect(self.range_dict_list_index_change_slot)
        self.view.save_range_dict_button.setEnabled(False)
        self.view.copy_range_button.setEnabled(False)
        self.view.paste_range_button.setEnabled(False)
        self.view.new_range_dict_button.clicked.connect(self.new_range_dict_button_slot)
        self.view.edit_range_dict_button.toggled.connect(self.edit_range_dict_button_toggled_slot)
        self.view.save_range_dict_button.clicked.connect(self.save_button_slot)
        self.view.copy_range_button.clicked.connect(self.copy_range_button_slot)
        self.view.paste_range_button.clicked.connect(self.paste_range_button_slot)
        self.view.invert_range_button.clicked.connect(self.invert_range_button_slot)

        for radio_button_group in self.view.radio_button_groups:
            for button in radio_button_group.buttons():
                button.toggled.connect(self.radio_button_slot)

        for i, (button_group_label, button_label) in enumerate(self.model.current_radio_button_setting.items()):
            radio_button_group = self.view.radio_button_groups[i]
            button_id = self.model.range_dict_schema[button_group_label].index(button_label)
            button = radio_button_group.button(button_id)
            button.setChecked(True)

        self.view.check_button.clicked.connect(self.check)
        self.view.reset_button.clicked.connect(self.reset)

    def shift_key_pressed_slot(self):

        for row_i in range(13):
            for col_i in range(13):
                hand_button_id = to_list_index(row_i, col_i)
                hand_button = self.view.hand_grid_button_group.button(hand_button_id)
                hand_button.shift_key_pressed = True
                if hand_button.underMouse():
                    hand_button.toggle()

    def shift_key_released_slot(self):

        for row_i in range(13):
            for col_i in range(13):
                hand_button_id = to_list_index(row_i, col_i)
                hand_button = self.view.hand_grid_button_group.button(hand_button_id)
                hand_button.shift_key_pressed = False

    def __create_hand_button_function(self, button, button_row, button_col):

        def function():
            self.model.range_entered[button_row][button_col] ^= True
            if self.model.editing_mode:
                self.view.set_editing_mode_color(button)
                self.model.reference_range[button_row][button_col] = button.isChecked()

        return function

    def __create_hand_button_under_mouse_function(self, button):

        def function():
            if button.isChecked():
                button.setChecked(False)
            else:
                button.setChecked(True)

        return function

    def __create_hand_button_pressed_function(self, button):

        def function():
            if button.isChecked():
                button.setChecked(False)
            else:
                button.setChecked(True)

        return function

    def uncheck_all_hand_buttons(self):

        for id in range(13 * 13):
            button = self.view.hand_grid_button_group.button(id)
            button.setChecked(False)

    def update_model_on_radio_buttons(self):

        checked_ids = [radio_button_group.checkedId() for radio_button_group in self.view.radio_button_groups]
        label_id_dict = OrderedDict(zip(self.model.range_dict_schema.keys(), checked_ids))
        self.model.set_radio_button_setting(label_id_dict)

    def disable_all_radio_buttons(self):

        for label in self.view.radio_button_group_labels:
            label.setEnabled(False)

        for radio_button_group in self.view.radio_button_groups:
            for button in radio_button_group.buttons():
                button.setEnabled(False)

    def enable_applicable_radio_buttons(self):

        applicable_dict = self.model.applicable_radio_buttons

        for i, (group_label, button_labels) in enumerate(applicable_dict.items()):

            if len(button_labels) > 0:
                label_widget = self.view.radio_button_group_labels[i]
                label_widget.setEnabled(True)
                button_group = self.view.radio_button_groups[i]
                button_ids = [self.model.range_dict_schema[group_label].index(button_label)
                              for button_label in button_labels]
                for button_id in button_ids:
                    button = button_group.button(button_id)
                    button.setEnabled(True)
                if (button_group.checkedButton() is None) or (not button_group.checkedButton().isEnabled()):
                    button_group.button(button_ids[0]).setChecked(True)

    def setup_radio_butttons(self):

        for radio_button_group in self.view.radio_button_groups:
            for button in radio_button_group.buttons():
                button.toggled.connect(self.radio_button_slot)

        for i, (button_group_label, button_label) in enumerate(self.model.current_radio_button_setting.items()):
            radio_button_group = self.view.radio_button_groups[i]
            button_id = self.model.range_dict_schema[button_group_label].index(button_label)
            button = radio_button_group.button(button_id)
            button.setChecked(True)

    def range_dict_list_index_change_slot(self, index):

        self.model.current_range_dict_list_index = index
        self.model.load_range_dict()
        self.view.clear_radio_button_parent_layout()
        self.view.populate_radio_button_parent_layout()
        self.model.check_default_radio_buttons()
        self.setup_radio_butttons()
        self.disable_all_radio_buttons()
        self.enable_applicable_radio_buttons()

    def new_range_dict_button_slot(self):

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

    def edit_range_dict_button_toggled_slot(self):

        if self.view.edit_range_dict_button.isChecked():
            self.edit_range_dict_button_checked_slot()
        else:
            self.edit_range_dict_button_unchecked_slot()

    def edit_range_dict_button_checked_slot(self):

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

    def edit_range_dict_button_unchecked_slot(self):

        self.model.editing_mode = False
        self.view.check_button.setEnabled(True)
        self.view.save_range_dict_button.setEnabled(False)
        self.view.copy_range_button.setEnabled(False)
        self.view.paste_range_button.setEnabled(False)
        self.view.reset_colors()

    def save_button_slot(self):

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

    def copy_range_button_slot(self):

        self.model.copied_range = self.model.reference_range
        self.view.paste_range_button.setEnabled(True)

    def paste_range_button_slot(self):

        for row_i in range(13):
            for col_i in range(13):
                hand_button_id = to_list_index(row_i, col_i)
                hand_button = self.view.hand_grid_button_group.button(hand_button_id)
                hand_button.setChecked(self.model.copied_range[row_i][col_i])

    def invert_range_button_slot(self):

        for row_i in range(13):
            for col_i in range(13):
                hand_button_id = to_list_index(row_i, col_i)
                hand_button = self.view.hand_grid_button_group.button(hand_button_id)
                hand_button.toggle()

    def radio_button_slot(self):

        self.update_model_on_radio_buttons()
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
