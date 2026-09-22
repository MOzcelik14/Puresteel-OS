# Puresteel ISO oluşturma

Puresteel, Debian `live-build` kullanarak amd64 hibrit ISO üretir.

## Tek komutla derleme

### Linux

Debian, Ubuntu veya Linux Mint benzeri APT tabanlı sistemde:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash
```

### Windows 10 / 11

PowerShell'de çalıştır:

```powershell
irm https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/windows-build.ps1 | iex
```

Windows yardımcısı WSL2 kullanır. PowerShell sözdizimi GitHub'ın Windows CI ortamında kontrol edilir. Mevcut Debian/Ubuntu WSL dağıtımını bulup hazırlar; yoksa Debian WSL kurulumunu başlatır. Windows bir kez yeniden başlatılmayı veya Linux kullanıcısı oluşturulmasını isteyebilir. Ardından aynı komutu tekrar çalıştır.

Gerçek ISO derlemesi güvenilirlik ve hız için WSL içindeki Linux dosya sisteminde yapılır. Son ISO ile SHA256, PowerShell'in başlatıldığı Windows klasörüne kopyalanır.

Linux derleyicisi varsayılan olarak etkileşimli terminal menüsü açar. Bu menüden ISO oluşturabilir, Git ref'ini, dosya adını veya çıktı klasörünü değiştirebilir, ayrıntılı günlükleri açabilir, gereksinimleri denetleyebilir, önceki günlükleri görebilir ya da çıkabilirsin. `whiptail` zaten kuruluysa ok tuşlu pencere kullanılır; değilse ek bağımlılık istemeyen numaralı Bash menüsü açılır. Menü girdileri `/dev/tty` üzerinden geldiği için normal `curl | bash` komutu etkileşimli çalışır. Windows/WSL, otomatik derleme için özellikle `--build` gönderir.

**sudo kullanmadan veya dosya yazmadan** menünün önizlemesi:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash -s -- --preview-menu
```

Terminal olmadan (betik, CI) derlemek için açıkça `--build` kullan:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash -s -- --build
```

Numaralı menü için `--text-menu`, salt-okunur sistem denetimi için `--check`, mevcut beş derleme aşamasının önizlemesi için `--preview` kullanabilirsin. Çıkış veya iptal seçimi derlemeyi başlatmaz.

**Önemli:** `curl` ile çağrılan betik, mevcut bilgisayara Puresteel kurmaz; kurulabilir bir ISO oluşturur.

Derleyici her çalıştırma için `~/.cache/puresteel-builder/run.XXXXXXXX/source` altında ayrı bir kaynak klasörü oluşturur. **Kullanıcının seçtiği mevcut bir klasörü özyinelemeli olarak silmez** ve önceki derlemeden kalan root sahipli dosyaları yeniden kullanmaya çalışmaz. Eski `run.*` klasörleri hata günlükleri için bırakılır ve disk alanı tüketir. Artık ihtiyacın olmadığına emin olduğun belirli eski klasörleri kendin silebilirsin.

Özel `PURESTEEL_WORKDIR` konumları kullanıcının ev dizinindeki `.cache` altında olmalıdır. ISO ve günlük, varsayılan olarak komutu çalıştırdığın çıktı dizinine yazılır.

Linux bootstrap betiği:

1. `sudo` ve kullanılabilir disk alanını denetler.
2. Gerekli host derleme bağımlılıklarını kurar.
3. Host'ta `live-build` eksik veya eskiyse güncel Debian Live Team sürümünü kurar.
4. Seçilen Puresteel kaynak sürümünü getirir.
5. ISO'yu oluşturur.
6. ISO ve SHA256 dosyasını başlatıldığı klasöre yazar.

Beklenen çıktı:

```text
Puresteel-Plasma-amd64.iso
Puresteel-Plasma-amd64.iso.sha256
```

Linux derleyicisi beş aşamalı Puresteel terminal arayüzü gösterir. Bütün APT, Git ve live-build çıktısı ISO yanında `puresteel-bootstrap.log` dosyasına kaydedilir. Ayrıntılı live-build çıktısı çalışma klasöründe `build.log` olarak da bulunur. Hata durumunda son günlük satırları gösterilir; tüm süreci canlı izlemek için `--verbose` kullan.

**sudo çağırmadan, paket kurmadan, kaynak klonlamadan ve ISO oluşturmadan** terminal görünümü önizlemesi:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash -s -- --preview
```

Gerçek derlemede ayrıntılı çıktı:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash -s -- --verbose
```

Derleyici mevcut bilgisayara Puresteel kurmaz; önyüklenebilir kurulum ISO'su üretir. ANSI renkleri yalnızca terminalde kullanılır; `NO_COLOR=1` ile kapatılabilir.

Varsayılan olarak `main` dalındaki tam donanımlı rolling Plasma sürümü derlenir. Belirli bir etiket/dal için:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | PURESTEEL_REF=v1.0.0 bash
```

## Tam donanımlı Plasma imajı

Varsayılan ISO'da Steam başlatıcısı ve kontrolcü kuralları, 32/64-bit Wine, 32-bit Vulkan/Mesa/NVIDIA kullanıcı alanı, GameMode/MangoHud, Heroic Games Launcher, ProtonUp-Qt ve ONLYOFFICE (gerekli runtime'larıyla sistem Flatpak'leri), Kdenlive, Audacity, FFmpeg ve C/C++/Python geliştirici araçları bulunur.

Steam'in upstream istemcisi ilk açılışta kendi güncellemelerini indirmek isteyebilir. Oyunlar, Proton çalıştırıcıları ve tescilli içerikler ISO'ya gömülmez. ISO derlenirken Heroic/diğer Flatpak'ler Flathub üzerinden kurulduğu için Debian yansılarının yanında Flathub erişimi de gerekir.

Bu tam sürüm, önceki 2,5 GB minimal ISO'dan daha çok disk alanı ve daha uzun GitHub Actions çalışma süresi ister. Son ISO boyutu ilgili derlemenin sonucuna bağlıdır.

## Otomatik rolling ISO

`main` dalına her push kod ve paket kontrollerini, ardından ISO derlemesini ve statik smoke testini başlatır. GitHub Actions artifact'leri 7 gün saklanır. Cloudflare R2 yapılandırılmışsa başarılı testten sonra aynı iş `Puresteel-Latest.iso`, SHA256 ve JSON bilgisini herkese açık bucket'a yükler. Başarısız derleme önceki yayımlanmış ISO'yu bilerek silmez.

Kurulum ISO'su üretmek ile kurulu sistemi güncellemek arasındaki farklar, sınırlar ve altyapı için [Rolling ISO](ROLLING.md) rehberine bak.

## Elle Linux derlemesi

Ortak bağımlılıkları kur:

```bash
sudo apt update
sudo apt install -y \
  git curl wget ca-certificates gnupg po4a \
  dpkg-dev apt-utils debootstrap debian-archive-keyring \
  squashfs-tools xorriso isolinux syslinux syslinux-common \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools rsync \
  make python3 qemu-system-x86 ovmf
```

Puresteel güncel `live-build` gerektirir. Dağıtımın eski sürümü sunuyorsa Debian Live Team'in Salsa sürümünü kur:

```bash
sudo apt remove -y live-build || true
rm -rf /tmp/live-build
git clone https://salsa.debian.org/live-team/live-build.git /tmp/live-build
sudo make -C /tmp/live-build install
```

Doğrula:

```bash
which lb
lb --version
```

Puresteel'i klonla:

```bash
git clone https://github.com/MOzcelik14/Puresteel-OS.git
cd Puresteel-OS
```

Derle:

```bash
./build.sh
```

Derleme betiği eski live-build durumunu temizler, yapılandırmayı yeniden üretir, Puresteel GRUB temasını geri koyar, güncel Puresteel Center `.deb` paketini oluşturup `config/packages.chroot/` içine ekler ve `build.log` tutarak hibrit ISO'yu oluşturur.

Canlı açılış parametreleri:

```text
boot=live components quiet splash username=puresteel hostname=puresteel
```

## ISO derlemelerinde Puresteel paketleri

Puresteel'e ait paketler `config/packages.chroot/` üzerinden ISO'ya eklenir; böylece ISO oluşturma çevrimiçi Puresteel APT deposundan bağımsızdır. Kurulu makineler sonraki Puresteel paketlerini imzalı depodan alır.

Örnek:

```text
config/packages.chroot/
└── puresteel-center_<current-version>_all.deb
```

## Puresteel Center paketi

Yayımlamadan güncel Center paketini üret:

```bash
./scripts/build-center-package.sh
```

Center ve APT deposu için yeni sürüm hazırla:

```bash
./scripts/release-center.sh 2.0.0-1
```

Kaynak paket temel sürümü `2.0.0-1`'dir. Ayrı bir imzalı yayın yapılana kadar çevrimiçi depo eski `1.0.1-1` Center paketini gösterebilir. ISO derlemesi kendi başına APT paketi yayımlamaz. Güncelleme yayımlamadan önce [Güncellemeler / APT deposu](UPDATES.md) belgesini oku.

## ISO'yu QEMU'da test et

UEFI/KVM örneği:

```bash
qemu-system-x86_64 \
  -enable-kvm \
  -m 8G \
  -smp 8 \
  -cpu host \
  -bios /usr/share/ovmf/OVMF.fd \
  -cdrom live-image-amd64.hybrid.iso \
  -boot d
```

Sanal makineler önyükleme, masaüstü, Calamares ve temel uygulama testleri için yararlıdır. GPU, Wi-Fi, uyku/uyanma, ses ve oyunlar için gerçek donanım da önemlidir.

Puresteel 1.0 canlı ortamı, NVIDIA sürücüsü dâhil Intel + NVIDIA RTX 3050 hibrit dizüstünde test edilmiştir. Bu geçmiş test, sonraki tüm rolling ISO'ların aynı donanımda doğrulandığı anlamına gelmez.

## İmza anahtarı

Puresteel APT deposu özel bir GPG anahtarıyla imzalanır. Özel anahtar Git'te saklanmaz.

Yeni geliştirme bilgisayarına geçerken yedeklediğin **mevcut** özel anahtarı içeri aktar:

```bash
gpg --import Puresteel-APT-PRIVATE-KEY.asc
gpg --list-secret-keys
```

Özel imza anahtarını asla repoya commit etme.

## Push öncesi

Yararlı kontroller:

```bash
git status
bash -n build.sh
bash -n bootstrap.sh
bash -n scripts/build-center-package.sh
bash -n scripts/release-center.sh
```

Puresteel Center Python kaynakları:

```bash
python3 -m compileall -q packages/puresteel-center/rootfs/usr/share/puresteel-center
```

## İlgili belgeler

- [Kurulum](INSTALL.md)
- [Puresteel Center](PURESTEEL_CENTER.md)
- [Güncellemeler / paket deposu](UPDATES.md)
- [Donanım](HARDWARE.md)
- [Sorun giderme](TROUBLESHOOTING.md)
