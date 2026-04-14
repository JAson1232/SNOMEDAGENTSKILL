
import sys
sys.path.append("/home/iason/CodingProjects/SNOMEDAPI")
from snomed_client import SNOMEDClient

client = SNOMEDClient()

# Hypertension (38341003)
# It's a disorder (disorder) -> finding site (363698007)
# Let's verify what the finding site is for Hypertension.
# The previous script said "Finding site: Hypertension" which is weird.
# Maybe I am using the wrong attribute?
# Finding site attribute = 363698007

# Let's perform a lookup for the hypertension finding site.
# Wait, lookup() returned properties. Maybe finding site isn't a property in that API call.
# Let's try searching for the finding site directly? 
# "38341003 : 363698007 = *" resulted in Hypertension itself?
# Ah, I see. 38341003 is the concept.
# If I use `client.get_axioms` it returns attributes, but it seems it returned empty list.

# Let's try to query the ECL expression for 'Hypertension' directly to see its Finding site.
# The attribute ID for 'Finding site' is 363698007.

results = client.get_ecl("38341003 : 363698007 = *")
print(results)
# Actually, this is wrong. "38341003 : 363698007 = *" means:
# Find concepts where the concept is a subtype of 38341003 AND has a finding site.
# No, I want the finding site OF 38341003.
# The SNOMED API client doesn't seem to have a direct "get attributes for concept" method
# other than `get_axioms()` which returned empty.
