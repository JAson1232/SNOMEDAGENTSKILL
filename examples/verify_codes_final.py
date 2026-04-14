
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

concepts = [
    ("Hypertension", "38341003"),
    ("Angina pectoris", "194828000"),
    ("Hypercholesterolemia", "13644009"),
    ("Statin drug", "413838009"),
    ("Myocardial ischemia", "414029004"),
    ("Osteoarthritis", "396275006"),
    ("Peripheral nerve block", "88815003"),
    ("Chronic kidney disease", "709044004"),
    ("Ezetimibe", "408041006"),
    ("PCSK9 inhibitor", "737573001")
]

for name, code in concepts:
    valid = client.validate(code)
    print(f"{name} ({code}): {valid}")
