# FR_Timer.py
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QDateTime, QDate, QTime
from PyQt6.QtGui import QPixmap
from pathlib import Path

base_path = Path(__file__).parent

class TimerDisplayScreen(QWidget):
    def __init__(self, unit):
        super().__init__()
        self.unit = unit
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

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
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color:#112D4E;")

        logo_right = QLabel()
        logo_right.setPixmap(
            QPixmap(str(base_path / "VTC.png")).scaled(
                200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        )
        logo_right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header_layout.addWidget(logo_left, 0, 0)
        header_layout.addWidget(title, 0, 1)
        header_layout.addWidget(logo_right, 0, 2)
        header_container.setLayout(header_layout)
        self.layout.addWidget(header_container)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("font-size: 16px; background-color: transparent; color: #112D4E;")
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        self.layout.addLayout(close_layout)

        self.jobs_layout = QVBoxLayout()
        self.jobs_layout.setContentsMargins(50, 20, 50, 20)
        self.layout.addLayout(self.jobs_layout)
        self.layout.addStretch()

        self.jobs = {}
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timers)
        self.timer.start(1000)

    def set_data_screen(self, screen):
        self.data_screen = screen

    def add_or_update_job(self, horno, job, salida, finish=False, exposure_override=None):
        job = job.strip().upper()
        key = (horno, job)

        if finish:
            if key in self.jobs:
                widget = self.jobs[key]["widget"]
                self.jobs_layout.removeWidget(widget)
                widget.deleteLater()
                del self.jobs[key]
                return

        now = QDateTime.currentDateTime()
        salida_dt = QDateTime(QDate.currentDate(), salida)
        if salida_dt > now:
            salida_dt = salida_dt.addDays(-1)

        diff_secs = salida_dt.secsTo(now)
        exposure_seconds = (exposure_override or 12) * 3600
        remaining_secs = exposure_seconds - diff_secs

        if remaining_secs <= 0:
            remaining_secs = 0

        end_time = now.addSecs(remaining_secs)

        job_row = QWidget()
        row_layout = QHBoxLayout()
        job_row.setLayout(row_layout)

        timer_label = QLabel()
        timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row_layout.addWidget(timer_label)
        self.jobs_layout.addWidget(job_row)

        self.jobs[key] = {
            "end_time": end_time,
            "widget": job_row,
            "label": timer_label,
            "paused": False,
            "paused_at": None,
            "exposure": exposure_seconds
        }
        self.update_timers()

    def toggle_pause(self, horno, job):
        key = (horno, job)
        if key not in self.jobs:
            return
        data = self.jobs[key]
        if data["paused"]:
            paused_time = data["paused_at"].secsTo(QDateTime.currentDateTime())
            data["end_time"] = data["end_time"].addSecs(paused_time)
            data["paused"] = False
            data["paused_at"] = None
        else:
            data["paused"] = True
            data["paused_at"] = QDateTime.currentDateTime()

    def update_timers(self):
        now = QDateTime.currentDateTime()
        num_jobs = len(self.jobs)
        font_sizes = {
            1: 210,
            2: 180,
            3: 120,
            4: 96,
            5: 77,
            6: 64,
            7: 55,
            8: 48
        }
        font_size = font_sizes.get(num_jobs, 48)

        for (horno, job), data in list(self.jobs.items()):
            label = data["label"]
            if data["paused"]:
                label.setText(f"{job} - Paused")
                label.setStyleSheet(f"background-color: gray; color: white; font-size: {font_size}px;")
                continue

            remaining = now.secsTo(data["end_time"])
            exposure = data["exposure"]

            if remaining <= 0:
                over = -remaining
                hrs, rem = divmod(over, 3600)
                mins, secs = divmod(rem, 60)
                label.setText(f"{job} - Time exceeded by: {hrs:02}:{mins:02}:{secs:02}")
                label.setStyleSheet(f"background-color: #8B0000; color: white; font-size: {font_size}px;")
            else:
                hrs, rem = divmod(remaining, 3600)
                mins, secs = divmod(rem, 60)
                percent = remaining / exposure
                color = ""
                if percent <= 1/6:
                    color = "red"
                elif percent <= 0.5:
                    color = "yellow"
                label.setText(f"{job} - {hrs:02}:{mins:02}:{secs:02}")
                label.setStyleSheet(f"background-color: {color}; color: #112D4E; font-size: {font_size}px;" if color else f"color: #112D4E; font-size: {font_size}px;")
