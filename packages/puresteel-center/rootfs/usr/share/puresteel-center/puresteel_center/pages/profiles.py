from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget
from ..services.profile_service import apply, current, status
from .base import page_header

PROFILES = (
    ("balanced", "Balanced", "Dengeli günlük kullanım", "Balanced everyday behaviour"),
    ("gaming", "Gaming", "Oyun için yüksek performans", "High performance for games"),
    ("creator", "Creator", "Render, ses ve video işleri", "Rendering, audio and video workloads"),
    ("battery", "Battery", "Pil ömrü ve düşük güç tüketimi", "Battery life and lower power use"),
)


class ProfilesPage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__(); self.lang = lang; self.setObjectName("ContentPage")
        layout = QVBoxLayout(self); layout.setContentsMargins(42, 36, 42, 36); layout.setSpacing(14)
        self.title, self.subtitle = page_header(layout, "", "")
        self.grid = QGridLayout(); self.grid.setSpacing(12); self.buttons = {}; self.desc = {}
        for i, (key, name, tr_desc, en_desc) in enumerate(PROFILES):
            card = QFrame(); card.setObjectName("Card"); box = QVBoxLayout(card)
            title = QLabel(name); title.setObjectName("CardNumber"); desc = QLabel(); desc.setWordWrap(True); desc.setObjectName("CardText")
            btn = QPushButton(); btn.setObjectName("SecondaryButton"); btn.clicked.connect(lambda _=False, k=key: self.apply_profile(k))
            box.addWidget(title); box.addWidget(desc); box.addStretch(); box.addWidget(btn)
            self.desc[key] = (desc, tr_desc, en_desc); self.buttons[key] = btn; self.grid.addWidget(card, i // 2, i % 2)
        layout.addLayout(self.grid)
        self.current_label = QLabel(); self.current_label.setObjectName("StatusLabel"); layout.addWidget(self.current_label)
        self.details = QTextEdit(); self.details.setReadOnly(True); self.details.setMaximumHeight(150); layout.addWidget(self.details)
        self.refresh_btn = QPushButton(); self.refresh_btn.clicked.connect(self.refresh); layout.addWidget(self.refresh_btn)
        self.set_language(lang); self.refresh()

    def set_language(self, lang):
        self.lang = lang
        self.title.setText("Puresteel Profilleri" if lang == "tr" else "Puresteel Profiles")
        self.subtitle.setText("Güç ve bellek davranışını tek tıkla değiştir." if lang == "tr" else "Switch power and memory behaviour with one click.")
        for key, (label, tr_desc, en_desc) in self.desc.items(): label.setText(tr_desc if lang == "tr" else en_desc)
        for btn in self.buttons.values(): btn.setText("Uygula" if lang == "tr" else "Apply")
        self.refresh_btn.setText("Durumu yenile" if lang == "tr" else "Refresh status")
        self.refresh()

    def refresh(self):
        name = current(); code, out = status()
        prefix = "Etkin profil" if self.lang == "tr" else "Active profile"
        self.current_label.setText(f"{prefix}: {name}")
        self.details.setPlainText(out if code == 0 else "Puresteel profile tool unavailable")
        for key, btn in self.buttons.items(): btn.setEnabled(key != name)

    def apply_profile(self, name):
        code, out = apply(name)
        QMessageBox.information(self, "Puresteel", out[-4000:] or ("OK" if code == 0 else "Failed"))
        self.refresh()
