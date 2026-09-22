# Puresteel Plasma: Wi-Fi ve KWallet

Puresteel; Debian 13 üzerinde SDDM, `libpam-kwallet5`, `kwallet6` ve `plasma-nm` ile gelir. SDDM otomatik giriş varsayılan olarak kapalıdır.

## Wi-Fi şifresinin tekrar tekrar sorulmasını önleme

- **Yeni bir kurulumda** SDDM giriş ekranında hesap şifrenle oturum aç. `kdewallet` adlı şifrelenmiş cüzdanın parolası hesap parolanla aynıysa PAM üzerinden otomatik açılabilir. Bu kullanım için otomatik girişi etkinleştirme.
- KWallet **farklı bir parola** sorarsa Cüzdan ayarlarını aç, cüzdanın kilidini kaldır ve istersen parolayı giriş parolanla eşitle. Daha önce değişmiş bir parola veya eski bir şifreli profil, sadece paket kurmakla düzelmez.
- **Sistem Ayarları → Wi-Fi ve İnternet → bağlantıyı seç → Wi-Fi Güvenliği** bölümünde KWallet kullanmak için **Parolayı yalnızca bu kullanıcı için sakla (şifreli)** seçeneğini kullan. Eski kayıt bulunamıyorsa parolayı yeniden kaydet.
- Wi-Fi'nin **giriş yapmadan önce** çalışması gerekiyorsa veya bağlantının KWallet kilidine bağlı olmasını istemiyorsan **Parolayı tüm kullanıcılar için sakla (şifrelenmemiş)** seçeneğini bilinçli olarak seçebilirsin. NetworkManager parolayı KWallet yerine root tarafından yönetilen bağlantı profilinde saklar. Bu bir gizlilik/güvenlik tercihidir; dağıtım bunu sessizce varsayılan yapmaz.

Parola istemeyen ve PSK değerlerini göstermeyen tanılama için:

```bash
puresteelctl wifi
```

Tanılama çıktısında bağlantı ve SSID adları görünebilir; paylaşmadan önce incele.

KDE ağ ayarlarını açmak için:

```bash
puresteelctl wifi --open-settings
```

Puresteel; KWallet'ı devre dışı bırakmaz, cüzdan parolasını boşaltmaz, GNOME Keyring'den gizli bilgileri kopyalamaz veya mevcut kullanıcı bağlantılarını izinsiz şekilde dönüştürmez.
