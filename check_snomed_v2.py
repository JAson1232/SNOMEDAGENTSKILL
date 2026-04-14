from snomed_client import SNOMEDClient
import sys

def search_and_print(term):
    client = SNOMEDClient()
    try:
        results = client.search(term, limit=5)
        print(f"Results for '{term}':")
        for concept in results:
            print(f"- {concept['code']}: {concept['display']}")
    except Exception as e:
        print(f"Error searching for '{term}': {e}")

if __name__ == "__main__":
    terms = ["knee osteoarthritis", "Osteotomy", "Postoperative pain management", "opioid", "Peripheral nerve block", "Epidural anesthesia"]
    for term in terms:
        search_and_print(term)
