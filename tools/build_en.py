#!/usr/bin/env python3
"""Genera en/index.html (versión en inglés) a partir de index.html.

La página principal guarda cada texto en español y en inglés (data-es / data-en).
Este script deja el inglés escrito en el HTML para que Google lo lea en /en/.

Uso, después de cambiar index.html:   python3 tools/build_en.py
Necesita:                              pip install beautifulsoup4
"""
import json, pathlib
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://www.rossyuyuni.com"
TITLE = "Posada Rossy · Guesthouse in Uyuni from 80 Bs | Salt Flats Tours"
DESC = ("Posada Rossy, a family-run guesthouse in Uyuni, Bolivia. Single room 80 Bs, "
        "couple 120 Bs per night. Hot shower 24 h, WiFi and shared kitchen. Book directly on WhatsApp.")
OG_TITLE = "Posada Rossy · Guesthouse in Uyuni, Bolivia"
OG_DESC = "Single 80 Bs, couple 120 Bs per night. Book directly on WhatsApp."
LD_DESC = "Family-run guesthouse in Uyuni with hot shower 24 h, WiFi and shared kitchen. Uyuni Salt Flats tours."
ARIA = {
    "Principal": "Main", "Menú": "Menu", "Filtrar fotos": "Filter photos", "Reseñas": "Reviews",
    "Aviso de cookies": "Cookie notice", "Foto ampliada": "Enlarged photo", "Cerrar": "Close",
    "Foto anterior": "Previous photo", "Foto siguiente": "Next photo",
    "Posada Rossy, inicio": "Posada Rossy, home",
    "Croquis: la posada está en la calle Fernando Alonso, entre las calles Sucre y Camacho":
        "Sketch map: the guesthouse is on Calle Fernando Alonso, between Sucre and Camacho streets",
}

soup = BeautifulSoup((ROOT / "index.html").read_text(encoding="utf-8"), "html.parser")
soup.html["lang"] = "en"

for el in soup.select("[data-en]"):
    el.string = el["data-en"]
for el in soup.select("[data-en-html]"):
    el.clear()
    el.append(BeautifulSoup(el["data-en-html"], "html.parser"))
for el in soup.select("[data-en-alt]"):
    el["alt"] = el["data-en-alt"]
for el in soup.select("[data-en-aria]"):
    el["aria-label"] = el["data-en-aria"]
for el in soup.select("[aria-label]"):
    if el["aria-label"] in ARIA:
        el["aria-label"] = ARIA[el["aria-label"]]
for a in soup.select("#lang-es, #lang-en, [data-set-lang]"):
    a["aria-current"] = "true" if a.get("hreflang") == "en" else "false"

soup.title.string = TITLE
soup.find("meta", attrs={"name": "description"})["content"] = DESC
soup.find("meta", property="og:title")["content"] = OG_TITLE
soup.find("meta", property="og:description")["content"] = OG_DESC
soup.find("meta", property="og:url")["content"] = SITE + "/en/"
soup.find("meta", property="og:locale")["content"] = "en_US"
soup.find("link", rel="canonical")["href"] = SITE + "/en/"

for sc in soup.find_all("script", type="application/ld+json"):
    data = json.loads(sc.string)
    if data.get("@type") == "LodgingBusiness":
        data["description"] = LD_DESC
    elif data.get("@type") == "FAQPage":
        data["mainEntity"] = [
            {"@type": "Question", "name": d.summary["data-en"],
             "acceptedAnswer": {"@type": "Answer", "text": d.p["data-en"]}}
            for d in soup.select(".faq details")]
    sc.string = "\n" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"

out = ROOT / "en" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(soup.decode(formatter="minimal"), encoding="utf-8")
print("Escrito", out.relative_to(ROOT), f"({out.stat().st_size // 1024} KB)")
