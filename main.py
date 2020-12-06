import sys

from PySide2.QtWidgets import QApplication

from controller import Controller
from model import Model
from view import View

app = QApplication()
model = Model()
view = View(model)
controller = Controller(model, view)
view.window.show()
sys.exit(app.exec_())