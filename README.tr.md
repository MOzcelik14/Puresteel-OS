<p align="center">
  <img src="config/includes.chroot/usr/share/pixmaps/puresteel-installer.png" width="128" alt="Puresteel logosu">
</p>

<h1 align="center">Puresteel</h1>

<p align="center">
  Debian 13 · KDE Plasma · amd64 · Intel / AMD / NVIDIA · Flatpak · Steam / Wine
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README.tr.md">Türkçe</a> · <a href="https://mozcelik14.github.io/Puresteel-OS/">Dokümantasyon</a>
</p>

---

Puresteel; KDE Plasma merkezli, Debian 13 (Trixie) tabanlı bağımsız bir Linux dağıtımıdır. Temiz bir masaüstü deneyimini; oyun, içerik üretimi, geniş ekran kartı desteği, grafiksel kurulum aracı ve Puresteel'e ait sistem yönetimi/güncelleme altyapısıyla birleştirir.

Mevcut geliştirme hedefi **Puresteel 1.0 "Burak"** sürümüdür.

## Genel bakış

| | |
|---|---|
| **Taban** | Debian 13 (Trixie) |
| **Mimari** | amd64 + uyumluluk için i386 multiarch |
| **Masaüstü** | KDE Plasma / SDDM / Breeze Dark |
| **Kurulum** | Calamares |
| **Init** | systemd |
| **Grafik** | Intel, AMD ve NVIDIA; hibrit GPU desteği |
| **Uygulamalar** | APT + Flatpak / Flathub |
| **Kabuk** | Fish + Starship |
| **Güncellemeler** | Debian APT + imzalı Puresteel APT deposu + Flatpak |

## Puresteel'i farklı kılanlar

### Puresteel Center

Puresteel kendi Qt 6 / PySide6 sistem yönetim uygulamasıyla gelir. Dağıtımın günlük yönetim işlerini tek arayüzde toplar:

| Modül | İşlev |
|---|---|
| **Güncellemeler** | APT ve Flatpak güncellemelerini denetler; sistem güncellemelerini Polkit üzerinden kurar |
| **Uygulamalar** | APT ve Flatpak yazılımlarını arar, kurar ve kaldırır |
| **Sürücüler** | Intel, AMD ve NVIDIA GPU'ları; kernel sürücülerini, firmware, DKMS, Vulkan ve VA-API durumunu gösterir |
| **Kaynaklar** | APT kaynaklarını gösterir, Flatpak remote'larını yönetir |
| **Yedekleme** | Kullanıcı verilerini, ayarları ve paket listelerini yedekler |
| **Sistem Raporları** | Kernel, disk, bellek, GPU, servis ve journal tanılama bilgilerini toplar |

Puresteel Center **Türkçe ve İngilizce** arayüz sunar ve ISO'dan bağımsız güncellenebilmesi için normal bir Debian paketi olarak paketlenir.

[Puresteel Center dokümantasyonu →](docs/PURESTEEL_CENTER.md)

### İmzalı Puresteel paket deposu

Puresteel'e ait paketler GitHub Pages üzerinde yayınlanan imzalı bir APT deposundan dağıtılır. ISO, o anki Puresteel paketlerini yerel `.deb` olarak içerir; kurulu sistemler sonraki sürümleri normal APT güncellemeleriyle alır.

```text
Puresteel kaynak kodu
      │
      ├── .deb oluştur
      │
      ├── imzalı Puresteel APT deposu
      │          │
      │          └── apt update / apt full-upgrade
      │
      └── ISO build → mevcut .deb ISO'ya gömülür
```

[Güncelleme ve paket deposu dokümantasyonu →](docs/UPDATES.md)

### Grafik desteği

Puresteel tek bir GPU üreticisine bağlı değildir.

- **Intel** — entegre grafikler ve Arc sınıfı harici ekran kartları
- **AMD** — entegre Radeon grafikler ve harici Radeon GPU'lar
- **NVIDIA** — Debian proprietary sürücü yığını, DKMS, Vulkan ve hibrit grafik desteği
- **Hibrit sistemler** — Intel + NVIDIA, AMD + NVIDIA ve çoklu GPU düzenleri

[Donanım dokümantasyonu →](docs/HARDWARE.md)

### Oyun ve içerik üretimi

Varsayılan imaj Linux oyun ve medya üretimi için gerekli temelleri içerir:

- Steam
- Wine / Wine64 / Wine32
- Winetricks
- i386 multiarch ve 32-bit Vulkan kütüphaneleri
- Heroic Games Launcher
- ProtonUp-Qt
- Kdenlive
- Audacity
- TubeConverter
- ONLYOFFICE Desktop Editors
- Zen Browser
- VLC ve Audacious

Flatpak uygulamaları sistem genelinde Flathub üzerinden kurulur.

### Power-user varsayılanları

Puresteel; Fish, Starship, Fastfetch, btop, htop, Git, curl, wget, Vim, Nano, fzf, ripgrep, fd-find, bat, tmux ve arşiv araçlarıyla gelir. ZRAM zstd sıkıştırmasıyla etkinleştirilmiştir ve sistem Puresteel'e özgü performans varsayılanları kullanır.

## Masaüstü ve branding

Puresteel boot'tan masaüstüne kadar tutarlı koyu bir görsel kimlik kullanır:

- özel GRUB görseli
- Puresteel Plymouth açılış animasyonu
- Puresteel SDDM arka planı
- Puresteel duvar kağıdı
- Breeze Dark varsayılanları
- Puresteel ikon özelleştirmeleri
- Puresteel branding'li Calamares

## Kaynak koddan build

Puresteel Debian `live-build` kullanır.

```bash
git clone https://github.com/MOzcelik14/Puresteel-OS.git
cd Puresteel-OS
./build.sh
```

Build almadan önce güncel bir `live-build` ve gerekli host araçlarının kurulu olması gerekir.

[Ayrıntılı build rehberi →](docs/BUILD.md)

## Kurulum

Oluşturulan hybrid ISO'yu USB belleğe yazın, UEFI modunda Puresteel live ortamını başlatın ve masaüstündeki Calamares kurucusunu açın.

[Kurulum rehberi →](docs/INSTALL.md)

## Dokümantasyon

- [Kurulum](docs/INSTALL.md)
- [Puresteel build rehberi](docs/BUILD.md)
- [Puresteel Center](docs/PURESTEEL_CENTER.md)
- [Güncellemeler ve APT deposu](docs/UPDATES.md)
- [Donanım ve grafik](docs/HARDWARE.md)
- [Sorun giderme](docs/TROUBLESHOOTING.md)
- [Değişiklik günlüğü](CHANGELOG.md)
- [Geliştirme notları](RELEASE_NOTES.md)

## Proje durumu

Puresteel aktif geliştirme aşamasındadır. Repo, 1.0 "Burak" geliştirme hattını takip eder; final sürüm açıkça yayınlanana kadar test imajları pre-release olarak değerlendirilmelidir.

Özellikle kurulum, suspend/resume, Wi-Fi, ses, çoklu monitör, hibrit grafik ve oyun iş yüklerinde gerçek donanım testleri değerlidir.

## Lisanslama

Puresteel farklı upstream lisanslara sahip yazılımları bir araya getirir. Debian paketleri, Flatpak uygulamaları ve üçüncü taraf bileşenler kendi lisanslarını korur. Yapılandırmaya bağlı olarak imaj Debian non-free firmware ve proprietary NVIDIA bileşenleri içerebilir.
