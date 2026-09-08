from PyQt5.QtCore import (
    QPoint, QPropertyAnimation, QRect, QSize, Qt, QTimer, pyqtProperty,
)
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PyQt5.QtWidgets import QApplication, QWidget

# Avatar states
IDLE       = "idle"
WATCHING   = "watching"
THINKING   = "thinking"
SPEAKING   = "speaking"
ALERT      = "alert"
CONCERNED  = "concerned"
ERROR      = "error"
AWAY       = "away"

STATE_COLORS = {
    IDLE:      QColor(80, 140, 255),
    WATCHING:  QColor(200, 200, 200),
    THINKING:  QColor(255, 180, 40),
    SPEAKING:  QColor(60, 210, 100),
    ALERT:     QColor(255, 140, 30),
    CONCERNED: QColor(160, 80, 220),
    ERROR:     QColor(220, 50, 50),
    AWAY:      QColor(60, 60, 60),
}


class AvatarWidget(QWidget):
    def __init__(self, on_click=None):
        super().__init__()
        self._state = IDLE
        self._pulse = 0.0
        self._spin_angle = 0
        self._on_click = on_click
        self._drag_pos = None

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(QSize(80, 80))

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

        self._pulse_dir = 1

    def set_state(self, state: str):
        self._state = state
        self.update()

    def _tick(self):
        self._pulse += 0.05 * self._pulse_dir
        if self._pulse >= 1.0:
            self._pulse_dir = -1
        elif self._pulse <= 0.0:
            self._pulse_dir = 1

        if self._state == THINKING:
            self._spin_angle = (self._spin_angle + 8) % 360

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self._state == AWAY:
            self._draw_away(painter)
            return

        color = STATE_COLORS.get(self._state, STATE_COLORS[IDLE])
        alpha = int(180 + 75 * self._pulse)
        color.setAlpha(alpha)

        # Outer glow ring
        glow = QColor(color)
        glow.setAlpha(40)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(4, 4, 72, 72)

        # Main face circle
        face_color = QColor(30, 30, 40, 230)
        painter.setBrush(QBrush(face_color))
        ring_pen = QPen(color, 2)
        painter.setPen(ring_pen)
        painter.drawEllipse(8, 8, 64, 64)

        # Eyes
        self._draw_eyes(painter, color)

        # Thinking spinner
        if self._state == THINKING:
            self._draw_spinner(painter, color)

        # Speaking pulse dot
        if self._state == SPEAKING:
            self._draw_mouth_pulse(painter, color)

        painter.end()

    def _draw_eyes(self, painter: QPainter, color: QColor):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))

        if self._state == IDLE:
            # Half-closed
            painter.drawEllipse(22, 33, 10, 6)
            painter.drawEllipse(48, 33, 10, 6)
        elif self._state in (WATCHING, SPEAKING):
            # Normal open
            painter.drawEllipse(21, 30, 12, 12)
            painter.drawEllipse(47, 30, 12, 12)
            # Pupils
            painter.setBrush(QBrush(QColor(20, 20, 30)))
            painter.drawEllipse(25, 34, 6, 6)
            painter.drawEllipse(51, 34, 6, 6)
        elif self._state in (ALERT, ERROR):
            # Wide open
            painter.drawEllipse(20, 28, 14, 14)
            painter.drawEllipse(46, 28, 14, 14)
            painter.setBrush(QBrush(QColor(20, 20, 30)))
            painter.drawEllipse(24, 32, 6, 6)
            painter.drawEllipse(50, 32, 6, 6)
        elif self._state == CONCERNED:
            # Downturned — angled ellipses approximated
            painter.drawEllipse(22, 32, 10, 8)
            painter.drawEllipse(48, 32, 10, 8)
        elif self._state == THINKING:
            # Spinning — just dots
            painter.drawEllipse(23, 34, 8, 8)
            painter.drawEllipse(49, 34, 8, 8)

    def _draw_spinner(self, painter: QPainter, color: QColor):
        pen = QPen(color, 2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.save()
        painter.translate(40, 56)
        painter.rotate(self._spin_angle)
        painter.drawArc(-8, -8, 16, 16, 0, 240 * 16)
        painter.restore()

    def _draw_mouth_pulse(self, painter: QPainter, color: QColor):
        alpha = int(100 + 155 * self._pulse)
        c = QColor(color)
        c.setAlpha(alpha)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(c))
        w = int(6 + 8 * self._pulse)
        painter.drawEllipse(40 - w // 2, 53, w, 5)

    def _draw_away(self, painter: QPainter):
        alpha = int(80 + 40 * self._pulse)
        c = QColor(100, 100, 120, alpha)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(c))
        painter.drawEllipse(34, 34, 12, 12)

    # --- Dragging ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            if self._on_click:
                self._on_click()
