
from PyQt5 import QtGui, QtCore, QtWidgets

from color.colors import *

MAX_CURSOR_SIZE=32

class Picker(QtWidgets.QPushButton):
    def __init__(self, parent, text, model):
        QtWidgets.QPushButton.__init__(self, text, parent)
        self.model = model
        self.color = None
        self._picking = False
        self._clicked = False
        self.border_color = None
        self.text = text
        self._colors = []
        self._grabbed_image = None
        self.clicked.connect(self._prepare)

    def emulate_click(self):
        self.clicked.emit(False)
        self._clicked = False
        self._picking = False
        self.repaint()

    def getColor(self):
        return self.model.getColor()

    def setColor(self, clr, undo=False):
        if self.model.to_set_color():
            self.model.setColor(clr)

    def is_empty(self):
        return self.model.getColor() is None
    
    def paintEvent(self, event):
        if not self._picking and not self._clicked:
            QtWidgets.QPushButton.paintEvent(self, event)
            return 

        clr = self.getColor()
        if clr is not None:
            tooltip = self.model.get_tooltip()
            if tooltip is not None:
                self.setToolTip(tooltip)
        qp = QtWidgets.QPainter()
        qp.begin(self)
        self.drawWidget(event, qp)
        qp.end()

    def _inner_square(self, rect):
        w,h = rect.width(), rect.height()
        size = min(w,h)
        if w > h:
            dx = (w - size) // 2
            dy = 0
        else:
            dx = 0
            dy = (h - size) // 2
        return QtCore.QRectF(rect.x()+dx, rect.y()+dy, size, size)
    
    def _mk_cursor(self):
        img = QtGui.QPixmap(MAX_CURSOR_SIZE, MAX_CURSOR_SIZE)
        img.fill(QtGui.QColor(255,255,255,0))
        qp = QtGui.QPainter()
        qp.begin(img)
        sqr_size = min(MAX_CURSOR_SIZE, self.model.options.picker_area)
        middle = MAX_CURSOR_SIZE//2
        d = (MAX_CURSOR_SIZE - sqr_size) // 2
        qp.drawRect(d,d, sqr_size, sqr_size)
        qp.drawLine(middle, 0, middle, d)
        qp.drawLine(middle, MAX_CURSOR_SIZE-d, middle, MAX_CURSOR_SIZE)
        qp.drawLine(0, middle, d, middle)
        qp.drawLine(MAX_CURSOR_SIZE-d, middle, MAX_CURSOR_SIZE, middle)
        qp.end()
        return QtGui.QCursor(img)

    def drawWidget(self, event,  qp):
        #print("Painting " + str(self))
        w, h = self.size().width(),  self.size().height()
        if self._clicked and not self._picking:
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, _("Click and drag to pick color"))
            return 
        if self.is_empty():
            if (w >= 70) and (h > 20):
                qp.drawText(event.rect(), QtCore.Qt.AlignCenter, _("<unset>"))
            if self.border_color is not None:
                qp.setPen(self.border_color)
                qp.drawRect(0, 0,  w,  h)
            return
        
        if self.border_color is not None:
            qp.setPen(self.border_color)
        clr = self.getColor()
        qp.setBrush(clr)
        if self._grabbed_image is None:
            qp.drawRect(0, 0,  w,  h)
        else:
            src_rect = QtCore.QRectF(0, 0, self._grabbed_image.width(), self._grabbed_image.height())
            if w >= h:
                qp.drawRect(0, 0,  w // 2,  h)
                rect = QtCore.QRectF(w // 2 + 1, 0, w // 2, h)
            else:
                qp.drawRect(0, 0,  w,  h // 2)
                rect = QtCore.QRectF(0, h // 2 + 1, w, h // 2)
            dst_rect = self._inner_square(rect)
            qp.drawImage(dst_rect, self._grabbed_image, src_rect)
        if (w >= 150) and (h >= 50):
            qp.setPen(clr.invert())
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, clr.verbose())

    def mouseMoveEvent(self, event):
        if self._picking:
            self._pick_color(event.globalPos())
            return
        return QtWidgets.QPushButton.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        res = QtWidgets.QPushButton.mousePressEvent(self, event)
        self._picking = self._clicked

        if self._picking:
            self._pick_color(event.globalPos())
        return res
    
    def mouseReleaseEvent(self, event):
        if self._picking:
            self._picking = False
            self.releaseKeyboard()
            self.releaseMouse()
            self._pick_color(event.globalPos())
        if self._clicked:
            self._clicked = False
            self.repaint()
        return QtWidgets.QPushButton.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event):
        if self._clicked or self._picking:
            if event.key() == QtCore.Qt.Key_Escape:
                self._picking = False
                self._clicked = False
                self.releaseKeyboard()
                self.releaseMouse()
            event.accept()
            return
        return QtWidgets.QPushButton.keyPressEvent(self, event)

    def _prepare(self, event):
        #print "Clicked"
        self._clicked = True
        self.grabKeyboard()
        self.grabMouse(self._mk_cursor())
        self._colors = []
        self.repaint()

    def _average(self):
        n = 0
        rr = 0
        gg = 0
        bb = 0
        if not self._colors:
            return None
        for r,g,b in self._colors:
            n += 1
            rr += r
            gg += g
            bb += b
        return Color(rr // n, gg // n, bb // n)

    def _grab(self, img):
        colors = []
        for x in range(0, img.width()):
            for y in range(0, img.height()):
                r,g,b,a = QtGui.QColor(img.pixel(x,y)).getRgb()
                colors.append((r,g,b))
        return colors

    def _pick_color(self, pos):
        desktop = QtWidgets.QApplication.desktop().winId()
        #screen = QtWidgets.QApplication.desktop().primaryScreen()
        size = self.model.options.picker_area
        dx = dy = size // 2
        pixmap = QtGui.QPixmap.grabWindow(desktop, pos.x() - dx, pos.y() - dy, size, size)
        self._grabbed_image = img = pixmap.toImage()
        if self.model.options.picker_average:
            self._colors.extend(self._grab(img))
        else:
            self._colors = self._grab(img)
        color = self._average()
        self.setColor(color)
        self.repaint()

