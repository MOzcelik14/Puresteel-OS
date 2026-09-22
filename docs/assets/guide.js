/* Puresteel documentation: render the exact same Markdown published in /docs.
 * Vendored Showdown + DOMPurify avoid third-party network requests at runtime.
 * Only explicit local .md file names are accepted from URL query parameters.
 */
(function () {
  "use strict";
  const docs = [
    ["INSTALL", "Installation", "Kurulum"],
    ["BUILD", "Build the ISO", "ISO oluşturma"],
    ["PURESTEEL_CENTER", "Puresteel Center", "Puresteel Center"],
    ["UPDATES", "Rolling updates", "Rolling güncellemeler"],
    ["ROLLING", "ISO publishing", "ISO yayımlama"],
    ["HARDWARE", "Hardware & drivers", "Donanım ve sürücüler"],
    ["KDE-WIFI", "KDE / Wi-Fi", "KDE / Wi-Fi"],
    ["PLATFORM", "Platform tools", "Platform araçları"],
    ["QA", "Quality assurance", "Kalite kontrol"],
    ["TROUBLESHOOTING", "Troubleshooting", "Sorun giderme"]
  ];
  const known = new Set(docs.map(function (d) { return d[0]; }));
  const lang = localStorage.getItem("puresteel-lang") === "tr" ||
    (!localStorage.getItem("puresteel-lang") && navigator.language.toLowerCase().startsWith("tr")) ? "tr" : "en";
  document.documentElement.lang = lang;
  const tr = lang === "tr";
  const params = new URLSearchParams(location.search);
  const requested = (params.get("doc") || "INSTALL").toUpperCase();
  const current = known.has(requested) ? requested : "INSTALL";
  const github = "https://github.com/MOzcelik14/Puresteel-OS/blob/main/";
  const content = document.getElementById("content");
  const navigation = document.getElementById("docnav");
  const search = document.getElementById("doc-search");
  const toc = document.getElementById("toc");
  const definition = docs.find(function (d) { return d[0] === current; });
  const label = tr ? definition[2] : definition[1];
  document.title = label + " · Puresteel";
  document.getElementById("crumb").textContent = label;
  const original = github + "docs/" + current + ".md";
  document.getElementById("source").href = original;
  document.getElementById("edit-link").href = original;
  search.placeholder = tr ? "Belge ara…" : "Find a guide…";
  for (const node of document.querySelectorAll("[data-tr]")) {
    if (tr) node.textContent = node.getAttribute("data-tr");
  }

  for (const entry of docs) {
    const link = document.createElement("a");
    link.href = "guide.html?doc=" + encodeURIComponent(entry[0]);
    link.textContent = tr ? entry[2] : entry[1];
    if (entry[0] === current) {
      link.classList.add("current");
      link.setAttribute("aria-current", "page");
    }
    navigation.appendChild(link);
  }
  search.addEventListener("input", function () {
    const term = search.value.trim().toLocaleLowerCase();
    for (const link of navigation.querySelectorAll("a")) {
      link.hidden = !link.textContent.toLocaleLowerCase().includes(term);
    }
  });
  function slug(text) {
    return text.toLocaleLowerCase().normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9ğüşöçı -]/g, "")
      .trim().replace(/\s+/g, "-").replace(/-+/g, "-") || "section";
  }
  function localLink(href) {
    if (!href || href.startsWith("#")) return href;
    if (/^(?:https?:|mailto:|tel:|data:|\/\/)/i.test(href)) return href;
    const match = href.match(/^(?:\.\/)?(?:docs\/)?([A-Za-z0-9_-]+)\.md(#[A-Za-z0-9_-]+)?$/i);
    if (match) {
      const stem = match[1].toUpperCase();
      if (known.has(stem)) return "guide.html?doc=" + encodeURIComponent(stem) + (match[2] || "");
      if (stem === "README") return github + "README.md" + (match[2] || "");
    }
    if (/^\.\.\/README(?:\.tr)?\.md(?:#.*)?$/i.test(href)) return github + href.slice(3);
    if (href.startsWith("../")) return github + href.slice(3);
    // Relative image and media links must resolve against docs/, not guide.html query.
    if (!href.startsWith("/")) return href;
    return href;
  }
  function fail(message) {
    content.replaceChildren();
    const box = document.createElement("div");
    box.className = "notice";
    box.appendChild(document.createTextNode(message + " "));
    const a = document.createElement("a");
    a.href = original;
    a.textContent = tr ? "Belgeyi GitHub'da aç ↗" : "Open document on GitHub ↗";
    box.appendChild(a);
    content.appendChild(box);
  }
  fetch(current + ".md", {cache:"no-cache"}).then(function (response) {
    if (!response.ok) throw Error("HTTP " + response.status);
    return response.text();
  }).then(function (markdown) {
    if (!window.showdown || !window.DOMPurify) throw Error("Markdown renderer unavailable");
    const converter = new showdown.Converter({
      tables: true, strikethrough: true, tasklists: true, ghCodeBlocks: true,
      literalMidWordUnderscores: true, simplifiedAutoLink: true,
      ghCompatibleHeaderId: true, emoji: false
    });
    let html = converter.makeHtml(markdown);
    html = DOMPurify.sanitize(html, {USE_PROFILES: {html:true}});
    content.innerHTML = html;
    let slugCount = new Map();
    for (const heading of content.querySelectorAll("h1,h2,h3,h4")) {
      let id = heading.id || slug(heading.textContent);
      let count = slugCount.get(id) || 0;
      slugCount.set(id, count + 1);
      if (count) id += "-" + count;
      heading.id = id;
      if (heading.matches("h2,h3")) {
        const a = document.createElement("a");
        a.href = "#" + encodeURIComponent(id);
        a.textContent = heading.textContent;
        if (heading.tagName === "H3") a.classList.add("depth3");
        toc.appendChild(a);
      }
    }
    for (const link of content.querySelectorAll("a[href]")) {
      const originalHref = link.getAttribute("href");
      link.setAttribute("href", localLink(originalHref));
      if (/^https?:\/\//i.test(link.href) && new URL(link.href).origin !== location.origin) {
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      }
    }
    for (const image of content.querySelectorAll("img[src]")) {
      const src = image.getAttribute("src");
      if (src && src.startsWith("../")) image.src = github.replace("github.com/", "raw.githubusercontent.com/").replace("/blob/", "/") + src.slice(3);
      image.loading = "lazy";
    }
    for (const pre of content.querySelectorAll("pre")) {
      const code = pre.querySelector("code");
      if (!code) continue;
      const button = document.createElement("button");
      button.className = "copy-code";
      button.type = "button";
      button.textContent = tr ? "Kopyala" : "Copy";
      button.addEventListener("click", function () {
        navigator.clipboard.writeText(code.textContent).then(function () {
          button.textContent = tr ? "Kopyalandı" : "Copied";
          setTimeout(function () { button.textContent = tr ? "Kopyala" : "Copy"; }, 1500);
        }).catch(function () { button.textContent = "!"; });
      });
      pre.insertBefore(button, pre.firstChild);
    }
    if (location.hash) {
      const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (target) requestAnimationFrame(function () { target.scrollIntoView(); });
    }
  }).catch(function (error) {
    fail(tr ? "Belge şu anda görüntülenemiyor." : "This document could not be displayed.");
    console.warn("Puresteel documentation viewer:", error.message);
  });
}());
