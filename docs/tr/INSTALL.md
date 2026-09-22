# Puresteel kurulumu

> Geliştirme hattı: **Puresteel 1.0 "Burak"**  
> Taban: Debian 13 (Trixie) · Masaüstü: KDE Plasma · Kurucu: Calamares

Puresteel, hem canlı ortamı çalıştırabilen hem de sistemi kurabilen hibrit bir ISO olarak dağıtılır. USB'den başlatabilir, canlı masaüstünü deneyebilir ve Calamares ile diske kurabilirsin.

## Önerilen sistem gereksinimleri

- x86-64 işlemci
- En az 8 GB RAM
- En az 40 GB boş depolama
- UEFI destekli bilgisayar
- Önerilen: internet bağlantısı

Daha düşük donanımlı bilgisayarlar da açılabilir. Bu değerler KDE Plasma, Flatpak uygulamaları ve oyun/içerik üretimi işleri için ek alan bırakır.

## ISO'yu USB belleğe yazma

Ham disk imajı yazabilen bir araç kullan:

- GNOME Disks (Diskler)
- KDE ISO Image Writer
- Fedora Media Writer
- Balena Etcher
- DD modunda Rufus
- Linux üzerinde `dd`

Örnek:

```bash
sudo dd if=live-image-amd64.hybrid.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

`/dev/sdX` yerine `/dev/sdX1` gibi bir bölümü değil, **USB aygıtının tamamını** yaz.

> **Dikkat:** `dd` seçilen aygıtın içeriğini siler. Komutu çalıştırmadan önce hedef diski mutlaka doğrula.

## Canlı sistemi başlatma

1. USB'den UEFI modunda önyükleme yap.
2. Puresteel canlı ortamını başlat.
3. Klavye, ağ, görüntü ve sesin çalıştığını kontrol et.
4. Gerekiyorsa ekran kartının durumunu kurulumdan önce incele.
5. Masaüstünden veya uygulama menüsünden Puresteel kurucusunu aç.

## Calamares ile kurulum

Calamares şu adımlarda yardımcı olur:

- Dil ve bölgesel ayarlar
- Klavye düzeni
- Saat dilimi
- Disk bölümlendirme
- Kullanıcı hesabı oluşturma
- Önyükleyici kurulumu

Temiz kurulumda otomatik bölümlendirme daha kolaydır. Özel disk düzeni veya çoklu önyükleme için elle bölümlendirmeyi seçebilirsin.

**Disk bölümlerini değiştirmeden önce önemli dosyalarını yedekle.**

## Ekran kartı notları

Puresteel Intel, AMD ve NVIDIA sistemlerini destekleyecek şekilde hazırlanır.

### Intel

Intel entegre ve yeni nesil harici GPU'ları, ilgili firmware paketleriyle Linux çekirdeği ve Mesa grafik altyapısını kullanır.

### AMD

AMD APU ve harici Radeon kartlar, desteklenen donanımlarda ağırlıklı olarak `amdgpu` sürücüsünü ve çekirdek/Mesa altyapısını kullanır.

### NVIDIA

Puresteel, Debian'ın tescilli NVIDIA sürücü yığınını ve hibrit grafik bileşenlerini içerir.

NVIDIA donanımında açılıştan veya kurulumdan sonra sürücüyü kontrol et:

```bash
nvidia-smi
```

Daha ayrıntılı bilgi için **Puresteel Center → Sürücüler** bölümünü aç.

## Kurulumdan sonra

Yararlı kontroller:

```bash
cat /etc/os-release
uname -r
zramctl
swapon --show
sysctl vm.swappiness
flatpak list
dpkg --print-foreign-architectures
```

Puresteel APT deposunu denetle:

```bash
cat /etc/apt/sources.list.d/puresteel.sources
sudo apt update
```

Puresteel Center dâhil Puresteel'e ait paketler, **imzalı depoya daha yeni sürüm yayımlandığında**, normal APT güncellemeleriyle yükseltilir:

```bash
sudo apt full-upgrade
```

## Puresteel Center

Puresteel Center şu işlevler için grafiksel arayüz sağlar:

- Güncellemeler
- Uygulamalar
- Grafik donanımı ve sürücü durumu
- Yazılım kaynakları
- Yedekleme
- Sistem raporları

Ayrıntılar: [Puresteel Center](PURESTEEL_CENTER.md).

## Sorun giderme

Beklenmedik bir durum yaşarsan [Sorun giderme](TROUBLESHOOTING.md) rehberine bak.

Geliştirme aşamasındaki ISO'lara önemli işlerini emanet etmeden önce gerçek donanımda test yapman önerilir.
