# coding: utf-8

from PyQt5 import QtGui, QtCore, QtWidgets

#from color.colors import *

DISABLED=3

class SelectButton(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        QtWidgets.QComboBox.__init__(self, parent)

        self.addItem(_("Left button"), userData=1)
        self.addItem(_("Middle button"), userData=4)
        self.addItem(_("Right button"), userData=2)
        self.addItem(_("Disable"), userData=DISABLED)

    def get_button(self):
        idx = self.currentIndex()
        button_id, ok = self.itemData(idx).toInt()
        if not ok:
            button_id = DISABLED
        if button_id == DISABLED:
            return None
        else:
            return QtCore.Qt.MouseButton(button_id)

    def set_button(self, button):
        if button == None:
            idx = self.findData(DISABLED)
        else:
            idx = self.findData(int(button))
        self.setCurrentIndex(idx)

class OptionsDialog(QtWidgets.QDialog):
    def __init__(self, options, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)

        self.options = options

        tabs = QtWidgets.QTabWidget(self)

        selector_tab = QtGui.QWidget()
        layout = QtGui.QFormLayout()
        self.hue_steps_checkbox = QtGui.QCheckBox(selector_tab)
        layout.addRow(_("Show hue steps swatches"), self.hue_steps_checkbox)
        self.hue_steps_count = QtGui.QSpinBox(selector_tab)
        self.hue_steps_count.setMinimum(6)
        self.hue_steps_count.setMaximum(36)
        layout.addRow(_("Number of hue steps"), self.hue_steps_count)
        selector_tab.setLayout(layout)

        input_tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()

        self.select_button = SelectButton(input_tab)
        layout.addRow(_("Select color with"), self.select_button)
        self.clear_button = SelectButton(input_tab)
        layout.addRow(_("Clear color swatch with"), self.clear_button)
        self.mark_button = SelectButton(input_tab)
        layout.addRow(_("Toggle mark on palette slot"), self.mark_button)
        self.menu_button = SelectButton(input_tab)
        layout.addRow(_("Show context menu on"), self.menu_button)

        input_tab.setLayout(layout)

        picker_tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()

        self.picker_area = QtWidgets.QSpinBox(picker_tab)
        self.picker_area.setMinimum(1)
        self.picker_area.setMaximum(15)
        layout.addRow(_("Picker area size"), self.picker_area)
        self.picker_average = QtWidgets.QCheckBox(picker_tab)
        layout.addRow(_("Average color while mouse dragging"), self.picker_average)

        picker_tab.setLayout(layout)

        tabs.addTab(selector_tab, _("General"))
        tabs.addTab(input_tab, _("Input"))
        tabs.addTab(picker_tab, _("Color picker"))
        
        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        ok = QtWidgets.QPushButton(_("&OK"))
        ok.clicked.connect(self._on_ok)
        cancel = QtWidgets.QPushButton(_("&Cancel"))
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tabs)
        layout.addLayout(buttons,1)
        self.setLayout(layout)

        self.setWindowTitle(_("Preferences"))

        self.load_settings()

    def _on_ok(self):
        self.save_settings()
        self.options.store()
        self.accept()

    def load_settings(self):

        if self.options.show_hue_steps:
            self.hue_steps_checkbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.hue_steps_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.hue_steps_count.setValue(self.options.hue_steps)

        self.select_button.set_button(self.options.select_button)
        self.clear_button.set_button(self.options.clear_button)
        self.mark_button.set_button(self.options.mark_button)
        self.menu_button.set_button(self.options.menu_button)

        self.picker_area.setValue(self.options.picker_area)

        if self.options.picker_average:
            self.picker_average.setCheckState(QtCore.Qt.Checked)
        else:
            self.picker_average.setCheckState(QtCore.Qt.Unchecked)

    def save_settings(self):

        self.options.show_hue_steps = (self.hue_steps_checkbox.checkState() == QtCore.Qt.Checked)
        self.options.hue_steps = self.hue_steps_count.value()

        self.options.select_button = self.select_button.get_button()
        self.options.clear_button = self.clear_button.get_button()
        self.options.mark_button = self.mark_button.get_button()
        self.options.menu_button = self.menu_button.get_button()

        self.options.picker_area = self.picker_area.value()
        self.options.picker_average = (self.picker_average.checkState() == QtCore.Qt.Checked)

