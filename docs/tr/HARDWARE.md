# Donanım ve grafik desteği

Puresteel, standart x86-64 masaüstü ve dizüstü bilgisayarları hedefler. Tek bir üreticiye bağlı kalmadan Intel, AMD ve NVIDIA grafik donanımlarını destekleyecek şekilde yapılandırılır.

## İşlemci desteği

Intel ve AMD mikro kod paketleri ISO'da bulunur:

- `intel-microcode`
- `amd64-microcode`

Çekirdek, Debian'ın amd64 çekirdek paketidir.

## Intel grafik birimleri

Modern Intel grafik altyapısı için firmware ve kullanıcı alanı bileşenleri:

- `firmware-intel-graphics`
- `firmware-intel-misc`
- `intel-media-va-driver-non-free`
- Mesa Vulkan ve DRI bileşenleri

Donanım nesline göre etkin çekirdek sürücüsü `i915` veya `xe` olabilir.

Kapsam, mevcut Debian çekirdek/Mesa sürümlerinin desteklediği entegre Intel GPU'ları ve yeni nesil harici Intel kartları içerir.

## AMD grafik birimleri

AMD entegre ve harici Radeon grafik desteği:

- `firmware-amd-graphics`
- `mesa-vulkan-drivers`
- `mesa-va-drivers`
- `libgl1-mesa-dri`
- `xserver-xorg-video-amdgpu`

Desteklenen modern Radeon kartlar genellikle `amdgpu` çekirdek sürücüsünü kullanır. Eski kartlarda çekirdek desteğine göre `radeon` etkin olabilir.

## NVIDIA grafik birimleri

Puresteel, Debian'ın tescilli NVIDIA altyapısını içerir:

- `nvidia-driver`
- `nvidia-settings`
- `firmware-nvidia-graphics`
- `linux-headers-amd64`
- Oyun için uygun sürücü sürümüyle eşleşen 32-bit NVIDIA/Vulkan kullanıcı alanı kütüphaneleri
- `switcheroo-control`

NVIDIA çekirdek modülleri DKMS ile oluşturulur. Puresteel, kullanılan Debian sürücü paketleri için gereken modül takma adlarını ve yapılandırmasını da içerir.

Durumu kontrol et:

```bash
nvidia-smi
```

## Hibrit grafik

Puresteel şu tür dizüstü ve çoklu GPU sistemlerini hedefler:

- Intel iGPU + NVIDIA dGPU
- AMD iGPU + NVIDIA dGPU
- Intel iGPU + AMD dGPU
- AMD iGPU + AMD dGPU

Desteklenen ortamlarda `switcheroo-control` masaüstü düzeyinde GPU entegrasyonu sağlar.

Uygulamaları harici GPU'ya yönlendirme davranışı; ekran kartlarına, çekirdeğe, pencere yöneticisine ve uygulamaya göre değişir.

## Vulkan ve 32-bit uyumluluk

Tam donanımlı Puresteel ISO'sunda `i386` mimarisi ve Steam/Wine için gereken 32-bit grafik bileşenleri bulunur. Bunlar arasında `steam-libs-i386`, `wine32:i386`, `libvulkan1:i386`, `mesa-vulkan-drivers:i386` ve `libgl1-mesa-dri:i386` yer alır. NVIDIA kullanan sistemler için ilgili 32-bit NVIDIA paketleri de tam ISO derlemesinde doğrulanır.

Kurulu sürücünün sağlığını ve APT'nin önerdiği değişiklikleri kontrol etmek için:

```bash
sudo apt update
apt-cache policy nvidia-driver nvidia-driver-libs:i386 nvidia-vulkan-icd:i386
sudo apt-get -s install nvidia-driver-libs:i386 nvidia-vulkan-icd:i386
```

Simülasyon paket kaldırmayı veya istenmeyen NVIDIA sürücü değişimini öneriyorsa işlemi uygulama. Yalnızca Intel/AMD bulunan bir makineye üreticiye özgü NVIDIA kütüphaneleri kurma.

## VA-API

Puresteel, donanım ve sürücü destekliyorsa video hızlandırma için VA-API bileşenlerini içerir.

Puresteel Center'ın **Sürücüler** sayfasında Vulkan ve VA-API durumunu inceleyebilirsin.

## Tanılama komutları

GPU ve etkin sürücüler:

```bash
lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'
```

Yüklü grafik modülleri:

```bash
lsmod | grep -E 'nvidia|nouveau|amdgpu|radeon|i915|xe'
```

Vulkan:

```bash
vulkaninfo --summary
```

VA-API:

```bash
vainfo
```

DKMS:

```bash
dkms status
```

Hibrit grafik servisi:

```bash
systemctl status switcheroo-control
```

## Gerçek donanımda test

Sanal makineler üreticiye özgü GPU davranışını tam olarak doğrulayamaz. Genel dağıtımdan önce farklı bilgisayarlarda test et:

- Yalnızca Intel grafik
- Yalnızca AMD grafik
- Yalnızca NVIDIA grafik
- Intel + NVIDIA hibrit dizüstü
- AMD + NVIDIA hibrit dizüstü
- Çoklu monitör
- Uyku ve uyanma
- HDMI/DisplayPort ses
- Vulkan kullanan oyunlar

## Donanım sorunu bildirme

Grafik sorunlarında şu çıktıların ilgili bölümlerini ekle:

```bash
uname -a
lspci -nnk
lsmod
dkms status
```

NVIDIA için ayrıca:

```bash
nvidia-smi
```

Puresteel Center → **Sistem Raporları** bu bilgilerin önemli bölümünü toplayabilir. Paylaşmadan önce kişisel bilgi içerip içermediklerini kontrol et.
