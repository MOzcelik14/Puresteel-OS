"""Puresteel GPU Driver Manager – honest APT options and background operations."""
import shlex
import shutil
import subprocess

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QHBoxLayout, QInputDialog, QLabel,
    QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)
from ..i18n import t
from ..services.driver_service import (
    collect, install_driver, repair, simulate_install, simulate_repair,
)
from .base import page_header


class DriverTask(QObject):
    done = Signal(str, object)

    def __init__(self, kind, value=None):
        super().__init__()
        self.kind = kind
        self.value = value

    @Slot()
    def run(self):
        try:
            handlers = {
                "collect": lambda: collect(),
                "preview-install": lambda: simulate_install(self.value),
                "install": lambda: install_driver(self.value),
                "preview-repair": lambda: simulate_repair(self.value),
                "repair": lambda: repair(self.value),
            }
            result = handlers[self.kind]()
        except Exception as exc:
            result = {"error": str(exc)} if self.kind == "collect" else (1, str(exc))
        self.done.emit(self.kind, result)


class DriversPage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__()
        self.lang = lang
        self.thread = None
        self.worker = None
        self.pending = None
        self.detected_vendors = set()
        self.setObjectName("ContentPage")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(42, 36, 42, 36)
        outer.setSpacing(14)
        self.title, self.subtitle = page_header(outer, "", "")
        self.status = QLabel()
        self.status.setObjectName("StatusLabel")
        self.status.setWordWrap(True)
        outer.addWidget(self.status)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(14)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        self.table = QTableWidget(0, 4)
        self.table.setObjectName("DataTable")
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(150)
        layout.addWidget(self.table)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.info = {}
        for i, key in enumerate(("nvidia_driver", "dkms", "hybrid", "nouveau",
                                  "firmware", "vulkan", "vaapi", "headers", "secureboot")):
            card = QFrame()
            card.setObjectName("Card")
            box = QVBoxLayout(card)
            box.setContentsMargins(16, 12, 16, 12)
            label = QLabel()
            label.setObjectName("CardNumber")
            value = QLabel("…")
            value.setObjectName("CardText")
            value.setWordWrap(True)
            value.setTextInteractionFlags(value.textInteractionFlags() |
                                           value.textInteractionFlags().__class__.TextSelectableByMouse)
            box.addWidget(label)
            box.addWidget(value)
            self.info[key] = (label, value)
            grid.addWidget(card, i // 2, i % 2)
        layout.addLayout(grid)

        selection = QHBoxLayout()
        self.driver_label = QLabel()
        self.driver_combo = QComboBox()
        self.driver_combo.setMinimumWidth(270)
        self.install_btn = QPushButton()
        self.install_btn.setObjectName("PrimaryButton")
        self.install_btn.clicked.connect(self.preview_install)
        selection.addWidget(self.driver_label)
        selection.addWidget(self.driver_combo, 1)
        selection.addWidget(self.install_btn)
        layout.addLayout(selection)

        actions = QHBoxLayout()
        self.refresh_btn = QPushButton()
        self.refresh_btn.setObjectName("PrimaryButton")
        self.refresh_btn.clicked.connect(self.refresh)
        self.intel_btn = QPushButton()
        self.amd_btn = QPushButton()
        self.nvidia_btn = QPushButton()
        self.nvidia_run_btn = QPushButton()
        self.controls = [
            self.refresh_btn, self.install_btn,
            self.intel_btn, self.amd_btn, self.nvidia_btn, self.nvidia_run_btn,
        ]
        for button in (self.intel_btn, self.amd_btn, self.nvidia_btn, self.nvidia_run_btn):
            button.setObjectName("SecondaryButton")
            actions.addWidget(button)
        self.intel_btn.clicked.connect(lambda: self.preview_repair("intel"))
        self.amd_btn.clicked.connect(lambda: self.preview_repair("amd"))
        self.nvidia_btn.clicked.connect(lambda: self.preview_repair("nvidia"))
        self.nvidia_run_btn.clicked.connect(self.run_on_nvidia)
        actions.insertWidget(0, self.refresh_btn)
        actions.addStretch()
        layout.addLayout(actions)

        self.plan_label = QLabel()
        layout.addWidget(self.plan_label)
        self.plan_output = QPlainTextEdit()
        self.plan_output.setReadOnly(True)
        self.plan_output.setMinimumHeight(160)
        layout.addWidget(self.plan_output)
        self.note = QLabel()
        self.note.setObjectName("StatusLabel")
        self.note.setWordWrap(True)
        layout.addWidget(self.note)

        self.set_language(lang)
        self.refresh()

    def set_language(self, lang):
        self.lang = lang
        tr = lang == "tr"
        self.title.setText("GPU & Sürücüler" if tr else "GPU & Drivers")
        self.subtitle.setText(
            "Etkin sürücüyü, depodaki seçenekleri ve değişiklik planını denetle."
            if tr else "Inspect active drivers, repository choices and planned changes.")
        self.table.setHorizontalHeaderLabels([
            t(lang, "gpu_vendor"), t(lang, "gpu_model"), t(lang, "gpu_driver"), "Kernel modules",
        ])
        for key, (label, _) in self.info.items():
            label.setText({
                "headers": "Kernel headers",
                "secureboot": "Secure Boot",
            }.get(key, t(lang, key)))
        self.refresh_btn.setText(t(lang, "driver_refresh"))
        self.intel_btn.setText(t(lang, "repair_intel"))
        self.amd_btn.setText(t(lang, "repair_amd"))
        self.nvidia_btn.setText(t(lang, "repair_nvidia"))
        self.nvidia_run_btn.setText("NVIDIA ile çalıştır" if tr else "Run on NVIDIA")
        self.driver_label.setText("Depodaki NVIDIA sürücüsü:" if tr else "Repository NVIDIA driver:")
        self.install_btn.setText("Önizle ve kur" if tr else "Preview and install")
        self.plan_label.setText("APT işlem önizlemesi / APT transaction preview")
        self.note.setText(
            "Sadece etkin Debian depolarındaki sürücüler listelenir. İşlem öncesinde "
            "kernel header'ları ve APT kaldırma planı denetlenir. Sürücü değişimi "
            "sonrasında yeniden başlatma gerekebilir."
            if tr else
            "Only packages in enabled APT sources are offered. Kernel headers and "
            "APT removals are checked before installing. A reboot may be required.")

    def start_task(self, kind, value=None):
        if self.thread is not None:
            return
        self.status.setText(("İşleniyor: " if self.lang == "tr" else "Working: ") + kind)
        for button in self.controls:
            button.setEnabled(False)
        self.thread = QThread(self)
        self.worker = DriverTask(kind, value)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.done.connect(self.task_done)
        self.worker.done.connect(self.thread.quit)
        self.worker.done.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.task_finished)
        self.thread.start()

    def refresh(self):
        self.start_task("collect")

    def task_done(self, kind, result):
        if kind == "collect":
            if "error" in result:
                self.status.setText("GPU detection failed: " + result["error"])
            else:
                self.display_devices(result)
            return
        code, message = result
        self.plan_output.setPlainText(message)
        if kind.startswith("preview-"):
            if code:
                QMessageBox.warning(self, "Puresteel", message[-6000:])
                self.status.setText("APT preview rejected" if self.lang != "tr"
                                    else "APT önizlemesi güvenli işlem sunamadı")
                return
            label = ("Bu işlemi gerçekleştirmek istiyor musun?\n"
                     "Kurulumdan önce bağımlılıklar yeniden kontrol edilecek."
                     if self.lang == "tr" else
                     "Proceed with this transaction?\nDependencies will be checked again.")
            if QMessageBox.question(self, "Puresteel GPU Manager", label + "\n\n" + message[:3000]) == QMessageBox.Yes:
                self.pending = ("install" if kind == "preview-install" else "repair",
                                self.requested_value)
            else:
                self.status.setText("Cancelled" if self.lang != "tr" else "İptal edildi")
            return
        box = QMessageBox.information if code == 0 else QMessageBox.warning
        box(self, "Puresteel", message[-6000:] or ("Completed" if code == 0 else "Failed"))
        self.status.setText(
            ("İşlem tamamlandı; yeniden başlatma gerekebilir." if self.lang == "tr"
             else "Operation completed; reboot may be required.")
            if code == 0 else
            ("İşlem başarısız; logu incele." if self.lang == "tr"
             else "Operation failed; inspect the log."))
        self.pending = ("collect", None)

    def task_finished(self):
        self.thread = None
        self.worker = None
        for button in self.controls:
            button.setEnabled(True)
        self.apply_visibility()
        if self.pending is not None:
            kind, value = self.pending
            self.pending = None
            QTimer.singleShot(0, lambda: self.start_task(kind, value))

    def display_devices(self, data):
        self.table.setRowCount(0)
        self.detected_vendors = set()
        for gpu in data.get("gpus", []):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.detected_vendors.add(gpu["vendor"].lower())
            for col, text in enumerate((gpu["vendor"], gpu["model"],
                                         gpu["driver"], gpu["modules"])):
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
        firmware = [
            "{}: {}".format(pkg["name"], pkg["installed"] or "not installed")
            for pkg in data.get("firmware", [])
        ]
        values = {
            "nvidia_driver": data.get("nvidia", "Unknown"),
            "dkms": data.get("dkms", "Unknown"),
            "hybrid": t(self.lang, "active") if data.get("switcheroo") else t(self.lang, "inactive"),
            "nouveau": t(self.lang, "enabled") if data.get("nouveau") else t(self.lang, "disabled"),
            "firmware": "\n".join(firmware) or "—",
            "vulkan": data.get("vulkan", "Unknown"),
            "vaapi": data.get("vaapi", "Unknown"),
            "headers": data.get("headers") or "Missing for " + data.get("kernel", "?"),
            "secureboot": data.get("secureboot", "Unknown"),
        }
        for key, value in values.items():
            self.info[key][1].setText(value)
        previous = self.driver_combo.currentData()
        self.driver_combo.clear()
        for choice in data.get("choices", []):
            installed = choice["installed"] or "not installed"
            version = choice["candidate"] or "unavailable"
            self.driver_combo.addItem(
                "{} · installed: {} · candidate: {}".format(choice["name"], installed, version),
                choice["name"],
            )
        index = self.driver_combo.findData(previous)
        if index >= 0:
            self.driver_combo.setCurrentIndex(index)
        self.status.setText(
            "{} GPU(s) found; {} NVIDIA package choice(s).".format(
                len(data.get("gpus", [])), len(data.get("choices", []))))
        self.apply_visibility()

    def apply_visibility(self):
        busy = self.thread is not None
        for name, button in (("intel", self.intel_btn), ("amd", self.amd_btn),
                             ("nvidia", self.nvidia_btn)):
            button.setVisible(name in self.detected_vendors)
            button.setEnabled(not busy)
        self.nvidia_run_btn.setVisible("nvidia" in self.detected_vendors)
        self.nvidia_run_btn.setEnabled(not busy)
        available = self.driver_combo.count() > 0 and "nvidia" in self.detected_vendors
        self.driver_combo.setEnabled(not busy and available)
        self.install_btn.setVisible(available)
        self.install_btn.setEnabled(not busy and available)
        self.refresh_btn.setEnabled(not busy)

    def preview_install(self):
        name = self.driver_combo.currentData()
        if name:
            self.requested_value = name
            self.start_task("preview-install", name)

    def preview_repair(self, vendor):
        self.requested_value = vendor
        self.start_task("preview-repair", vendor)

    def run_on_nvidia(self):
        if not shutil.which("puresteel-nvidia-run"):
            QMessageBox.warning(self, "Puresteel", "puresteel-nvidia-run unavailable")
            return
        text, ok = QInputDialog.getText(
            self, "NVIDIA Offload",
            "Komut (örn. blender)" if self.lang == "tr" else "Command (e.g. blender)")
        if not ok or not text.strip():
            return
        try:
            subprocess.Popen(["puresteel-nvidia-run", *shlex.split(text)],
                             start_new_session=True)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Puresteel", str(exc))
