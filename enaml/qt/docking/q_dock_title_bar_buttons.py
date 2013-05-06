#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QPainter, QImage, QFrame, QCursor

from atom.api import Atom, Bool, Int, Value

# Make sure the resources get registered.
from . import dock_resources


class QDockTitleBarButtons(QFrame):
    """ A QFrame which manages the buttons for a QDockTitleBar.

    """
    #: A signal emitted when the close button is clicked.
    closeButtonClicked = pyqtSignal()

    class TitleButtonState(Atom):
        """ A private class which manages the object state.

        """
        #: Whether or not the close image is pressed.
        close_pressed = Bool(False)

    class ButtonImages(Atom):
        """ A private class for managing the button images.

        """
        #: The default button image.
        Default = 0

        #: The close hover button image.
        CloseHover = 1

        #: The close press button image.
        ClosePress = 2

        #: The array offset for the active button image.
        active = Int(Default)

        #: The images used to render the buttons.
        images = Value(factory=lambda: [
            QImage(':dock_images/titlebtn_s.png'),
            QImage(':dock_images/titlebtn_h.png'),
            QImage(':dock_images/titlebtn_p.png'),
        ])

    def __init__(self, parent=None):
        """ Initialize a QDockTitleBarButtons instance.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the window buttons.

        """
        super(QDockTitleBarButtons, self).__init__(parent)
        self.setMouseTracking(True)
        self._buttons = self.ButtonImages()
        self._state = self.TitleButtonState()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def hoverButtons(self, pos):
        """ Update the buttons for a hovered position.

        Parameters
        ----------
        pos : QPoint
            The position of interest, expressed in local coordinates.

        """
        buttons = self._buttons
        if self.rect().contains(pos):
            active = buttons.CloseHover
        else:
            active = buttons.Default
        if buttons.active != active:
            buttons.active = active
            self.update()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def sizeHint(self):
        """ Get the size hint for the window buttons.

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """ Get the minimum size hint for the window buttons.

        """
        buttons = self._buttons
        return buttons.images[buttons.Default].size()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def leaveEvent(self, event):
        """ Handle the leave event for the buttons.

        """
        buttons = self._buttons
        if buttons.active != buttons.Default:
            buttons.active = buttons.Default
            self.update()

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the buttons.

        """
        if event.button() == Qt.LeftButton:
            buttons = self._buttons
            state = self._state
            rect = self.rect()
            pos = event.pos()
            if rect.contains(pos):
                state.close_pressed = True
                active = buttons.ClosePress
            else:
                state.close_pressed = False
                active = buttons.Default
            if active != buttons.active:
                buttons.active = active
                self.update()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the buttons.

        """
        state = self._state
        if not state.close_pressed:
            self.hoverButtons(event.pos())
            return
        btns = self._buttons
        rect = self.rect()
        pos = event.pos()
        if rect.contains(pos):
            if state.close_pressed:
                active = btns.ClosePress
            else:
                active = btns.CloseHover
        else:
            active = btns.Default
        if active != btns.active:
            btns.active = active
            self.update()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the buttons.

        """
        if event.button() == Qt.LeftButton:
            state = self._state
            rect = self.rect()
            pos = event.pos()
            if rect.contains(pos) and state.close_pressed:
                self.closeButtonClicked.emit()
            state.close_pressed = False
            pos = self.mapFromGlobal(QCursor.pos())
            self.hoverButtons(pos)

    def paintEvent(self, event):
        """ Handle the paint event for the buttons.

        """
        super(QDockTitleBarButtons, self).paintEvent(event)
        painter = QPainter(self)
        buttons = self._buttons
        target = buttons.active
        image = buttons.images[target]
        painter.drawImage(self.rect(), image)
