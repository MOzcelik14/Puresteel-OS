\
from pathlib import Path
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame,QGridLayout,QHBoxLayout,QLabel,QPushButton,QVBoxLayout,QWidget
from ..i18n import t

class HomePage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__()
        self.lang=lang
        self.setObjectName("ContentPage")
        resource=Path(__file__).resolve().parents[1]/"resources"
        layout=QVBoxLayout(self); layout.setContentsMargins(42,36,42,36); layout.setSpacing(22)

        hero=QFrame(); hero.setObjectName("HeroPanel")
        hb=QHBoxLayout(hero); hb.setContentsMargins(30,26,30,26); hb.setSpacing(28)
        left=QVBoxLayout(); left.setSpacing(9)
        self.kicker=QLabel(); self.kicker.setObjectName("Eyebrow")
        self.title=QLabel(); self.title.setObjectName("PageTitle")
        self.subtitle=QLabel(); self.subtitle.setObjectName("Lead"); self.subtitle.setWordWrap(True)
        left.addWidget(self.kicker); left.addWidget(self.title); left.addWidget(self.subtitle)
        buttons=QHBoxLayout()
        self.update_btn=QPushButton(); self.update_btn.setObjectName("PrimaryButton")
        self.driver_btn=QPushButton(); self.driver_btn.setObjectName("SecondaryButton")
        self.update_btn.clicked.connect(lambda:self._go(1)); self.driver_btn.clicked.connect(lambda:self._go(3))
        buttons.addWidget(self.update_btn); buttons.addWidget(self.driver_btn); buttons.addStretch()
        left.addLayout(buttons)
        hb.addLayout(left,1)
        logo=QLabel(); logo.setObjectName("HeroLogo")
        logo.setPixmap(QIcon(str(resource/"puresteel.png")).pixmap(QSize(150,150)))
        hb.addWidget(logo)
        layout.addWidget(hero)

        grid=QGridLayout(); grid.setSpacing(14)
        self.cards=[]
        for i in range(4):
            card=QFrame(); card.setObjectName("Card")
            cb=QVBoxLayout(card); cb.setContentsMargins(20,18,20,18); cb.setSpacing(7)
            num=QLabel(f"0{i+1}"); num.setObjectName("CardNumber")
            h=QLabel(); h.setObjectName("CardTitle")
            p=QLabel(); p.setObjectName("CardText"); p.setWordWrap(True)
            cb.addWidget(num); cb.addWidget(h); cb.addWidget(p); cb.addStretch()
            self.cards.append((h,p)); grid.addWidget(card,i//2,i%2)
        layout.addLayout(grid); layout.addStretch()
        self.set_language(lang)

    def _go(self,row):
        w=self.window()
        if hasattr(w,"nav"): w.nav.setCurrentRow(row)

    def set_language(self,lang):
        self.lang=lang
        self.kicker.setText(t(lang,"welcome_kicker")); self.title.setText(t(lang,"welcome_title"))
        self.subtitle.setText(t(lang,"welcome_subtitle"))
        self.update_btn.setText(t(lang,"quick_updates")); self.driver_btn.setText(t(lang,"quick_drivers"))
        pairs=[("home_updates","home_updates_text"),("home_drivers","home_drivers_text"),
               ("home_apps","home_apps_text"),("home_reports","home_reports_text")]
        for (h,p),(hk,pk) in zip(self.cards,pairs):
            h.setText(t(lang,hk)); p.setText(t(lang,pk))
