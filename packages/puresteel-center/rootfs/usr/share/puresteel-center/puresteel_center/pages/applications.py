"""APT/Flatpak application catalog. All package operations run off the GUI thread."""
from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)
from ..i18n import t
from ..services.app_service import (
    apt_search, flatpak_search, apt_installed, flatpak_installed, install, remove,
)
from .base import page_header


class CatalogWorker(QObject):
    done = Signal(str, object)

    def __init__(self, action, value):
        super().__init__()
        self.action = action
        self.value = value

    @Slot()
    def run(self):
        try:
            if self.action == "search":
                rows = (apt_search(self.value) + flatpak_search(self.value))[:120]
                result = [(source, name, description,
                           apt_installed(name) if source == "APT" else flatpak_installed(name))
                          for source, name, description in rows]
            else:
                source, name = self.value
                result = install(source, name) if self.action == "install" else remove(source, name)
        except Exception as exc:
            result = [] if self.action == "search" else (1, str(exc))
        self.done.emit(self.action, result)


class ApplicationsPage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__()
        self.lang = lang
        self.thread = None
        self.worker = None
        self.refresh_after = False
        self.setObjectName("ContentPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(15)
        self.title, self.subtitle = page_header(layout, "", "")
        row = QHBoxLayout()
        self.query = QLineEdit()
        self.search_btn = QPushButton()
        self.search_btn.setObjectName("PrimaryButton")
        self.search_btn.clicked.connect(self.search)
        self.query.returnPressed.connect(self.search)
        row.addWidget(self.query, 1)
        row.addWidget(self.search_btn)
        layout.addLayout(row)
        self.table = QTableWidget(0, 4)
        self.table.setObjectName("DataTable")
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)
        actions = QHBoxLayout()
        self.install_btn = QPushButton()
        self.remove_btn = QPushButton()
        self.install_btn.setObjectName("PrimaryButton")
        self.remove_btn.setObjectName("SecondaryButton")
        self.install_btn.clicked.connect(lambda: self.act(True))
        self.remove_btn.clicked.connect(lambda: self.act(False))
        actions.addWidget(self.install_btn)
        actions.addWidget(self.remove_btn)
        actions.addStretch()
        layout.addLayout(actions)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.set_language(lang)

    def set_language(self, lang):
        self.lang = lang
        self.title.setText(t(lang, "apps_title"))
        self.subtitle.setText(t(lang, "apps_intro"))
        self.query.setPlaceholderText(t(lang, "search_placeholder"))
        self.search_btn.setText(t(lang, "search"))
        self.install_btn.setText(t(lang, "install"))
        self.remove_btn.setText(t(lang, "remove"))
        self.table.setHorizontalHeaderLabels([
            t(lang, "source"), t(lang, "package"), "Description", t(lang, "installed"),
        ])

    def start_task(self, action, value):
        if self.thread is not None:
            return
        for control in (self.search_btn, self.install_btn, self.remove_btn):
            control.setEnabled(False)
        self.status.setText(
            "İşlem sürüyor…" if self.lang == "tr" else "Working…")
        self.thread = QThread(self)
        self.worker = CatalogWorker(action, value)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.done.connect(self.task_done)
        self.worker.done.connect(self.thread.quit)
        self.worker.done.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.task_finished)
        self.thread.start()

    def search(self):
        query = self.query.text().strip()
        if len(query) >= 2:
            self.table.setRowCount(0)
            self.start_task("search", query)

    def task_done(self, action, result):
        if action == "search":
            for source, name, description, installed in result:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for column, value in enumerate((
                    source, name, description,
                    t(self.lang, "installed") if installed else t(self.lang, "not_installed"),
                )):
                    self.table.setItem(row, column, QTableWidgetItem(value))
            if not result:
                self.table.insertRow(0)
                self.table.setItem(0, 1, QTableWidgetItem(t(self.lang, "no_results")))
            self.table.resizeColumnsToContents()
            self.status.setText(f"{len(result)} results")
            return
        code, output = result
        box = QMessageBox.information if code == 0 else QMessageBox.warning
        box(self, t(self.lang, "operation_done") if code == 0 else
            t(self.lang, "operation_failed"), output[-6000:] or
            ("OK" if code == 0 else "Failed"))
        self.status.setText(
            "Operation completed" if code == 0 else "Operation failed")
        self.refresh_after = True

    def task_finished(self):
        self.thread = None
        self.worker = None
        for control in (self.search_btn, self.install_btn, self.remove_btn):
            control.setEnabled(True)
        if self.refresh_after:
            self.refresh_after = False
            QTimer.singleShot(0, self.search)

    def selected(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        source = self.table.item(row, 0)
        name = self.table.item(row, 1)
        return (source.text(), name.text()) if source and name else None

    def act(self, installing):
        if self.thread is not None:
            return
        target = self.selected()
        if target is None:
            return
        verb = ("Kur" if installing else "Kaldır") if self.lang == "tr" else (
            "Install" if installing else "Remove")
        if QMessageBox.question(self, "Puresteel", f"{verb}: {target[1]}?") != QMessageBox.Yes:
            return
        self.start_task("install" if installing else "remove", target)
