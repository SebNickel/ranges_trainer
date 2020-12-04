import sys

import numpy as np
from PySide2.QtWidgets import QApplication

from model import Model
from view import View
from controller import Controller

test_dict = dict()
position_labels = ['UTG', 'UTG+1', 'UTG+2', 'LJ', 'HJ', 'CO', 'BN', 'SB', 'BB']
action_labels = ['RFI', 'Call RFI', '3bet', 'Call 3bet', '4bet', 'Call 4bet', '5bet shove', 'Limp-call', 'Limp-3bet']

for label in position_labels:
    test_dict[label] = dict()

for hero_pos_label in position_labels:
    for action_label in ['RFI'] + action_labels[-2:]:
        test_dict[hero_pos_label][action_label] = np.zeros((13, 13), dtype=bool)

for hero_pos_label in position_labels:
    for action_label in action_labels[1:-2]:
        test_dict[hero_pos_label][action_label] = dict()
        for villain_pos_label in position_labels:
            test_dict[hero_pos_label][action_label][villain_pos_label] = np.zeros((13, 13), dtype=bool)

utg_rfi = np.zeros((13, 13), dtype=bool)
utg_rfi[0] = True
utg_rfi[1][:4] = True
for i in range(13):
    utg_rfi[i][i] = True
utg_rfi[2][0] = True
utg_rfi[2][3] = True
utg_rfi[3][4] = True
utg_rfi[4][5] = True
utg_rfi[5][6] = True

test_dict['UTG']['RFI'] = utg_rfi

app = QApplication()
model = Model(test_dict)
view = View(model)
controller = Controller(model, view)
view.window.show()
sys.exit(app.exec_())