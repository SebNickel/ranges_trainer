from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QEnterEvent, QKeyEvent
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QToolButton, \
    QPushButton, QRadioButton, QButtonGroup, QSizePolicy, QComboBox

from model import Model


def to_list_index(row_i, col_i, num_cols=13):

    return (row_i * num_cols) + col_i


def clear_layout(layout):

    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        elif child.layout():
            clear_layout(child.layout())
            child.layout().deleteLater()


# I'd like to be able to toggle hand grid buttons by holding the left mouse button down and dragging the cursor over
# them. Unfortunately the way widgets grab the mouse makes that very complicated, so until I find a way to make that
# work, it will be the shift key that needs to be held down while dragging the cursor over the buttons.
class HandGridButton(QToolButton):

    def __init__(self):

        super().__init__()
        self.shift_key_pressed = False

    def enterEvent(self, event: QEnterEvent):

        if self.shift_key_pressed:
            self.toggle()


class CustomWindow(QWidget):

    shift_key_pressed = Signal()
    shift_key_released = Signal()

    def keyPressEvent(self, event: QKeyEvent) -> None:

        if event.key() == Qt.Key_Shift:
            self.shift_key_pressed.emit()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:

        if event.key() == Qt.Key_Shift:
            self.shift_key_released.emit()


class View:

    def __init__(self, model: Model):

        self.model = model

        self.window = CustomWindow()
        self.parent_layout = QHBoxLayout()
        self.hand_grid_layout = QGridLayout()
        self.side_bar_layout = QVBoxLayout()
        self.range_dict_button_layout = QGridLayout()
        self.radio_button_parent_layout = QVBoxLayout()
        self.command_button_layout = QHBoxLayout()

        self.range_dict_list_widget = QComboBox()

        self.parent_layout.addLayout(self.hand_grid_layout)
        self.parent_layout.addLayout(self.side_bar_layout)
        self.side_bar_layout.addWidget(self.range_dict_list_widget)
        self.side_bar_layout.addLayout(self.range_dict_button_layout)
        self.side_bar_layout.addLayout(self.radio_button_parent_layout)
        self.side_bar_layout.addLayout(self.command_button_layout)

        self.hand_grid_button_group = QButtonGroup()
        self.hand_grid_button_group.setExclusive(False)
        self.new_range_dict_button = QPushButton('New')
        self.edit_range_dict_button = QPushButton('Edit')
        self.save_range_dict_button = QPushButton('Save')
        self.copy_range_button = QPushButton('Copy')
        self.paste_range_button = QPushButton('Paste')
        self.invert_range_button = QPushButton('Invert')
        self.check_button = QPushButton('Check')
        self.reset_button = QPushButton('Reset')

        for i in range(13):
            self.hand_grid_layout.setColumnMinimumWidth(i, 50)
            self.hand_grid_layout.setRowMinimumHeight(i, 50)
        self.hand_grid_layout.setHorizontalSpacing(0)
        self.hand_grid_layout.setVerticalSpacing(0)

        self.edit_range_dict_button.setCheckable(True)

        self.hand_button_size_policy = QSizePolicy()
        self.hand_button_size_policy.setHeightForWidth(True)
        self.hand_button_size_policy.setVerticalPolicy(QSizePolicy.Minimum)
        self.hand_button_size_policy.setHorizontalPolicy(QSizePolicy.Ignored)

        self.__populate_hand_grid_layout()
        self.range_dict_button_layout.addWidget(self.new_range_dict_button, 0, 0)
        self.range_dict_button_layout.addWidget(self.edit_range_dict_button, 0, 1)
        self.range_dict_button_layout.addWidget(self.save_range_dict_button, 0, 2)
        self.range_dict_button_layout.addWidget(self.copy_range_button, 1, 0)
        self.range_dict_button_layout.addWidget(self.paste_range_button, 1, 1)
        self.range_dict_button_layout.addWidget(self.invert_range_button, 1, 2)
        self.command_button_layout.addWidget(self.check_button)
        self.command_button_layout.addWidget(self.reset_button)

        self.populate_radio_button_parent_layout()

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
                button = HandGridButton()

                button.setCheckable(True)
                button.setToolButtonStyle(Qt.ToolButtonTextOnly)
                button.setText(hand_str)
                button.setSizePolicy(self.hand_button_size_policy)
                self.hand_grid_button_group.addButton(button, id=button_id)
                self.hand_grid_layout.addWidget(button, row_i, col_i)

    def clear_radio_button_parent_layout(self):

        clear_layout(self.radio_button_parent_layout)

    def populate_radio_button_parent_layout(self):

        self.radio_button_layouts = [QGridLayout() for _ in self.model.range_dict_schema.keys()]
        label_names = list(self.model.range_dict_schema.keys())
        self.radio_button_group_labels = [QLabel('<h2>{}</h2>'.format(label_name)) for label_name in label_names]
        for label, layout in zip(self.radio_button_group_labels, self.radio_button_layouts):
            self.radio_button_parent_layout.addWidget(label)
            self.radio_button_parent_layout.addLayout(layout)
        self.radio_button_groups = [QButtonGroup() for _ in self.model.range_dict_schema.keys()]
        radio_button_horizontal_spacing = 2
        for layout in self.radio_button_layouts:
            layout.setHorizontalSpacing(radio_button_horizontal_spacing)
        for label_name, layout, button_group in zip(label_names, self.radio_button_layouts, self.radio_button_groups):
            self.__populate_radio_button_layout(layout,
                                                button_group,
                                                self.model.range_dict_schema[label_name])

    @staticmethod
    def __populate_radio_button_layout(grid_layout, button_group, labels, num_cols=3):

        for i in range(len(labels)):
            row_i = i // num_cols
            col_i = i % num_cols
            radio_button = QRadioButton(labels[i])
            grid_layout.addWidget(radio_button, row_i, col_i)
            button_group.addButton(radio_button, id=i)
