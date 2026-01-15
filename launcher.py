#!/usr/bin/env python3
"""
A.B.E.L - J.A.R.V.I.S. Style Launcher
Interface FUI/Sci-Fi avec effets holographiques
"""

import subprocess
import sys
import os
import webbrowser
import math
import random
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFrame, QGraphicsDropShadowEffect,
    QProgressBar, QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QPropertyAnimation,
    QEasingCurve, QSize, QRect, QPoint, Property
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QPainter, QPen, QBrush,
    QLinearGradient, QRadialGradient, QFontDatabase
)


# === J.A.R.V.I.S. DESIGN SYSTEM ===
COLORS = {
    "bg_deep": "#020617",
    "bg_panel": "rgba(2, 6, 23, 0.85)",
    "cyan": "#00f3ff",
    "cyan_dim": "rgba(0, 243, 255, 0.3)",
    "cyan_glow": "rgba(0, 243, 255, 0.15)",
    "white": "#ffffff",
    "text_dim": "rgba(0, 243, 255, 0.6)",
    "success": "#00ff88",
    "error": "#ff3333",
    "warning": "#ffaa00",
    "border": "rgba(0, 243, 255, 0.4)",
}


STYLESHEET = """
QMainWindow {
    background-color: #020617;
}
QWidget {
    background-color: transparent;
    color: #00f3ff;
    font-family: 'Consolas', 'Courier New', monospace;
    text-transform: uppercase;
}
QPushButton {
    background-color: rgba(0, 243, 255, 0.1);
    border: 1px solid rgba(0, 243, 255, 0.4);
    color: #00f3ff;
    padding: 14px 28px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 3px;
    text-transform: uppercase;
}
QPushButton:hover {
    background-color: rgba(0, 243, 255, 0.25);
    border-color: #00f3ff;
}
QPushButton:pressed {
    background-color: rgba(0, 243, 255, 0.4);
}
QPushButton:disabled {
    background-color: rgba(0, 243, 255, 0.05);
    color: rgba(0, 243, 255, 0.3);
    border-color: rgba(0, 243, 255, 0.15);
}
QPushButton#primary {
    background-color: rgba(0, 243, 255, 0.2);
    border: 2px solid #00f3ff;
}
QPushButton#primary:hover {
    background-color: rgba(0, 243, 255, 0.35);
}
QPushButton#danger {
    background-color: rgba(255, 51, 51, 0.15);
    border-color: rgba(255, 51, 51, 0.5);
    color: #ff3333;
}
QPushButton#danger:hover {
    background-color: rgba(255, 51, 51, 0.3);
    border-color: #ff3333;
}
QTextEdit {
    background-color: rgba(0, 243, 255, 0.03);
    border: 1px solid rgba(0, 243, 255, 0.2);
    padding: 12px;
    font-family: 'Consolas', monospace;
    font-size: 10px;
    color: rgba(0, 243, 255, 0.7);
    letter-spacing: 1px;
}
QProgressBar {
    background-color: rgba(0, 243, 255, 0.1);
    border: 1px solid rgba(0, 243, 255, 0.3);
    height: 3px;
}
QProgressBar::chunk {
    background-color: #00f3ff;
}
QScrollBar:vertical {
    background-color: rgba(0, 243, 255, 0.05);
    width: 6px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: rgba(0, 243, 255, 0.3);
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


class DockerWorker(QThread):
    """Worker thread pour les commandes Docker."""
    output = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, command: list, cwd: str):
        super().__init__()
        self.command = command
        self.cwd = cwd

    def run(self):
        try:
            kwargs = {
                "cwd": self.cwd,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "text": True,
                "bufsize": 1
            }
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(self.command, **kwargs)

            for line in iter(process.stdout.readline, ''):
                if line:
                    self.output.emit(line.strip())

            process.wait()
            success = process.returncode == 0
            self.finished_signal.emit(success, "" if success else "COMMAND FAILED")

        except FileNotFoundError:
            self.finished_signal.emit(False, "DOCKER NOT FOUND - INSTALL DOCKER DESKTOP")
        except Exception as e:
            self.finished_signal.emit(False, str(e).upper())


class ArcReactorWidget(QWidget):
    """Widget cercle concentrique rotatif style Arc Reactor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        self._angle = 0
        self._angle2 = 0
        self._pulse = 1.0
        self._pulse_dir = -1

        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        self.timer.start(30)

    def _animate(self):
        self._angle = (self._angle + 0.8) % 360
        self._angle2 = (self._angle2 - 0.5) % 360
        self._pulse += self._pulse_dir * 0.02
        if self._pulse <= 0.6:
            self._pulse_dir = 1
        elif self._pulse >= 1.0:
            self._pulse_dir = -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # Outer glow
        glow = QRadialGradient(cx, cy, 90)
        glow.setColorAt(0, QColor(0, 243, 255, int(30 * self._pulse)))
        glow.setColorAt(1, QColor(0, 243, 255, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - 90), int(cy - 90), 180, 180)

        # Ring 3 (outer) - dashed, rotating
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._angle)
        pen = QPen(QColor(0, 243, 255, int(80 * self._pulse)))
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(-70, -70, 140, 140)
        painter.restore()

        # Ring 2 (middle) - solid, counter-rotating
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._angle2)
        pen = QPen(QColor(0, 243, 255, int(150 * self._pulse)))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(-50, -50, 100, 100)

        # Tick marks
        for i in range(12):
            painter.rotate(30)
            painter.drawLine(45, 0, 50, 0)
        painter.restore()

        # Ring 1 (inner) - thick, rotating
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._angle * 1.5)
        pen = QPen(QColor(0, 243, 255, int(200 * self._pulse)))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawArc(-30, -30, 60, 60, 0, 270 * 16)
        painter.restore()

        # Center core
        core = QRadialGradient(cx, cy, 20)
        core.setColorAt(0, QColor(255, 255, 255, int(255 * self._pulse)))
        core.setColorAt(0.5, QColor(0, 243, 255, int(200 * self._pulse)))
        core.setColorAt(1, QColor(0, 243, 255, 0))
        painter.setBrush(core)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - 15), int(cy - 15), 30, 30)


class HUDPanel(QFrame):
    """Panel style HUD avec coins coupes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cut = 15  # Corner cut size

        # Background
        path_bg = []
        path_bg.append((cut, 0))
        path_bg.append((w - cut, 0))
        path_bg.append((w, cut))
        path_bg.append((w, h - cut))
        path_bg.append((w - cut, h))
        path_bg.append((cut, h))
        path_bg.append((0, h - cut))
        path_bg.append((0, cut))

        from PySide6.QtGui import QPolygon
        polygon = QPolygon([QPoint(int(x), int(y)) for x, y in path_bg])

        painter.setBrush(QColor(2, 6, 23, 220))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(polygon)

        # Border
        pen = QPen(QColor(0, 243, 255, 100))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(polygon)

        # Corner accents
        pen.setColor(QColor(0, 243, 255, 200))
        pen.setWidth(2)
        painter.setPen(pen)

        # Top-left corner accent
        painter.drawLine(0, cut + 20, 0, cut)
        painter.drawLine(0, cut, cut, 0)
        painter.drawLine(cut, 0, cut + 20, 0)

        # Bottom-right corner accent
        painter.drawLine(w, h - cut - 20, w, h - cut)
        painter.drawLine(w, h - cut, w - cut, h)
        painter.drawLine(w - cut, h, w - cut - 20, h)


class StatusIndicator(QWidget):
    """Indicateur de statut avec pulse."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self._color = QColor(COLORS['error'])
        self._pulse_opacity = 1.0
        self._pulse_dir = -1

        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._timer.start(50)
        self._active = False

    def set_status(self, status: str):
        if status == "running":
            self._color = QColor(COLORS['success'])
            self._active = True
        elif status == "starting":
            self._color = QColor(COLORS['warning'])
            self._active = True
        else:
            self._color = QColor(COLORS['error'])
            self._active = False
            self._pulse_opacity = 1.0
        self.update()

    def _animate(self):
        if self._active:
            self._pulse_opacity += self._pulse_dir * 0.06
            if self._pulse_opacity <= 0.3:
                self._pulse_dir = 1
            elif self._pulse_opacity >= 1.0:
                self._pulse_dir = -1
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Outer glow
        glow = QRadialGradient(7, 7, 10)
        glow_color = QColor(self._color)
        glow_color.setAlphaF(0.3 * self._pulse_opacity)
        glow.setColorAt(0, glow_color)
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(-3, -3, 20, 20)

        # Main dot
        color = QColor(self._color)
        color.setAlphaF(self._pulse_opacity)
        painter.setBrush(color)
        painter.drawEllipse(2, 2, 10, 10)


class TechLabel(QLabel):
    """Label avec effet de texte technique."""

    def __init__(self, text, parent=None, glow=True):
        super().__init__(text.upper(), parent)
        self.setStyleSheet(f"""
            color: #00f3ff;
            font-family: 'Consolas', monospace;
            letter-spacing: 2px;
        """)

        if glow:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(15)
            effect.setColor(QColor(0, 243, 255, 180))
            effect.setOffset(0, 0)
            self.setGraphicsEffect(effect)


class LinkCard(QFrame):
    """Carte cliquable style HUD."""

    clicked = Signal()

    def __init__(self, title: str, url: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(36)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 243, 255, 0.05);
                border: 1px solid rgba(0, 243, 255, 0.2);
            }
            QFrame:hover {
                background-color: rgba(0, 243, 255, 0.15);
                border-color: rgba(0, 243, 255, 0.5);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)

        label = QLabel(f"[ {title.upper()} ]")
        label.setStyleSheet("color: #00f3ff; font-size: 10px; letter-spacing: 2px; border: none; background: transparent;")
        layout.addWidget(label)
        layout.addStretch()

        arrow = QLabel(">")
        arrow.setStyleSheet("color: #00f3ff; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(arrow)

    def mousePressEvent(self, event):
        webbrowser.open(self.url)
        self.clicked.emit()


class MicroText(QLabel):
    """Micro texte decoratif qui defile."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            color: rgba(0, 243, 255, 0.4);
            font-family: 'Consolas', monospace;
            font-size: 8px;
            letter-spacing: 1px;
        """)
        self._update_text()

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_text)
        self.timer.start(100)

    def _update_text(self):
        coords = f"{random.uniform(-90, 90):.4f}N {random.uniform(-180, 180):.4f}E"
        seq = f"V.{random.randint(0, 99):02d}.{random.randint(0, 99):02d}"
        hex_val = f"0x{random.randint(0, 65535):04X}"
        self.setText(f"{coords}  //  {seq}  //  {hex_val}")


class AbelLauncher(QMainWindow):
    """Fenetre principale - J.A.R.V.I.S. Interface."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("A.B.E.L // SYSTEM INTERFACE")
        self.setFixedSize(600, 700)
        self.setStyleSheet(STYLESHEET)

        self.is_running = False
        self.worker = None
        self.project_dir = Path(__file__).parent.absolute()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Background gradient
        central.setStyleSheet("""
            background: qradialgradient(
                cx: 0.5, cy: 0.3, radius: 1,
                fx: 0.5, fy: 0.3,
                stop: 0 #0a1628,
                stop: 1 #020617
            );
        """)

        layout = QVBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(30, 20, 30, 20)

        self._create_header(layout)
        self._create_main_panel(layout)
        self._create_footer(layout)
        self._center_window()

        QTimer.singleShot(500, self._check_status)

    def _create_header(self, layout):
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(5)

        # Top decorative line
        line_widget = QWidget()
        line_widget.setFixedHeight(1)
        line_widget.setStyleSheet("background-color: rgba(0, 243, 255, 0.3);")
        header_layout.addWidget(line_widget)

        # System time
        time_layout = QHBoxLayout()
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            color: rgba(0, 243, 255, 0.5);
            font-size: 9px;
            letter-spacing: 3px;
        """)
        self._update_time()
        time_layout.addWidget(self.time_label)
        time_layout.addStretch()

        sys_label = QLabel("SYSTEM ONLINE")
        sys_label.setStyleSheet("""
            color: rgba(0, 243, 255, 0.5);
            font-size: 9px;
            letter-spacing: 3px;
        """)
        time_layout.addWidget(sys_label)
        header_layout.addLayout(time_layout)

        # Timer for time update
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_time)
        self.time_timer.start(1000)

        layout.addWidget(header)

    def _update_time(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%Y.%m.%d // %H:%M:%S"))

    def _create_main_panel(self, layout):
        # Main container
        main_panel = HUDPanel()
        main_layout = QVBoxLayout(main_panel)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Arc reactor + title section
        top_section = QHBoxLayout()

        # Arc reactor
        self.arc_reactor = ArcReactorWidget()
        top_section.addWidget(self.arc_reactor)

        top_section.addSpacing(20)

        # Title section
        title_section = QVBoxLayout()
        title_section.setSpacing(8)

        title = TechLabel("A.B.E.L")
        title.setStyleSheet("""
            color: #00f3ff;
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 8px;
        """)
        title_section.addWidget(title)

        subtitle = QLabel("AUTONOMOUS BACKEND ENTITY FOR LIVING")
        subtitle.setStyleSheet("""
            color: rgba(0, 243, 255, 0.6);
            font-size: 10px;
            letter-spacing: 3px;
        """)
        title_section.addWidget(subtitle)

        version = QLabel("[ VERSION 2.0.0 // BUILD 2024.12 ]")
        version.setStyleSheet("""
            color: rgba(0, 243, 255, 0.4);
            font-size: 9px;
            letter-spacing: 2px;
        """)
        title_section.addWidget(version)

        title_section.addStretch()
        top_section.addLayout(title_section)
        top_section.addStretch()

        main_layout.addLayout(top_section)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: rgba(0, 243, 255, 0.2);")
        main_layout.addWidget(sep)

        # Status section
        status_section = QHBoxLayout()

        self.status_indicator = StatusIndicator()
        status_section.addWidget(self.status_indicator)
        status_section.addSpacing(10)

        self.status_label = QLabel("SYSTEM OFFLINE")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['error']};
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 3px;
        """)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(10)
        glow.setColor(QColor(COLORS['error']))
        glow.setOffset(0, 0)
        self.status_label.setGraphicsEffect(glow)

        status_section.addWidget(self.status_label)
        status_section.addStretch()

        self.progress = QProgressBar()
        self.progress.setFixedWidth(120)
        self.progress.setRange(0, 0)
        self.progress.hide()
        status_section.addWidget(self.progress)

        main_layout.addLayout(status_section)

        # Micro text decoration
        self.micro_text = MicroText()
        main_layout.addWidget(self.micro_text)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.start_btn = QPushButton("INITIALIZE")
        self.start_btn.setObjectName("primary")
        self.start_btn.setFixedHeight(50)
        self.start_btn.clicked.connect(self._start_abel)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("SHUTDOWN")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.setFixedHeight(50)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_abel)
        btn_layout.addWidget(self.stop_btn)

        main_layout.addLayout(btn_layout)

        # Links section
        links_label = QLabel("// QUICK ACCESS")
        links_label.setStyleSheet("color: rgba(0, 243, 255, 0.4); font-size: 9px; letter-spacing: 2px;")
        main_layout.addWidget(links_label)

        links_layout = QHBoxLayout()
        links_layout.setSpacing(10)

        links_layout.addWidget(LinkCard("API DOCS", "http://localhost:8000/docs"))
        links_layout.addWidget(LinkCard("DASHBOARD", "http://localhost:3000"))
        links_layout.addWidget(LinkCard("QDRANT", "http://localhost:6333/dashboard"))

        main_layout.addLayout(links_layout)

        # Log section
        log_label = QLabel("// SYSTEM LOG")
        log_label.setStyleSheet("color: rgba(0, 243, 255, 0.4); font-size: 9px; letter-spacing: 2px;")
        main_layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        main_layout.addWidget(self.log_text)

        layout.addWidget(main_panel, 1)

    def _create_footer(self, layout):
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 10, 0, 0)

        left = QLabel("STARK INDUSTRIES // R&D DIVISION")
        left.setStyleSheet("color: rgba(0, 243, 255, 0.3); font-size: 8px; letter-spacing: 2px;")
        footer_layout.addWidget(left)

        footer_layout.addStretch()

        right = QLabel("CLASSIFIED // LEVEL 7 ACCESS")
        right.setStyleSheet("color: rgba(0, 243, 255, 0.3); font-size: 8px; letter-spacing: 2px;")
        footer_layout.addWidget(right)

        layout.addWidget(footer)

    def _center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _log(self, message: str, level: str = "info"):
        colors = {
            "info": "rgba(0, 243, 255, 0.7)",
            "success": COLORS['success'],
            "error": COLORS['error'],
            "warning": COLORS['warning']
        }
        color = colors.get(level, "rgba(0, 243, 255, 0.7)")

        timestamp = datetime.now().strftime("%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
        self.log_text.append(
            f'<span style="color: rgba(0, 243, 255, 0.4)">[{timestamp}]</span> '
            f'<span style="color: {color}">{message.upper()}</span>'
        )
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def _update_status(self, running: bool, starting: bool = False):
        self.is_running = running

        # Update glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(10)
        glow.setOffset(0, 0)

        if starting:
            self.status_indicator.set_status("starting")
            self.status_label.setText("INITIALIZING...")
            self.status_label.setStyleSheet(f"color: {COLORS['warning']}; font-size: 12px; font-weight: bold; letter-spacing: 3px;")
            glow.setColor(QColor(COLORS['warning']))
            self.progress.show()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
        elif running:
            self.status_indicator.set_status("running")
            self.status_label.setText("SYSTEM ONLINE")
            self.status_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 12px; font-weight: bold; letter-spacing: 3px;")
            glow.setColor(QColor(COLORS['success']))
            self.progress.hide()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            self.status_indicator.set_status("stopped")
            self.status_label.setText("SYSTEM OFFLINE")
            self.status_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 12px; font-weight: bold; letter-spacing: 3px;")
            glow.setColor(QColor(COLORS['error']))
            self.progress.hide()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

        self.status_label.setGraphicsEffect(glow)

    def _check_status(self):
        try:
            kwargs = {"capture_output": True, "text": True}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            result = subprocess.run(
                ["docker-compose", "ps", "-q"],
                cwd=str(self.project_dir),
                **kwargs
            )

            running = bool(result.stdout.strip())
            self._update_status(running)

            if running:
                self._log("Docker services detected - system operational", "success")
            else:
                self._log("System ready for initialization", "info")

        except Exception:
            self._log("Docker status check failed", "warning")

    def _start_abel(self):
        self._update_status(False, starting=True)
        self._log("Initiating boot sequence...", "info")

        self.worker = DockerWorker(
            ["docker-compose", "up", "-d", "--build"],
            str(self.project_dir)
        )
        self.worker.output.connect(lambda msg: self._log(msg))
        self.worker.finished_signal.connect(self._on_start_finished)
        self.worker.start()

    def _on_start_finished(self, success: bool, error: str):
        if success:
            self._log("All systems operational - A.B.E.L. online", "success")
            self._update_status(True)
        else:
            self._log(f"Boot sequence failed: {error}", "error")
            self._update_status(False)

    def _stop_abel(self):
        self._update_status(True, starting=True)
        self._log("Initiating shutdown sequence...", "warning")

        self.worker = DockerWorker(
            ["docker-compose", "down"],
            str(self.project_dir)
        )
        self.worker.output.connect(lambda msg: self._log(msg))
        self.worker.finished_signal.connect(self._on_stop_finished)
        self.worker.start()

    def _on_stop_finished(self, success: bool, error: str):
        if success:
            self._log("Shutdown complete - entering standby", "info")
        else:
            self._log(f"Shutdown error: {error}", "error")
        self._update_status(False)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.wait()
        event.accept()


def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#020617"))
    palette.setColor(QPalette.WindowText, QColor("#00f3ff"))
    palette.setColor(QPalette.Base, QColor("#020617"))
    palette.setColor(QPalette.Text, QColor("#00f3ff"))
    app.setPalette(palette)

    window = AbelLauncher()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
