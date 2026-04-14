
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

results = client.search("Coronary computed tomography angiography")
for r in results:
    print(f"{r['display']} ({r['code']}): {client.validate(r['code'])}")
