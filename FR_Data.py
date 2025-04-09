from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox,
    QTimeEdit, QMessageBox, QHBoxLayout, QScrollArea
)
from PyQt6.QtCore import QTime, QTimer, Qt, QDateTime, QDate
from PyQt6.QtGui import QFont

UNIT_HORNOS = {
    "E2X": ["HB-1", "HB-2", "HB-3", "HB-4"],
    "MPU": ["VPD"]
}

class DataEntryScreen(QWidget):
    def __init__(self, add_job_callback, get_jobs_callback, unit):
        super().__init__()
        self.add_job_callback = add_job_callback
        self.get_jobs_callback = get_jobs_callback
        self.unit = unit

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(40, 20, 40, 20)

        title = QLabel(f"Jobs Input - {self.unit}")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #112D4E;")
        layout.addWidget(title)

        self.dropdown = QComboBox()
        self.dropdown.addItems(UNIT_HORNOS.get(self.unit, []))

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

        version_label = QLabel("Version 1.0.5")
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
        salida = self.time_input.time()

        if not job:
            QMessageBox.warning(self, "Error", "Invalid Job")
            return

        now = QDateTime.currentDateTime()
        salida_dt = QDateTime(QDate.currentDate(), salida)
        if salida_dt > now:
            salida_dt = salida_dt.addDays(-1)

        if salida_dt.secsTo(now) > 12 * 3600:
            QMessageBox.warning(self, "Error", "More than 12 hours have passed since this exit time.")
            return

        self.add_job_callback(horno, job, salida)
        self.job_input.clear()
        self.time_input.setTime(QTime.currentTime())
        self.refresh_jobs_display()

    def stop_job_direct(self, horno, job):
        self.add_job_callback(horno, job, None, finish=True)
        self.refresh_jobs_display()

    def pause_job_direct(self, horno, job):
        self.add_job_callback(horno, job, None, pause=True)
        QTimer.singleShot(200, self.refresh_jobs_display)
