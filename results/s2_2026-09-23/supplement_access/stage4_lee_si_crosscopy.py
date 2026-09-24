"""Stage 4: independent second copy of the Lee SI from the PMC Open Access AWS open-data
bucket (listed in stage 3), plus that record's metadata JSON."""
from access_log import fetch

base = "https://pmc-oa-opendata.s3.amazonaws.com/PMC9321688.1/"
fetch("lee2022_pmc_opendata_si_s001", base + "CSSC-15-0-s001.pdf", "pmc_aws_open_data", "lee2022", ext="pdf")
fetch("lee2022_pmc_opendata_meta", base + "PMC9321688.1.json", "pmc_aws_open_data", "lee2022", ext="json")
