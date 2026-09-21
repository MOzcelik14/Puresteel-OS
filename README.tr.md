<p align="center">
  <img src="config/includes.chroot/usr/share/pixmaps/puresteel-installer.png" width="128" alt="Puresteel logosu">
</p>

<h1 align="center">Puresteel</h1>

<p align="center">
  <a href="README.md">English</a> · <a href="README.tr.md">Türkçe</a> · <a href="https://mozcelik14.github.io/Puresteel-OS/">Web sitesi</a>
</p>

---

Puresteel; temiz bir masaüstü deneyimi, oyun ve içerik üretimi araçları, geniş ekran kartı desteği, grafiksel kurulum aracı ve kendi sistem yönetimi/güncelleme altyapısına odaklanan Debian 13 (Trixie) tabanlı bağımsız bir Linux dağıtımıdır.

Puresteel'in güncel masaüstü yığını **minimal KDE Plasma 6 + SDDM + Wayland** şeklindedir. `kde-standard` veya `kde-full` kurulmaz; yalnızca Plasma masaüstü, temel ayarlar, Dolphin, Konsole, ağ, güç/ekran bileşenleri ve Puresteel araçları seçilir.

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

Windows betiği WSL2 ve Debian/Ubuntu ortamını otomatik kullanır. WSL kurulu değilse ilk çalıştırma Windows'un WSL/Debian kurulumunu başlatır. Windows bir kez yeniden başlatma veya ilk Linux kullanıcısını oluşturma isteyebilir; sonrasında aynı komutu tekrar çalıştırmanız yeterlidir.

Elle veya geliştirme amaçlı build için [docs/BUILD.md](docs/BUILD.md) belgesine bakabilirsiniz.

## Genel bakış

| | |
|---|---|
| **Taban** | Debian 13 (Trixie) |
| **Mimari** | amd64 + i386 multiarch |
| **Masaüstü** | KDE Plasma 6 / SDDM / Wayland |
| **Kurulum** | Calamares |
| **Init** | systemd |
| **Grafik** | Intel, AMD ve NVIDIA; hibrit GPU desteği |
| **Uygulamalar** | APT + Flatpak / Flathub |
| **Kabuk** | Fish + Starship |
| **Güncellemeler** | Debian APT + imzalı Puresteel APT deposu + Flatpak |

## Puresteel Center

Puresteel kendi Qt 6 / PySide6 sistem yönetim uygulamasıyla gelir. Güncellemeler, uygulamalar, sürücüler, kaynaklar, yedekleme ve sistem raporlarını tek arayüzde toplar. Türkçe ve İngilizce arayüz desteklenir.

[Puresteel Center dokümantasyonu →](docs/PURESTEEL_CENTER.md)

## Grafik desteği

- **Intel** — Linux/Mesa üzerinden entegre grafikler ve Arc sınıfı harici kartlar
- **AMD** — `amdgpu` / Mesa üzerinden entegre ve harici Radeon GPU'lar
- **NVIDIA** — Debian proprietary sürücü yığını, DKMS, Vulkan ve hibrit grafik entegrasyonu
- **Hibrit sistemler** — Intel + NVIDIA, AMD + NVIDIA ve Linux grafik yığınının desteklediği diğer çoklu GPU düzenleri

KDE Plasma live ortamı Intel + NVIDIA hibrit bir dizüstünde RTX 3050 ile test edilmiştir; `nvidia-smi` başarılı şekilde çalışmıştır.

[Donanım dokümantasyonu →](docs/HARDWARE.md)

## Oyun ve içerik üretimi

Varsayılan imaj Steam, Wine, Winetricks, i386 multiarch, Vulkan kütüphaneleri, Heroic Games Launcher, ProtonUp-Qt, Kdenlive, Audacity, TubeConverter, ONLYOFFICE Desktop Editors, Zen Browser, VLC ve Audacious içerir. Flatpak uygulamaları sistem genelinde Flathub üzerinden kurulur.

## Power-user varsayılanları

Puresteel; Fish, Starship, Fastfetch, btop, htop, Git, curl, wget, Vim, Nano, fzf, ripgrep, fd-find, bat, tmux ve arşiv araçlarıyla gelir. ZRAM zstd sıkıştırmasıyla etkinleştirilmiştir ve Puresteel'e özgü bellek ayarları kullanılır.

## Masaüstü ve branding

Puresteel Wayland üzerinde minimal KDE Plasma 6 ve SDDM, Puresteel duvar kağıdı varsayılanları, Breeze Light varsayılanları ve Puresteel masaüstü branding'i ve Puresteel'e ait GRUB, Plymouth, ikon ve Calamares branding'ini kullanır. Sistem dili Puresteel Language Settings üzerinden değiştirilebilir.

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

## Sürüm geçmişi

Yayınlanmış `v1.0.0` etiketi, ilk Puresteel 1.0 "Burak" sürümünün tarihsel kaydı olarak korunur. Güncel geliştirme hattı minimal KDE Plasma 6 kullanır ve eski sürüm geçmişi yeniden yazılmaz.

## Lisanslama

Puresteel farklı upstream lisanslara sahip yazılımları bir araya getirir. Debian paketleri, Flatpak uygulamaları ve üçüncü taraf bileşenler kendi lisanslarını korur. Yapılandırmaya bağlı olarak imaj Debian non-free firmware ve proprietary NVIDIA bileşenleri içerebilir.


### KDE Wallet ve Wi-Fi

Puresteel, Debian'ın `libpam-kwallet5` PAM entegrasyonunu kurar ve SDDM'de parola ile oturum açmayı varsayılan yapar. Böylece şifreli `kdewallet` giriş parolasıyla açılır ve Plasma NetworkManager kayıtlı Wi-Fi parolasını her yeniden başlatmada tekrar sormaz. Otomatik giriş, PAM'in wallet'ı açmak için kullanacağı bir giriş parolası olmadığı için kurucuda varsayılan olarak gizlenir. citeturn943285search5turn542915search1
