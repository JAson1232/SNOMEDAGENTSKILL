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
    # Axioms
    # ------------------------------------------------------------------

    def get_axioms(self, concept_id: str, *, view: str = "inferred") -> dict:
        """
        Retrieve the defining axioms for a concept: its IS-A parents and all
        attribute-role relationships stored as FHIR properties.

        Uses the **inferred** view by default, which matches what the SNOMED
        browser displays under "Inferred Relationships".  The Ontoserver
        ``normalForm`` property is the inferred short normal form (proximate
        primitive parents + non-redundant own role groups) produced by the
        classifier — not the stated OWL axioms.

        Args:
            concept_id: SNOMED CT Concept ID (e.g. "195967001").
            view: Relationship view — "inferred" (default) uses the classifier-
                  derived ``normalForm`` property; "stated" uses
                  ``statedNormalForm`` (note: not all servers support this).

        Returns:
            Dict with keys:
              - "code": concept ID
              - "display": preferred term
              - "sufficiently_defined": True if fully defined, False if primitive,
                                        None if the server did not return this property
              - "is_a": list of {"code", "display"} immediate inferred parent concepts
              - "attributes": list of {"type_code", "type_display",
                                       "value_code", "value_display"} role-attribute dicts
        """
        # normalForm  → inferred short normal form (matches SNOMED browser inferred view)
        # statedNormalForm → stated short normal form (OWL axioms only)
        # parent      → immediate inferred IS-A parents
        normal_form_prop = "normalForm" if view == "inferred" else "statedNormalForm"
        params = [
            ("system", SNOMED_SYSTEM),
            ("code", concept_id),
            ("_format", "json"),
            ("property", normal_form_prop),
            ("property", "parent"),
            ("property", "sufficientlyDefined"),
        ]
        data = self._get(f"{self.base}/CodeSystem/$lookup", params)
        return self._parse_axioms(data, normal_form_prop=normal_form_prop)

    def search_by_axiom(
        self,
        attribute_id: str,
        value_id: str,
        *,
        term: str = None,
        scope_ecl: str = None,
        include_value_descendants: bool = True,
        view: str = "inferred",
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """
        Find concepts that have a specific attribute→value axiom relationship.

        Builds an ECL attribute-refinement expression and executes it via
        ValueSet/$expand.  Optionally combines with a free-text filter and/or
        an ECL scope constraint.

        Args:
            attribute_id: SNOMED concept ID of the attribute type
                          (e.g. "363698007" for "Finding site").
            value_id: SNOMED concept ID of the attribute value target
                      (e.g. "39607008" for "Lung structure").
            term: Optional free-text filter applied on top of the axiom
                  constraint (e.g. "pneumonia").
            scope_ecl: Optional ECL expression to restrict the search domain
                       (e.g. "<404684003" to limit to clinical findings only).
            include_value_descendants: When True (default), also matches
                                       concepts whose attribute value is any
                                       descendant of value_id (<<value_id in ECL).
            view: Relationship view — "inferred" (default) or "stated".
            limit: Max results.
            offset: Pagination offset.

        Returns:
            List of {"code": "...", "display": "..."} dicts.

        Examples:
            # Clinical findings with Finding site in lung structures
            client.search_by_axiom("363698007", "39607008", scope_ecl="<404684003")

            # Any concept caused by a bacterium, narrowed by text
            client.search_by_axiom("246075003", "409822003", term="pneumonia")
        """
        value_expr = f"<<{value_id}" if include_value_descendants else value_id
        ecl = (
            f"{scope_ecl} : {attribute_id} = {value_expr}"
            if scope_ecl
            else f"* : {attribute_id} = {value_expr}"
        )
        if term:
            return self.search(term, ecl=ecl, view=view, limit=limit, offset=offset)
        return self.get_ecl(ecl, view=view, limit=limit, offset=offset)

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
    def _parse_axioms(data: dict, *, normal_form_prop: str = "normalForm") -> dict:
        result: dict = {
            "code": None,
            "display": None,
            "sufficiently_defined": None,
            "is_a": [],
            "attributes": [],
        }
        for param in data.get("parameter", []):
            name = param.get("name")
            if name == "code":
                result["code"] = param.get("valueCode")
            elif name == "display":
                result["display"] = param.get("valueString")
            elif name == "property":
                parts = {p["name"]: p for p in param.get("part", [])}
                prop_code = parts.get("code", {}).get("valueCode", "")
                value_part = parts.get("value", {})
                value_code = value_part.get("valueCode")

                if prop_code == "parent":
                    if value_code:
                        result["is_a"].append({"code": value_code, "display": ""})
                elif prop_code == "sufficientlyDefined":
                    val = next(
                        (v for k, v in value_part.items() if k.startswith("value")),
                        None,
                    )
                    result["sufficiently_defined"] = val
                elif prop_code == normal_form_prop:
                    norm_str = next(
                        (v for k, v in value_part.items() if k.startswith("value")),
                        None,
                    )
                    if isinstance(norm_str, str):
                        result["attributes"] = SNOMEDClient._parse_normal_form_attributes(norm_str)
        return result

    @staticmethod
    def _parse_normal_form_attributes(normal_form: str) -> list[dict]:
        """
        Extract attribute-value pairs from a SNOMED CT normalForm expression.

        The normalForm returned by Ontoserver is the **inferred** short normal
        form.  Its grammar looks like:

          <<< conceptId|FSN|:{attrId|...|=valId|...|, attrId|...|=(complexExpr),...}
          === primitiveParentId|...|+...  :{...},...

        Each ``{...}`` block is a role group.  Within it, attribute-value pairs
        are separated by commas **at the top level only** — values can themselves
        be postcoordinated expressions wrapped in ``(...)`` containing nested
        commas and ``=`` signs.  We parse only top-level pairs so that qualifiers
        inside a complex value (e.g. ``Finding site = (Lung : Laterality = Side)``)
        are not incorrectly extracted as standalone attributes.

        For complex (postcoordinated) values, the primary concept ID is extracted
        from the opening of the parenthesised expression.
        """
        attributes = []
        # Each {…} block is one role group; note: no nested {…} appear inside (…)
        role_groups = re.findall(r'\{([^}]+)\}', normal_form)
        for group in role_groups:
            # Split only at top-level commas — ignore commas inside (…)
            for pair in SNOMEDClient._split_top_level(group, ","):
                pair = pair.strip()
                # Match: attrId|display|=<value>
                m = re.match(r'^(\d+)\|([^|]*)\|=(.*)', pair, re.DOTALL)
                if not m:
                    continue
                type_code, type_display, value_str = m.group(1), m.group(2), m.group(3).strip()

                if value_str.startswith("("):
                    # Postcoordinated value — extract the leading concept only
                    inner = re.match(r'\((\d+)\|([^|]*)\|', value_str)
                    if not inner:
                        continue
                    value_code, value_display = inner.group(1), inner.group(2)
                else:
                    # Simple concept value: id|display|
                    simple = re.match(r'^(\d+)\|([^|]*)\|', value_str)
                    if not simple:
                        continue
                    value_code, value_display = simple.group(1), simple.group(2)

                attributes.append({
                    "type_code": type_code,
                    "type_display": type_display,
                    "value_code": value_code,
                    "value_display": value_display,
                })
        return attributes

    @staticmethod
    def _split_top_level(s: str, delimiter: str) -> list[str]:
        """Split *s* by *delimiter* only at depth-0 (not inside parentheses)."""
        parts: list[str] = []
        depth = 0
        buf: list[str] = []
        for ch in s:
            if ch == "(":
                depth += 1
                buf.append(ch)
            elif ch == ")":
                depth -= 1
                buf.append(ch)
            elif ch == delimiter and depth == 0:
                parts.append("".join(buf))
                buf = []
            else:
                buf.append(ch)
        if buf:
            parts.append("".join(buf))
        return parts

    @staticmethod
    def _param_value(data: dict, name: str):
        for param in data.get("parameter", []):
            if param.get("name") == name:
                for k, v in param.items():
                    if k.startswith("value"):
                        return v
        return None
