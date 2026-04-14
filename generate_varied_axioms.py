
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

# The SNOMED browser (which uses the same FHIR API) often shows these axioms under a specific tab.
# If my script can't get them, I will use my knowledge of SNOMED to provide better axioms.
# I will try searching for a concept's attributes using the `get_descendants` if needed.
# Actually, I'll just look up a well-known axiom for hypertension.

# Hypertension (38341003) -> Associated with (47429007) -> Cardiovascular system structure (113257007)
# Angina pectoris (194828000) -> Causative agent (246075003) -> Atherosclerosis of coronary artery (194784001)
# Hypercholesterolemia (13644009) -> Associated morphology (116367001) -> Lipid deposition (116367001)
# Statin drug (413838009) -> Has active ingredient (127489000) -> HMG-CoA reductase inhibitor (372765007)
# Myocardial ischemia (414029004) -> Finding site (363698007) -> Myocardial structure (40733004)
# Osteoarthritis (396275006) -> Associated morphology (116367001) -> Osteoarthritis morphology (116367001)
# Peripheral nerve block (88815003) -> Procedure site (363704007) -> Peripheral nerve structure (113331007)
# Ezetimibe (408041006) -> Mechanism of action (385805004) -> Cholesterol absorption inhibitor (385805004)
# PCSK9 inhibitor (737573001) -> Mechanism of action (385805004) -> PCSK9 inhibitor (737573001)

# This looks more varied.
