from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)
from ..i18n import t
from ..services.driver_service import collect, repair
from .base import page_header

class DriverWorker(QObject):
    done = Signal(dict)
    def run(self):
        self.done.emit(collect())

class DriversPage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__()
        self.lang = lang
        self.thread = None
        self.detected_vendors = set()
        self.setObjectName("ContentPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(14)

        self.title, self.subtitle = page_header(layout, "", "")

        self.table = QTableWidget(0, 4)
        self.table.setObjectName("DataTable")
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.info = {}
        for i, key in enumerate(("nvidia_driver","dkms","hybrid","nouveau","firmware","vulkan","vaapi")):
            card = QFrame()
            card.setObjectName("Card")
            box = QVBoxLayout(card)
            box.setContentsMargins(18, 15, 18, 15)
            label = QLabel()
            label.setObjectName("CardNumber")
            value = QLabel("…")
            value.setObjectName("CardText")
            value.setWordWrap(True)
            box.addWidget(label)
            box.addWidget(value)
            self.info[key] = (label, value)
            grid.addWidget(card, i // 2, i % 2)
        layout.addLayout(grid)

        actions = QHBoxLayout()
        self.refresh_btn = QPushButton()
        self.refresh_btn.setObjectName("PrimaryButton")
        self.refresh_btn.clicked.connect(self.refresh)

        self.intel_btn = QPushButton()
        self.amd_btn = QPushButton()
        self.nvidia_btn = QPushButton()
        for b in (self.intel_btn, self.amd_btn, self.nvidia_btn):
            b.setObjectName("SecondaryButton")
            actions.addWidget(b)
        self.intel_btn.clicked.connect(lambda: self.repair_vendor("intel"))
        self.amd_btn.clicked.connect(lambda: self.repair_vendor("amd"))
        self.nvidia_btn.clicked.connect(lambda: self.repair_vendor("nvidia"))
        actions.insertWidget(0, self.refresh_btn)
        actions.addStretch()
        layout.addLayout(actions)

        self.note = QLabel()
        self.note.setObjectName("StatusLabel")
        self.note.setWordWrap(True)
        layout.addWidget(self.note)

        self.set_language(lang)
        self.refresh()

    def set_language(self, lang):
        self.lang = lang
        self.title.setText(t(lang, "drivers_title"))
        self.subtitle.setText(t(lang, "drivers_intro"))
        self.table.setHorizontalHeaderLabels([
            t(lang, "gpu_vendor"), t(lang, "gpu_model"),
            t(lang, "gpu_driver"), "Kernel modules"
        ])
        for key, (label, _) in self.info.items():
            label.setText(t(lang, key))
        self.refresh_btn.setText(t(lang, "driver_refresh"))
        self.intel_btn.setText(t(lang, "repair_intel"))
        self.amd_btn.setText(t(lang, "repair_amd"))
        self.nvidia_btn.setText(t(lang, "repair_nvidia"))
        self.note.setText(t(lang, "driver_action_note"))

    def refresh(self):
        self.refresh_btn.setEnabled(False)
        self.thread = QThread(self)
        worker = DriverWorker()
        self.worker = worker
        worker.moveToThread(self.thread)
        self.thread.started.connect(worker.run)
        worker.done.connect(self.show)
        worker.done.connect(self.thread.quit)
        worker.done.connect(worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def show(self, data):
        self.table.setRowCount(0)
        self.detected_vendors = set()

        for gpu in data.get("gpus", []):
            r = self.table.rowCount()
            self.table.insertRow(r)
            vals = (gpu["vendor"], gpu["model"], gpu["driver"], gpu["modules"])
            for c, value in enumerate(vals):
                self.table.setItem(r, c, QTableWidgetItem(value))
            self.detected_vendors.add(gpu["vendor"].lower())

        self.info["nvidia_driver"][1].setText(data.get("nvidia", "?"))
        self.info["dkms"][1].setText(data.get("dkms", "?"))
        self.info["hybrid"][1].setText(t(self.lang, "active") if data.get("switcheroo") else t(self.lang, "inactive"))
        self.info["nouveau"][1].setText(t(self.lang, "enabled") if data.get("nouveau") else t(self.lang, "disabled"))
        self.info["firmware"][1].setText(", ".join(data.get("firmware", [])) or "—")
        self.info["vulkan"][1].setText(data.get("vulkan", "?"))
        self.info["vaapi"][1].setText(data.get("vaapi", "?"))

        self.intel_btn.setVisible("intel" in self.detected_vendors)
        self.amd_btn.setVisible("amd" in self.detected_vendors)
        self.nvidia_btn.setVisible("nvidia" in self.detected_vendors)
        self.table.resizeColumnsToContents()
        self.refresh_btn.setEnabled(True)

    def repair_vendor(self, vendor):
        code, out = repair(vendor)
        QMessageBox.information(
            self,
            t(self.lang, "operation_done") if code == 0 else t(self.lang, "operation_failed"),
            out[-5000:] or "OK"
        )
        self.refresh()
