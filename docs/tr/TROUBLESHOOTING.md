# Puresteel sorun giderme

Bu sayfada canlı ISO, kurulu Puresteel ve proje paket/güncelleme altyapısı için temel denetimler bulunur.

## Puresteel Center açılmıyor

Terminalden başlat:

```bash
puresteel-center
```

Python/Qt hatası varsa paketin kurulu olduğunu kontrol et:

```bash
dpkg -l | grep puresteel-center
```

Dosyalarını listele:

```bash
dpkg -L puresteel-center
```

## Puresteel Center güncelleme göstermiyor

APT indeksini elle yenile:

```bash
sudo apt update
```

Ardından kaynak tanımına bak:

```bash
cat /etc/apt/sources.list.d/puresteel.sources
```

Depo adresi şu olmalı:

```text
https://mozcelik14.github.io/Puresteel-OS/apt
```

## Puresteel APT deposu hataları

Çevrimiçi imzalı metadata'yı kontrol et:

```bash
curl -I https://mozcelik14.github.io/Puresteel-OS/apt/dists/stable/InRelease
```

Kurulu açık anahtarın bulunduğunu doğrula:

```bash
ls -l /usr/share/keyrings/puresteel-archive-keyring.asc
```

Sorunu çözmek için imza doğrulamasını **kapatma**.

## NVIDIA yüklenmiyor

GPU ve etkin çekirdek sürücüsü:

```bash
lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'
```

DKMS durumu:

```bash
dkms status
```

Yüklü modüller:

```bash
lsmod | grep -E 'nvidia|nouveau'
```

Sürücünün kendisi:

```bash
nvidia-smi
```

Beklenmedik şekilde `nouveau` etkinse `/etc/modprobe.d/` içindeki Puresteel yapılandırmasını incele.

## AMD GPU sorunları

`amdgpu` veya `radeon` etkinliğini denetle:

```bash
lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'
lsmod | grep -E 'amdgpu|radeon'
```

Firmware ve grafik paketleri:

```bash
dpkg -l | grep -E 'firmware-amd-graphics|mesa-vulkan-drivers|mesa-va-drivers'
```

## Intel GPU sorunları

`i915` veya `xe` etkinliğini denetle:

```bash
lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'
lsmod | grep -E 'i915|xe'
```

Intel firmware paketleri:

```bash
dpkg -l | grep -E 'firmware-intel-graphics|firmware-intel-misc'
```

## Vulkan sorunları

```bash
vulkaninfo --summary
```

Steam/Wine için i386 mimarisini de kontrol et:

```bash
dpkg --print-foreign-architectures
```

Beklenen çıktıda şu bulunmalı:

```text
i386
```

## Flatpak sorunları

Tanımlı uzak depolar:

```bash
flatpak remotes
```

Kurulu uygulamalar:

```bash
flatpak list
```

Güncelleme:

```bash
flatpak update
```

## ZRAM ve bellek ayarları

```bash
zramctl
swapon --show
sysctl vm.swappiness
```

## Başarısız servisler

```bash
systemctl --failed
```

Bir servisin ayrıntılı günlüğü:

```bash
journalctl -u SERVICE_NAME -b
```

Açılıştaki son yüksek öncelikli hatalar:

```bash
journalctl -p 3 -b
```

## Calamares kurulumu başarısız oluyor

Mümkünse çıktıyı görebilmek için kurucuyu terminalden başlat. Şunları denetle:

- Canlı ortamın yeterli boş RAM'i var mı?
- Hedef disk görünüyor mu?
- Bilgisayar doğru UEFI/legacy modunda mı başlatıldı?
- Hedef dosya sistemi başka araç tarafından bağlı mı?

Disk bölümlerini değiştiren kurulumu tekrar denemeden önce önemli verilerini yedekle.

## ISO derlemesi başarısız oluyor

`build.log` dosyasının son satırlarını incele.

Yararlı sözdizimi denetimleri:

```bash
bash -n build.sh
bash -n scripts/build-center-package.sh
bash -n scripts/release-center.sh
```

Hata `puresteel-center` paketinden bahsediyorsa yerel .deb var mı bak:

```bash
ls -lh config/packages.chroot/puresteel-center_*.deb
```

Puresteel Center imaja yerel `.deb` üzerinden kurulmalıdır; ISO derlemesi çevrimiçi Puresteel deposuna ihtiyaç duymamalıdır.

## Rapor toplama

Puresteel Center → **Sistem Raporları**, sık kullanılan tanılama bilgilerini metin dosyası olarak üretebilir.

Elle hazırlanan rapora en azından ilgili komutların çıktılarını ekle:

```bash
cat /etc/os-release
uname -a
lspci -nnk
lsmod
dkms status
systemctl --failed
```

**Paylaşmadan önce çıktıdaki kullanıcı adı, SSID veya diğer kişisel bilgileri kontrol et.**
