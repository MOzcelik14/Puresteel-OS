from pathlib import Path

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from ..i18n import t
from ..services.release_service import release_status


class ReleaseWorker(QObject):
    done = Signal(object)

    @Slot()
    def run(self):
        self.done.emit(release_status())


class HomePage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__()
        self.lang = lang
        self.release_thread = None
        self.release_worker = None
        self.release_data = None
        self.setObjectName("ContentPage")
        resource = Path(__file__).resolve().parents[1] / "resources"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(18)

        hero = QFrame()
        hero.setObjectName("HeroPanel")
        hb = QHBoxLayout(hero)
        hb.setContentsMargins(30, 26, 30, 26)
        hb.setSpacing(28)
        left = QVBoxLayout()
        left.setSpacing(9)
        self.kicker = QLabel()
        self.kicker.setObjectName("Eyebrow")
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("Lead")
        self.subtitle.setWordWrap(True)
        left.addWidget(self.kicker)
        left.addWidget(self.title)
        left.addWidget(self.subtitle)
        buttons = QHBoxLayout()
        self.update_btn = QPushButton()
        self.update_btn.setObjectName("PrimaryButton")
        self.driver_btn = QPushButton()
        self.driver_btn.setObjectName("SecondaryButton")
        self.update_btn.clicked.connect(lambda: self._go(2))
        self.driver_btn.clicked.connect(lambda: self._go(4))
        buttons.addWidget(self.update_btn)
        buttons.addWidget(self.driver_btn)
        buttons.addStretch()
        left.addLayout(buttons)
        hb.addLayout(left, 1)
        logo = QLabel()
        logo.setObjectName("HeroLogo")
        logo.setPixmap(QIcon(str(resource / "puresteel.png")).pixmap(QSize(132, 132)))
        hb.addWidget(logo)
        layout.addWidget(hero)

        release = QFrame()
        release.setObjectName("ReleasePanel")
        band = QHBoxLayout(release)
        band.setContentsMargins(20, 14, 20, 14)
        detail = QVBoxLayout()
        detail.setSpacing(4)
        self.release_heading = QLabel()
        self.release_heading.setObjectName("CardNumber")
        self.release_text = QLabel()
        self.release_text.setObjectName("ReleaseText")
        self.release_text.setWordWrap(True)
        self.release_note = QLabel()
        self.release_note.setObjectName("CardText")
        self.release_note.setWordWrap(True)
        detail.addWidget(self.release_heading)
        detail.addWidget(self.release_text)
        detail.addWidget(self.release_note)
        band.addLayout(detail, 1)
        self.release_btn = QPushButton()
        self.release_btn.setObjectName("SecondaryButton")
        self.release_btn.clicked.connect(self.refresh_release)
        band.addWidget(self.release_btn)
        layout.addWidget(release)

        grid = QGridLayout()
        grid.setSpacing(14)
        self.cards = []
        for i in range(4):
            card = QFrame()
            card.setObjectName("Card")
            cb = QVBoxLayout(card)
            cb.setContentsMargins(20, 18, 20, 18)
            cb.setSpacing(7)
            num = QLabel(f"0{i + 1}")
            num.setObjectName("CardNumber")
            title = QLabel()
            title.setObjectName("CardTitle")
            description = QLabel()
            description.setObjectName("CardText")
            description.setWordWrap(True)
            cb.addWidget(num)
            cb.addWidget(title)
            cb.addWidget(description)
            cb.addStretch()
            self.cards.append((title, description))
            grid.addWidget(card, i // 2, i % 2)
        layout.addLayout(grid)
        layout.addStretch()
        self.set_language(lang)
        QTimer.singleShot(0, self.refresh_release)

    def _go(self, row):
        window = self.window()
        if hasattr(window, "nav"):
            window.nav.setCurrentRow(row)

    def refresh_release(self):
        if self.release_thread is not None:
            return
        self.release_btn.setEnabled(False)
        self.release_text.setText("Denetleniyor…" if self.lang == "tr" else "Checking…")
        thread = QThread(self)
        self.release_thread = thread
        worker = ReleaseWorker()
        self.release_worker = worker
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.done.connect(self.render_release)
        worker.done.connect(thread.quit)
        worker.done.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self.release_finished)
        thread.start()

    def render_release(self, data):
        self.release_data = data
        tr = self.lang == "tr"
        installed = data["installed"] or ("Kurulu değil" if tr else "Not installed")
        candidate = data["candidate"] or ("Bulunamadı" if tr else "Unavailable")
        self.release_text.setText(
            f"Center: {installed}  •  APT: {candidate}  •  Kernel: {data['kernel']}"
        )
        if not data["source_ok"] or not data["key_ok"]:
            self.release_note.setText(
                "⚠ Puresteel APT kaynağı veya imza anahtarı eksik."
                if tr else "⚠ Puresteel APT source or archive key is missing."
            )
        elif data["pending"]:
            self.release_note.setText(
                "● Yeni Puresteel paketi mevcut; Güncellemeler'den güvenli kur."
                if tr else "● A Puresteel package update is available; apply it safely from Updates."
            )
        else:
            self.release_note.setText(
                "Yerel APT önbelleği gösteriliyor; yeni paketler için APT indeksini yenile."
                if tr else "Showing local APT cache; refresh APT indexes to discover new packages."
            )

    def release_finished(self):
        self.release_thread = None
        self.release_worker = None
        self.release_btn.setEnabled(True)

    def set_language(self, lang):
        self.lang = lang
        self.kicker.setText(t(lang, "welcome_kicker"))
        self.title.setText(t(lang, "welcome_title"))
        self.subtitle.setText(t(lang, "welcome_subtitle"))
        self.update_btn.setText(t(lang, "quick_updates"))
        self.driver_btn.setText(t(lang, "quick_drivers"))
        tr = lang == "tr"
        self.release_heading.setText("ROLLING SÜRÜM DURUMU" if tr else "ROLLING RELEASE STATUS")
        self.release_btn.setText("Yenile" if tr else "Refresh")
        if self.release_data is not None:
            self.render_release(self.release_data)
        else:
            self.release_text.setText("Paket durumunu denetlemek için Yenile." if tr
                                      else "Refresh to inspect package status.")
            self.release_note.setText("Kurulu sürüm ve APT indeksindeki aday gösterilir."
                                      if tr else "Shows the installed version and APT index candidate.")
        pairs = [
            ("home_updates", "home_updates_text"),
            ("home_drivers", "home_drivers_text"),
            ("home_apps", "home_apps_text"),
            ("home_reports", "home_reports_text"),
        ]
        for (title, desc), (title_key, desc_key) in zip(self.cards, pairs):
            title.setText(t(lang, title_key))
            desc.setText(t(lang, desc_key))
