# Validation rule catalog (excerpt)

This excerpt demonstrates stable-ID cross-references using five representative
rules drawn from `rules/rules.yaml`. The full catalog ships in the canonical
`@adobe/design-data-spec` package.

## Rules

<dl>

<dt><dfn id="SPEC-001" export>SPEC-001</dfn> — `alias-target-exists`</dt>
<dd>

- **Severity:** error
- **Category:** reference-integrity
- **Assert:** Every alias `$ref` MUST resolve to an existing token in the dataset.
- **Message:** `Alias target not found for $ref: {path}`
- **Introduced in:** `1.0.0-draft`

</dd>

<dt><dfn id="SPEC-005" export>SPEC-005</dfn> — `cascade-coverage`</dt>
<dd>

- **Severity:** error
- **Category:** completeness
- **Assert:** Mode set declarations MUST satisfy coverage rules (e.g. `default ∈ modes`; peer mode requirements from coverage metadata).
- **Message:** `Mode-set coverage violation for {mode_set}`
- **Introduced in:** `1.0.0-draft`

</dd>

<dt><dfn id="SPEC-006" export>SPEC-006</dfn> — `specificity-correctness`</dt>
<dd>

- **Severity:** warning
- **Category:** type-safety
- **Assert:** When two tokens from the same layer match a context with equal specificity, the tie MUST be broken by document order (earlier in file wins; lexicographically earlier file path wins across files). Ties MUST be reported as warnings.
- **Message:** `Ambiguous cascade resolution (specificity tie) between {token_a} and {token_b} for context {context}; resolved by document order`
- **Introduced in:** `1.0.0-draft`

</dd>

<dt><dfn id="SPEC-009" export>SPEC-009</dfn> — `name-field-enum-sync`</dt>
<dd>

- **Severity:** warning
- **Category:** naming-consistency
- **Assert:** Recognized name object fields (`component`, `state`, `variant`, etc.) SHOULD use values drawn from the corresponding design-system-registry enums when those enums are available.
- **Message:** `Token name field '{field}' value '{value}' is not in the design-system-registry enum for '{field}'`
- **Introduced in:** `1.0.0-draft`

</dd>

<dt><dfn id="SPEC-017" export>SPEC-017</dfn> — `string-name-tech-debt`</dt>
<dd>

- **Severity:** warning
- **Category:** tech-debt
- **Assert:** Token names SHOULD be structured name objects. A plain string name is permitted as a temporary escape hatch but MUST be treated as tech debt and tracked for remediation.
- **Message:** `Token "{name}" uses a string name instead of a name object — treat as tech debt and plan remediation`
- **Spec ref:** [String-name escape hatch](token-format.md#string-name-escape-hatch)
- **Introduced in:** `1.0.0-draft`

</dd>

</dl>
