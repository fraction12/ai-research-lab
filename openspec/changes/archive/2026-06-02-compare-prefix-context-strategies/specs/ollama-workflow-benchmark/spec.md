## ADDED Requirements

### Requirement: Compare full-prompt and prefix-context strategies

The benchmark SHALL compare a full-prompt baseline against a prefix-context strategy for the same workflow fixture.

#### Scenario: Run comparison mode

- **WHEN** the user selects comparison mode
- **THEN** the system runs each selected scenario with the full prompt baseline
- **AND** the system primes a reusable prefix context and runs each selected scenario tail with that context

#### Scenario: Report strategy deltas

- **WHEN** comparison mode completes
- **THEN** the system reports baseline prompt evaluation cost, prefix-context prime cost, prefix-context tail cost, amortized prefix-context cost, and the delta between strategies

### Requirement: Build reusable prefix from stable blocks

The prefix-context strategy SHALL build the reusable prefix from stable or semi-stable blocks common to the selected scenarios.

#### Scenario: Common reusable blocks exist

- **WHEN** selected scenarios share stable or semi-stable blocks
- **THEN** the system primes Ollama with those blocks before running volatile tails

#### Scenario: No reusable prefix exists

- **WHEN** selected scenarios do not share any stable or semi-stable blocks
- **THEN** the system exits with an actionable error explaining that prefix-context comparison requires reusable blocks

### Requirement: Mark Ollama context reuse as a proxy

The benchmark SHALL mark prefix-context results as a proxy measurement rather than proof of SSD-backed KV reuse.

#### Scenario: Prefix-context result is persisted

- **WHEN** the system writes prefix-context result metadata
- **THEN** the metadata records that Ollama `context` reuse is deprecated API behavior and not persistent SSD-backed KV cache

### Requirement: Avoid accidental exact replay in repeated samples

The benchmark SHALL support repeated samples that vary the volatile request so exact-prompt replay does not hide changed-tail prompt cost.

#### Scenario: Vary repeated runs

- **WHEN** the user enables varied repeated runs
- **THEN** the system appends a benchmark-only run marker to each full prompt or changed-tail prompt
- **AND** the system does not append that marker to the reusable prefix prime

### Requirement: Preserve reusable prefix alignment

The benchmark SHALL keep volatile benchmark metadata after reusable prompt blocks so the measured prompt layout reflects stable-prefix reuse.

#### Scenario: Assemble scenario prompt

- **WHEN** the system assembles a scenario prompt
- **THEN** stable and semi-stable blocks appear before scenario-specific benchmark metadata
