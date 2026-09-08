import threading

from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget,
)

from core import config_loader


class _Signals(QObject):
    message_received = pyqtSignal(str, str)  # (role, text)


class ChatWindow(QWidget):
    def __init__(self, on_send=None):
        super().__init__()
        self._on_send = on_send
        self._signals = _Signals()
        self._signals.message_received.connect(self._append_bubble)
        self._drag_pos = None

        cfg = config_loader.load()
        self._agent_name = cfg["agent"]["name"]
        pos = cfg["ui"]["chat_position"]

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(360, 500)
        self.move(pos["x"], pos["y"])

        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Main card
        card = QFrame(self)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(22, 22, 32, 230);
                border-radius: 14px;
                border: 1px solid rgba(80, 120, 255, 120);
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(44)
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 60, 200);
                border-radius: 14px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(14, 0, 10, 0)

        name_label = QLabel(self._agent_name)
        name_label.setStyleSheet("color: rgba(120, 170, 255, 255); font-size: 13px; font-weight: bold; background: transparent; border: none;")
        h_layout.addWidget(name_label)
        h_layout.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,80,80,160);
                color: white;
                border-radius: 12px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover { background: rgba(255,80,80,220); }
        """)
        close_btn.clicked.connect(self.hide)
        h_layout.addWidget(close_btn)
        card_layout.addWidget(header)

        # Messages scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self._messages_container = QWidget()
        self._messages_container.setStyleSheet("background: transparent;")
        self._messages_layout = QVBoxLayout(self._messages_container)
        self._messages_layout.setContentsMargins(10, 10, 10, 10)
        self._messages_layout.setSpacing(8)
        self._messages_layout.addStretch()

        scroll.setWidget(self._messages_container)
        self._scroll = scroll
        card_layout.addWidget(scroll)

        # Input row
        input_frame = QFrame()
        input_frame.setFixedHeight(52)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 45, 200);
                border-radius: 14px;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }
        """)
        i_layout = QHBoxLayout(input_frame)
        i_layout.setContentsMargins(10, 8, 10, 8)
        i_layout.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask Hermes anything...")
        self._input.setStyleSheet("""
            QLineEdit {
                background: rgba(50, 50, 70, 200);
                color: #e0e0f0;
                border-radius: 8px;
                border: 1px solid rgba(100,120,255,80);
                padding: 6px 10px;
                font-size: 12px;
            }
        """)
        self._input.returnPressed.connect(self._send)
        i_layout.addWidget(self._input)

        send_btn = QPushButton("→")
        send_btn.setFixedSize(34, 34)
        send_btn.setStyleSheet("""
            QPushButton {
                background: rgba(80,140,255,200);
                color: white;
                border-radius: 17px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover { background: rgba(80,140,255,255); }
        """)
        send_btn.clicked.connect(self._send)
        i_layout.addWidget(send_btn)

        card_layout.addWidget(input_frame)
        outer.addWidget(card)

    def _send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self.append_message("user", text)
        if self._on_send:
            threading.Thread(target=self._on_send, args=(text,), daemon=True).start()

    def append_message(self, role: str, text: str):
        self._signals.message_received.emit(role, text)

    def _append_bubble(self, role: str, text: str):
        is_user = role == "user"

        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(260)
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        if is_user:
            bubble.setStyleSheet("""
                QLabel {
                    background: rgba(80,140,255,180);
                    color: white;
                    border-radius: 10px;
                    padding: 8px 12px;
                    font-size: 12px;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QLabel {
                    background: rgba(50,50,70,220);
                    color: #d0d8ff;
                    border-radius: 10px;
                    padding: 8px 12px;
                    font-size: 12px;
                    border: 1px solid rgba(100,120,255,60);
                }
            """)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        if is_user:
            row.addStretch()
            row.addWidget(bubble)
        else:
            row.addWidget(bubble)
            row.addStretch()

        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent;")
        row_widget.setLayout(row)

        self._messages_layout.insertWidget(self._messages_layout.count() - 1, row_widget)
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )

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
