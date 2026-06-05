## ADDED Requirements

### Requirement: Serve a local Codex research cockpit
The lab SHALL provide a local web application that can run inside the Codex in-app browser and visualize repository research state.

#### Scenario: Start the cockpit
- **WHEN** the user runs the cockpit start command from the repo root
- **THEN** a local HTTP server starts without requiring external package installation
- **AND** the server prints a localhost URL suitable for opening in the Codex in-app browser

#### Scenario: Load in Codex browser
- **WHEN** the user opens the cockpit URL in Codex's in-app browser
- **THEN** the first screen shows the current lab overview rather than a landing page
- **AND** it shows tracks, active OpenSpec changes, experiments, papers, and chart summaries

### Requirement: Index repo-backed research data
The cockpit SHALL build its state from repo files and preserve source file paths for every derived item.

#### Scenario: Index tracks
- **WHEN** the indexer scans `research/*`
- **THEN** it identifies research tracks, README summaries, note counts, experiment counts, and evidence counts
- **AND** each track item links back to the relevant repo path

#### Scenario: Index experiments
- **WHEN** the indexer scans experiment folders
- **THEN** it reads common artifacts such as `summary.json`, `case-metrics.json`, `failure-classifications.json`, `artifact-manifest.json`, `commands.md`, and `README.md`
- **AND** it extracts comparable metrics such as case count, pass rate, mean score, controls, failures, datasets, models, and generated timestamps when present

#### Scenario: Index paper evidence
- **WHEN** the indexer scans paper-harvest evidence folders
- **THEN** it reads paper summaries, arXiv IDs, OpenAlex IDs, publication years, OA status, raw output paths, and no-PDF status
- **AND** it clearly labels raw provider artifacts as evidence rather than curated claims

#### Scenario: Index OpenSpec state
- **WHEN** the indexer scans `openspec/changes`
- **THEN** it extracts active change names, status, completed task counts, total task counts, and artifact presence
- **AND** it distinguishes archived changes from active changes

### Requirement: Visualize experiment and evidence data
The cockpit SHALL provide built-in charts that make research state and experiment outcomes easier to compare.

#### Scenario: View experiment charts
- **WHEN** experiment summary data includes controls or pass-rate style metrics
- **THEN** the cockpit shows comparative charts for controls, pass rates, mean scores, and case counts
- **AND** chart rows retain source experiment links

#### Scenario: View benchmark charts
- **WHEN** benchmark result data includes prompt-processing, token, latency, or savings metrics
- **THEN** the cockpit shows compact trend or comparison charts
- **AND** missing metrics are treated as unavailable rather than zero

#### Scenario: View paper charts
- **WHEN** paper harvest data is present
- **THEN** the cockpit shows paper counts by year, OA status, and source/evidence folder
- **AND** it surfaces whether PDFs or full-text artifacts were downloaded

### Requirement: Support Codex-native agent actions
The cockpit SHALL help the user hand structured research work back to the Codex thread without hiding the action.

#### Scenario: Generate an action prompt
- **WHEN** the user selects an agent action such as refresh status, harvest papers, summarize failures, or draft a falsifying test
- **THEN** the cockpit produces a copyable prompt containing target paths, current context, expected artifacts, and verification criteria
- **AND** the prompt is suitable to paste into the current Codex thread

#### Scenario: Avoid silent mutation
- **WHEN** the user interacts with v1 cockpit controls
- **THEN** the cockpit does not directly edit research files, launch experiments, delete artifacts, or commit changes
- **AND** mutation remains the responsibility of the Codex thread following an explicit user prompt

### Requirement: Preserve research discipline in the UI
The cockpit SHALL reflect the lab's research rules rather than just display generic metrics.

#### Scenario: Show experiment discipline
- **WHEN** experiment artifacts lack hypothesis, baseline, controls, metrics, confounders, raw artifact path, or stop rule signals
- **THEN** the cockpit flags those gaps as research-discipline warnings

#### Scenario: Show claim discipline
- **WHEN** notes or summaries contain paper-facing or novelty-oriented language
- **THEN** the cockpit highlights associated evidence and prior-art links when available
- **AND** does not label claims as proven solely from metrics
