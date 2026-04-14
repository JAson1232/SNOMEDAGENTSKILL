
import sys
import os

# Add the directory to sys.path to import snomed_client
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

codes_to_verify = [
    "13635005", "49601007", "413838009", "395914002", "710894002",
    "73211009", "13644009", "16550005", "709044004", "39628006",
    "113331007", "309990004", "22253000", "387713003", "37274000",
    "231264006", "231278007", "231279004", "231245000", "194828000",
    "414029004", "53741008", "257785002", "373110003", "29857009",
    "267036007", "442655000", "44533000", "77477000", "44321000"
]

for code in codes_to_verify:
    is_valid = client.validate(code)
    display = client.get_display(code)
    print(f"Code: {code}, Valid: {is_valid}, Display: {display}")
