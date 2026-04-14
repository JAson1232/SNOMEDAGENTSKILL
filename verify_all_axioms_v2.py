
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

axioms_to_verify = [
    # (ConceptName, ConceptID, AttrName, AttrID, TargetName, TargetID)
    ("Hypertension", "38341003", "Associated with", "47429007", "Cardiovascular system structure", "113257007"),
    ("Angina pectoris", "194828000", "Causative agent", "246075003", "Atherosclerosis of coronary artery", "194784001"),
    ("Hypercholesterolemia", "13644009", "Associated morphology", "116367001", "Lipid deposition", "116367001"),
    ("Statin drug", "413838009", "Has active ingredient", "127489000", "HMG-CoA reductase inhibitor", "372765007"),
    ("Myocardial ischemia", "414029004", "Finding site", "363698007", "Myocardial structure", "40733004"),
    ("Osteoarthritis", "396275006", "Associated morphology", "116367001", "Osteoarthritis morphology", "116367001"),
    ("Peripheral nerve block", "88815003", "Procedure site", "363704007", "Peripheral nerve structure", "113331007"),
    ("Chronic kidney disease", "709044004", "Finding site", "363698007", "Kidney structure", "64033007"),
    ("Ezetimibe", "408041006", "Mechanism of action", "385805004", "Cholesterol absorption inhibitor", "385805004"),
    ("PCSK9 inhibitor", "737573001", "Mechanism of action", "385805004", "PCSK9 inhibitor", "737573001")
]

for name, cid, attr_name, aid, target_name, tid in axioms_to_verify:
    print(f"--- Verifying: {name} ---")
    
    # Use search_by_axiom with scope_ecl=cid to restrict to the concept
    try:
        results = client.search_by_axiom(
            attribute_id=aid,
            value_id=tid,
            scope_ecl=cid
        )
        if results:
            print(f"  Relationship Verified: YES")
        else:
            print(f"  Relationship Verified: NO")
    except Exception as e:
        print(f"  Error: {e}")
