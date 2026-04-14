
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

concepts = [
    ("38341003", "Hypertension"),
    ("194828000", "Angina pectoris"),
    ("13644009", "Hypercholesterolemia"),
    ("413838009", "Statin drug"),
    ("414029004", "Myocardial ischemia"),
    ("39628006", "Osteoarthritis"),
    ("231264006", "Peripheral nerve block"),
    ("709044004", "Chronic kidney disease"),
    ("395914002", "Ezetimibe"),
    ("710894002", "PCSK9 inhibitor")
]

for code, name in concepts:
    try:
        # Check concept validity
        is_valid = client.validate(code)
        # We can't easily query the finding site directly with the provided client without knowing the specific API method.
        # But let's check the description and if it exists.
        print(f"Concept: {name} ({code}), Valid: {is_valid}")
    except Exception as e:
        print(f"Error checking {name} ({code}): {str(e)}")
