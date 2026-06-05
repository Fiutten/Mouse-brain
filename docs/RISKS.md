# Risk Register

## R1: Regional modularity is decorative

Severity: high.

Failure mode:

- A generic RNN or temporal baseline matches or beats the regional model on every metric.

Mitigation:

- Add baselines early.
- Measure generalization and contrafactual coherence, not just accuracy.
- Do not add biological detail before this is resolved.

## R2: Lesions are rhetorical

Severity: high.

Failure mode:

- Virtual lesions produce outputs but are not tied to empirical expectations.

Mitigation:

- Pre-register expected deficit per lesion.
- Link each lesion to evidence in the knowledge graph.
- Compare with literature or datasets containing perturbations when available.

## R3: LLM layer becomes a wrapper

Severity: medium.

Failure mode:

- Agents generate plausible text but do not improve experiments.

Mitigation:

- Keep deterministic agents first.
- Evaluate agents by executable hypotheses, blocked bad claims and traceability.

## R4: Excess biological detail

Severity: high.

Failure mode:

- More regions, cell types or mechanisms create unidentifiable parameters.

Mitigation:

- Add detail only after Level 0 proves value.
- Require each detail to improve a metric or explain a failure.

## R5: Consciousness claim contamination

Severity: high.

Failure mode:

- The project becomes speculative and unfalsifiable.

Mitigation:

- Use "access", "broadcasting", "engagement" and "global state".
- Do not claim subjective experience.

## R6: Dataset access or complexity blocks progress

Severity: medium.

Failure mode:

- Allen/IBL data ingestion takes too long or requires unavailable dependencies.

Mitigation:

- Build loader interfaces first.
- Start with small public sessions.
- Keep synthetic tests as sanity checks.

Current status:

- Loader interfaces and adapter contracts are implemented.
- Real session normalization remains open.
