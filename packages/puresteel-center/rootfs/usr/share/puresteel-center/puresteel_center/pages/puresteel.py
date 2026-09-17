import subprocess
from pathlib import Path
from PySide6.QtWidgets import QFrame,QGridLayout,QLabel,QMessageBox,QPushButton,QVBoxLayout,QWidget
from ..services.common import privileged
from .base import page_header


class PuresteelPage(QWidget):
    def __init__(self, lang="tr"):
        super().__init__(); self.lang=lang; self.setObjectName("ContentPage")
        l=QVBoxLayout(self); l.setContentsMargins(42,36,42,36); l.setSpacing(14)
        self.title,self.subtitle=page_header(l,"","")
        self.status=QLabel(); self.status.setObjectName("StatusLabel"); self.status.setWordWrap(True); l.addWidget(self.status)
        self.grid=QGridLayout(); self.grid.setSpacing(12); l.addLayout(self.grid)
        self.buttons=[]
        actions=[
            ("welcome", lambda:self.launch("puresteel-welcome")),
            ("defaults", lambda:self.launch("puresteel-apply-defaults")),
            ("snapshot", lambda:self.launch("timeshift-gtk")),
            ("essentials", lambda:self.pack("essentials")),
            ("creator", lambda:self.pack("creator")),
            ("developer", lambda:self.pack("developer")),
            ("gaming", lambda:self.pack("gaming")),
            ("safe_update", self.safe_update),
        ]
        for i,(key,callback) in enumerate(actions):
            card=QFrame(); card.setObjectName("Card"); box=QVBoxLayout(card)
            label=QLabel(); label.setObjectName("CardNumber"); text=QLabel(); text.setObjectName("CardText"); text.setWordWrap(True)
            btn=QPushButton(); btn.setObjectName("SecondaryButton"); btn.clicked.connect(callback)
            box.addWidget(label); box.addWidget(text); box.addStretch(); box.addWidget(btn)
            self.grid.addWidget(card,i//2,i%2); self.buttons.append((key,label,text,btn))
        l.addStretch(); self.set_language(lang)

    def current_status(self):
        profile=Path("/etc/puresteel/profile").read_text().strip() if Path("/etc/puresteel/profile").exists() else "balanced"
        channel=Path("/etc/puresteel/channel").read_text().strip() if Path("/etc/puresteel/channel").exists() else "stable"
        hardware=Path("/etc/puresteel/hardware-mode").read_text().strip() if Path("/etc/puresteel/hardware-mode").exists() else "auto"
        return profile,channel,hardware

    def set_language(self,lang):
        self.lang=lang
        tr=lang=="tr"
        self.title.setText("Puresteel Sistemi" if tr else "Puresteel System")
        self.subtitle.setText("Puresteel'a özgü araçları, paketleri ve güvenli bakım özelliklerini yönet." if tr else "Manage Puresteel-specific tools, packs and safe maintenance features.")
        p,c,h=self.current_status(); self.status.setText((f"Profil: {p}   •   Kanal: {c}   •   Donanım modu: {h}" if tr else f"Profile: {p}   •   Channel: {c}   •   Hardware mode: {h}"))
        texts={
            "welcome":(("Hoş Geldin","Puresteel araçlarına ve belgelere ulaş."),("Welcome","Open Puresteel tools and documentation.")),
            "defaults":(("Varsayılanları Uygula","Puresteel tema, ikon ve Cinnamon tercihlerini uygula."),("Apply Defaults","Apply Puresteel theme, icon and Cinnamon defaults.")),
            "snapshot":(("Snapshot","Timeshift geri dönüş noktalarını yönet."),("Snapshots","Manage Timeshift restore points.")),
            "essentials":(("Essentials","Temel günlük uygulama paketini kur."),("Essentials","Install the everyday essentials pack.")),
            "creator":(("Creator Pack","Video, ses ve üretim araçlarını hazırla."),("Creator Pack","Prepare video, audio and creator tools.")),
            "developer":(("Developer Pack","Derleme ve geliştirme araçlarını kur."),("Developer Pack","Install development and build tools.")),
            "gaming":(("Gaming Pack","Steam, Wine, GameMode ve gaming araçlarını hazırla."),("Gaming Pack","Prepare Steam, Wine, GameMode and gaming tools.")),
            "safe_update":(("Güvenli Güncelle","Mümkünse snapshot al, sonra sistemi güncelle."),("Safe Update","Create a snapshot when possible, then update the system.")),
        }
        for key,label,text,btn in self.buttons:
            title,desc=texts[key][0 if tr else 1]; label.setText(title); text.setText(desc); btn.setText("Aç" if key in ("welcome","snapshot") and tr else "Open" if key in ("welcome","snapshot") else "Uygula" if tr else "Apply")

    def launch(self,cmd):
        try: subprocess.Popen([cmd])
        except OSError as exc: QMessageBox.warning(self,"Puresteel",str(exc))

    def pack(self,name):
        code,out=privileged("app-pack",name,timeout=3600)
        QMessageBox.information(self,"Puresteel",out[-5000:] or ("OK" if code==0 else "Failed"))

    def safe_update(self):
        code,out=privileged("safe-upgrade",timeout=7200)
        QMessageBox.information(self,"Puresteel",out[-5000:] or ("OK" if code==0 else "Failed"))
