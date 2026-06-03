## ADDED Requirements

### Requirement: Use Printing Press as the primary paper-harvesting toolchain
The lab SHALL use Printing Press and printed provider CLIs as the primary mechanism for research-paper collection unless a custom implementation is explicitly justified by a concrete workflow gap.

#### Scenario: Start a paper-harvesting run
- **WHEN** an agent needs to collect research paper findings for a track or negative-space scan
- **THEN** the agent uses an installed printed CLI or Printing Press workflow before writing custom scraper or library code
- **AND** records the command, provider, query, timestamp, and output location

### Requirement: Keep skill scope aligned to tool purpose
The lab SHALL install general Printing Press orchestration skills in user scope and research-specific printed/focused skills in project scope.

#### Scenario: Install Printing Press orchestration skills
- **WHEN** a Printing Press orchestration skill is installed for machine-wide use
- **THEN** it is installed under the Codex user-scope skills directory

#### Scenario: Install research paper source skills
- **WHEN** a focused paper-source or generated research-harvester skill is installed for this lab
- **THEN** it is installed under this repo's `.codex/skills/` directory
- **AND** it is not installed globally unless explicitly approved

### Requirement: Preserve research evidence from provider runs
The lab SHALL preserve raw provider outputs and source metadata from paper-finding runs before using them in research claims.

#### Scenario: Save provider output
- **WHEN** a paper-finding CLI returns results used for research
- **THEN** the agent saves or references the raw output, source URLs, provider name, query, command, timestamp, and CLI version
- **AND** the resulting research note can trace each cited paper back to the provider run

#### Scenario: Provider run fails
- **WHEN** a provider request fails due to rate limiting, timeout, auth, or upstream error
- **THEN** the agent records the failed command and error rather than treating the paper search as complete

#### Scenario: arXiv Atom API is rate-limited
- **WHEN** an arXiv Atom API request is rate-limited or provider-throttled
- **THEN** the agent stops retrying that API path
- **AND** may use `openalex-pp-cli` exact arXiv DOI-form lookup plus arXiv HTML confirmation to collect metadata
- **AND** records the fallback commands, URLs, raw outputs, timestamps, and no-PDF/full-text status

### Requirement: Avoid productizing the internal harvester
The lab SHALL treat any generated paper-harvesting CLI as internal research infrastructure rather than a standalone product.

#### Scenario: Scope new functionality
- **WHEN** new harvester functionality is proposed
- **THEN** it is accepted only if it improves current research collection, provenance, dedupe, tagging, or export work
- **AND** product, marketing, or general library-manager features are excluded

### Requirement: Print an internal paper-harvester CLI
The lab SHALL use Printing Press to generate a focused internal `paper-harvester` CLI around the proven OpenAlex/arXiv fallback workflow.

#### Scenario: Generate the internal CLI
- **WHEN** the lab needs a durable paper-harvesting command instead of a one-off evidence script
- **THEN** the agent generates the CLI with `cli-printing-press`
- **AND** the generated CLI supports exact arXiv DOI-form OpenAlex lookups and arXiv HTML confirmation
- **AND** the CLI remains scoped as internal research infrastructure

#### Scenario: Install the generated skill for this repo
- **WHEN** the generated CLI has a Codex skill
- **THEN** the focused paper-harvester skill is installed under this repo's `.codex/skills/`
- **AND** the skill is not installed in user scope unless explicitly approved

### Requirement: Guard PDF and full-text collection
The lab SHALL avoid PDF or full-text fetching by default and only collect file artifacts when open-access/license-safe provenance is recorded.

#### Scenario: Metadata collection
- **WHEN** a paper-finding run collects metadata
- **THEN** it stores source links and metadata without downloading PDFs by default

#### Scenario: PDF collection requested
- **WHEN** a PDF or full-text artifact is requested
- **THEN** the run verifies and records open-access/license-safe provenance before storing the file
