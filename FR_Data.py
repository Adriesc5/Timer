# FR_Data.py
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox,
    QTimeEdit, QMessageBox, QHBoxLayout, QScrollArea
)
from PyQt6.QtCore import QTime, QTimer, Qt, QDateTime, QDate
from PyQt6.QtGui import QFont
import re
from webhook_trigger import send_alert
from config import WEBHOOK_URL

HORNO_LIST_E2X = ["HB-1", "HB-2", "HB-3", "HB-4"]
HORNO_LIST_MPU = ["VPD"]

class DataEntryScreen(QWidget):
    def __init__(self, add_job_callback, get_jobs_callback, unit):
        super().__init__()
        self.unit = unit
        self.selected_kvbil = "<350KVBIL"
        self.add_job_callback = add_job_callback
        self.get_jobs_callback = get_jobs_callback
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(40, 20, 40, 20)

        title = QLabel("Jobs Input")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #112D4E;")
        layout.addWidget(title)

        self.dropdown = QComboBox()
        horno_list = HORNO_LIST_E2X if unit == "E2X" else HORNO_LIST_MPU
        self.dropdown.addItems(horno_list)

        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText("Job #")
        self.job_input.returnPressed.connect(self.start_job)

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setTime(QTime.currentTime())

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.clock_label)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_job)

        layout.addWidget(QLabel("Oven:"))
        layout.addWidget(self.dropdown)
        layout.addWidget(QLabel("Job:"))
        layout.addWidget(self.job_input)
        layout.addWidget(QLabel("Oven Exit Time:"))
        layout.addWidget(self.time_input)

        if self.unit == "MPU":
            btn_row = QHBoxLayout()
            self.low_btn = QPushButton("<350KVBIL")
            self.high_btn = QPushButton(">350KVBIL")

            self.low_btn.setCheckable(True)
            self.high_btn.setCheckable(True)
            self.low_btn.setChecked(True)

            self.low_btn.clicked.connect(lambda: self.select_kvbil("<350KVBIL"))
            self.high_btn.clicked.connect(lambda: self.select_kvbil(">350KVBIL"))

            btn_row.addWidget(self.low_btn)
            btn_row.addWidget(self.high_btn)
            layout.addLayout(btn_row)

        layout.addWidget(self.start_btn)

        layout.addWidget(QLabel("Active Jobs:"))
        self.jobs_list_container = QWidget()
        self.jobs_list = QVBoxLayout()
        self.jobs_list_container.setLayout(self.jobs_list)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.jobs_list_container)
        scroll.setFixedHeight(240)
        layout.addWidget(scroll)

        version_label = QLabel("Version 1.0.5.7")
        version_label.setStyleSheet("font-size: 12px; color: gray;")
        version_row = QHBoxLayout()
        version_row.addWidget(version_label)
        version_row.addStretch()
        layout.addLayout(version_row)

        self.setLayout(layout)
        self.refresh_jobs_display()

        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.refresh_jobs_display)
        self.sync_timer.start(2000)

    def select_kvbil(self, value):
        self.selected_kvbil = value
        self.low_btn.setChecked(value == "<350KVBIL")
        self.high_btn.setChecked(value == ">350KVBIL")

    def update_clock(self):
        now = QDateTime.currentDateTime()
        self.clock_label.setText(f"Time: {now.toString('HH:mm:ss')}")

    def refresh_jobs_display(self):
        while self.jobs_list.count():
            item = self.jobs_list.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        jobs = list(self.get_jobs_callback().items())
        jobs.sort()
        for (horno, job), data in jobs:
            row = QHBoxLayout()
            label = QLabel(f"{horno} - {job}")
            stop_btn = QPushButton("Stop")
            stop_btn.setStyleSheet("background-color: darkred; color: white; font-size: 14px;")
            stop_btn.clicked.connect(lambda _, h=horno, j=job: self.stop_job_direct(h, j))
            pause_btn = QPushButton("Pause" if not data.get("paused") else "Resume")
            pause_btn.setStyleSheet("background-color: #f0ad4e; color: white; font-size: 14px;")
            pause_btn.clicked.connect(lambda _, h=horno, j=job: self.pause_job_direct(h, j))

            row.addWidget(label)
            row.addStretch()
            row.addWidget(stop_btn)
            row.addWidget(pause_btn)

            container = QWidget()
            container.setLayout(row)
            self.jobs_list.addWidget(container)

    def start_job(self):
        horno = self.dropdown.currentText()
        job = self.job_input.text().strip().upper()

        if not re.match(r"^[A-Z]{2}\d{3}[A-Z]$", job):
            QMessageBox.warning(self, "Invalid Job Format", "Job format must be two letters, three digits, and one letter (e.g., AB123C).")
            return

        salida = self.time_input.time()

        if not job:
            QMessageBox.warning(self, "Error", "Invalid Job")
            return

        now = QDateTime.currentDateTime()
        salida_dt = QDateTime(QDate.currentDate(), salida)
        if salida_dt > now:
            salida_dt = salida_dt.addDays(-1)

        if salida_dt.secsTo(now) > 18 * 3600:
            QMessageBox.warning(self, "Error", "More than 18 hours have passed since this exit time.")
            return

        exposure_hours = 12
        if self.unit == "MPU":
            exposure_hours = 12 if self.selected_kvbil == "<350KVBIL" else 18

        self.add_job_callback(horno, job, salida, exposure_hours=exposure_hours)
        self.job_input.clear()
        self.time_input.setTime(QTime.currentTime())
        self.refresh_jobs_display()

    def stop_job_direct(self, horno, job):
        jobs = self.get_jobs_callback()
        data = jobs.get((horno, job))
        if data:
            start_time = data["end_time"].addSecs(-data["exposure"])
            remaining = QDateTime.currentDateTime().secsTo(data["end_time"])
            actual_time = QDateTime.currentDateTime().toPyDateTime()
            start_time = data["end_time"].addSecs(-data["exposure"]).toPyDateTime()
            exposure_seconds = (actual_time - start_time).total_seconds()
            exposure_hours = round(exposure_seconds / 3600, 2)

            send_alert(
                horno, job, start_time, exposure_seconds, WEBHOOK_URL,
                tipo="registro", unidad=self.unit, actual=actual_time,
                horas_expuestas=exposure_hours
            )
        self.add_job_callback(horno, job, None, finish=True)
        self.refresh_jobs_display()

    def pause_job_direct(self, horno, job): 
        self.add_job_callback(horno, job, None, pause=True)
        QTimer.singleShot(200, self.refresh_jobs_display())
