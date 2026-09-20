from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget,
)
from ..i18n import t
from ..services.source_service import (
    apt_sources, flatpak_remotes, add_flatpak_remote, remove_flatpak_remote,
)
from .base import page_header


class RemoteWorker(QObject):
    done = Signal(int, str)

    def __init__(self, operation, arguments):
        super().__init__()
        self.operation = operation
        self.arguments = arguments

    @Slot()
    def run(self):
        try:
            if self.operation == "add":
                result = add_flatpak_remote(*self.arguments)
            else:
                result = remove_flatpak_remote(*self.arguments)
        except Exception as exc:
            result = (1, str(exc))
        self.done.emit(*result)


class SourcesPage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__()
        self.lang = lang
        self.worker = None
        self.thread = None
        self.setObjectName("ContentPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(15)
        self.title, self.subtitle = page_header(layout, "", "")
        self.tabs = QTabWidget()
        self.tabs.setObjectName("Tabs")
        layout.addWidget(self.tabs, 1)

        apt = QWidget()
        ap_layout = QVBoxLayout(apt)
        self.aptlist = QListWidget()
        self.apttext = QTextEdit()
        self.apttext.setReadOnly(True)
        self.aptlist.currentRowChanged.connect(self.show_apt)
        ap_layout.addWidget(self.aptlist)
        ap_layout.addWidget(self.apttext, 1)
        self.tabs.addTab(apt, "APT")

        flat = QWidget()
        flat_layout = QVBoxLayout(flat)
        self.flat = QListWidget()
        self.flat.currentItemChanged.connect(lambda *_: self.update_remove_button())
        flat_layout.addWidget(self.flat, 1)
        row = QHBoxLayout()
        self.name = QLineEdit()
        self.url = QLineEdit()
        self.add_btn = QPushButton()
        self.remove_btn = QPushButton()
        self.add_btn.clicked.connect(self.add_remote)
        self.remove_btn.clicked.connect(self.remove_remote)
        for widget in (self.name, self.url, self.add_btn, self.remove_btn):
            row.addWidget(widget)
        flat_layout.addLayout(row)
        self.tabs.addTab(flat, "Flatpak")
        self.note = QLabel()
        self.note.setObjectName("StatusLabel")
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        self.files = []
        self.set_language(lang)
        self.refresh()

    def set_language(self, lang):
        self.lang = lang
        self.title.setText(t(lang, "sources_title"))
        self.subtitle.setText(t(lang, "sources_intro"))
        self.tabs.setTabText(0, t(lang, "apt_sources"))
        self.tabs.setTabText(1, t(lang, "flatpak_remotes"))
        self.name.setPlaceholderText(t(lang, "remote_name"))
        self.url.setPlaceholderText(t(lang, "remote_url"))
        self.add_btn.setText(t(lang, "add"))
        self.remove_btn.setText(t(lang, "remove_selected"))
        self.note.setText(
            "Sistem APT/Flatpak kaynakları burada salt okunur; yalnızca kendi kullanıcı Flatpak kaynaklarını yönetebilirsin."
            if lang == "tr" else
            "System APT/Flatpak sources are read-only here; only user Flatpak remotes can be managed."
        )
        self.update_remove_button()

    def refresh(self):
        self.files = apt_sources()
        self.aptlist.clear()
        for path, _ in self.files:
            self.aptlist.addItem(path)
        self.flat.clear()
        rows, errors = flatpak_remotes()
        for name, url, scope in rows:
            item = QListWidgetItem(f"[{scope}] {name}  —  {url}")
            item.setData(Qt.UserRole, (name, scope))
            self.flat.addItem(item)
        if errors:
            self.note.setText(errors[-800:])
        self.update_remove_button()

    def show_apt(self, row):
        if 0 <= row < len(self.files):
            self.apttext.setPlainText(self.files[row][1])

    def update_remove_button(self):
        selected = self.flat.currentItem()
        scope = selected.data(Qt.UserRole)[1] if selected else ""
        self.remove_btn.setEnabled(self.thread is None and scope == "user")

    def operate(self, action, arguments):
        if self.thread is not None:
            return
        self.add_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.thread = QThread(self)
        self.worker = RemoteWorker(action, arguments)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.done.connect(self.operation_done)
        self.worker.done.connect(self.thread.quit)
        self.worker.done.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.operation_finished)
        self.thread.start()

    def operation_done(self, code, message):
        dialog = QMessageBox.information if code == 0 else QMessageBox.warning
        dialog(self, t(self.lang, "operation_done") if code == 0 else
               t(self.lang, "operation_failed"), message or
               ("OK" if code == 0 else "Operation failed"))

    def operation_finished(self):
        self.thread = None
        self.worker = None
        self.add_btn.setEnabled(True)
        self.refresh()

    def add_remote(self):
        name, url = self.name.text().strip(), self.url.text().strip()
        if name and url:
            self.operate("add", (name, url))

    def remove_remote(self):
        item = self.flat.currentItem()
        if item is None:
            return
        name, scope = item.data(Qt.UserRole)
        if scope != "user":
            return
        question = (f"{name} adlı kullanıcı Flatpak kaynağı kaldırılsın mı?"
                    if self.lang == "tr" else
                    f"Remove user Flatpak remote {name}?")
        if QMessageBox.question(self, "Puresteel", question) == QMessageBox.Yes:
            self.operate("remove", (name, scope))
