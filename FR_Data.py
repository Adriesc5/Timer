# FR_Data.py
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QTimeEdit,
    QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import QTime, QTimer, Qt, QDateTime, QDate
from PyQt6.QtGui import QFont

HORNO_LIST = ["HB-1", "HB-2", "HB-3", "HB-4"]

class DataEntryScreen(QWidget):
    def __init__(self, add_job_callback, get_jobs_callback):
        super().__init__()
        self.add_job_callback = add_job_callback
        self.get_jobs_callback = get_jobs_callback
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(40, 20, 40, 20)

        # Title
        title = QLabel("Jobs Input")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #112D4E;")
        layout.addWidget(title)

        # Inputs
        self.dropdown = QComboBox()
        self.dropdown.addItems(HORNO_LIST)
        self.dropdown.setStyleSheet("font-size: 16px;")

        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText("Job #")
        self.job_input.returnPressed.connect(self.start_job)
        self.job_input.setStyleSheet("font-size: 16px;")

        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setStyleSheet("font-size: 16px;")
        self.time_input.setMinimumTime(QTime(0, 0))

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_label.setStyleSheet("font-size: 16px; color: #3F3F3F;")
        layout.addWidget(self.clock_label)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("background-color: #3F72AF; color: white; font-size: 16px;")
        self.start_btn.clicked.connect(self.start_job)

        layout.addWidget(QLabel("Oven:"))
        layout.addWidget(self.dropdown)
        layout.addWidget(QLabel("Job:"))
        layout.addWidget(self.job_input)
        layout.addWidget(QLabel("Oven Exit Time:"))
        layout.addWidget(self.time_input)

        button_row = QHBoxLayout()
        button_row.addWidget(self.start_btn)
        layout.addLayout(button_row)

        layout.addWidget(QLabel("Active Jobs:"))
        from PyQt6.QtWidgets import QScrollArea
        self.jobs_list_container = QWidget()
        self.jobs_list = QVBoxLayout()
        self.jobs_list_container.setLayout(self.jobs_list)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.jobs_list_container)
        scroll.setFixedHeight(240)
        layout.addWidget(scroll)

        self.setLayout(layout)
        self.refresh_jobs_display()

        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.refresh_jobs_display)
        self.sync_timer.start(2000)

    def update_clock(self):
        now = QDateTime.currentDateTime()
        self.clock_label.setText(f"Time: {now.toString('HH:mm:ss')}")

        salida = self.time_input.time()
        salida_dt = QDateTime(QDate.currentDate(), salida)
        if salida_dt > now:
            self.clock_label.setStyleSheet("font-size: 16px; color: red;")
        else:
            self.clock_label.setStyleSheet("font-size: 16px; color: #3F3F3F;")

    def refresh_jobs_display(self):
        while self.jobs_list.count():
            item = self.jobs_list.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        jobs = list(self.get_jobs_callback())
        jobs.sort()  # oldest first based on key order
        for (horno, job) in jobs:
            row = QHBoxLayout()
            label = QLabel(f"{horno} - {job}")
            label.setStyleSheet("font-size: 16px;")

            stop_btn = QPushButton("Stop")
            stop_btn.setStyleSheet("background-color: darkred; color: white; font-size: 14px;")
            stop_btn.clicked.connect(lambda _, h=horno, j=job: self.stop_job_direct(h, j))
            row.addWidget(label)
            row.addStretch()
            row.addWidget(stop_btn)
            container = QWidget()
            container.setLayout(row)
            self.jobs_list.addWidget(container)

    def start_job(self):
        horno = self.dropdown.currentText()
        job = self.job_input.text().strip().upper()
        salida = self.time_input.time()

        if not job:
            QMessageBox.warning(self, "Error", "Invalid Job")
            return

        now = QDateTime.currentDateTime()
        salida_dt = QDateTime(QDate.currentDate(), salida)

        # Si la salida es mayor que ahora, asumimos que fue ayer
        if salida_dt > now:
            salida_dt = salida_dt.addDays(-1)

        # Validar que no se excedan las 12 horas desde la hora de salida
        elapsed_secs = salida_dt.secsTo(now)
        if elapsed_secs > 12 * 3600:
            QMessageBox.warning(self, "Error", "The exit time exceeds the 12-hour job limit.")
            return


        current_jobs = self.get_jobs_callback()

        if (horno, job) in current_jobs:
            QMessageBox.warning(self, "Duplicate", f"Job '{job}' is already registered in {horno}.")
            return

        count = sum(1 for (h, _) in current_jobs if h == horno)
        if count >= 2:
            QMessageBox.warning(self, "Limit Reached", f"Only 2 jobs are allowed per oven: {horno}")
            return

        self.add_job_callback(horno, job, salida)
        self.job_input.clear()
        self.time_input.setTime(QTime.currentTime())
        self.job_input.setFocus()
        self.refresh_jobs_display()

    def stop_job_direct(self, horno, job):
        self.add_job_callback(horno, job, None, finish=True)
        self.refresh_jobs_display()
