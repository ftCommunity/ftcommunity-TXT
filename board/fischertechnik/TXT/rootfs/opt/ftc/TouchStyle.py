# TouchStyle application
#
# Initially meant to implement a TXT Qt style. Now also includes
# additional functionality to communicate with the app launcher and
# the like
import os
import socket
import struct
import time
import weakref

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

__version__ = '1.8'


TouchStyle_version = float(__version__)  # Kept for backward compatibility

# enable special features for the Fischertechnik TXT
# The TXT can be detected by the presence of /etc/fw-ver.txt
TXT = os.path.isfile("/etc/fw-ver.txt")
# TX-Pi?
TXPI = os.path.isfile('/etc/tx-pi')
# check for Fischertechnik community firmware app development settings
DEV = os.path.isfile("/etc/ft-cfw-dev.txt")


DEV_ORIENTATION = "PORTRAIT"

if DEV:
    TXT = False
    # versuche, die dev config zu lesen
    try:
        dcfile = open("/etc/ft-cfw-dev.txt", "r")
        for line in dcfile:
            if not ("#" in line):
                if "orientation" in line and "landscape" in line:
                    DEV_ORIENTATION = "LANDSCAPE"
        dcfile.close()
    except:
        pass
        
        

INPUT_EVENT_DEVICE = None

if TXT and not TXPI:  # The TX-Pi has no hardware button but is treated as TXT
    # TXT values
    INPUT_EVENT_DEVICE = "/dev/input/event1"
    INPUT_EVENT_CODE = 116
elif 'TOUCHUI_BUTTON_INPUT' in os.environ:
    (d, c) = os.environ.get('TOUCHUI_BUTTON_INPUT').split(':')
    INPUT_EVENT_DEVICE = d
    INPUT_EVENT_CODE = int(c)

INPUT_EVENT_FORMAT = 'llHHI'
INPUT_EVENT_SIZE = struct.calcsize(INPUT_EVENT_FORMAT)

STYLE_NAME = "themes/default/style.qss"




        
def getScreenSize():
    if TXT or TXPI:
        return QApplication.desktop().screenGeometry().size()

    if 'SCREEN' in os.environ:
        (w, h) = os.environ.get('SCREEN').split('x')
        return QSize(int(w), int(h))

    if DEV_ORIENTATION == "LANDSCAPE":
        return QSize(320, 240)
    
    return QSize(240, 320)
        


# background thread to monitor power button event device
class ButtonThread(QThread):
    power_button_released = pyqtSignal()
    
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        in_file = open(INPUT_EVENT_DEVICE, "rb")
        event = in_file.read(INPUT_EVENT_SIZE)
        while event:
            (tv_sec, tv_usec, type, code, value) = struct.unpack(INPUT_EVENT_FORMAT, event)
            if type == 1 and code == INPUT_EVENT_CODE and value == 0:
                self.power_button_released.emit()
            event = in_file.read(INPUT_EVENT_SIZE)
        return

if INPUT_EVENT_DEVICE:
    BUTTON_THREAD = ButtonThread()
    BUTTON_THREAD.start()
else:
    BUTTON_THREAD = None


def TouchSetStyle(self):
    # try to find style sheet and load it
    base = os.path.dirname(os.path.realpath(__file__)) + "/"
    if os.path.isfile(base + STYLE_NAME):
        self.setStyleSheet("file:///" + base + STYLE_NAME)
    elif os.path.isfile("/opt/ftc/" + STYLE_NAME):
        self.setStyleSheet("file:///" + "/opt/ftc/" + STYLE_NAME)


class TouchMenu(QMenu):
    def __init__(self, parent=None):
        super(TouchMenu, self).__init__(parent)

    def on_button_clicked(self):
        pos = self.parent().mapToGlobal(QPoint(0, 40))
        self.popup(pos)


# The TXTs window title bar
class TouchTitle(QLabel):
    def __init__(self, str, parent=None):
        super(TouchTitle, self).__init__(str, parent)
        self.setObjectName("titlebar")
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.close = QPushButton(self)
        self.close.setObjectName("closebut")
        self.parent = parent
        self.close.clicked.connect(parent.close)
        self.close.move(self.width() - 40, self.height() // 2 - 20)
        self.installEventFilter(self)
        self.menubut = None
        self.confbut = None

    def eventFilter(self, obj, event):
        if event.type() == event.Resize:
            self.close.move(self.width() - 40, self.height() // 2 - 20)
            if self.menubut:
                self.menubut.move(8, self.height() // 2 - 20)
            if self.confbut:
                self.confbut.move(8, self.height() // 2 - 20)
        return False

    def addMenu(self):
        self.menubut = QPushButton(self)
        self.menubut.setObjectName("menubut")
        self.menubut.move(8, self.height() // 2 - 20)
        self.menu = TouchMenu(self.menubut)
        self.menubut.clicked.connect(self.menu.on_button_clicked)
        return self.menu

    def addConfirm(self):
        self.confbut = QPushButton(self)
        self.confbut.setObjectName("confirmbut")
        self.confbut.move(8, self.height() // 2 - 20)
        self.confbut.setDefault(True)
        self.confbut.clicked.connect(self.parent.close)
        return self.confbut
    
    def setCancelButton(self):
        self.close.setObjectName("cancelbut")


# The TXT does not use windows. Instead we just paint custom toplevel
# windows fullscreen. This widget is closed when the pwoer button is
# being pressed.
#
# To do: This class notifies the launcher which should be de-coupled.
class TouchBaseWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setFixedSize(getScreenSize())
        self.setObjectName("centralwidget")

        if BUTTON_THREAD:
            BUTTON_THREAD.power_button_released.connect(self.close)

    # TXT windows are always fullscreen on arm (txt itself)
    # and windowed else (e.g. on PC)
    def show(self):
        if TXT or TXPI and not DEV:
            QWidget.showFullScreen(self)
        else:
            QWidget.show(self)
        # send a message to the launcher once the main widget has been
        # drawn for the first time
        self.notify_launcher()

    def notify_launcher(self):
        # send a signal so launcher knows that the app
        # is up and can stop the busy animation
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect(("localhost", 9000))
            sock.sendall(bytes("app-running {}\n".format(os.getpid()), "UTF-8"))
        except socket.error as msg:
            pass
        finally:
            sock.close()



class TouchWindow(TouchBaseWidget):
    def __init__(self,str):
        TouchBaseWidget.__init__(self)
        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.titlebar = TouchTitle(str, self)
        self.layout.addWidget(self.titlebar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # add an empty widget as the centralWidget
        self.centralWidget = QWidget()
        self.layout.addWidget(self.centralWidget)
        self.setLayout(self.layout)

    def setCentralWidget(self, w):
        # remove the old central widget and add a new one
        self.centralWidget.deleteLater()
        self.centralWidget = w
        self.layout.addWidget(self.centralWidget)

    def addMenu(self):
        return self.titlebar.addMenu()


class TouchDialog(QDialog):
    def __init__(self,title,parent):
        QDialog.__init__(self,parent)

        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(getScreenSize())
        self.setObjectName("centralwidget")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        if title:
            self.titlebar = TouchTitle(title, self)
            self.layout.addWidget(self.titlebar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # add an empty widget as the centralWidget
        self.centralWidget = QWidget()
        self.layout.addWidget(self.centralWidget)
        self.setLayout(self.layout)

    def setCentralWidget(self, w):
        # remove the old central widget and add a new one
        self.centralWidget.deleteLater()
        self.centralWidget = w
        self.layout.addWidget(self.centralWidget)

    def addMenu(self):
        return self.titlebar.addMenu()

    def addConfirm(self):
        return self.titlebar.addConfirm()
    
    def setCancelButton(self):
        return self.titlebar.setCancelButton()
        
    # TXT windows are always fullscreen
    def exec_(self):
        if TXT or TXPI and not DEV:
            QWidget.showFullScreen(self)
        else:
            QWidget.show(self)
        QDialog.exec_(self)


class TouchMessageBox(TouchDialog):
    """ Versatile MessageBox for TouchUI
        
        msg = TouchMessageBox(title, parent)
        
        Methods:
        
        msg.addConfirm() adds confirm button at the left of the title
        msg.setCancelButton() changes style of the close icon to cancel icon
        
        msg.addPixmap(QPixmap) adds a QPixmap to be shown on top of the message text
        msg.setPixmapBelow() places the pixmap below the text (inbetween text and buttons), defalt is above the text
        
        msg.setText(text) sets message text, default ist empty string
        msg.setPosButton(pos_button_text) sets text for positive button, default is None (no button)
        msg.setNegButton(neg_button_text) sets text for negative button, default is None (no button)
        
        msg.setTextSize(size) set 4- big 3 - normal (default); 2 - smaller; 1 - smallest
        msg.setBtnTextSize(size)
        
        msg.alignTop() aligns message text to top of the window
        msg.alignCenter() centers text in window (default)
        msg.alignBottom() aligns message text to bottom of the window
    
        msg.buttonsVertical(bool=True) arrange buttons on top of each other (True, default) or side-by-side (False)
        msg.buttonsHorizontal(bool=True) see above...
        
        Return values:
        
        (success, text) = msg.exec_()
        success == True if one of the buttons or the confirm button was used
        success == False if MessageBox was closed by its close icon (top right)
        
        text == None if MessageBox was closed by its close icon
        text == pos_button_text | neg_button_text depending on which button was clicked
    """
    
    
    def __init__(self,title,parent):
        TouchDialog.__init__(self, title, parent)
        self.buttVert = True
        self.align = 2
        self.textSize = 3
        self.btnTextSize = 3
        self.pixmap = None
        self.pmapalign = 1
        self.text = ""
        self.text_okay = None
        self.text_deny = None
        self.confbutclicked = False
        self.confirm = None
        self.result = ""
        
    def addConfirm(self):
        self.confirm = self.titlebar.addConfirm()
        self.confirm.clicked.connect(self.on_confirm)
        
    def addPixmap(self, pmap: QPixmap):
        self.pixmap=pmap

    def setPixmapBelow(self):
        self.pmapalign = 2

    def buttonsVertical(self, flag=True):
        self.buttVert = flag

    def buttonsHorizontal(self, flag=True):
        self.buttVert = not flag

    def setText(self, text):
        self.text = text

    def setPosButton(self, text):
        self.text_okay = text

    def setNegButton(self, text):
        self.text_deny = text

    def setTextSize(self, size):
        if size > 0 and size < 5:
            self.textSize = size
        else:
            self.textSize = 3

    def setBtnTextSize(self, size):
        if size > 0 and size < 5:
            self.btnTextSize = size
        else:
            self.btnTextSize = 3

    def alignTop(self):
        self.align = 1

    def alignCenter(self):
        self.align = 2

    def alignBottom(self):
        self.align = 3

    def on_confirm(self):
        self.confbutclicked = True
        self.close()
        
    def on_select(self):
        self.result = self.sender().text()
        self.close()
     
    def exec_(self):
        self.result = ""
        self.layout = QVBoxLayout()
        
        # the pixmap ist (in case of pmapalign=1
        if self.pixmap and self.pmapalign==1:
            ph = QHBoxLayout()
            ph.addStretch()
            p = QLabel()
            p.setPixmap(self.pixmap)
            ph.addWidget(p)
            ph.addStretch()
            self.layout.addLayout(ph)
            
        # text horiontal alignment in vbox
        if self.align > 1:
            self.layout.addStretch()
        
        # the message is:
        textfield = QTextEdit(self.text)#QLabel(self.text)

        if self.textSize == 4:
            textfield.setObjectName("biglabel")
        elif self.textSize == 3:
            textfield.setObjectName("smalllabel")
        elif self.textSize == 2:
            textfield.setObjectName("smallerlabel")
        elif self.textSize == 1:
            textfield.setObjectName("tinylabel")

        textfield.setAlignment(Qt.AlignCenter)
        textfield.setReadOnly(True)
        self.layout.addWidget(textfield)
        
        # the pixmap ist (in case of pmapalign=1
        if self.pixmap and self.pmapalign == 2:
            ph = QHBoxLayout()
            ph.addStretch()
            p = QLabel()
            p.setPixmap(self.pixmap)
            ph.addWidget(p)
            ph.addStretch()
            self.layout.addLayout(ph)
        
        
        # the buttons are:
        if not (self.text_okay==None and self.text_deny==None):
            butbox = QWidget()
            if self.buttVert:
                blayou = QVBoxLayout()
            else:
                blayou = QHBoxLayout()
            butbox.setLayout(blayou)
            if self.buttVert:
                blayou.addStretch()

        if self.text_okay is not None:
            but_okay = QPushButton(self.text_okay)

            if self.btnTextSize == 4:
                but_okay.setObjectName("biglabel")
            elif self.btnTextSize == 3:
                but_okay.setObjectName("smalllabel")
            elif self.btnTextSize == 2:
                but_okay.setObjectName("smallerlabel")
            elif self.btnTextSize == 1:
                but_okay.setObjectName("tinylabel")
            
            but_okay.clicked.connect(self.on_select)
        
            blayou.addWidget(but_okay)

        if self.text_deny is not None:
            but_deny = QPushButton(self.text_deny)

            if self.btnTextSize == 4:
                but_deny.setObjectName("biglabel")
            elif self.btnTextSize == 3:
                but_deny.setObjectName("smalllabel")
            elif self.btnTextSize == 2:
                but_deny.setObjectName("smallerlabel")
            elif self.btnTextSize == 1:
                but_deny.setObjectName("tinylabel")

            but_deny.clicked.connect(self.on_select)

            blayou.addWidget(but_deny)
        
        # finalize layout
        if self.align < 3:
            self.layout.addStretch()
        
        if not (self.text_okay==None and self.text_deny==None):
            self.layout.addWidget(butbox)
        
        self.centralWidget.setLayout(self.layout)
        
        # and run...
        TouchDialog.exec_(self)
        if self.confbutclicked == True:
            return True, None
        if self.result:
            return True, self.result
        if self.confirm != None:
            return False, None
        return None, None


class _LazyTouchHandler(QObject):
    """Defer importing touch_keyboard until a QLineEdit is actually tapped."""
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._handler = None

    def eventFilter(self, widget, event):
        if (event.type() == QEvent.MouseButtonPress
                and widget.inherits("QLineEdit")
                and not widget.inherits("FocusLineEdit")):
            if self._handler is None:
                import touch_keyboard
                self._handler = touch_keyboard.TouchHandler(self.parent())
            return self._handler.eventFilter(widget, event)
        return False


class _TouchWindowObserver(QObject):
    """Forward spontaneous QWindow mouse events from a single top-level window to TouchTapGuard."""

    def __init__(self, guard):
        super(_TouchWindowObserver, self).__init__(guard)
        self._guard = guard

    def eventFilter(self, obj, event):
        etype = event.type()
        if etype in (QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.MouseButtonRelease):
            self._guard._handle_window_mouse(etype, event)
        return False


class TouchTapGuard(QObject):
    """Track pointer displacement, dropouts, and scroll state to reject swipe-triggered taps."""

    DEFAULT_MAX_TAP_DISTANCE = 10
    DEFAULT_MIN_TAP_HOLD_MS = 110
    DEFAULT_COALESCE_GAP_MS = 140
    DEFAULT_POST_DRAG_COOLDOWN_MS = 250

    def __init__(
        self,
        scroll_area=None,
        scroller=None,
        max_tap_distance=DEFAULT_MAX_TAP_DISTANCE,
        min_tap_hold_ms=DEFAULT_MIN_TAP_HOLD_MS,
        coalesce_gap_ms=DEFAULT_COALESCE_GAP_MS,
        post_drag_cooldown_ms=DEFAULT_POST_DRAG_COOLDOWN_MS,
        filter_viewport_clicks=False,
        parent=None,
    ):
        super(TouchTapGuard, self).__init__(parent or scroll_area)
        self._scroll_area = scroll_area
        self._scroller = scroller
        self._viewport = (
            scroll_area.viewport()
            if hasattr(scroll_area, "viewport")
            else scroll_area
        )
        self._max_dist = max_tap_distance
        self._min_tap_hold_ms = min_tap_hold_ms
        self._coalesce_gap_ms = coalesce_gap_ms
        self._coalesce_gap_s = coalesce_gap_ms / 1000.0
        self._post_drag_cooldown_s = post_drag_cooldown_ms / 1000.0
        self._filter_viewport_clicks = bool(filter_viewport_clicks)

        # Fallback per-widget state (used only before QWindow events arrive, e.g. direct QTest calls)
        self._press_pos = None
        self._press_scroll = None
        self._suppressed = False
        self._forwarding = False
        self._gesture_suppressed = False

        # Authoritative physical pointer timeline on windowHandle() before QScroller buffering/replay
        self._window_observer = _TouchWindowObserver(self)
        self._hooked_top_widget_ref = None
        self._hooked_window_id = None
        self._seen_window_events = False
        self._phys_active = False
        self._phys_press_pos = None
        self._phys_press_ts = 0
        self._phys_press_mono = 0.0
        self._phys_press_scroll = None
        self._phys_moved = False
        self._phys_suppressed = False
        self._chain_origin_pos = None
        self._last_phys_press_pos = None
        self._last_phys_release_pos = None
        self._last_phys_release_mono = None
        self._last_phys_release_ts = 0
        self._last_phys_dur_ms = 0.0
        self._last_phys_was_drag = False
        self._last_phys_suppressed = False
        self._last_drag_mono = None
        self._last_phys_stroke_id = 0

        # Deferred confirmation timer for single-sample (< min_tap_hold_ms) releases
        self._pending_widget_ref = None
        self._pending_callback = None
        self._pending_stroke_id = -1
        self._pending_timer = QTimer(self)
        self._pending_timer.setSingleShot(True)
        self._pending_timer.timeout.connect(self._fire_pending_tap)

    def _current_scroll_value(self):
        if self._scroll_area is None or not hasattr(self._scroll_area, "verticalScrollBar"):
            return None
        vbar = self._scroll_area.verticalScrollBar()
        return vbar.value() if vbar is not None else None

    def _scrolled_since(self, press_scroll):
        if press_scroll is None:
            return False
        cur = self._current_scroll_value()
        return cur is not None and abs(cur - press_scroll) > 2

    def _on_window_destroyed(self, *_args):
        self._hooked_window_id = None
        self._hooked_top_widget_ref = None

    def attach_window_observer(self):
        """Install passive mouse observer on the top-level QWindow hosting our scroll area."""
        host = self._viewport or self._scroll_area
        if host is None:
            return
        top = host.window() if hasattr(host, "window") else None
        wh = top.windowHandle() if top is not None else None
        if wh is None:
            return
        try:
            win_id = int(wh.winId())
        except Exception:
            win_id = id(top)
        old_top = self._hooked_top_widget_ref() if self._hooked_top_widget_ref is not None else None
        if self._hooked_window_id == win_id and old_top is top:
            return
        wh.installEventFilter(self._window_observer)
        try:
            wh.destroyed.connect(self._on_window_destroyed)
        except Exception:
            pass
        self._hooked_window_id = win_id
        self._hooked_top_widget_ref = weakref.ref(top)

    def _in_scroll_viewport(self, global_pos):
        if QApplication.activePopupWidget() is not None:
            return False
        vp = self._viewport
        if vp is None or not vp.isVisible():
            return False
        return vp.rect().contains(vp.mapFromGlobal(global_pos))

    def _cancel_pending_tap(self):
        if self._pending_timer.isActive():
            self._pending_timer.stop()
        self._pending_widget_ref = None
        self._pending_callback = None
        self._pending_stroke_id = -1

    def _schedule_deferred_tap(self, widget, callback):
        self._cancel_pending_tap()
        self._pending_widget_ref = weakref.ref(widget) if widget is not None else None
        self._pending_callback = callback
        self._pending_stroke_id = self._last_phys_stroke_id
        self._pending_timer.start(self._coalesce_gap_ms)

    def _fire_pending_tap(self):
        cb = self._pending_callback
        w_ref = self._pending_widget_ref
        stroke_id = self._pending_stroke_id
        self._pending_widget_ref = None
        self._pending_callback = None
        self._pending_stroke_id = -1
        if cb is None or self._phys_active or stroke_id != self._last_phys_stroke_id:
            return
        if self._gesture_suppressed or self._last_phys_suppressed or self.is_scroller_scrolling():
            return
        if QApplication.activePopupWidget() is not None:
            return
        if w_ref is not None:
            w = w_ref()
            try:
                if w is None or not w.isVisible() or not w.isEnabled():
                    return
            except RuntimeError:
                return
        cb()

    def is_scroller_scrolling(self):
        return (
            self._scroller is not None
            and self._scroller.state() in (QScroller.Dragging, QScroller.Scrolling)
        )

    def _moved_too_far(self, global_pos, origin=None):
        ref = origin if origin is not None else self._press_pos
        if ref is None:
            return False
        return (global_pos - ref).manhattanLength() > self._max_dist

    def _elapsed_ms(self, start_ts, start_mono, end_ts, end_mono):
        if (
            start_ts
            and end_ts >= start_ts
            and QApplication.platformName() != "offscreen"
        ):
            return float(end_ts - start_ts)
        return (end_mono - start_mono) * 1000.0

    def _any_moved_too_far(self, global_pos, origins):
        return any(self._moved_too_far(global_pos, origin) for origin in origins if origin is not None)

    def _active_drag_detected(self, global_pos):
        return (
            self._any_moved_too_far(global_pos, (self._phys_press_pos, self._chain_origin_pos))
            or self._scrolled_since(self._phys_press_scroll)
            or self.is_scroller_scrolling()
        )

    def _on_window_press(self, event, now):
        global_pos = event.globalPos()
        if not self._in_scroll_viewport(global_pos):
            return
        self._seen_window_events = True
        self._gesture_suppressed = False
        self._cancel_pending_tap()

        scrolling = self.is_scroller_scrolling()
        ev_ts = event.timestamp()
        within_gap = False
        if self._last_phys_release_mono is not None:
            gap_ms = self._elapsed_ms(
                self._last_phys_release_ts,
                self._last_phys_release_mono,
                ev_ts,
                now,
            )
            within_gap = (
                gap_ms <= self._coalesce_gap_ms
                or (now - self._last_phys_release_mono) <= self._coalesce_gap_s
            )
        if within_gap:
            if self._chain_origin_pos is None:
                self._chain_origin_pos = self._last_phys_press_pos
            displaced = self._any_moved_too_far(
                global_pos,
                (self._last_phys_release_pos, self._last_phys_press_pos, self._chain_origin_pos),
            )
            suppressed = (
                scrolling
                or self._last_phys_was_drag
                or self._last_phys_suppressed
                or displaced
            )
        else:
            self._chain_origin_pos = global_pos
            suppressed = scrolling

        self._phys_active = True
        self._phys_press_pos = global_pos
        self._phys_press_ts = ev_ts
        self._phys_press_mono = now
        self._phys_press_scroll = self._current_scroll_value()
        self._phys_moved = False
        self._phys_suppressed = suppressed
        if suppressed:
            self._last_drag_mono = now

    def _on_window_release(self, event, now):
        global_pos = event.globalPos()
        ev_ts = event.timestamp()
        dur_ms = self._elapsed_ms(self._phys_press_ts, self._phys_press_mono, ev_ts, now)
        moved = self._phys_moved or self._active_drag_detected(global_pos)
        in_cooldown = (
            self._last_drag_mono is not None
            and (self._phys_press_mono - self._last_drag_mono) <= self._post_drag_cooldown_s
            and dur_ms < self._min_tap_hold_ms
        )
        suppressed = self._phys_suppressed or moved or in_cooldown or self._gesture_suppressed
        if suppressed or moved:
            self._last_drag_mono = now

        self._last_phys_press_pos = self._phys_press_pos
        self._last_phys_release_pos = global_pos
        self._last_phys_release_mono = now
        self._last_phys_release_ts = ev_ts
        self._last_phys_dur_ms = dur_ms
        self._last_phys_was_drag = moved or self.is_scroller_scrolling()
        self._last_phys_suppressed = suppressed
        self._last_phys_stroke_id += 1
        self._phys_active = False

    def _handle_window_mouse(self, etype, event):
        now = time.monotonic()
        if etype == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self._on_window_press(event, now)
        elif etype == QEvent.MouseMove and self._phys_active and (event.buttons() & Qt.LeftButton):
            if self._active_drag_detected(event.globalPos()):
                self._phys_moved = True
                self._phys_suppressed = True
                self._last_drag_mono = now
        elif etype == QEvent.MouseButtonRelease and self._phys_active and event.button() == Qt.LeftButton:
            self._on_window_release(event, now)

    def mark_suppressed(self):
        self._suppressed = True
        self._gesture_suppressed = True
        self._phys_suppressed = True
        self._last_phys_suppressed = True
        self._cancel_pending_tap()

    def _current_window_suppressed(self):
        if self._gesture_suppressed or self.is_scroller_scrolling():
            return True
        if self._phys_active:
            return self._phys_suppressed
        return self._last_phys_suppressed

    def on_press(self, global_pos):
        self.attach_window_observer()
        self._gesture_suppressed = False
        if self._seen_window_events:
            return not self._current_window_suppressed()
        if self.is_scroller_scrolling():
            self._press_pos = None
            self._press_scroll = None
            self._suppressed = True
            return False
        self._press_pos = global_pos
        self._press_scroll = self._current_scroll_value()
        self._suppressed = False
        return True

    def on_move(self, global_pos):
        if self._seen_window_events:
            return not self._current_window_suppressed()
        if self._press_pos is not None and not self._suppressed:
            if self._moved_too_far(global_pos) or self._scrolled_since(self._press_scroll):
                self._suppressed = True
        return not self._suppressed

    def consume_release(self, global_pos, widget=None, callback=None):
        """Return 'allow', 'defer', or 'suppress' for a button release."""
        self.attach_window_observer()
        if self._seen_window_events:
            suppressed = (
                self._current_window_suppressed()
                or self._scrolled_since(self._phys_press_scroll)
            )
            self._gesture_suppressed = False
            if suppressed:
                self._cancel_pending_tap()
                return "suppress"
            if callback is not None and self._last_phys_dur_ms < self._min_tap_hold_ms:
                self._schedule_deferred_tap(widget, callback)
                return "defer"
            return "allow"

        suppress = (
            self._suppressed
            or self._gesture_suppressed
            or self._moved_too_far(global_pos)
            or self._scrolled_since(self._press_scroll)
            or self.is_scroller_scrolling()
        )
        self._press_pos = None
        self._press_scroll = None
        self._suppressed = False
        self._gesture_suppressed = False
        return "suppress" if suppress else "allow"

    def should_suppress_release(self, global_pos):
        return self.consume_release(global_pos) == "suppress"

    def eventFilter(self, obj, event):
        etype = event.type()
        if etype in (QEvent.Show, QEvent.ParentChange, QEvent.ShowToParent, QEvent.WindowActivate, QEvent.Paint):
            self.attach_window_observer()
            return False

        if not self._filter_viewport_clicks or self._forwarding:
            return False
        if etype == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if not self.on_press(event.globalPos()):
                event.accept()
                return True
        elif etype == QEvent.MouseMove and (event.buttons() & Qt.LeftButton):
            self.on_move(event.globalPos())
        elif etype == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if self.should_suppress_release(event.globalPos()):
                # Release outside viewport so item views reset pressed state without clicking.
                cancel_pos = QPoint(-1, -1)
                cancel_ev = QMouseEvent(
                    QEvent.MouseButtonRelease,
                    cancel_pos,
                    obj.mapToGlobal(cancel_pos),
                    Qt.LeftButton,
                    Qt.NoButton,
                    event.modifiers(),
                )
                self._forwarding = True
                try:
                    QApplication.sendEvent(obj, cancel_ev)
                finally:
                    self._forwarding = False
                event.accept()
                return True
        return False


def configure_touch_scroller(
    widget,
    drag_distance_px=10,
    suppress_drag_clicks=False,
    scroll_area=None,
    max_tap_distance=10,
):
    """Enable left-button kinetic scrolling with DPI-scaled thresholds and shared tap guard."""
    QScroller.grabGesture(widget, QScroller.LeftMouseButtonGesture)
    scroller = QScroller.scroller(widget)
    props = scroller.scrollerProperties()
    screen = QApplication.primaryScreen()
    dpi = screen.physicalDotsPerInchY() if screen is not None else 0.0
    if dpi > 0:
        props.setScrollMetric(
            QScrollerProperties.DragStartDistance,
            drag_distance_px * 0.0254 / dpi,
        )
    props.setScrollMetric(QScrollerProperties.MaximumClickThroughVelocity, 0.0)
    scroller.setScrollerProperties(props)
    area = scroll_area
    if area is None and isinstance(widget.parentWidget(), QAbstractScrollArea):
        area = widget.parentWidget()
    if suppress_drag_clicks or area is not None:
        guard = getattr(area, "_touch_tap_guard", None) if area is not None else None
        if guard is None:
            guard = TouchTapGuard(
                area or widget,
                scroller=scroller,
                max_tap_distance=max_tap_distance,
                filter_viewport_clicks=suppress_drag_clicks,
                parent=widget,
            )
            widget.installEventFilter(guard)
            guard.attach_window_observer()
            if area is not None:
                area._touch_tap_guard = guard
        widget._touch_tap_guard = guard
    return scroller


class TouchApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        self.installEventFilter(_LazyTouchHandler(self))
        TouchSetStyle(self)


_BUSY_FRAME_CACHE = {}


def _draw_busy_dot(size, color_hex):
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    painter = QPainter(img)
    painter.setPen(Qt.white)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setBrush(QBrush(QColor(color_hex)))
    painter.drawEllipse(0, 0, img.width() - 1, img.height() - 1)
    painter.end()
    return img


def render_busy_frames(width, height, dot_size=16, dark_hex="#808080", bright_hex="#fcce04"):
    """Pre-render and cache the 8 rotated QPixmap frames for BusyAnimation."""
    key = (width, height, dot_size, dark_hex, bright_hex)
    cached = _BUSY_FRAME_CACHE.get(key)
    if cached is not None:
        return cached

    dark = _draw_busy_dot(dot_size, dark_hex)
    bright = _draw_busy_dot(dot_size, bright_hex)
    radius = min(width, height) // 2 - dot_size
    frames = []
    for step in range(0, 360, 45):
        pm = QPixmap(width, height)
        pm.fill(Qt.transparent)
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(width // 2, height // 2)
        painter.rotate(45 + step)
        painter.drawImage(0, radius, bright)
        for _ in range(7):
            painter.rotate(45)
            painter.drawImage(0, radius, dark)
        painter.end()
        frames.append(pm)

    result = (tuple(frames), dark, bright)
    _BUSY_FRAME_CACHE[key] = result
    return result


class BusyAnimation(QWidget):
    """Shows a busy animation on top of any application.
    """
    expired = pyqtSignal()

    def __init__(self, parent=None, process=None, timeout_s=None):
        # if an process or a timeout is specified, then the widget
        # closes itself if process.poll() is not None, or if the
        # timeout is expired, respectively.
        super(BusyAnimation, self).__init__(parent)
        self.resize(64, 64)
        # center relative to parent
        self.move(QPoint(parent.width() // 2 - 32, parent.height() // 2 - 32))
        self.step = 0
        self.process = process
        # create a timer to close this window after the timeout expired
        self.etimer = QTimer(self)
        if timeout_s:
            self.etimer.setSingleShot(True)
            self.etimer.timeout.connect(self.timer_expired)
            self.etimer.start(timeout_s * 1000)
        # animate at 5 frames/sec
        self.atimer = QTimer(self)
        self.atimer.timeout.connect(self.animate)
        self.atimer.start(200)
        # reuse pre-rendered frames to avoid rotating bitmaps on every tick
        self._frames, self.dark, self.bright = render_busy_frames(self.width(), self.height())

    def draw(self, size, color):
        return _draw_busy_dot(size, color.name() if isinstance(color, QColor) else color)

    def timer_expired(self):
        # App launch expired without callback ...
        self.expired.emit()

    def animate(self):
        # if the app isn't running anymore then stop the
        # animation. This typically only happens for non-txt-styled
        # apps or with apps crashing.
        #
        # We might tell the user that the app ended unexpectedly
        if self.process is not None and self.process.poll() is not None:
            self.close()
            return
        self.step = (self.step + 45) % 360
        self.update()

    def close(self):
        self.etimer.stop()
        self.atimer.stop()
        super(BusyAnimation, self).close()
        super(BusyAnimation, self).deleteLater()

    def paintEvent(self, event):
        frame_idx = (self.step // 45) % len(self._frames)
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, self._frames[frame_idx])
        painter.end()
