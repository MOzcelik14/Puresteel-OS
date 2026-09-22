# Vendored documentation renderer dependencies

- Showdown 2.1.0 — https://github.com/showdownjs/showdown — MIT license (see showdown.LICENSE).
- DOMPurify 3.2.6 — https://github.com/cure53/DOMPurify — Apache-2.0 / MPL-2.0 dual license (see DOMPurify.LICENSE).

Both JavaScript files are bundled locally so Puresteel documentation works without a third-party CDN at runtime. DOMPurify sanitizes the HTML generated from the repository's Markdown sources.
