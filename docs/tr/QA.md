# Puresteel ISO entegrasyon ve kalite kontrolü

Bu belge bir **yayın kontrolüdür**; testlerin yapıldığı varsayımı değildir. Yeni bir Plasma ISO'sunu tam doğrulanmış diye duyurmadan önce taze ISO oluşturulmalı ve aşağıdaki testler belgelenmelidir. Kod veya paket CI'sinin başarılı olması, kurulu sistemin açıldığını kanıtlamaz.

## Güncel doğrulama kapsamı

Kod/paket CI'si ve salt-okunur terminal menüsü testleri, tek başına kurulumu test edilmiş Plasma sürümü anlamına gelmez. Statik ISO smoke testi; tam donanımlı APT paketlerini, i386 sürücülerini, Heroic/ProtonUp-Qt/ONLYOFFICE sistem Flatpak'lerini denetler. Bu, **otomatik Calamares GUI kurulumu değildir**.

Smoke testi `main` dalına her push'tan sonra ve gecelik olarak, kod/paket/Windows CI denetimlerinin ardından çalışır. `workflow_dispatch` ile elle de başlatılabilir. Aşağıdaki QEMU ve fiziksel donanım onay kutuları, sadece gerçekten kaydedilmiş test kanıtı varsa işaretlenmelidir.

## Otomatik statik kontroller

```sh
python3 -m unittest discover -s tests -v
./scripts/build-center-package.sh
./scripts/build-meta-packages.sh
./scripts/build-component-packages.sh
./build.sh
./scripts/smoke-iso.sh path/to/puresteel.iso
```

`smoke-iso.sh`, **oluşturulmuş ISO'nun** canlı dosya sistemi içindeki dosyaları ve paket manifestini inceler. Önyükleme testinin yerini tutmaz.

## QEMU ile temiz kurulum

QEMU kurulu x86_64 Linux bilgisayarda:

```sh
qemu-img create -f qcow2 puresteel-qa.qcow2 48G
qemu-system-x86_64 -enable-kvm -m 4096 -smp 4 \
  -drive file=puresteel-qa.qcow2,format=qcow2,if=virtio \
  -cdrom path/to/puresteel.iso -boot d -vga virtio
```

KVM yoksa `-enable-kvm` seçeneğini kaldır (daha yavaştır). Fiziksel bilgisayarının diskini QEMU'ya bağlama. Calamares'i yalnızca test için oluşturduğun sanal disk üzerinde çalıştır; bilgisayarı kapat, ISO'yu çıkar ve kurulu qcow2'yi başlat. UEFI/OVMF kapsamı için gerekirse yepyeni bir sanal diskle testi tekrarla.

### Her test için geçme/kalma kaydı

- [ ] Canlı ortam KDE Plasma Wayland'a ulaşıyor; Puresteel Breeze Light duvar kâğıdı ve SDDM görünüyor.
- [ ] Calamares, qcow2 dışındaki diskleri değiştirmeden tamamlanıyor.
- [ ] Kurulu sistem SDDM/Plasma ile açılıyor ve X11 alternatifi sunuyor.
- [ ] First Run bir kez görünüyor ve tamamlandı bilgisi korunuyor.
- [ ] Dil, açık/koyu Puresteel teması, ikon, duvar kâğıdı, donanım ve güç profili uygulanıyor.
- [ ] SDDM parolalı girişi, aynı parolalı `kdewallet`'ı PAM üzerinden açıyor; Wi-Fi parolası tekrar istenmiyor.
- [ ] Kullanıcıya ait eski Wi-Fi bağlantıları yalnızca onayla taşınıyor; `puresteelctl wifi` PSK sızdırmıyor.
- [ ] NVIDIA testi için Plasma X11 oturumu var.
- [ ] KDE PIM/Akonadi/Discover önyüklü değil; Steam, 32/64-bit Wine, Heroic, ProtonUp-Qt, ONLYOFFICE, Kdenlive, Audacity ve geliştirici araçları mevcut.
- [ ] Center ve bütün kartlar 1366×768 çözünürlükte kullanılabiliyor.
- [ ] Profil değişiklikleri yeniden başlatma sonrası korunuyor; Doctor swap ve ZRAM'i gösteriyor.
- [ ] ISO için seçilen yedi Puresteel paketi dpkg kaydında var; tam sürüm uygulamaları ve üç gerekli sistem Flatpak'i mevcut.
- [ ] `puresteelctl snapshot create` listelenebilir ve geri yüklenebilir snapshot oluşturuyor.
- [ ] Timeshift başarısızsa Safe Update duruyor (yalnızca **gözden çıkarılabilir VM'de** dene).
- [ ] Safe Update son güncelleme JSON'una gerçek snapshot kimliğini yazıyor.
- [ ] GRUB Puresteel Recovery, kurulu VM'de konsolu açıyor.
- [ ] Onarım arayüzü ve GRUB Recovery, LightDM yerine `sddm.service`'i etkinleştiriyor.
- [ ] Dolphin `admin://` açık Polkit onayı sonrası `kio-admin` ile açılıyor.
- [ ] Undo Last Update kayıtlı snapshot'ı gösteriyor, mevcut olduğunu denetliyor ve onay istiyor.
- [ ] Timeshift, test için yapılan değişikliği geri alabiliyor.
- [ ] `puresteel-info` ve crash raporunda SSID, kullanıcı adı, MAC, IP veya ham journal kayıtları bulunmuyor.
- [ ] `scripts/release-artifacts.sh` manifesti ISO içindeki paketlerle eşleşiyor.

## Gerçek donanım (VM testlerinden sonra isteğe bağlı)

NVIDIA offload, kernel yükseltmeleri sonrası DKMS, Wi-Fi, PipeWire, yüksek tazeleme hızı, uyku/uyanma, pil raporlaması, Secure Boot ve MOK için uygun fiziksel bilgisayar gerekir.

CI veya QEMU başarılı oldu diye bunları geçmiş sayma. Kişisel verilerini Timeshift'ten ayrı olarak yedekle; geri alınamaz iş istasyonunda yıkıcı rollback testleri yapma.
