"""Stage 3: Lee 2022 article-PDF routes discovered in stage 2.

- MPG PuRe REST component content endpoint named in the item record
  (publisher-version, CC BY 4.0, MD5 94617fc3fce5269c8400cbd15de1fd1e).
- PMC OA web service at its current host, and the PMC Open Access AWS open-data bucket.
"""
from access_log import fetch

PMC = "PMC9321688"
fetch("lee2022_pure_rest_content",
      "https://pure.mpg.de/rest/items/item_3379113_6/component/file_3400083/content",
      "institutional_repository_rest_content", "lee2022", ext="pdf")
fetch("lee2022_pmc_oa_service_newhost", "https://pmc.ncbi.nlm.nih.gov/tools/oa-service/oa.fcgi",
      "pmc_oa_service", "lee2022", params={"id": PMC}, ext="xml")
fetch("lee2022_pmc_oa_service_utils", "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi",
      "pmc_oa_service", "lee2022", params={"id": PMC, "format": "pdf"}, ext="xml")
fetch("lee2022_pmc_opendata_listing", "https://pmc-oa-opendata.s3.amazonaws.com/",
      "pmc_aws_open_data", "lee2022", params={"list-type": "2", "prefix": f"{PMC}."}, ext="xml")
