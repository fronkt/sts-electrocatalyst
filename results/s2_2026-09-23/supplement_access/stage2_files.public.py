"""Stage 2: actual file routes.

Lim 2021: publisher supplementary-material landing URLs registered in Crossref for the
five component DOIs (s001-s005), Frontiers figshare portal records, ndownloader files.
Lee 2022: Wiley publisher routes (pdfdirect, downloadSupplement, full, Crossref TDM links
without a token), PMC OA web service package, Europe PMC supplementaryFiles + full-text
XML + PDF render, MPG PuRe repository REST record.
"""
import json

from access_log import fetch, json_of

LIM = "10.3389/fenrg.2021.606313"
LEE = "10.1002/cssc.202200015"
EMAIL = "<contact-email-redacted>"
BROWSER = {"Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8"}

# ---- Lim: publisher component landing pages (as registered for each s00N DOI)
for n in range(1, 6):
    sdoi = f"{LIM}.s00{n}"
    fetch(f"lim2021_s00{n}_publisher_landing",
          f"https://www.frontiersin.org/articles/{LIM}/supplementary-material/{sdoi}",
          "publisher_si_component_url", "lim2021", headers=BROWSER)
fetch("lim2021_publisher_si_anchor",
      f"https://www.frontiersin.org/articles/{LIM}/full#supplementary-material",
      "publisher_si_landing", "lim2021", headers=BROWSER, ext="html")

# ---- Lim: figshare portal records + files
lim_ids = [13902611, 13902614, 13902620, 13902623, 13902626]
files_manifest = []
for aid in lim_ids:
    rec = fetch(f"lim2021_figshare_{aid}", f"https://api.figshare.com/v2/articles/{aid}",
                "figshare_article", "lim2021", ext="json")
    meta = json_of(rec) or {}
    for f in meta.get("files", []):
        files_manifest.append({"article_id": aid, "doi": meta.get("doi"),
                               "resource_doi": meta.get("resource_doi"),
                               "title": meta.get("title"), "file": f})
        ext = f["name"].rsplit(".", 1)[-1].lower()
        fetch(f"lim2021_file_{f['id']}", f["download_url"], "figshare_ndownloader", "lim2021",
              ext=ext, note=f"figshare name={f['name']} computed_md5={f.get('computed_md5')}")
(__import__("pathlib").Path(__file__).parent / "lim2021_figshare_manifest.json").write_text(
    json.dumps(files_manifest, indent=2), encoding="utf-8")

# ---- Lee: publisher routes
fetch("lee2022_wiley_pdfdirect", f"https://onlinelibrary.wiley.com/doi/pdfdirect/{LEE}",
      "publisher_pdf_unpaywall", "lee2022", headers=BROWSER)
fetch("lee2022_wiley_si_direct",
      "https://chemistry-europe.onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002%2Fcssc.202200015&file=cssc202200015-sup-0001-misc_information.pdf",
      "publisher_si_direct", "lee2022", headers=BROWSER)
fetch("lee2022_wiley_full", f"https://chemistry-europe.onlinelibrary.wiley.com/doi/full/{LEE}",
      "publisher_si_landing", "lee2022", headers=BROWSER, ext="html")
fetch("lee2022_crossref_tdm_pdf", f"https://onlinelibrary.wiley.com/doi/pdf/{LEE}",
      "crossref_link_text_mining_no_token", "lee2022", headers=BROWSER)
fetch("lee2022_crossref_tdm_xml", f"https://onlinelibrary.wiley.com/doi/full-xml/{LEE}",
      "crossref_link_text_mining_no_token", "lee2022", headers=BROWSER)

# ---- Lee: PMC / Europe PMC
PMC = "PMC9321688"
fetch("lee2022_pmc_oa_service", "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi",
      "pmc_oa_service", "lee2022", params={"id": PMC}, ext="xml")
fetch("lee2022_europepmc_supplementary", f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles",
      "europepmc_supplementary_files", "lee2022", ext="zip")
fetch("lee2022_europepmc_fulltextxml", f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML",
      "europepmc_fulltext_xml", "lee2022", ext="xml")
fetch("lee2022_europepmc_pdf_render", "https://europepmc.org/backend/ptpmcrender.fcgi",
      "europepmc_pdf_render", "lee2022", params={"accid": PMC, "blobtype": "pdf"}, ext="pdf")

# ---- Lee: MPG PuRe repository record (REST)
fetch("lee2022_pure_item_rest", "https://pure.mpg.de/rest/items/item_3379113",
      "institutional_repository_rest", "lee2022", ext="json")
fetch("lee2022_pure_component_retry",
      "https://pure.mpg.de/pubman/item/item_3379113_6/component/file_3400083/ChemSusChem%2B-%2B2022%2B-%2BLee%2B-%2BEpitaxial%2BCore%25u2010Shell%2BOxide%2BNanoparticles%2BFirst%25u2010Principles%2BEvidence%2Bfor%2BIncreased%2BActivity%2Band.pdf",
      "institutional_repository_file", "lee2022", headers=BROWSER)
