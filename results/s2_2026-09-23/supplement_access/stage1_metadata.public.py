"""Stage 1: metadata routes (Crossref, DataCite, Unpaywall, Europe PMC, PMC, OpenAlex,
figshare, Zenodo) for Lim 2021 and Lee 2022. Records every request."""
from access_log import fetch

LIM = "10.3389/fenrg.2021.606313"
LEE = "10.1002/cssc.202200015"
EMAIL = "<contact-email-redacted>"

for tgt, doi in (("lim2021", LIM), ("lee2022", LEE)):
    fetch(f"{tgt}_crossref_work", f"https://api.crossref.org/works/{doi}", "crossref_works", tgt,
          params={"mailto": EMAIL}, ext="json")
    fetch(f"{tgt}_unpaywall", f"https://api.unpaywall.org/v2/{doi}", "unpaywall", tgt,
          params={"email": EMAIL}, ext="json")
    fetch(f"{tgt}_europepmc_search", "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
          "europepmc_search", tgt, params={"query": f'DOI:"{doi}"', "format": "json",
                                           "resultType": "core"}, ext="json")
    fetch(f"{tgt}_ncbi_idconv", "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/",
          "pmc_idconv", tgt, params={"ids": doi, "format": "json", "email": EMAIL}, ext="json")
    fetch(f"{tgt}_openalex", f"https://api.openalex.org/works/doi:{doi}", "openalex", tgt,
          params={"mailto": EMAIL}, ext="json")
    fetch(f"{tgt}_datacite_related", "https://api.datacite.org/dois", "datacite_search", tgt,
          params={"query": f'relatedIdentifiers.relatedIdentifier:"{doi}"', "page[size]": 50},
          ext="json")
    fetch(f"{tgt}_figshare_search", "https://api.figshare.com/v2/articles/search",
          "figshare_search", tgt, method="POST", ext="json",
          json_body={"resource_doi": doi, "page_size": 50})
    fetch(f"{tgt}_figshare_search_text", "https://api.figshare.com/v2/articles/search",
          "figshare_search", tgt, method="POST", ext="json",
          json_body={"search_for": f'"{doi}"', "page_size": 50})
    fetch(f"{tgt}_zenodo_search", "https://zenodo.org/api/records", "zenodo_search", tgt,
          params={"q": f'"{doi}"', "size": 25}, ext="json")

# Frontiers registers per-file supplement DOIs as <article DOI>.s00N (checked, not assumed)
for n in range(1, 7):
    sdoi = f"{LIM}.s00{n}"
    fetch(f"lim2021_si_doi_s00{n}_crossref", f"https://api.crossref.org/works/{sdoi}",
          "crossref_si_doi", "lim2021", params={"mailto": EMAIL}, ext="json")
    fetch(f"lim2021_si_doi_s00{n}_datacite", f"https://api.datacite.org/dois/{sdoi}",
          "datacite_si_doi", "lim2021", ext="json")
    fetch(f"lim2021_si_doi_s00{n}_resolve", f"https://doi.org/api/handles/{sdoi}",
          "doi_handle_api", "lim2021", ext="json")
