import json
import requests

params = {
    "gene": "EGFR",
    "aa_change": "p.(=)",
    "dna_change": "c.2573G>A",
    "exons": "2", # optional
    "tumor": "Adenocarcinoma",
    "tissue": "Lung",
    "variant_type": "silent",
    "transcript": "ENST00000256078" #optional
}
params_cnv = {
    "variant_type": "CNV",
    "gene": "CDKN2A",
    "cnv_type": "loss",
    "tumor": "Squamous Cell Carcinoma",
    "tissue": "Lung"
}
params_fusion = {
    "variant_type": "rearrangement",
    "gene": "ERG",
    "partner_gene": "TMPRSS2",
    "tumor": "Adenocarcinoma",
    "tissue": "Prostate"
}

p = json.dumps([params])
url = 'https://pmkb.weill.cornell.edu/api/lookups'
headers = {
    'Content-Type': 'application/json'
}
response = requests.post(url, data=p, headers=headers)
print response.text.encode('utf-8')
