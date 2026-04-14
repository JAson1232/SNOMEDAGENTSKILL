
import sys
import os

# Add the directory to sys.path to import snomed_client
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

codes_to_verify = [
    "38341003",
    "720568003",
    "429198000",
    "845891000000103",
    "1356877007",
    "712832005",
    "40511000119107",
    "698638005"
]

for code in codes_to_verify:
    try:
        is_valid = client.validate(code)
        display = client.get_display(code)
        print(f"Code: {code}, Valid: {is_valid}, Display: {display}")
    except Exception as e:
        print(f"Code: {code}, Error: {str(e)}")
