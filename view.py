from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QToolButton, \
    QPushButton, QRadioButton, QButtonGroup, QSizePolicy, QComboBox

from model import Model


def to_list_index(row_i, col_i, num_cols=13):

    return (row_i * num_cols) + col_i


class View:

    def __init__(self, model: Model):

        self.model = model

        self.window = QWidget()
        self.parent_layout = QHBoxLayout()
        self.hand_grid_layout = QGridLayout()
        self.side_bar_layout = QVBoxLayout()
        self.range_dict_button_layout = QHBoxLayout()
        self.hero_pos_layout = QGridLayout()
        self.action_layout = QGridLayout()
        self.villain_pos_layout = QGridLayout()
        self.command_button_layout = QHBoxLayout()

        self.range_dict_list_widget = QComboBox()
        self.hero_pos_label = QLabel('<h2>Position</h2>')
        self.action_label = QLabel('<h2>Action</h2>')
        self.villain_pos_label = QLabel('<h2>VS</h2>')

        self.parent_layout.addLayout(self.hand_grid_layout)
        self.parent_layout.addLayout(self.side_bar_layout)
        self.side_bar_layout.addWidget(self.range_dict_list_widget)
        self.side_bar_layout.addLayout(self.range_dict_button_layout)
        self.side_bar_layout.addWidget(self.hero_pos_label)
        self.side_bar_layout.addLayout(self.hero_pos_layout)
        self.side_bar_layout.addWidget(self.action_label)
        self.side_bar_layout.addLayout(self.action_layout)
        self.side_bar_layout.addWidget(self.villain_pos_label)
        self.side_bar_layout.addLayout(self.villain_pos_layout)
        self.side_bar_layout.addLayout(self.command_button_layout)

        self.hand_grid_button_group = QButtonGroup()
        self.hand_grid_button_group.setExclusive(False)
        self.hero_pos_button_group = QButtonGroup()
        self.action_button_group = QButtonGroup()
        self.villain_pos_button_group = QButtonGroup()
        self.new_range_dict_button = QPushButton('New')
        self.edit_range_dict_button = QPushButton('Edit')
        self.save_range_dict_button = QPushButton('Save')
        self.check_button = QPushButton('Check')
        self.reset_button = QPushButton('Reset')

        for i in range(13):
            self.hand_grid_layout.setColumnMinimumWidth(i, 50)
            self.hand_grid_layout.setRowMinimumHeight(i, 50)
        self.hand_grid_layout.setHorizontalSpacing(0)
        self.hand_grid_layout.setVerticalSpacing(0)

        self.edit_range_dict_button.setCheckable(True)

        radio_button_horizontal_spacing = 2
        self.hero_pos_layout.setHorizontalSpacing(radio_button_horizontal_spacing)
        self.action_layout.setHorizontalSpacing(radio_button_horizontal_spacing)
        self.villain_pos_layout.setHorizontalSpacing(radio_button_horizontal_spacing)

        self.hand_button_size_policy = QSizePolicy()
        self.hand_button_size_policy.setHeightForWidth(True)
        self.hand_button_size_policy.setVerticalPolicy(QSizePolicy.Minimum)
        self.hand_button_size_policy.setHorizontalPolicy(QSizePolicy.Ignored)

        self.__populate_hand_grid_layout()
        self.range_dict_button_layout.addWidget(self.new_range_dict_button)
        self.range_dict_button_layout.addWidget(self.edit_range_dict_button)
        self.range_dict_button_layout.addWidget(self.save_range_dict_button)
        self.__populate_radio_button_layout(self.hero_pos_layout,
                                            self.hero_pos_button_group,
                                            self.model.position_labels)
        self.__populate_radio_button_layout(self.action_layout,
                                            self.action_button_group,
                                            self.model.action_labels)
        self.__populate_radio_button_layout(self.villain_pos_layout,
                                            self.villain_pos_button_group,
                                            self.model.position_labels)
        self.command_button_layout.addWidget(self.check_button)
        self.command_button_layout.addWidget(self.reset_button)

        self.parent_layout.setSizeConstraint(QHBoxLayout.SetFixedSize)

        self.window.setLayout(self.parent_layout)

        self.hand_button_editing_mode_style_sheet_unchecked = 'background-color: gray; color: white'
        self.hand_button_editing_mode_style_sheet_checked = 'background-color: deeppink; color: black'
        self.new_range_dict_dialog_title = 'Create new range dict'
        self.new_range_dict_dialog_label = 'New range dict name:'

    def display_feedback(self):

        incorrectly_checked_button_ids = self.model.incorrectly_checked.flatten().nonzero()[0]
        incorrectly_left_unchecked_button_ids = self.model.incorrectly_left_unchecked.flatten().nonzero()[0]
        correctly_checked_button_ids = self.model.correctly_checked.flatten().nonzero()[0]
        for id in incorrectly_checked_button_ids:
            button = self.hand_grid_button_group.button(id)
            button.setStyleSheet('background-color: red')
        for id in incorrectly_left_unchecked_button_ids:
            button = self.hand_grid_button_group.button(id)
            button.setStyleSheet('background-color: yellow')
        for id in correctly_checked_button_ids:
            button = self.hand_grid_button_group.button(id)
            button.setStyleSheet('background-color: lime')

    def reset_colors(self):

        for id in range(13 * 13):
            button = self.hand_grid_button_group.button(id)
            button.setStyleSheet('background-color: white')

    def set_editing_mode_color(self, hand_button):

        if hand_button.isChecked():
            hand_button.setStyleSheet(self.hand_button_editing_mode_style_sheet_checked)
        else:
            hand_button.setStyleSheet(self.hand_button_editing_mode_style_sheet_unchecked)

    def set_editing_mode_colors(self):

        for id in range(13 * 13):
            button = self.hand_grid_button_group.button(id)
            self.set_editing_mode_color(button)

    def __indices_to_hand_str(self, row_i, col_i):

        if row_i < col_i:
            card1 = self.model.card_ranks[row_i]
            card2 = self.model.card_ranks[col_i]
            suited_str = 's'
        elif row_i > col_i:
            card1 = self.model.card_ranks[col_i]
            card2 = self.model.card_ranks[row_i]
            suited_str = 'o'
        else:
            card1 = self.model.card_ranks[row_i]
            card2 = self.model.card_ranks[col_i]
            suited_str = ''

        return '{}{}{}'.format(card1, card2, suited_str)

    def __populate_hand_grid_layout(self):

        for row_i in range(13):
            for col_i in range(13):
                hand_str = self.__indices_to_hand_str(row_i, col_i)
                button_id = to_list_index(row_i, col_i)
                button = QToolButton()
                button.setCheckable(True)
                button.setToolButtonStyle(Qt.ToolButtonTextOnly)
                button.setText(hand_str)
                button.setSizePolicy(self.hand_button_size_policy)
                self.hand_grid_button_group.addButton(button, id=button_id)
                self.hand_grid_layout.addWidget(button, row_i, col_i)

    @staticmethod
    def __populate_radio_button_layout(grid_layout, button_group, labels, num_cols=3):

        for i in range(len(labels)):
            row_i = i // num_cols
            col_i = i % num_cols
            radio_button = QRadioButton(labels[i])
            grid_layout.addWidget(radio_button, row_i, col_i)
            button_group.addButton(radio_button, id=i)
