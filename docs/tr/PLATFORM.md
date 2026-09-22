# Puresteel platform katmanı

Puresteel, Debian 13 ve KDE Plasma 6 üzerine dağıtıma özgü bir yönetim katmanı ekler.

## Günlük komutlar

- `puresteelctl status`
- `puresteelctl doctor`
- `puresteelctl snapshot create`
- `puresteelctl update`
- `puresteelctl gpu status`
- `puresteelctl battery`
- `puresteelctl firmware status`
- `puresteelctl health all`
- `puresteelctl logs`
- `puresteelctl secureboot status`
- `puresteelctl flatpak repair`
- `puresteelctl kernel`

## Kurtarma

GRUB'daki **Puresteel Recovery** menüsünden paket, initramfs/GRUB ve SDDM onarma; NVIDIA DKMS'i yeniden oluşturma; Timeshift geri yükleme ve son güncellemeyi geri alma akışlarına erişilebilir.

## Secure Boot

Puresteel, Secure Boot/MOK durumunu raporlayabilir ve sahibinin sağladığı DER açık anahtarı kaydedebilir. Özel imza anahtarları ISO'ya veya repoya eklenmez. Uçtan uca Secure Boot doğrulaması için imzalı önyükleme dosyaları ve gerçek donanım testi de gerekir.

## Yayın bütünlüğü

`scripts/release-artifacts.sh IMAGE.iso`; SHA256, paket manifesti ve kaynak/provenance bilgileri üretir. Zırhlı ayrık GPG imzası, yalnızca imza anahtarı özellikle yapılandırıldıysa oluşturulur.

## Donanım raporları

`puresteel-hw-report`, GitHub donanım bildirim şablonu için sınırlı bir JSON raporu üretir. Ana makine adı, kullanıcı adı, seri numarası, MAC ve IP adreslerini bilinçli olarak dışarıda bırakır.

## Paketleme ve güncellemeler

`build.sh`; Center, platform araçları, Recovery, tema/markalama, masaüstü varsayılanları ve beş rol metapaketi için sürümlendirilmiş Debian paketleri hazırlar.

`config/includes.chroot` içindeki dosyalar bu geçiş boyunca derlemenin temel kaynaklarıdır; kurulu sistemde ilgili bileşen paketleri de aynı dosyaların sahipliğini üstlenir. Bu sayede daha yeni sürümler APT ile gelebilir. `scripts/release-center.sh` yalnızca Center'ı değil, Puresteel'e ait toplam on paketi imzalı depoya hazırlar. Bunun GitHub'da otomatik yayımlanması için orijinal özel anahtarın güvenli biçimde tanımlanmış olması gerekir.

Safe Update, güncelleme öncesi Timeshift snapshot'ı oluşturulup doğrulanamazsa APT işlemini engeller. `puresteelctl update --no-snapshot` seçeneğini ancak bu riski bilerek kabul ediyorsan kullan. Recovery'deki **Undo Last Update**, gerçek snapshot kimliğini okur ve Timeshift'e geçmeden önce hedef/dosya sistemi onayı ister.

`puresteel-info` ve `puresteel-crash-helper` yalnızca izin verilen tanılama alanlarını kullanır. `puresteel-logs` ise **özeldir**, kişisel bilgi içerebilir. Sınırlı donanım raporunda bile bazı model adları ayırt edici olabilir.

CI; sözdizimi, bileşen paketleri ve root gerektirmeyen güvenlik testlerini denetler. CI'nin başarılı olması Calamares, GRUB Recovery veya NVIDIA'nın gerçek bilgisayarda çalıştığını **tek başına kanıtlamaz**. Bunlar [Kalite kontrol](QA.md) belgesindeki ayrı entegrasyon testleridir.

## GPU sürücü yöneticisi

Center'ın GPU/Sürücüler sayfası, yalnızca etkin Debian APT depolarında bulunan NVIDIA sürücü metapaketlerini listeler. Etkin PCI çekirdek sürücüsü, paket adayı/kurulu sürüm, çalışan çekirdeğe uygun header, DKMS, firmware, Secure Boot, Vulkan ve `vainfo` çıkış durumu gösterilir.

Puresteel kurulum veya onarım öncesinde `--no-remove` ile APT simülasyonu yapar. Yetkili yardımcı; izin verilen paket listesi, GPU varlığı, kernel header'ları, APT adayı ve paket kaldırma denetimlerini tekrarlar. Paket kaldırabilecek NVIDIA geçişlerinde güvenli olduğunu tahmin etmek yerine işlemi reddeder.

Arayüz QThread işçileri kullanır; uzun APT işlemleri GUI iş parçacığında yürütülmez. APT işleminin başarıyla tamamlanması, yeniden başlatma olmadan sürücünün etkinleştiği anlamına gelmez: DKMS ve donanım kurulu makinede test edilmelidir.

## Plasma ve Wi-Fi

Puresteel, `kde-full` veya `kde-standard` yerine seçilmiş Plasma bileşenlerini kullanır: SDDM, Breeze Light, Dolphin, Konsole, plasma-nm, plasma-pa, Polkit KDE aracısı, Wayland ve KWin/X11 yedek oturumu.

**Güncel tam donanımlı ISO**, masaüstüne ek olarak Gaming/Creator/Developer araçlarını, Heroic, ProtonUp-Qt ve ONLYOFFICE sistem Flatpak'lerini de içerir. Bu özellik önceki minimal ISO'dan farklıdır. Çok büyük eski 96-font paketi yerine sık kullanılan dört Nerd Font ağırlığı vardır.

İlk girişte Puresteel duvar kâğıdı bir kere ayarlanır; her yeniden başlatmada kullanıcı tercihi ezilmez. KWallet korunur; SDDM parola girişi ile `libpam-kwallet5`, hesap ve cüzdan parolaları uyuştuğunda şifreli Wi-Fi bilgilerine erişebilir. Eski bağlantılar ve açık rıza gerektiren sistem genelinde parola saklama seçenekleri için [KDE / Wi-Fi](KDE-WIFI.md) rehberine bak. Hiçbir parola dönüşümü kendiliğinden yapılmaz.
