import subprocess
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QLabel, QMessageBox, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)
from ..services.common import privileged
from .base import page_header


class MaintenanceWorker(QObject):
    done = Signal(int, str)

    def __init__(self, action, args, timeout):
        super().__init__()
        self.action = action
        self.args = args
        self.timeout = timeout

    @Slot()
    def run(self):
        self.done.emit(*privileged(self.action, *self.args, timeout=self.timeout))


class PuresteelPage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__()
        self.lang = lang
        self.setObjectName("ContentPage")
        self.worker = None
        self.thread = None
        self.buttons = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(14)
        self.title, self.subtitle = page_header(layout, "", "")
        self.status = QLabel()
        self.status.setObjectName("StatusLabel")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        scroller = QScrollArea(self)
        scroller.setWidgetResizable(True)
        scroller.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        self.grid = QGridLayout(body)
        self.grid.setSpacing(12)
        scroller.setWidget(body)
        layout.addWidget(scroller, 1)

        actions = [
            ("welcome", lambda: self.launch("puresteel-welcome")),
            ("snapshot", lambda: self.launch("puresteel-snapshots")),
            ("safe_update", lambda: self.start_action("safe-upgrade", (), 7200)),
            ("battery", lambda: self.launch_terminal("puresteel-battery")),
            ("firmware", lambda: self.launch_terminal("puresteel-firmware status")),
            ("health", lambda: self.launch_terminal("puresteel-health all")),
            ("logs", lambda: self.launch_terminal("puresteel-logs")),
            ("secureboot", lambda: self.launch_terminal("puresteel-secureboot status")),
            ("flatpak", lambda: self.start_action("flatpak-repair", (), 3600)),
            ("kernel", lambda: self.launch_terminal("puresteel-kernel")),
            ("essentials", lambda: self.start_action("app-pack", ("essentials",), 3600)),
            ("creator", lambda: self.start_action("app-pack", ("creator",), 3600)),
            ("developer", lambda: self.start_action("app-pack", ("developer",), 3600)),
            ("gaming", lambda: self.start_action("app-pack", ("gaming",), 3600)),
        ]
        for i, (key, callback) in enumerate(actions):
            card = QFrame()
            card.setObjectName("Card")
            box = QVBoxLayout(card)
            title = QLabel()
            title.setObjectName("CardNumber")
            description = QLabel()
            description.setObjectName("CardText")
            description.setWordWrap(True)
            button = QPushButton()
            button.setObjectName("SecondaryButton")
            button.clicked.connect(callback)
            box.addWidget(title)
            box.addWidget(description)
            box.addStretch()
            box.addWidget(button)
            self.grid.addWidget(card, i // 2, i % 2)
            self.buttons.append((key, title, description, button))
        self.set_language(lang)

    def current_status(self):
        def read(name, fallback):
            path = Path("/etc/puresteel") / name
            try:
                return path.read_text().strip()
            except OSError:
                return fallback
        return read("profile", "balanced"), read("channel", "stable"), read("hardware-mode", "auto")

    def set_language(self, lang):
        self.lang = lang
        tr = lang == "tr"
        self.title.setText("Puresteel Sistemi" if tr else "Puresteel System")
        self.subtitle.setText("Puresteel bakım, donanım ve güvenlik araçları." if tr else "Puresteel maintenance, hardware and security tools.")
        p, c, h = self.current_status()
        self.status.setText(f"Profil: {p}   •   Kanal: {c}   •   Donanım modu: {h}" if tr else f"Profile: {p}   •   Channel: {c}   •   Hardware mode: {h}")
        texts = {
            "welcome": (("Hoş Geldin", "Puresteel araçları ve belgeleri."), ("Welcome", "Puresteel tools and documentation.")),
            "snapshot": (("Snapshot", "Timeshift geri dönüş noktalarını yönet."), ("Snapshots", "Manage Timeshift restore points.")),
            "safe_update": (("Güvenli Güncelle", "Doğrulanmış snapshot oluşturmadan güncellemez."), ("Safe Update", "Requires a verified snapshot before upgrading.")),
            "battery": (("Pil Sağlığı", "Kapasite, döngü ve güç profili."), ("Battery Health", "Capacity, cycles and power profile.")),
            "firmware": (("Firmware", "fwupd cihaz durumunu göster."), ("Firmware", "Show fwupd device status.")),
            "health": (("Sistem Sağlığı", "Gaming/Creator bağımlılıklarını denetle."), ("System Health", "Check Gaming/Creator dependencies.")),
            "logs": (("Loglar", "Tanılama günlüklerini göster."), ("Logs", "Show diagnostic logs.")),
            "secureboot": (("Secure Boot", "Secure Boot, MOK ve DKMS durumunu göster."), ("Secure Boot", "Show Secure Boot, MOK and DKMS state.")),
            "flatpak": (("Flatpak Onar", "Sistem Flatpak kurulumunu onar."), ("Repair Flatpak", "Repair system Flatpak installation.")),
            "kernel": (("Kernel", "Çalışan ve alternatif kernelleri göster."), ("Kernel", "Show current and alternate kernels.")),
            "essentials": (("Essentials", "Günlük uygulamaları kur."), ("Essentials", "Install everyday essentials.")),
            "creator": (("Creator Pack", "Video ve ses araçlarını kur."), ("Creator Pack", "Install video and audio tools.")),
            "developer": (("Developer Pack", "Geliştirme araçlarını kur."), ("Developer Pack", "Install development tools.")),
            "gaming": (("Gaming Pack", "Oyun araçlarını kur."), ("Gaming Pack", "Install gaming tools.")),
        }
        action_keys = {"safe_update", "flatpak", "essentials", "creator", "developer", "gaming"}
        for key, label, description, button in self.buttons:
            title, detail = texts[key][0 if tr else 1]
            label.setText(title)
            description.setText(detail)
            button.setText(("Uygula" if key in action_keys else "Aç") if tr else ("Apply" if key in action_keys else "Open"))

    def launch(self, command):
        try:
            subprocess.Popen([command])
        except OSError as exc:
            QMessageBox.warning(self, "Puresteel", str(exc))

    def launch_terminal(self, command):
        try:
            subprocess.Popen(["gnome-terminal", "--", "sh", "-lc", command + "; printf '\\nPress Enter to close...'; read x"])
        except OSError as exc:
            QMessageBox.warning(self, "Puresteel", str(exc))

    def start_action(self, action, args, timeout):
        if self.thread is not None:
            return
        if action == "safe-upgrade":
            text = ("Snapshot oluşturulamazsa güncelleme iptal edilecek. Devam edilsin mi?"
                    if self.lang == "tr" else "Update will stop if the snapshot cannot be verified. Continue?")
            if QMessageBox.question(self, "Puresteel Safe Update", text) != QMessageBox.Yes:
                return
        for _, _, _, button in self.buttons:
            button.setEnabled(False)
        self.thread = QThread(self)
        self.worker = MaintenanceWorker(action, args, timeout)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.done.connect(self.action_done)
        self.worker.done.connect(self.thread.quit)
        self.worker.done.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.action_finished)
        self.thread.start()

    def action_done(self, code, output):
        message = output[-6000:] or ("Completed" if code == 0 else "Failed")
        if code == 0:
            QMessageBox.information(self, "Puresteel", message)
        else:
            QMessageBox.warning(self, "Puresteel", message)

    def action_finished(self):
        self.thread = None
        self.worker = None
        for _, _, _, button in self.buttons:
            button.setEnabled(True)
        self.set_language(self.lang)
