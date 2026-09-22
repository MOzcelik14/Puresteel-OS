# Puresteel Center

Puresteel Center, dağıtımın Qt 6 / PySide6 tabanlı sistem yönetimi uygulamasıdır. Amaç, günlük sistem bakım araçlarını ayrı ayrı uygulamalara dağıtmak yerine tek bir arayüzde toplamaktır.

## Modüller

### Ana sayfa

Sık kullanılan işlemlere hızlı erişim ve salt-okunur bir rolling sürüm paneli sunar. Panelde kurulu Center sürümü, yerel APT önbelleğindeki aday sürüm, çekirdek ve kaynak/imza anahtarı dosyalarının durumu görünür. Bu kontrol canlı paket indeksini indirmez ve güncelleme kurmaz.

### Güncellemeler

- Puresteel'e ait imzalı APT güncellemelerini Debian paketlerinden ayırır
- APT güncellemelerini denetler
- Flatpak güncellemelerini denetler
- Yetkili yardımcı üzerinden sistem paketi güncellemelerini kurabilir
- Grafiksel arayüz root olarak çalışmaz

### Uygulamalar

- APT kataloğunda arama
- Flatpak araması
- Uygulama kurma ve kaldırma
- İki paket ekosistemini bir arayüzde sunma

### Sürücüler

Sürücüler sayfası tek bir üreticiyle sınırlı değildir: **Intel, AMD ve NVIDIA** için tasarlanmıştır.

İnceleyebildiği bilgiler:

- Algılanan GPU'lar
- Etkin çekirdek sürücüsü
- Kullanılabilir çekirdek modülleri
- NVIDIA sürücü durumu / `nvidia-smi`
- DKMS durumu
- `nouveau` durumu
- `switcheroo-control`
- Grafik firmware paketleri
- Vulkan erişilebilirliği
- VA-API erişilebilirliği

Intel/AMD tarafı genellikle çekirdek + firmware + Mesa bütünüdür; NVIDIA'nın tescilli sürücüleri ayrıca yönetilir.

### Yazılım kaynakları

- APT kaynak dosyalarını görüntüler
- Flatpak uzak depolarını listeler
- Kullanıcının Flatpak uzak depolarını ekler/kaldırır

Yanlış bir işlemle paket yöneticisinin bozulmasını önlemek için sistem APT kaynak dosyalarının düzenlenmesi özellikle kısıtlı tutulur.

### Yedekleme

Seçilen kullanıcı dosyalarını ve sistem/paket bilgilerini arşivleyebilir:

- Belgeler
- Resimler
- Müzik
- `.config`
- Elle kurulmuş APT paketlerinin listesi
- Kurulu Flatpak uygulamalarının listesi

### Sistem Raporları

Sorun giderme için şu tür bilgileri toplayabilir:

- Çekirdek ve işletim sistemi
- Bellek kullanımı
- Dosya sistemi kullanımı
- PCI grafik aygıtları
- NVIDIA ve DKMS durumu
- Başarısız systemd servisleri
- Son journal hataları

Raporlar hata ayıklama veya issue açma amacıyla metin dosyasına kaydedilebilir. Paylaşmadan önce içeriği denetle.

## Diller

Arayüzün desteklediği diller:

- Türkçe
- İngilizce

Dil tercihi Qt ayarlarında saklanır ve sonraki açılışta geri yüklenir.

## Yetki modeli

Puresteel Center grafiksel arayüzünün tamamı **root olarak çalışmaz**.

Yetkili işlemler şu akışla yapılır:

```text
Puresteel Center arayüzü
        │
        ▼
      pkexec
        │
        ▼
Polkit yetkilendirmesi
        │
        ▼
/usr/lib/puresteel-center/puresteel-helper
        │
        ├── apt upgrade
        ├── apt install/remove
        └── grafik sürücüsü onarma
```

Yardımcı program rastgele kabuk komutları değil, önceden tanımlı sınırlı eylemler kabul eder.

Paketteki önemli dosyalar:

```text
/usr/bin/puresteel-center
/usr/share/puresteel-center/
/usr/lib/puresteel-center/puresteel-helper
/usr/share/polkit-1/actions/org.puresteel.center.policy
/usr/share/applications/puresteel-center.desktop
```

## Paketleme

Puresteel Center Debian paket kaynakları:

```text
packages/puresteel-center/
```

Temel sürüm `2.0.0-1`'dir. İmzalı otomatik yayınlar sürüme commit damgalı `+git` eki koyar. Kurulu Center gerçek paket sürümünü kendi dosyasından okur.

Temel sürüm dosyası:

```text
packages/puresteel-center/VERSION
```

Yayımlamadan paket oluştur:

```bash
./scripts/build-center-package.sh
```

Puresteel APT deposuna yeni sürüm hazırlama:

```bash
./scripts/release-center.sh 2.0.0-1
```

Bu betik **orijinal Puresteel özel APT imza anahtarına** ihtiyaç duyar. Center ve bileşen paketlerini yeniden oluşturur, APT deposunu imzalar ve yeni ISO'larda çevrimdışı kurulabilmeleri için güncel `.deb` dosyalarını `config/packages.chroot/` içine hazırlar. Ayrı imzalı yayın yapılana kadar çevrimiçi depo eski paketleri gösterebilir. İmzasız metadata yayımlama.

## Kurulu sistemleri güncelleme

İmzalı Puresteel deposunda daha yeni paket yayımlandığında kurulu sistemler normal APT akışıyla yükseltir:

```bash
sudo apt update
sudo apt full-upgrade
```

Puresteel Center'ı güncellemek için yeni bir ISO indirmen gerekmez.

## Geliştirme durumu

Center geliştirme aşamasındadır. Nihai sürümden önce yetkili paket işlemleri, yedekleme, grafik yönetimi ve paket yöneticisi sınır durumları hem canlı ortamda hem de kurulu gerçek sistemlerde test edilmelidir.
