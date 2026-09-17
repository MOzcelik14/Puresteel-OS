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
            ("snapshot", lambda:self.launch("puresteel-snapshots")),
            ("safe_update", self.safe_update),
            ("battery", lambda:self.launch_terminal("puresteel-battery")),
            ("firmware", lambda:self.launch_terminal("puresteel-firmware status")),
            ("health", lambda:self.launch_terminal("puresteel-health all")),
            ("logs", lambda:self.launch_terminal("puresteel-logs")),
            ("secureboot", lambda:self.launch_terminal("puresteel-secureboot status")),
            ("flatpak", self.flatpak_repair),
            ("kernel", lambda:self.launch_terminal("puresteel-kernel")),
            ("essentials", lambda:self.pack("essentials")),
            ("creator", lambda:self.pack("creator")),
            ("developer", lambda:self.pack("developer")),
            ("gaming", lambda:self.pack("gaming")),
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
        self.lang=lang; tr=lang=="tr"
        self.title.setText("Puresteel Sistemi" if tr else "Puresteel System")
        self.subtitle.setText("Puresteel'a özgü bakım, donanım ve güvenlik araçlarını yönet." if tr else "Manage Puresteel-specific maintenance, hardware and security tools.")
        p,c,h=self.current_status(); self.status.setText((f"Profil: {p}   •   Kanal: {c}   •   Donanım modu: {h}" if tr else f"Profile: {p}   •   Channel: {c}   •   Hardware mode: {h}"))
        texts={
            "welcome":(("Hoş Geldin","Puresteel araçları ve belgeleri."),("Welcome","Puresteel tools and documentation.")),
            "snapshot":(("Snapshot","Timeshift geri dönüş noktalarını yönet."),("Snapshots","Manage Timeshift restore points.")),
            "safe_update":(("Güvenli Güncelle","Snapshot alıp sistemi güncelle."),("Safe Update","Snapshot, then update the system.")),
            "battery":(("Pil Sağlığı","Kapasite, döngü ve güç profilini göster."),("Battery Health","Show capacity, cycles and power profile.")),
            "firmware":(("Firmware","fwupd cihaz ve firmware durumunu göster."),("Firmware","Show fwupd device and firmware state.")),
            "health":(("Sistem Sağlığı","Gaming ve Creator bağımlılıklarını test et."),("System Health","Test Gaming and Creator dependencies.")),
            "logs":(("Loglar","Boot, DKMS, ağ ve LightDM loglarını topla."),("Logs","Collect boot, DKMS, network and LightDM logs.")),
            "secureboot":(("Secure Boot","Secure Boot, MOK ve DKMS durumunu göster."),("Secure Boot","Show Secure Boot, MOK and DKMS state.")),
            "flatpak":(("Flatpak Onar","Sistem Flatpak kurulumunu doğrula ve temizle."),("Repair Flatpak","Repair and clean the system Flatpak installation.")),
            "kernel":(("Kernel","Çalışan ve alternatif kernelleri göster."),("Kernel","Show running and alternate kernels.")),
            "essentials":(("Essentials","Temel günlük uygulama paketini kur."),("Essentials","Install everyday essentials.")),
            "creator":(("Creator Pack","Video, ses ve üretim araçlarını hazırla."),("Creator Pack","Prepare creator tools.")),
            "developer":(("Developer Pack","Derleme ve geliştirme araçlarını kur."),("Developer Pack","Install developer tools.")),
            "gaming":(("Gaming Pack","Steam, Wine ve gaming araçlarını hazırla."),("Gaming Pack","Prepare gaming tools.")),
        }
        for key,label,text,btn in self.buttons:
            title,desc=texts[key][0 if tr else 1]; label.setText(title); text.setText(desc)
            btn.setText("Aç" if tr and key not in ("safe_update","flatpak","essentials","creator","developer","gaming") else "Open" if not tr and key not in ("safe_update","flatpak","essentials","creator","developer","gaming") else "Uygula" if tr else "Apply")

    def launch(self,cmd):
        try: subprocess.Popen([cmd])
        except OSError as exc: QMessageBox.warning(self,"Puresteel",str(exc))

    def launch_terminal(self,command):
        try: subprocess.Popen(["gnome-terminal","--","sh","-lc",command+"; printf '\nEnter ile kapat...'; read x"])
        except OSError as exc: QMessageBox.warning(self,"Puresteel",str(exc))

    def pack(self,name):
        code,out=privileged("app-pack",name,timeout=3600); QMessageBox.information(self,"Puresteel",out[-5000:] or ("OK" if code==0 else "Failed"))

    def safe_update(self):
        code,out=privileged("safe-upgrade",timeout=7200); QMessageBox.information(self,"Puresteel",out[-5000:] or ("OK" if code==0 else "Failed"))

    def flatpak_repair(self):
        code,out=privileged("flatpak-repair",timeout=3600); QMessageBox.information(self,"Puresteel",out[-5000:] or ("OK" if code==0 else "Failed"))
