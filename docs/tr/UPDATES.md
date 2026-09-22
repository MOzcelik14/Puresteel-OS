# Puresteel güncellemeleri ve paket deposu

Puresteel iki ana güncelleme kaynağı kullanır:

1. Temel işletim sistemi için Debian depoları.
2. Puresteel'e ait paketler için **imzalı Puresteel APT deposu**.

Flatpak uygulamaları Flatpak/Flathub üzerinden ayrıca güncellenir.

## Depo adresi

Kurulu sistemlerde şu URL kullanılır:

```text
https://mozcelik14.github.io/Puresteel-OS/apt
```

APT kaynak tanımı:

```text
/etc/apt/sources.list.d/puresteel.sources
```

Bu dosyanın başvurduğu Puresteel açık arşiv anahtarı:

```text
/usr/share/keyrings/puresteel-archive-keyring.asc
```

## ISO derlenirken Puresteel paketleri neden GitHub Pages'ten çekilmiyor?

Puresteel'e ait paketler ayrıca şu dizine kopyalanır:

```text
config/packages.chroot/
```

Böylece `live-build` paketleri ISO içine yerel olarak kurabilir. ISO oluşturmak; GitHub Pages'in çalışmasına, çevrimiçi Puresteel paket sunucusuna veya onun TLS bağlantısına bağlı olmaz.

Kurulumdan sonra daha yeni Puresteel paketleri çevrimiçi **imzalı** depodan APT ile indirilir.

## Depo yapısı

GitHub Pages doğrudan sunabilsin diye arşiv `docs/apt/` altında yayımlanır:

```text
docs/apt/
├── dists/
│   └── stable/
│       ├── InRelease
│       ├── Release
│       ├── Release.gpg
│       └── main/
│           └── binary-amd64/
│               ├── Packages
│               └── Packages.gz
├── pool/
│   └── main/
│       └── p/
│           └── puresteel-center/
└── puresteel-archive-keyring.asc
```

`InRelease` ve `Release.gpg`, Puresteel arşiv imza anahtarıyla oluşturulur.

## Puresteel Center yayımlama

Center paketinin kaynak kodu:

```text
packages/puresteel-center/
```

Yayımlamadan paket oluştur:

```bash
./scripts/build-center-package.sh
```

Yeni paket sürümü hazırla:

```bash
./scripts/release-center.sh 2.0.0-1
```

Kaynak paket temel sürümü `2.0.0-1`'dir. Bu belgenin hazırlandığı sırada commit edilmiş imzalı APT indeksi hâlâ `puresteel-center` için `1.0.1-1` sürümünü listeliyordu. Kaynak kodu merge etmek kurulu bilgisayarları kendiliğinden güncellemez. Yeni paketleri yayımlamak için **mevcut arşiv anahtarıyla eşleşen özel imza anahtarı**, yeniden oluşturulmuş bileşen paketleri, imzalı indeksler ve ayrı bir yayın commit'i gerekir. İmzasız ya da anahtarı tutmayan metadata yayımlama.

Yayın betiğinin temel adımları:

1. `packages/puresteel-center/VERSION` dosyasını günceller.
2. `.deb` paketini üretir.
3. Güncel paketi `config/packages.chroot/` içine kopyalar.
4. Paketi APT havuzuna ekler.
5. `Packages` ve `Packages.gz` indekslerini yeniden üretir.
6. `Release` metadata'sını oluşturur.
7. Arşivi imzalar.
8. Arşivin açık anahtarını dışarı aktarır.
9. Kurulu sisteme yönelik APT kaynak/anahtar dosyalarını hazırlar.

Ardından değişiklikleri commit edip gönder:

```bash
git add -A
git commit -m "Release Puresteel components 2.0.0"
git push
```

GitHub Pages, push'tan sonra güncel depoyu sunar.

## Kurulu Puresteel'i güncelleme

```bash
sudo apt update
sudo apt full-upgrade
flatpak update
```

APT, çevrimiçi depoda daha yeni bir `puresteel-center` paketi bulursa onu normal paket yükseltmesi olarak değerlendirir.

## Çevrimiçi depoyu doğrulama

İmzalı metadata:

```bash
curl -I https://mozcelik14.github.io/Puresteel-OS/apt/dists/stable/InRelease
```

Paket indeksi:

```bash
curl -I https://mozcelik14.github.io/Puresteel-OS/apt/dists/stable/main/binary-amd64/Packages.gz
```

Center kaydı:

```bash
curl -fsSL \
  https://mozcelik14.github.io/Puresteel-OS/apt/dists/stable/main/binary-amd64/Packages.gz \
  | gzip -dc \
  | sed -n '/^Package: puresteel-center$/,/^$/p'
```

## Yayımlamadan önce imzalı sürümü kontrol etme

Herkese açık APT arşivi, **özel anahtar olmadan** denetlenebilir:

```bash
python3 scripts/verify-apt-repository.py
```

Bu komut iki OpenPGP imzasını, imzalı Release/indeks SHA256 değerlerini, gzip indeksini, atıf yapılan bütün Debian paketlerinin hash/boyutlarını ve paket kontrol metadata'sını doğrular. GitHub CI aynı salt-okunur kontrolü kullanır.

Yeni sürümün kaynak sürümle eşleştiğini doğrulamak için:

```bash
python3 scripts/verify-apt-repository.py --require-current
```

**Önemli yayın engeli:** Kaynak sürümü ilerletmek için `docs/apt/puresteel-archive-keyring.asc` dosyasındaki açık anahtarla eşleşen **orijinal özel anahtar** gerekir. Özel anahtarı Git'e commit etme veya ilgisiz yeni bir anahtarla sessizce değiştirme. Orijinal anahtar güvenilir geliştirici bilgisayarında bulunuyorsa `./scripts/release-center.sh 2.0.0-1` çalıştır, değişiklikleri incele ve testlerden sonra yayımla. Sadece `main`'i değiştirmek geçerli imzalı APT sürümü üretmez.

## Main dalını koruma

Repo yöneticisi GitHub branch protection veya ruleset ile şunları ayarlamalıdır:

- `main` için pull request zorunluluğu
- `validate` ve `windows-powershell-syntax` durum kontrolleri
- Force-push ve dal silme engeli
- Kontrolleri atlayan istisnaların sınırlandırılması

Normal PR'lar `iso-smoke` işini bilerek atladığından bu isteğe bağlı gecelik işi zorunlu durum kontrolüne ekleme. Bu ayar repo dosyası değil GitHub Settings yetkisidir.

## İmza anahtarı

**Açık anahtar** repoda ve kurulu sistemde bulunmalıdır.

**Özel GPG imza anahtarı Git'e asla eklenmemelidir.** Şifreli/çevrimdışı yedeğini tut. Yeni derleme bilgisayarına geçince aynı orijinal özel anahtarı içeri aktar. Yayın betiği, sürüm dosyasını değiştirmeden önce özel anahtarın parmak izini yayımlanmış açık anahtarla karşılaştırır; kurulu bilgisayarları erişimsiz bırakabilecek ilgisiz yeni anahtarı reddeder.

```bash
gpg --import Puresteel-APT-PRIVATE-KEY.asc
gpg --list-secret-keys
```

Özel anahtarın kaybı kaynak kodu silmez; ancak mevcut güven kimliğiyle yeni paket deposu imzalanmasını engeller.

## Güvenlik modeli

APT, depo metadata'sını `Signed-By` ile belirtilen Puresteel açık anahtarına göre doğrular. Depo hatasını çözmek için TLS veya APT imza kontrolünü kapatma.

Paket deposu geçici olarak çalışmazsa kurulu Debian paketleri kullanılabilir kalır; depo geri gelene kadar yalnızca Puresteel'e ait paket güncellemeleri etkilenir.

## Otomatik imzalı rolling yayın

Başarılı bir `main` push'u veya elle tetiklenmiş başarılı validasyon sonrasında [Publish signed Puresteel APT](../.github/workflows/publish-apt.yml), `2.0.0+git20260922143000.abcdef123456-1` benzeri commit damgalı Debian sürümü üretir.

Center ve Puresteel'e ait diğer dokuz paketi oluşturur; iki imzalı Release biçimini ve indekslenmiş `.deb` hash'lerini doğrular, ardından imzalı `docs/apt` arşivini commit eder. Yalnızca `docs/apt` içeren commit yeni ISO build'i başlatmaz. Her paket için son iki rolling sürüm korunur; normal/elle yayımlanmış sürümler silinmez.

**Yayın otomasyonu, repo yöneticisi şu üç GitHub Actions secret'ını tanımlayana kadar bilerek devre dışıdır:**

- `PURESTEEL_APT_SIGNING_KEY_B64`: Parmak izi `docs/apt/puresteel-archive-keyring.asc` ile eşleşen **orijinal** özel arşiv anahtarının Base64 biçimi. Güvenilir kendi bilgisayarında dışarı aktar; sohbete, PR'a, issue'ya veya kaynak dosyasına yapıştırma.
- `PURESTEEL_APT_SIGNING_PASSPHRASE`: Özel anahtarın parolası. Yayımlama veya komut satırı argümanı olarak kullanma.
- `PURESTEEL_APT_PUBLISH_TOKEN`: Yalnızca `MOzcelik14/Puresteel-OS` için Contents Read/Write yetkili **fine-grained GitHub personal access token**. Yerleşik `GITHUB_TOKEN` ile yapılan push, APT arşivini sunacak GitHub Pages branch build'ini tetiklemediği için ayrıca gereklidir.

Özel anahtarı ve parolasını bu sohbete göndermeden güvenilir bilgisayarda hazırla; kodlanmış anahtarı doğrudan **GitHub repository Secret** formuna gir. Workflow geçici GPG evinde içeri aktarır, metadata'yı değiştirmeden önce açık anahtarla eşleştiğini denetler ve işlem bitince yerel kopyasını siler. Şifreli çevrimdışı yedek tut.

Orijinal anahtar kaybolduysa **sessizce yeni anahtara geçme**: kurulu sistemler mevcut açık anahtara güvenir. Bunun için ayrı ve doğrulanmış anahtar döndürme/taşıma süreci gerekir.

`packages/puresteel-center/VERSION` temel sürümü taşır; doğrulanmış her `main` commit'i kendine özgü zaman damgalı `+git` sürümü alır. ISO yine kendi Puresteel paketlerini çevrimiçi depoya ihtiyaç duymadan içerir. İmzalı APT yayımlama yalnızca yeni ISO'ları değil, **kurulu sistemleri de bir sonraki APT güncellemesinde** etkiler. Debian temel paketleri ve Flatpak güncellemeleri ayrıdır.

Otomatik yayın, workflow'da `Signed packages published` mesajı görülüp GitHub Pages yeni imzalı `InRelease` dosyasını sunana kadar başarılı sayılmamalıdır. Gerekli secret'lar yoksa mevcut depo korunur ve bilgilendirme gösterilir. Korunan `main` dalı, kapsamı sınırlandırılmış token için özel yayın kuralı gerektirebilir.

Üç secret tanımlandıktan sonra [Puresteel validation → Run workflow](https://github.com/MOzcelik14/Puresteel-OS/actions/workflows/validate.yml) sayfasında `main` üzerinde çalıştır. Başarılı olursa APT yayıncısı **aynı doğrulanmış commit** için çalışır. Gecelik ISO derlemesi tek başına gereksiz yeni paket sürümü yayımlamaz; normal paket yayınları kaynak değişiklikleri veya açıkça elle başlatılan doğrulama sonrasındadır.
