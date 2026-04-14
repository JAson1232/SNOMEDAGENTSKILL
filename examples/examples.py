"""
SNOMED CT API — usage examples demonstrating all client operations.

Run:
    python examples.py
"""

from snomed_client import SNOMEDClient

client = SNOMEDClient()


def example_search():
    print("=== Search: 'asthma' ===")
    results = client.search("asthma", limit=5)
    for r in results:
        print(f"  {r['code']}  {r['display']}")
    print()

    print("=== Search: 'diabetes' scoped to clinical findings ===")
    results = client.search("diabetes", ecl="<404684003", limit=5)
    for r in results:
        print(f"  {r['code']}  {r['display']}")
    print()


def example_lookup():
    print("=== Lookup concept 195967001 ===")
    info = client.lookup("195967001")
    print(f"  code:    {info['code']}")
    print(f"  display: {info['display']}")
    print(f"  version: {info['version']}")
    print(f"  synonyms:")
    for d in info["designations"][:3]:
        print(f"    [{d['use']}] {d['value']}")
    print()

    print("=== Quick display lookup ===")
    print(f"  22298006 → {client.get_display('22298006')}")
    print()


def example_descendants():
    print("=== Descendants of Asthma (195967001) [first 5] ===")
    descendants = client.get_descendants("195967001", limit=5)
    for d in descendants:
        print(f"  {d['code']}  {d['display']}")
    print()


def example_ecl():
    print("=== ECL: subtypes of Diabetes mellitus (<73211009) [first 5] ===")
    results = client.get_ecl("<73211009", limit=5)
    for r in results:
        print(f"  {r['code']}  {r['display']}")
    print()

    print("=== ECL: Asthma and all its subtypes (<<195967001) [first 5] ===")
    results = client.get_ecl("<<195967001", limit=5)
    for r in results:
        print(f"  {r['code']}  {r['display']}")
    print()


def example_subsumes():
    print("=== Subtype checks ===")
    print(f"  Asthma is subtype of Clinical finding? {client.is_subtype_of('195967001', '404684003')}")
    print(f"  Asthma is subtype of Procedure?        {client.is_subtype_of('195967001', '71388002')}")
    print()


def example_validate():
    print("=== Validate concept IDs ===")
    print(f"  195967001 (Asthma) valid?  {client.validate('195967001')}")
    print(f"  999999999 (fake) valid?    {client.validate('999999999')}")
    print()


if __name__ == "__main__":
    example_search()
    example_lookup()
    example_descendants()
    example_ecl()
    example_subsumes()
    example_validate()
