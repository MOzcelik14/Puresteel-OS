from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)
from ..i18n import t
from ..services.backup_service import create_backup
from .base import page_header


class BackupWorker(QObject):
    done = Signal(bool, str)

    def __init__(self, destination, selections):
        super().__init__()
        self.destination = destination
        self.selections = selections

    @Slot()
    def run(self):
        try:
            self.done.emit(True, create_backup(self.destination, self.selections))
        except Exception as exc:
            self.done.emit(False, str(exc))


class BackupPage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__()
        self.lang = lang
        self.thread = None
        self.worker = None
        self.setObjectName("ContentPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(14)
        self.title, self.subtitle = page_header(layout, "", "")
        self.boxes = {}
        for key in ("documents", "pictures", "music", "config", "packages"):
            cb = QCheckBox()
            cb.setChecked(key in ("documents", "pictures", "config", "packages"))
            self.boxes[key] = cb
            layout.addWidget(cb)
        row = QHBoxLayout()
        self.dest = QLineEdit(str(Path.home()))
        self.browse = QPushButton()
        self.browse.clicked.connect(self.choose)
        row.addWidget(self.dest, 1)
        row.addWidget(self.browse)
        layout.addLayout(row)
        self.create = QPushButton()
        self.create.setObjectName("PrimaryButton")
        self.create.clicked.connect(self.make)
        layout.addWidget(self.create)
        self.status = QLabel()
        self.status.setObjectName("StatusLabel")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()
        self.set_language(lang)

    def set_language(self, lang):
        self.lang = lang
        self.title.setText(t(lang, "backup_title"))
        self.subtitle.setText(t(lang, "backup_intro"))
        labels = {
            "documents": "backup_documents", "pictures": "backup_pictures",
            "music": "backup_music", "config": "backup_config", "packages": "backup_packages",
        }
        for key, cb in self.boxes.items():
            cb.setText(t(lang, labels[key]))
        self.browse.setText(t(lang, "browse"))
        self.create.setText(t(lang, "create_backup"))

    def choose(self):
        directory = QFileDialog.getExistingDirectory(self, t(self.lang, "choose_folder"), self.dest.text())
        if directory:
            self.dest.setText(directory)

    def make(self):
        if self.thread is not None:
            return
        self.create.setEnabled(False)
        self.browse.setEnabled(False)
        self.status.setText("Yedekleme sürüyor…" if self.lang == "tr" else "Backup in progress…")
        self.thread = QThread(self)
        self.worker = BackupWorker(
            self.dest.text(), {key: box.isChecked() for key, box in self.boxes.items()}
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.done.connect(self.completed)
        self.worker.done.connect(self.thread.quit)
        self.worker.done.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.finished)
        self.thread.start()

    def completed(self, ok, value):
        self.status.setText(t(self.lang, "backup_done", path=value) if ok
                            else t(self.lang, "backup_error", error=value))

    def finished(self):
        self.thread = None
        self.worker = None
        self.create.setEnabled(True)
        self.browse.setEnabled(True)
