"""
SNOMED CT FHIR R4 Client

Uses the CSIRO Ontoserver public FHIR R4 API — no authentication required.
Base URL: https://r4.ontoserver.csiro.au/fhir

All SNOMED concepts are identified by their numeric Concept ID (e.g. "195967001").
The SNOMED system URI is: http://snomed.info/sct
"""

import re
import urllib.parse
import requests

FHIR_BASE = "https://r4.ontoserver.csiro.au/fhir"
SNOMED_SYSTEM = "http://snomed.info/sct"
SNOMED_VS = "http://snomed.info/sct?fhir_vs"


class SNOMEDClient:
    def __init__(self, fhir_base: str = FHIR_BASE):
        self.base = fhir_base.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/fhir+json"})

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        term: str,
        *,
        ecl: str = None,
        view: str = "inferred",
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """
        Search SNOMED concepts by text, optionally scoped by an ECL expression.

        Args:
            term: Free-text search term (e.g. "heart failure").
            ecl: Optional ECL expression to scope the search (e.g. "<404684003").
                 When provided, only concepts matching the ECL will be searched.
            view: Relationship view to use — "inferred" (default) or "stated".
                  "inferred" uses the classifier-derived hierarchy (recommended for
                  most queries). "stated" uses only explicitly asserted relationships.
            limit: Max results to return (default 20).
            offset: Pagination offset.

        Returns:
            List of dicts: [{"code": "...", "display": "..."}, ...]
        """
        if ecl:
            if view == "stated":
                ecl = self._apply_stated_view(ecl)
            url_param = f"{SNOMED_VS}=ecl/{urllib.parse.quote(ecl)}"
        else:
            url_param = SNOMED_VS

        params = {
            "url": url_param,
            "filter": term,
            "count": limit,
            "offset": offset,
            "_format": "json",
        }
        data = self._get(f"{self.base}/ValueSet/$expand", params)
        return self._extract_contains(data)

    # ------------------------------------------------------------------
    # Concept lookup
    # ------------------------------------------------------------------

    def lookup(self, concept_id: str, *, include_designations: bool = True) -> dict:
        """
        Look up a SNOMED concept by its Concept ID.

        Args:
            concept_id: SNOMED CT Concept ID (e.g. "195967001").
            include_designations: Include all synonyms/designations in response.

        Returns:
            Dict with keys:
              - "code": concept ID
              - "display": preferred display term
              - "designations": list of {"language", "use", "value"} dicts
              - "properties": list of {"code", "value"} dicts (e.g. inactive, parent)
              - "version": SNOMED release version string
        """
        params = {
            "system": SNOMED_SYSTEM,
            "code": concept_id,
            "_format": "json",
        }
        data = self._get(f"{self.base}/CodeSystem/$lookup", params)
        return self._parse_lookup(data)

    def get_display(self, concept_id: str) -> str | None:
        """Return the preferred display term for a concept ID, or None if not found."""
        try:
            return self.lookup(concept_id, include_designations=False)["display"]
        except requests.exceptions.HTTPError:
            return None

    # ------------------------------------------------------------------
    # Hierarchy
    # ------------------------------------------------------------------

    def get_descendants(
        self,
        concept_id: str,
        *,
        view: str = "inferred",
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """
        Get all descendants (subtypes at all levels) of a concept.

        Args:
            concept_id: SNOMED concept ID.
            view: Relationship view to use — "inferred" (default) or "stated".
                  "inferred" uses the classifier-derived IS-A hierarchy.
                  "stated" uses only explicitly asserted IS-A relationships.
            limit: Max results.
            offset: Pagination offset.

        Returns:
            List of {"code": "...", "display": "..."} dicts.
        """
        if view == "stated":
            url_param = f"{SNOMED_VS}=ecl/{urllib.parse.quote(f'<!{concept_id}')}"
        else:
            url_param = f"{SNOMED_VS}=isa/{concept_id}"
        params = {
            "url": url_param,
            "count": limit,
            "offset": offset,
            "_format": "json",
        }
        data = self._get(f"{self.base}/ValueSet/$expand", params)
        return self._extract_contains(data)

    def get_ecl(
        self,
        ecl: str,
        *,
        view: str = "inferred",
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """
        Retrieve concepts matching an ECL (Expression Constraint Language) expression.

        Args:
            ecl: ECL expression (e.g. "<404684003", "<<195967001", "<73211009 AND <404684003").
            view: Relationship view to use — "inferred" (default) or "stated".
                  "inferred" uses the classifier-derived hierarchy.
                  "stated" rewrites ECL hierarchy operators to their stated variants
                  (e.g. "<X" → "<!X", "<<X" → "<<!X").
            limit: Max results.
            offset: Pagination offset.

        Returns:
            List of {"code": "...", "display": "..."} dicts.

        ECL Operators (inferred view, default):
            <X    — all subtypes of X (excluding X)
            <<X   — X and all subtypes of X
            >X    — all supertypes of X (excluding X)
            >>X   — X and all supertypes of X
            X OR Y  — union
            X AND Y — intersection
            X MINUS Y — exclusion

        ECL Operators (stated view):
            <!X   — stated subtypes of X (excluding X)
            <<!X  — X and its stated subtypes
            >!X   — stated supertypes of X (excluding X)
            >>!X  — X and its stated supertypes
        """
        if view == "stated":
            ecl = self._apply_stated_view(ecl)
        params = {
            "url": f"{SNOMED_VS}=ecl/{urllib.parse.quote(ecl)}",
            "count": limit,
            "offset": offset,
            "_format": "json",
        }
        data = self._get(f"{self.base}/ValueSet/$expand", params)
        return self._extract_contains(data)

    # ------------------------------------------------------------------
    # Relationship checks
    # ------------------------------------------------------------------

    def is_subtype_of(self, concept_id: str, parent_id: str) -> bool:
        """
        Check if concept_id is a subtype (direct or indirect) of parent_id.

        Uses FHIR $subsumes — returns True if codeA is subsumed by codeB.

        Args:
            concept_id: The candidate subtype concept ID.
            parent_id: The potential supertype concept ID.

        Returns:
            True if concept_id is a subtype of parent_id.
        """
        params = {
            "system": SNOMED_SYSTEM,
            "codeA": concept_id,
            "codeB": parent_id,
            "_format": "json",
        }
        data = self._get(f"{self.base}/CodeSystem/$subsumes", params)
        outcome = self._param_value(data, "outcome")
        # "subsumed-by" means codeA is a subtype of codeB
        return outcome == "subsumed-by"

    def validate(self, concept_id: str) -> bool:
        """
        Check if a concept ID exists and is active in SNOMED CT.

        Args:
            concept_id: SNOMED concept ID to validate.

        Returns:
            True if the concept is valid and active.
        """
        params = {
            "url": SNOMED_SYSTEM,
            "code": concept_id,
            "_format": "json",
        }
        data = self._get(f"{self.base}/CodeSystem/$validate-code", params)
        result = self._param_value(data, "result")
        return result is True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_stated_view(ecl: str) -> str:
        """
        Rewrite ECL hierarchy operators to use the stated (asserted) view.

        ECL 2.0 stated-view operators:
            <<X  →  <<!X   (X and its stated subtypes)
            <X   →  <!X    (stated subtypes of X)
            >>X  →  >>!X   (X and its stated supertypes)
            >X   →  >!X    (stated supertypes of X)

        Operators are processed longest-first so that << and >> are converted
        before their single-character counterparts.
        """
        # << and >> first (before < and > to avoid partial matches)
        ecl = re.sub(r'<<(?!!)', '<<!', ecl)
        ecl = re.sub(r'>>(?!!)', '>>!', ecl)
        # Then remaining < and > (not already part of <! / <<! / >! / >>!)
        ecl = re.sub(r'<(?![<!])', '<!', ecl)
        ecl = re.sub(r'>(?![>!])', '>!', ecl)
        return ecl

    def _get(self, url: str, params: dict) -> dict:
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _extract_contains(data: dict) -> list[dict]:
        return [
            {"code": e["code"], "display": e.get("display", "")}
            for e in data.get("expansion", {}).get("contains", [])
        ]

    @staticmethod
    def _parse_lookup(data: dict) -> dict:
        result = {"code": None, "display": None, "designations": [], "properties": [], "version": None}
        for param in data.get("parameter", []):
            name = param.get("name")
            if name == "code":
                result["code"] = param.get("valueCode")
            elif name == "display":
                result["display"] = param.get("valueString")
            elif name == "version":
                result["version"] = param.get("valueString")
            elif name == "designation":
                parts = {p["name"]: p for p in param.get("part", [])}
                designation = {
                    "language": parts.get("language", {}).get("valueCode"),
                    "use": parts.get("use", {}).get("valueCoding", {}).get("display"),
                    "value": parts.get("value", {}).get("valueString"),
                }
                result["designations"].append(designation)
            elif name == "property":
                parts = {p["name"]: p for p in param.get("part", [])}
                code = parts.get("code", {}).get("valueCode")
                value = next(
                    (v for k, v in parts.get("value", {}).items() if k.startswith("value")),
                    None,
                )
                if code:
                    result["properties"].append({"code": code, "value": value})
        return result

    @staticmethod
    def _param_value(data: dict, name: str):
        for param in data.get("parameter", []):
            if param.get("name") == name:
                for k, v in param.items():
                    if k.startswith("value"):
                        return v
        return None
