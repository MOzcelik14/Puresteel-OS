<p align="center">
  <img src="config/includes.chroot/usr/share/pixmaps/puresteel-installer.png" width="128" alt="Puresteel logosu">
</p>

<h1 align="center">Puresteel</h1>

<p align="center">
  <a href="README.md">English</a> · <a href="README.tr.md">Türkçe</a> · <a href="https://mozcelik14.github.io/Puresteel-OS/">Web sitesi</a>
</p>

---

Puresteel; temiz bir masaüstü deneyimi, oyun ve içerik üretimi araçları, geniş ekran kartı desteği, grafiksel kurulum aracı ve kendi sistem yönetimi/güncelleme altyapısına odaklanan Debian 13 (Trixie) tabanlı bağımsız bir Linux dağıtımıdır. Güncel geliştirme hattı **Cinnamon + LightDM + Slick Greeter** kullanır.

**Mevcut kararlı sürüm: Puresteel 1.0 "Burak" (KDE Plasma).** Bir sonraki geliştirme sürümünde masaüstü Cinnamon'a taşınmaktadır.

## ISO'yu tek komutla oluştur

### Linux

Debian, Ubuntu veya Linux Mint benzeri APT tabanlı bir sistemde:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash
```

### Windows 10 / 11

PowerShell'de şunu çalıştır:

```powershell
irm https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/windows-build.ps1 | iex
```

Windows betiği WSL2 ve Debian/Ubuntu ortamını otomatik kullanır. WSL kurulu değilse ilk çalıştırma Windows'un WSL/Debian kurulumunu başlatır. Windows bir kez yeniden başlatma veya ilk Linux kullanıcısını oluşturma isteyebilir; sonrasında aynı komutu tekrar çalıştırman yeterlidir. Oluşan ISO ve SHA256 dosyası PowerShell'i açtığın Windows klasörüne kopyalanır.

Linux bootstrap betiği gerekli host araçlarını kurar, kararlı Puresteel kaynağını indirir, hybrid ISO'yu oluşturur ve ISO ile SHA256 dosyasını komutun çalıştırıldığı dizine bırakır.

Elle veya geliştirme amaçlı build için [docs/BUILD.md](docs/BUILD.md) belgesine bakabilirsiniz.

## Genel bakış

| | |
|---|---|
| **Taban** | Debian 13 (Trixie) |
| **Mimari** | amd64 + uyumluluk için i386 multiarch |
| **Masaüstü** | Geliştirme hattında Cinnamon / LightDM / Slick Greeter; kararlı 1.0'da KDE Plasma / SDDM |
| **Kurulum** | Calamares |
| **Init** | systemd |
| **Grafik** | Intel, AMD ve NVIDIA; hibrit GPU desteği |
| **Uygulamalar** | APT + Flatpak / Flathub |
| **Kabuk** | Fish + Starship |
| **Güncellemeler** | Debian APT + imzalı Puresteel APT deposu + Flatpak |

## Puresteel Center

Puresteel kendi Qt 6 / PySide6 sistem yönetim uygulamasıyla gelir. Günlük yönetim işlerini tek arayüzde toplar:

| Modül | İşlev |
|---|---|
| **Güncellemeler** | APT ve Flatpak güncellemelerini kontrol eder ve Polkit korumalı işlemlerle kurar |
| **Uygulamalar** | APT ve Flatpak yazılımlarını arar, kurar ve kaldırır |
| **Sürücüler** | Intel, AMD ve NVIDIA GPU'ları; kernel sürücülerini, firmware, DKMS, Vulkan ve VA-API durumunu gösterir |
| **Kaynaklar** | APT kaynaklarını gösterir, Flatpak remote'larını yönetir |
| **Yedekleme** | Kullanıcı verilerini, ayarları ve paket listelerini yedekler |
| **Sistem Raporları** | Kernel, disk, bellek, GPU, servis ve journal tanılama bilgilerini toplar |

Puresteel Center Türkçe ve İngilizce arayüz sunar ve ISO'dan bağımsız güncellenebilmesi için ayrı bir Debian paketi olarak dağıtılır.

[Puresteel Center dokümantasyonu →](docs/PURESTEEL_CENTER.md)

## Paket güncellemeleri

Puresteel'e ait paketler GitHub Pages üzerinde yayınlanan imzalı APT deposundan dağıtılır. ISO, o anki Puresteel paketlerini yerel olarak içerir; kurulu sistemler sonraki sürümleri normal APT güncellemeleriyle alır.

[Güncelleme ve depo dokümantasyonu →](docs/UPDATES.md)

## Grafik desteği

- **Intel** — Linux/Mesa yığını üzerinden entegre grafikler ve Arc sınıfı harici kartlar
- **AMD** — `amdgpu` / Mesa üzerinden entegre ve harici Radeon GPU'lar
- **NVIDIA** — Debian proprietary sürücü yığını, DKMS, Vulkan ve hibrit grafik desteği
- **Hibrit sistemler** — Intel + NVIDIA, AMD + NVIDIA ve Linux grafik yığınının desteklediği diğer çoklu GPU düzenleri

1.0 live imajı Intel + NVIDIA hibrit bir dizüstünde RTX 3050 ile test edilmiştir; live ortamda `nvidia-smi` başarılı şekilde çalışmıştır.

[Donanım dokümantasyonu →](docs/HARDWARE.md)

## Oyun ve içerik üretimi

Varsayılan imaj Steam, Wine, Winetricks, i386 multiarch, Vulkan kütüphaneleri, Heroic Games Launcher, ProtonUp-Qt, Kdenlive, Audacity, TubeConverter, ONLYOFFICE Desktop Editors, Zen Browser, VLC ve Audacious içerir. Flatpak uygulamaları sistem genelinde Flathub üzerinden kurulur.

## Power-user varsayılanları

Puresteel; Fish, Starship, Fastfetch, btop, htop, Git, curl, wget, Vim, Nano, fzf, ripgrep, fd-find, bat, tmux ve arşiv araçlarıyla gelir. ZRAM zstd sıkıştırmasıyla etkinleştirilmiştir ve Puresteel'e özgü bellek ayarları kullanılır.

## Masaüstü ve branding

Geliştirme hattı X11 üzerinde Cinnamon, LightDM/Slick Greeter, Puresteel duvar kağıdı varsayılanları, Puresteel uygulama menüsü ikonu ve Puresteel'e ait GRUB, Plymouth, ikon ve Calamares branding'ini kullanır. Kararlı 1.0 ise yayınlanmış KDE Plasma/SDDM sürümü olarak kalır.

## Kurulum

Oluşturulan hybrid ISO'yu USB belleğe yazın, UEFI modunda Puresteel live ortamını başlatın ve masaüstündeki Calamares kurucusunu açın.

[Kurulum rehberi →](docs/INSTALL.md)

## Dokümantasyon

- [Web sitesi](https://mozcelik14.github.io/Puresteel-OS/)
- [Kurulum](docs/INSTALL.md)
- [Puresteel build rehberi](docs/BUILD.md)
- [Puresteel Center](docs/PURESTEEL_CENTER.md)
- [Güncellemeler ve APT deposu](docs/UPDATES.md)
- [Donanım ve grafik](docs/HARDWARE.md)
- [Sorun giderme](docs/TROUBLESHOOTING.md)
- [Değişiklik günlüğü](CHANGELOG.md)
- [Sürüm notları](RELEASE_NOTES.md)

## Sürüm durumu

Puresteel 1.0 "Burak" ilk kararlı sürümdür ve `v1.0.0` etiketi üzerinden yeniden üretilebilir. 1.0 sonrasındaki geliştirme hattında masaüstü KDE Plasma'dan Cinnamon'a taşınmaktadır; Cinnamon hattı kendi kararlı sürümü yayınlanana kadar geliştirme sürümü olarak değerlendirilmelidir.

## Lisanslama

Puresteel farklı upstream lisanslara sahip yazılımları bir araya getirir. Debian paketleri, Flatpak uygulamaları ve üçüncü taraf bileşenler kendi lisanslarını korur. Yapılandırmaya bağlı olarak imaj Debian non-free firmware ve proprietary NVIDIA bileşenleri içerebilir.
