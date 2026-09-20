# Puresteel Plasma Wi-Fi and KWallet

Puresteel ships Debian 13 SDDM, `libpam-kwallet5`, `kwallet6` and
`plasma-nm`. SDDM autologin is disabled by default.

## Prevent repeated Wi-Fi passwords

- On a *new* installation, log in through SDDM with your password.
  An encrypted wallet named `kdewallet` can unlock via PAM when its password
  matches your account password. Do not use autologin for this workflow.
- If KWallet prompts for a **different** password, open Wallet settings,
  unlock the wallet and align its password with your login password if desired.
  A changed password or an older encrypted profile cannot be fixed by package
  installation alone.
- In **System Settings > Wi-Fi & Internet > select connection > Wi-Fi Security**,
  choose **Store password for this user only (encrypted)** to keep KWallet,
  then re-save your password if the old record is missing.
- If you explicitly need Wi-Fi **before login** or never want the wallet to
  gate that connection, choose **Store password for all users (not encrypted)**.
  NetworkManager saves it to a root-controlled connection profile, not in
  KWallet. This is a privacy/security choice, not a silent distro default.

Run `puresteelctl wifi` for a diagnostic that never requests or prints PSKs.
It can print connection/SSID names; review output before sharing.
`puresteelctl wifi --open-settings` opens KDE settings.

The distro never disables KWallet, blanks a wallet password, copies secrets
from GNOME Keyring or silently converts existing user-owned connections.
