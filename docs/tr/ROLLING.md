# Puresteel rolling ISO dağıtımı

Puresteel'in **tek güncel sürümü** vardır: `main` dalındaki başarıyla derlenmiş en son commit. Ayrı bir stable veya nightly ISO kanalı yoktur.

## GitHub Actions

`main` dalına yapılan her push/merge; kod, paket, imzalı APT arşivi bütünlüğü ve PowerShell denetimlerini başlatır. Bunlar geçerse `iso-smoke` tam kurulum ISO'sunu üretir, dosya sistemini statik olarak denetler, SHA256 hesaplar ve ISO'yu ilgili çalışmanın artifact'ine ekler.

Günlük derleme, Debian'ın yukarı akış paketlerindeki değişiklikleri de kontrol eder. Pull request'ler ISO yayımlayamaz. GitHub Actions yoğun dönemlerde işleri sıraya alabilir.

[Puresteel ISO Actions](https://github.com/MOzcelik14/Puresteel-OS/actions/workflows/validate.yml)

R2 deposunun şimdilik herkese açık bir geliştirme adresi vardır:

- [En güncel ISO](https://pub-6bd67d084cc74faa8573569db4b21336.r2.dev/Puresteel-Latest.iso)
- [Eşleşen SHA256](https://pub-6bd67d084cc74faa8573569db4b21336.r2.dev/Puresteel-Latest.iso.sha256)
- [Derleme bilgileri](https://pub-6bd67d084cc74faa8573569db4b21336.r2.dev/Puresteel-Latest.json)

Cloudflare `r2.dev` geliştirme adreslerini trafik bakımından sınırlar. Geniş kitleye dağıtımda özel R2 alan adı gerekir. İndirme erişimi gizli R2 S3 yükleme kimlik bilgilerini açığa çıkarmaz.

R2 kullanılamıyorsa başarılı bir `main` çalışmasını seçip `puresteel-iso` artifact'ini indir. Artifact'ler ZIP arşividir, GitHub oturumu gerektirebilir ve **7 gün sonra silinir**; kalıcı herkese açık indirme bağlantısı değildir.

## Cloudflare R2 ile sürekli güncel indirme

Cloudflare R2'de bir bucket oluştur ve o bucket ile sınırlı **Object Read & Write** yetkili bir API token hazırla. Seçtiğin herkese açık alan adında indirmeyi etkinleştir. R2'nin S3 API uç noktası yalnızca yetkili yükleme içindir; herkese açık indirme adresi değildir. Cloudflare kimlik bilgilerini repo dosyasına, issue'ya, pull request'e veya sohbete koyma.

GitHub reposunda **Settings → Secrets and variables → Actions → New repository secret** yolundan şu dört secret'ı tanımla:

| GitHub Actions secret | Değer |
| --- | --- |
| `R2_ACCOUNT_ID` | Cloudflare hesap kimliği |
| `R2_ACCESS_KEY_ID` | Bucket kapsamlı R2 erişim anahtarı kimliği |
| `R2_SECRET_ACCESS_KEY` | İlgili gizli R2 erişim anahtarı |
| `R2_BUCKET` | Bucket adı |

Bunlar tamamlandığında, başarılı bir sonraki `main` ISO işi şu nesneleri yayımlar:

| Herkese açık nesne | İçerik |
| --- | --- |
| `Puresteel-Latest.iso` | Güncel rolling kurulum ISO'su |
| `Puresteel-Latest.iso.sha256` | Herkese açık ISO dosya adına uyumlu SHA256 |
| `Puresteel-Latest.json` | Git commit'i, yayımlanma zamanı, ISO bayt sayısı/SHA256 ve dosya adları (site güncellemesi sonrasındaki build'lerde) |

JSON manifesti en son yüklenir. Başarısız build mevcut ISO'yu korur. Dört R2 secret'ının hiçbiri tanımlı değilse GitHub artifact üretilir ama harici yükleme atlanır; yapılandırma eksikse yayın adımı başarısız olur.

Yarıda kalan bir aktarım, birbirini tutmayan yardımcı dosyalar bırakabilir. İndirdiğin medyayı kurmadan önce `.sha256` ile doğrula.

**Maliyet ve sınırlar:** ISO birkaç gigabayttır. Her kaynak değişikliği GitHub Actions işlem süresi ve artifact depolaması tüketir. R2 depolaması, işlemler ve herkese açık alan adı ayarları ücretsiz kullanım üstünde ücret doğurabilir. Otomatik dağıtımı açık tutarken tüketimi izle.

## ISO güncelliği, kurulu sistem güncelliği değildir

Otomatik ISO yayımlama, indirilen kurulum medyasını yeniler. Puresteel kurulu makinelerin yeni Puresteel dosyalarını `apt upgrade` üzerinden alması için ayrıca **imzalı Puresteel APT deposunda** daha yeni paketlerin bulunması gerekir.

Belgelerin hazırlandığı aşamada imzalı APT indeksi Center `1.0.1-1` sürümünü, kaynak kod ise `2.0.0-1` sürümünü gösteriyordu. Orijinal özel imza anahtarıyla otomatik yayın etkinleştirilmeden, her kurulu kullanıcıya her commit'in ulaştığı iddia edilmemelidir. Güncel durumu [Güncellemeler](UPDATES.md) ve [yayın sahibi kontrol listesi](https://github.com/MOzcelik14/Puresteel-OS/issues/17) üzerinden takip et.

## Testlerin kapsamı

ISO derlemesinin ve statik dosya sistemi kontrolünün başarılı olması, Calamares kurulumunun veya gerçek ekran kartı sürücülerinin çalıştığını tek başına kanıtlamaz. Bu testleri [Kalite kontrol](QA.md) belgesinde kaydet.
