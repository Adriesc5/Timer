# FR_Data.py
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QTimeEdit,
    QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import QTime, QTimer

HORNO_LIST = ["HB-1", "HB-2", "HB-3", "HB-4"]

class DataEntryScreen(QWidget):
    def __init__(self, add_job_callback, get_jobs_callback):
        super().__init__()
        self.add_job_callback = add_job_callback
        self.get_jobs_callback = get_jobs_callback
        layout = QVBoxLayout()

        self.dropdown = QComboBox()
        self.dropdown.addItems(HORNO_LIST)
        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText("Número de job")
        self.job_input.returnPressed.connect(self.start_job)

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_job)

        layout.addWidget(QLabel("Horno:"))
        layout.addWidget(self.dropdown)
        layout.addWidget(QLabel("Job:"))
        layout.addWidget(self.job_input)
        layout.addWidget(QLabel("Hora salida horno:"))
        layout.addWidget(self.time_input)

        button_row = QHBoxLayout()
        button_row.addWidget(self.start_btn)
        layout.addLayout(button_row)

        layout.addWidget(QLabel("Trabajos activos:"))
        self.jobs_list = QVBoxLayout()
        layout.addLayout(self.jobs_list)

        self.setLayout(layout)
        self.refresh_jobs_display()

        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.refresh_jobs_display)
        self.sync_timer.start(2000)

    def refresh_jobs_display(self):
        while self.jobs_list.count():
            item = self.jobs_list.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        jobs = self.get_jobs_callback()
        for (horno, job) in jobs:
            row = QHBoxLayout()
            label = QLabel(f"{horno} - {job}")
            stop_btn = QPushButton("Stop")
            stop_btn.setStyleSheet("background-color: darkred; color: white;")
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
            QMessageBox.warning(self, "Error", "Job inválido")
            return

        current_jobs = self.get_jobs_callback()

        # Validación duplicado exacto (horno, job)
        if (horno, job) in current_jobs:
            QMessageBox.warning(self, "Duplicado", f"El trabajo '{job}' ya está registrado en {horno}.")
            return

        # Validación límite por horno
        count = sum(1 for (h, _) in current_jobs if h == horno)
        if count >= 2:
            QMessageBox.warning(self, "Límite alcanzado", f"Solo se permiten 2 trabajos por horno: {horno}")
            return

        self.add_job_callback(horno, job, salida)
        self.job_input.clear()
        self.time_input.setTime(QTime(0, 0))
        self.refresh_jobs_display()

    def stop_job_direct(self, horno, job):
        self.add_job_callback(horno, job, None, finish=True)
        self.refresh_jobs_display()
