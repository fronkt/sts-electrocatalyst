"""Step 3: one ordinary GET per legal open-access / publisher / repository link.

Every attempt (success or failure) is receipted in receipts.jsonl and summarised in
download_attempts.json. No authentication, paywall bypass or shadow library.
"""
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from httpfetch import get, ROOT  # noqa: E402

TARGETS = [
    # case, label, url, role
    ("T01", "inico_article_wiley_pdfdirect", "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/cctc.202400813", "article"),
    ("T01", "inico_si_wiley", "https://chemistry-europe.onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002%2Fcctc.202400813&file=cctc202400813-sup-0001-misc_information.pdf", "si"),
    ("T02", "gauthier_acs_pdf", "https://pubs.acs.org/doi/pdf/10.1021/acs.jpcc.7b02383", "article"),
    ("T02", "gauthier_acs_suppl_page", "https://pubs.acs.org/doi/suppl/10.1021/acs.jpcc.7b02383", "si_listing"),
    ("T04", "divanis2020_rsc_pdf", "https://pubs.rsc.org/en/content/articlepdf/2020/sc/c9sc05897d", "article"),
    ("T04", "divanis2020_curis_pdf", "https://curis.ku.dk/ws/files/239911739/c9sc05897d.pdf", "article_submitted"),
    ("T04", "divanis2020_epmc_xml", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8157516/fullTextXML", "article_xml"),
    ("T04", "divanis2020_epmc_suppl", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8157516/supplementaryFiles", "si_zip"),
    ("T05", "mom2014_acs_pdf", "https://pubs.acs.org/doi/pdf/10.1021/jp409373c", "article"),
    ("P01", "zheng2025_mdpi_pdf", "https://www.mdpi.com/2073-4344/15/8/770/pdf?version=1755079145", "article"),
    ("P01", "zheng2025_mdpi_html", "https://www.mdpi.com/2073-4344/15/8/770", "article_html"),
    ("P02", "iro2nano_elsevier_api", "https://api.elsevier.com/content/article/PII:S016943322100667X?httpAccept=text/plain", "article_text"),
    ("P03", "kuo2017_acs_pdf", "https://pubs.acs.org/doi/pdf/10.1021/jacs.6b11932", "article"),
    ("P04", "ssrn7293461_landing", "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7293461", "landing"),
    ("P05", "snse2tio2_nature_pdf", "https://www.nature.com/articles/s41699-026-00721-1.pdf", "article"),
    ("P05", "snse2tio2_nature_html", "https://www.nature.com/articles/s41699-026-00721-1", "article_html"),
    ("P06", "conirO2_elsevier_api", "https://api.elsevier.com/content/article/PII:S0021951722000616?httpAccept=text/plain", "article_text"),
    ("P08", "divanis2021_rsc_pdf", "https://pubs.rsc.org/en/content/articlepdf/2021/cp/d1cp02999a", "article"),
    ("P08", "divanis2021_rsc_html", "https://pubs.rsc.org/en/content/articlehtml/2021/cp/d1cp02999a", "article_html"),
    ("P08", "divanis2021_ku_pdf", "https://researchprofiles.ku.dk/files/282092477/d1cp02999a.pdf", "article_repository"),
    ("P08", "divanis2021_rsc_si", "https://www.rsc.org/suppdata/d1/cp/d1cp02999a/d1cp02999a1.pdf", "si"),
    ("P08", "divanis2021_chemrxiv_v1_pdf", "https://chemrxiv.org/engage/api-gateway/chemrxiv/assets/orp/resource/item/60daf482bc1d6e36e6cd0134/original/lifting-the-discrepancy-between-experimental-results-and-the-theoretical-predictions-for-the-catalytic-activity-of-ru-o2-110-towards-oxygen-evolution-reaction.pdf", "preprint_v1"),
    ("P09", "chem2021_wiley_pdfdirect", "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/chem.202102356", "article"),
    ("P09", "chem2021_epmc_xml", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9293344/fullTextXML", "article_xml"),
    ("P09", "chem2021_epmc_suppl", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9293344/supplementaryFiles", "si_zip"),
    ("P10", "scimeetings_exhibit", "https://scimeetings.acs.org/exhibit/Computational-study-dissolution-oxygen-evolution/3428631", "landing"),
    ("P11", "strain2022_elsevier_api", "https://api.elsevier.com/content/article/PII:S2468606922001459?httpAccept=text/plain", "article_text"),
    ("P12", "copo2014_elsevier_api", "https://api.elsevier.com/content/article/PII:S0378775314008829?httpAccept=text/plain", "article_text"),
    ("V01", "iro2anion_acs_pdf", "https://pubs.acs.org/doi/pdf/10.1021/acs.jpcc.3c08103", "article"),
    ("V01", "iro2anion_chemrxiv_pdf", "https://chemrxiv.org/engage/api-gateway/chemrxiv/assets/orp/resource/item/6577cb3bfd283d7904cc4e29/original/acid-electrolyte-anions-adsorption-effects-on-ir-o2-electrocatalysts-for-oxygen-evolution-reaction.pdf", "preprint"),
]

if __name__ == "__main__":
    only = set(sys.argv[1:])
    res = []
    for case, label, url, role in TARGETS:
        if only and label not in only:
            continue
        rec, body = get(url, label, kind="file")
        rec.update({"case_id": case, "role": role})
        res.append(rec)
        print(case, label, rec.get("status"), rec.get("content_type"), rec.get("bytes"), rec.get("is_pdf_magic"))
    p = ROOT / "download_attempts.json"
    prev = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    p.write_text(json.dumps(prev + res, indent=1, ensure_ascii=False), encoding="utf-8")
