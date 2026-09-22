# Puresteel rolling ISO distribution

Puresteel maintains ONE current edition: the latest successfully built commit on `main`.
There are no separate stable and nightly ISO channels.

## GitHub Actions

Every push/merge to `main` triggers code, package, signed APT archive integrity,
and PowerShell checks. After those pass, `iso-smoke` builds the full installer ISO,
verifies its static contents, generates a checksum and attaches the ISO to its run.
A daily build also checks for upstream Debian package changes. Pull requests
cannot publish ISOs. GitHub Actions may queue builds during busy periods.

[Puresteel ISO Actions](https://github.com/MOzcelik14/Puresteel-OS/actions/workflows/validate.yml)

The R2 bucket now has a temporary public development URL:

- [Latest ISO](https://pub-6bd67d084cc74faa8573569db4b21336.r2.dev/Puresteel-Latest.iso)
- [Matching SHA256](https://pub-6bd67d084cc74faa8573569db4b21336.r2.dev/Puresteel-Latest.iso.sha256)
- [Build metadata](https://pub-6bd67d084cc74faa8573569db4b21336.r2.dev/Puresteel-Latest.json)

Cloudflare rate-limits `r2.dev` development URLs; a custom R2 domain is needed for production-scale public distribution. Download access does not expose the private R2 S3 upload credentials.

Until R2 is configured, select a successful `main` run and download its
`puresteel-iso` artifact. Artifacts are ZIP archives, can require GitHub login,
and expire after **7 days**. They are not permanent public download URLs.

## Configure permanent rolling downloads via Cloudflare R2

Create a Cloudflare R2 bucket and a bucket-scoped API token with Object Read
and Write permissions. Enable public downloads for the bucket on a chosen
public domain. The R2 S3 API endpoint is only for authorized upload, not a
public download URL. Cloudflare credentials must not go into repository files,
issues, pull requests or chat.

Under GitHub repository **Settings → Secrets and variables → Actions →
New repository secret**, configure all four secrets:

| GitHub Actions secret | Value |
| --- | --- |
| `R2_ACCOUNT_ID` | Cloudflare account ID |
| `R2_ACCESS_KEY_ID` | Bucket-scoped R2 access key ID |
| `R2_SECRET_ACCESS_KEY` | Corresponding R2 secret key |
| `R2_BUCKET` | Bucket name |

Once configured, the next successful `main` ISO job publishes these objects:

| Public object | Contents |
| --- | --- |
| `Puresteel-Latest.iso` | Current rolling installation ISO |
| `Puresteel-Latest.iso.sha256` | Checksum matching the public ISO filename |
| `Puresteel-Latest.json` | Git commit, publication time, ISO byte count/SHA256 and file names (on builds after the site update) |

The manifest is uploaded last. A failed build leaves the previous public ISO
in place. Missing all R2 secrets skips external publishing without failing the
GitHub artifact; incomplete credentials cause the publication step to fail.
An interrupted upload can leave incomplete related metadata; always verify
the `.sha256` file before installing downloaded media.

**Costs and limits:** an ISO is several gigabytes. Every source commit can
consume significant GitHub Actions compute minutes and artifact storage.
R2 storage, operations and public-domain setup may incur charges above
free usage. Monitor consumption when enabling automatic publishing.

## ISO freshness is not the same as installed-system freshness

Automatic ISO publishing updates the install/download media. Existing
Puresteel machines still need newer versions in the signed Puresteel APT
repository to receive updated Puresteel-owned files via `apt upgrade`.
The current signed APT index advertises Center `1.0.1-1`, while source is
`1.4.0-1`. Publishing package updates needs the ORIGINAL private signing key.
Do not confuse ISO publication with automatic package releases or
claim every installed user receives every commit. See [UPDATES.md](UPDATES.md)
and [release-owner checklist](https://github.com/MOzcelik14/Puresteel-OS/issues/17).

## Validation scope

An ISO build and static filesystem check do not prove successful Calamares
installation or correct drivers on physical hardware. Record those tests in
[QA.md](QA.md).
