# FR_Timer.py
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QDate, QTime
from PyQt6.QtGui import QPixmap
from pathlib import Path
base_path = Path(__file__).parent

MAX_JOBS_TOTAL = 8

class TimerDisplayScreen(QWidget):
    def __init__(self, show_login_or_data_callback):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.show_login_or_data_callback = show_login_or_data_callback

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Header
        header_container = QWidget()
        header_container.setFixedHeight(120)
        header_layout = QGridLayout()
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setColumnStretch(0, 1)
        header_layout.setColumnStretch(1, 2)
        header_layout.setColumnStretch(2, 1)

        logo_left = QLabel()
        logo_left.setPixmap(
            QPixmap(str(base_path / "TMC.png")).scaled(
                200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        )
        logo_left.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        title = QLabel("EXPOSURE TIME")
        title_font = title.font()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#112D4E;")

        logo_right = QLabel()
        #logo_right.setPixmap(QPixmap(str(base_path / "VTC-GTC_logo.png")).scaledToHeight(80))
        logo_right.setPixmap(
            QPixmap(str(base_path / "VTC-GTC_logo.png")).scaled(
                200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        )
        logo_right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header_layout.addWidget(logo_left, 0, 0)
        header_layout.addWidget(title, 0, 1)
        header_layout.addWidget(logo_right, 0, 2)
        header_container.setLayout(header_layout)
        self.layout.addWidget(header_container)

        # Botón cerrar
        close_btn_layout = QHBoxLayout()
        close_btn_layout.setContentsMargins(0, 0, 10, 0)
        close_btn = QPushButton("\u2715")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("font-size: 16px; background-color: transparent; color: #112D4E;")
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn_layout.addStretch()
        close_btn_layout.addWidget(close_btn)
        self.layout.addLayout(close_btn_layout)

        # Layout de jobs
        self.jobs_layout = QVBoxLayout()
        self.jobs_layout.setContentsMargins(50, 20, 50, 20)
        self.layout.addLayout(self.jobs_layout)

        self.layout.addStretch()

        self.jobs = {}  # {(horno, job): (end_time, widget, label)}
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timers)
        self.timer.start(1000)

    def add_or_update_job(self, horno, job, salida, finish=False):
        job = job.strip().upper()
        key = (horno, job)

        if finish:
            if key in self.jobs:
                widget = self.jobs[key][1]
                self.jobs_layout.removeWidget(widget)
                widget.deleteLater()
                del self.jobs[key]
            return

        if salida is None or not isinstance(salida, QTime):
            QMessageBox.warning(self, "Error", "Invalid exit time.")
            return

        if len(self.jobs) >= MAX_JOBS_TOTAL:
            QMessageBox.warning(self, "Maximum reached", "There are already 8 jobs on screen.")
            return

        now = QDateTime.currentDateTime()
        salida_dt = QDateTime(QDate.currentDate(), salida)
        if salida_dt > now:
            salida_dt = salida_dt.addDays(-1)

        diff_secs = salida_dt.secsTo(now)
        remaining_secs = (12 * 3600) - diff_secs

        if remaining_secs <= 0:
            QMessageBox.warning(self, "Time expired", f"The job '{job}' has exceeded the 12-hour limit since its departure.")
            return

        end_time = now.addSecs(remaining_secs)

        job_row = QWidget()
        row_layout = QHBoxLayout()
        job_row.setLayout(row_layout)

        timer_label = QLabel()
        timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = timer_label.font()
        font.setPointSize(48)
        font.setBold(True)
        timer_label.setFont(font)

        row_layout.addWidget(timer_label)

        self.jobs_layout.addWidget(job_row)
        self.jobs[key] = (end_time, job_row, timer_label)
        self.update_timers()

    def update_timers(self):
        now = QDateTime.currentDateTime()
        for (horno, job), (end_time, widget, label) in list(self.jobs.items()):
            remaining = now.secsTo(end_time)
            if remaining <= 0:
                exceeded = -remaining
                hrs = exceeded // 3600
                mins = (exceeded % 3600) // 60
                secs = exceeded % 60
                label.setText(f"{job} - Time exceeded by: {hrs:02d}:{mins:02d}:{secs:02d}")
                label.setStyleSheet("background-color: #8B0000; color: white;")
                continue
            hrs = remaining // 3600
            mins = (remaining % 3600) // 60
            secs = remaining % 60
            label.setText(f"{job} - {hrs:02d}:{mins:02d}:{secs:02d}")
            if hrs < 2:
                label.setStyleSheet("background-color: red; color: white;")
            elif hrs <= 6:
                label.setStyleSheet("background-color: yellow; color: #112D4E;")
            elif hrs <= 12:
                label.setStyleSheet("color: #112D4E;")    
            else:
                label.setStyleSheet("")