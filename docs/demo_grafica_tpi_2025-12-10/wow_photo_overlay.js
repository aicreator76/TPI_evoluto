/* WOW Photo Overlay
   - aggiunge colonna FOTO alle tabelle cataloghi
   - aggiunge FOTO + "Numero articolo" nel pannello dettaglio
*/
(function () {
  const IMG_BASE = "./assets/img/";
  const FALLBACK_SVG =
    'data:image/svg+xml;utf8,' +
    encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96">
      <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#0b1220"/><stop offset="1" stop-color="#13213a"/>
      </linearGradient></defs>
      <rect width="96" height="96" rx="18" fill="url(#g)"/>
      <text x="48" y="54" text-anchor="middle" font-family="Arial" font-size="12" fill="#9fb3d1">NO IMG</text>
    </svg>`);

  const CODE_RX = /\b(DPI|ACC|SOT|SG|IMB|ELM|FUN)[A-Z0-9-]*-[A-Z0-9-]+\b/g;

  function codeToImg(code) {
    if (!code) return FALLBACK_SVG;
    const safe = String(code).trim().replace(/[^\w\-\.]/g, "_");
    return `${IMG_BASE}${safe}.svg`;
  }

  function ensureCssLinked() {
    // se il CSS non è linkato, lo aggiungiamo al volo (best-effort)
    const href = "./wow_photo.css";
    const has = Array.from(document.querySelectorAll('link[rel="stylesheet"]'))
      .some(l => (l.getAttribute("href") || "").includes("wow_photo.css"));
    if (!has) {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = href;
      document.head.appendChild(link);
    }
  }

  function addPhotoColumnToTable(table) {
    if (!table) return;
    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");
    if (!thead || !tbody) return;

    // già fatto?
    const ths = Array.from(thead.querySelectorAll("th")).map(x => x.textContent.trim().toLowerCase());
    if (ths.includes("foto")) return;

    // aggiungi TH "Foto" in prima posizione
    const headerRow = thead.querySelector("tr");
    if (headerRow) {
      const th = document.createElement("th");
      th.textContent = "Foto";
      headerRow.insertBefore(th, headerRow.firstChild);
    }

    // per ogni riga: prendi CODICE dal primo TD originale e inserisci cella foto davanti
    Array.from(tbody.querySelectorAll("tr")).forEach(tr => {
      const tds = Array.from(tr.querySelectorAll("td"));
      if (!tds.length) return;

      const code = (tds[0].textContent || "").trim();
      const tdImg = document.createElement("td");

      const img = document.createElement("img");
      img.className = "wow-thumb";
      img.src = codeToImg(code);
      img.alt = code;
      img.loading = "lazy";
      img.onerror = () => { img.src = FALLBACK_SVG; };

      tdImg.appendChild(img);
      tr.insertBefore(tdImg, tr.firstChild);
    });
  }

  function findLikelyCatalogTables() {
    // prende tutte le tabelle "grandi" della pagina (cataloghi)
    return Array.from(document.querySelectorAll("table"))
      .filter(t => (t.textContent || "").includes("Codice") && (t.querySelectorAll("tr").length >= 3));
  }

  function findDetailPanel() {
    // pannello che contiene "Timeline revisioni" (come nella tua UI)
    const nodes = Array.from(document.querySelectorAll("*"))
      .filter(n => (n.textContent || "").includes("Timeline revisioni"));
    if (!nodes.length) return null;

    // risali a un container grande
    let el = nodes[0];
    for (let i = 0; i < 6; i++) {
      if (!el) break;
      if ((el.className || "").toString().match(/detail|modal|panel|drawer/i)) return el;
      el = el.parentElement;
    }
    return nodes[0].closest("section,div") || nodes[0].parentElement;
  }

  function extractCodeFromText(txt) {
    if (!txt) return null;
    const m = txt.match(CODE_RX);
    return m ? m[0] : null;
  }

  function enhanceDetailPanel(panel) {
    if (!panel) return;
    if (panel.__wowPhotoDone) return; // evita duplicati

    const code = extractCodeFromText(panel.innerText || "");
    if (!code) return;

    // cerca un punto “alto” dove inserire (prima di Timeline)
    const anchor = Array.from(panel.querySelectorAll("*"))
      .find(n => (n.textContent || "").trim().toLowerCase() === "timeline revisioni / eventi")
      || Array.from(panel.querySelectorAll("*"))
      .find(n => (n.textContent || "").includes("Timeline revisioni"));

    const wrap = document.createElement("div");

    const img = document.createElement("img");
    img.className = "wow-photo-lg";
    img.src = codeToImg(code);
    img.alt = code;
    img.loading = "lazy";
    img.onerror = () => { img.src = FALLBACK_SVG; };

    const box = document.createElement("div");
    box.className = "wow-articolo";
    box.innerHTML = `<span>Numero articolo</span> <span class="wow-tag-articolo"><b>${code}</b></span>`;

    wrap.appendChild(img);
    wrap.appendChild(box);

    if (anchor && anchor.parentElement) {
      anchor.parentElement.insertBefore(wrap, anchor);
    } else {
      panel.insertBefore(wrap, panel.firstChild);
    }

    panel.__wowPhotoDone = true;
  }

  function run() {
    ensureCssLinked();

    // 1) FOTO nelle tabelle catalogo
    findLikelyCatalogTables().forEach(addPhotoColumnToTable);

    // 2) FOTO + NUMERO ARTICOLO nel dettaglio (con observer, perché cambia live)
    const obs = new MutationObserver(() => {
      const panel = findDetailPanel();
      enhanceDetailPanel(panel);

      // anche se ricarica i cataloghi, rimetti la colonna foto
      findLikelyCatalogTables().forEach(addPhotoColumnToTable);
    });
    obs.observe(document.body, { childList: true, subtree: true });

    // kick iniziale
    enhanceDetailPanel(findDetailPanel());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
