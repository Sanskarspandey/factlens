# FactLens Reconciliation Ontology & Classification Rules

## 1. Executive Summary

FactLens implements an auditable 4-way Fact Reconciliation Ontology designed to rigorously verify factual consistency across heterogeneous PDF documents without fabricating false contradictions or assuming implicit conversions.

---

## 2. The 4 Cross-Document Relationship Types

When evaluating fact $F_A$ (Document 1) against fact $F_B$ (Document 2), FactLens classifies their relationship into **exactly one** of four mutually exclusive categories:

```
                      Candidate Facts (F_A, F_B)
                                  ↓
                        Context Comparison
                                  ↓
                         Value Comparison
                                  ↓
                        Evidence Validation
                                  ↓
                       Deterministic Decision
                                  ↓
                              Ambiguous?
                             ↙          ↘
                           No            Yes
                           ↓              ↓
                        Result      LLM Reasoning
                                          ↓
                                   Schema Validation
                                          ↓
                                       Result
```

---

### 1. `CORROBORATED`
- **Definition**: Both documents make consistent assertions regarding the same entity, metric, and temporal period, with values agreeing within strict numeric tolerance.
- **Strict Criteria**:
  1. Identical or coreferent **Entity**.
  2. Identical or synonymous **Metric/Attribute**.
  3. Compatible **Time Period** and **Fiscal Year**.
  4. Compatible **Reporting Scope** (e.g. Consolidated vs Consolidated).
  5. Identical **Currency** (e.g. INR vs INR) with zero currency conversion assumptions.
  6. Normalized numeric values agree within relative tolerance:
     $$\text{Relative Difference} = \frac{|V_A - V_B|}{\max(|V_A|, |V_B|)} \le \text{MATCH\_TOLERANCE} \quad (1.0\%)$$
- **Auditable Example**:
  - *Doc A*: "Company X recorded revenue of ₹100 crore in FY2024 (Consolidated)." $\rightarrow 1,000,000,000\text{ INR}$
  - *Doc B*: "Total revenue amounted to ₹1 billion during FY2024 (Consolidated)." $\rightarrow 1,000,000,000\text{ INR}$
  - **Outcome**: `CORROBORATED` (Relative Difference: $0.0\% \le 1.0\%$).

---

### 2. `CONTRADICTED`
- **Definition**: Both facts refer to the exact same entity, metric, and time period under identical reporting context, but present mutually exclusive, conflicting numerical values that exceed tolerance.
- **Strict Criteria**:
  1. Identical **Entity** and **Metric**.
  2. Identical **Time Period** / **Fiscal Year**.
  3. Compatible **Reporting Scope**, **Geography**, and **Currency**.
  4. Normalized numeric values materially diverge ($\text{Relative Difference} > 1.0\%$).
- **Explanation Requirement**:
  The system must provide an exact numerical breakdown:
  - Source reported value ($V_A$)
  - Candidate reported value ($V_B$)
  - Absolute difference ($|V_A - V_B|$)
  - Percentage difference ($\frac{|V_A - V_B|}{\max(|V_A|, |V_B|)} \times 100\%$)
- **Auditable Example**:
  - *Doc A*: "Company X revenue in FY2024 was ₹100 crore (Consolidated)." $\rightarrow 1,000,000,000\text{ INR}$
  - *Doc B*: "Company X revenue in FY2024 reached ₹150 crore (Consolidated)." $\rightarrow 1,500,000,000\text{ INR}$
  - **Outcome**: `CONTRADICTED` (Absolute diff: $₹500,000,000\text{ INR}$, Percentage diff: $33.33\%$, identical scope and currency).

---

### 3. `CONTEXTUALLY_DIFFERENT`
- **Definition**: The facts describe superficially similar metrics, but the divergence is explained by differing reporting contexts, accounting frameworks, time periods, or operational boundaries.
- **Context Takes Strict Precedence Over Numbers**: Facts with distinct contexts are **never** classified as contradictions, even if values differ.
- **Key Contextual Dimensions**:
  1. **Reporting Scope**: `Consolidated` vs `Standalone` vs `Segment`.
  2. **Temporal Scope**: `FY2023` vs `FY2024`, `Q1` vs `Q2`, `Q4 FY24` vs `Full Year FY24`.
  3. **Value Status**: `ACTUAL` vs `ESTIMATE` vs `FORECAST` vs `GUIDANCE` vs `TARGET`.
  4. **Accounting Framework**: `GAAP` vs `Non-GAAP`, `Reported` vs `Adjusted`.
  5. **Geographic Jurisdiction**: `Domestic` (e.g. India) vs `International` / `Global`.
  6. **Currency Isolation**: `INR` vs `USD` without direct exchange conversion.
- **Auditable Examples**:
  - *Consolidated vs Standalone*: "₹100 Cr (Consolidated)" vs "₹90 Cr (Standalone)" $\rightarrow$ `CONTEXTUALLY_DIFFERENT`.
  - *Temporal*: "₹100 Cr in FY2023" vs "₹150 Cr in FY2024" $\rightarrow$ `CONTEXTUALLY_DIFFERENT`.
  - *Actual vs Forecast*: "Actual was ₹100 Cr" vs "Forecast is ₹120 Cr" $\rightarrow$ `CONTEXTUALLY_DIFFERENT`.

---

### 4. `UNCERTAIN`
- **Definition**: The system does not possess sufficient or reliable information to definitively corroborate, contradict, or contextualize the claim.
- **Preserved Uncertainty Principle**: FactLens never manufactures a classification when evidence is incomplete or ambiguous.
- **Trigger Conditions**:
  1. **Missing Evidence Grounding**: Fact lacks verbatim quote in source PDF or failed extraction verification.
  2. **Unparseable Numeric Value**: Metric is stated qualitatively or raw number cannot be normalized.
  3. **Ambiguous Entity/Metric**: Entity or metric is missing or coreference is uncertain.
  4. **Sub-threshold Confidence**: High extraction ambiguity.
- **Auditable Example**:
  - *Doc A*: "Company reported revenue of ₹100 Cr."
  - *Doc B*: "Substantial volume was achieved in 2024." (Missing normalized value / ambiguous metric).
  - **Outcome**: `UNCERTAIN` (Preserves diagnostic notes in `uncertainty_notes`).

---

## 3. Decision Hierarchy & Algorithmic Rules

```text
STEP 1: Verify Grounding Evidence
        IF fact_a.evidence_quote is empty OR fact_b.evidence_quote is empty:
            RETURN UNCERTAIN (Reason: Missing verbatim grounding evidence)

STEP 2: Verify Normalized Values
        IF fact_a.normalized_value is None OR fact_b.normalized_value is None:
            RETURN UNCERTAIN (Reason: Missing or unparseable numeric value)

STEP 3: Verify Entity & Metric Plausibility
        IF fact_a.entity is None OR fact_b.entity is None OR fact_a.attribute is None OR fact_b.attribute is None:
            RETURN UNCERTAIN (Reason: Ambiguous entity or metric name)
        IF NOT entity_match OR NOT attribute_match:
            RETURN CONTEXTUALLY_DIFFERENT (Reason: Disjoint entities or metrics)

STEP 4: Evaluate Context Compatibility (Strict Precedence)
        IF dimension_differences is NOT empty:
            RETURN CONTEXTUALLY_DIFFERENT (Reason: Details differing dimensions: scope, time, status, currency, etc.)

STEP 5: Numerical Comparison on Identical Context
        rel_diff = abs(val_a - val_b) / max(abs(val_a), abs(val_b))
        IF rel_diff <= MATCH_TOLERANCE (0.01):
            RETURN CORROBORATED (Reason: Both agree within tolerance)
        ELSE:
            RETURN CONTRADICTED (Reason: Numerical contradiction with exact diffs)
```

---

## 4. Four Standard Demonstration Cases

| Case | Scenario | Fact A Context | Fact B Context | Expected Classification | Key Reason |
|---|---|---|---|---|---|
| **Case 1** | Corroboration | ₹100 Cr, FY2024, Consolidated | ₹1 Billion, FY2024, Consolidated | `CORROBORATED` | $100\text{ Cr} = 1\text{ Billion INR}$; relative diff $0.0\%$. |
| **Case 2** | Genuine Contradiction | ₹100 Cr, FY2024, Consolidated | ₹150 Cr, FY2024, Consolidated | `CONTRADICTED` | Identical context, 50% numerical discrepancy. |
| **Case 3a** | Scope Difference | ₹100 Cr, FY2024, Consolidated | ₹90 Cr, FY2024, Standalone | `CONTEXTUALLY_DIFFERENT` | Consolidated vs Standalone reporting scope. |
| **Case 3b** | Temporal Difference | ₹100 Cr, FY2023 | ₹150 Cr, FY2024 | `CONTEXTUALLY_DIFFERENT` | Distinct fiscal years (FY2023 vs FY2024). |
| **Case 3c** | Reporting Status | ₹100 Cr, ACTUAL | ₹120 Cr, FORECAST | `CONTEXTUALLY_DIFFERENT` | Actual historical performance vs future forecast. |
| **Case 4** | Failure / Ambiguity | ₹100 Cr, Evidence Verified | Unverified Quote or Missing Value | `UNCERTAIN` | Preserved uncertainty with audit trail. |
