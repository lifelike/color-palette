from copy import copy
from PyQt4 import QtGui, QtCore

from color.colors import *

class SetMixer(QtGui.QUndoCommand):
    def __init__(self, owner, pairs, old_mixer_idx, new_mixer_idx):
        QtGui.QUndoCommand.__init__(self)
        self.owner = owner
        self.setText(_("selecting color model"))
        self.old_mixer_idx = old_mixer_idx
        self.mixer_idx = new_mixer_idx
        self.pairs = pairs

    def redo(self):
        _,  mixer = self.pairs[self.mixer_idx]
        print("Selected mixer: " + str(mixer))
        self.owner.setMixer(mixer, self.mixer_idx)

    def undo(self):
        _,  mixer = self.pairs[self.old_mixer_idx]
        self.owner.setMixer(mixer, self.old_mixer_idx)

class ChangeColor(QtGui.QUndoCommand):
    def __init__(self, model, text, fn):
        QtGui.QUndoCommand.__init__(self)
        self.setText(text)
        self.fn = fn
        self.model = model

    def redo(self):
        self.old_color = self.model.getColor()
        color = self.fn(self.old_color)
        self.model.setColor(color)
        self.model.widget.repaint()

    def undo(self):
        self.model.setColor(self.old_color)
        self.model.widget.repaint()

class SetColor(QtGui.QUndoCommand):
    def __init__(self, model, color):
        QtGui.QUndoCommand.__init__(self)
        self.setText(_("setting color"))
        self.model = model
        self.color = color

    def redo(self):
        self.old_color = self.model.getColor()
        self.model.color = self.color
        self.model.widget.repaint()
        self.oldest_history_color = self.model.get_color_history().color_models[-1].getColor()
        self.model.get_color_history().push_new(self.color)
    
    def undo(self):
        self.model.color = self.old_color
        self.model.widget.repaint()
        self.model.get_color_history().push_old(self.old_color)

class Clear(QtGui.QUndoCommand):
    def __init__(self, model):
        QtGui.QUndoCommand.__init__(self)
        self.setText(_("clearing color swatch"))
        self.model = model

    def redo(self):
        self.old_color = self.model.getColor()
        self.model.color = None
        self.model.widget.repaint()

    def undo(self):
        self.model.color = self.old_color
        self.model.widget.repaint()


