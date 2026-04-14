
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

concepts = {
    "Hypertension": "38341003",
    "Angina pectoris": "194828000",
    "Hypercholesterolemia": "13644009",
    "Statin drug": "413838009",
    "Myocardial ischemia": "414029004",
    "Osteoarthritis": "396275006",
    "Peripheral nerve block": "88815003",
    "Ezetimibe": "408041006",
    "PCSK9 inhibitor": "737573001"
}

# The property code for "Finding site" or other attributes often comes in as
# just the concept ID, but lookup() might need to be explicitly queried
# for property details if CodeSystem/$lookup doesn't return them directly.
# Wait, looking at the code:
# elif prop_code and prop_code.isdigit() and value_code:
# It seems it treats all numeric property codes as attributes.
# Let's inspect the RAW output of lookup for one of these.
concept = "38341003" # Hypertension
lookup_data = client.lookup(concept)
print(f"Lookup for {concept}:")
print(lookup_data)
