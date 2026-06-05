import "@material/web/all.js";
import { styles as typescaleStyles } from "@material/web/typography/md-typescale-styles.js";
import "./styles.css";

if (typescaleStyles.styleSheet) {
  document.adoptedStyleSheets = [...document.adoptedStyleSheets, typescaleStyles.styleSheet];
}

type NullableNumber = number | null | undefined;

interface Metrics {
  tracks: number;
  experiments: number;
  papers: number;
  activeOpenSpecChanges: number;
  benchmarks: number;
  warnings: number;
}

interface Track {
  id: string;
  title: string;
  summary: string;
  path: string;
  readmePath: string | null;
  noteCount: number;
  experimentCount: number;
  evidenceCount: number;
}

interface Control {
  name: string;
  passRate?: NullableNumber;
  meanScore?: NullableNumber;
  caseCount?: NullableNumber;
}

interface Experiment {
  id: string;
  track: string;
  title: string;
  path: string;
  readmePath: string | null;
  generatedAt?: string | null;
  lastModified?: string | null;
  decision?: unknown;
  dataset?: unknown;
  model?: unknown;
  caseCount?: NullableNumber;
  controls?: Control[];
  warnings?: string[];
}

interface Paper {
  id?: string | null;
  title?: string | null;
  year?: number | string | null;
  oaStatus?: string | null;
  arxivId?: string | null;
  openAlexId?: string | null;
  sourcePath: string;
  rawOutputCount: number;
  pdfsDownloaded: boolean;
}

interface OpenSpecChange {
  name: string;
  path: string;
  completedTasks: number;
  totalTasks: number;
  status: string;
  lastModified: string;
}

interface BenchmarkStrategy {
  name: string;
  scenarioCount: number;
}

interface Benchmark {
  id: string;
  controls?: Control[];
  strategies?: BenchmarkStrategy[];
}

interface GraphNode {
  id: string;
  label: string;
  type: "track" | "experiment" | "paper" | string;
}

interface GraphEdge {
  source: string;
  target: string;
}

interface Graph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface OverviewData {
  generatedAt: string;
  repoRoot: string;
  metrics: Metrics;
  tracks: Track[];
  experiments: Experiment[];
  papers: Paper[];
  openSpecChanges: OpenSpecChange[];
  benchmarks: Benchmark[];
  graph: Graph;
}

interface AppState {
  data: OverviewData | null;
  experimentFilter: string;
  route: RouteId;
}

interface ChartRow {
  label: string;
  value: number;
  display: string;
}

type ValueElement = HTMLElement & { value: string };
type TextValueElement = HTMLElement & { value: string; textContent: string };
type DialogElement = HTMLElement & { show: () => void; close: () => void };
type RouteId = "overview" | "experiments" | "papers" | "graph" | "actions";

const routes = [
  { id: "overview", title: "Overview" },
  { id: "experiments", title: "Experiments" },
  { id: "papers", title: "Papers" },
  { id: "graph", title: "Graph" },
  { id: "actions", title: "Agent Actions" },
] as const satisfies readonly { id: RouteId; title: string }[];

const validRouteIds = new Set<RouteId>(routes.map((route) => route.id));

const state: AppState = {
  data: null,
  experimentFilter: "",
  route: "overview",
};

function qs<T extends Element>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) {
    throw new Error(`Missing required element: ${selector}`);
  }
  return element;
}

function pct(value: NullableNumber): string {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  return `${Math.round(Number(value) * 100)}%`;
}

function esc(value: unknown): string {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char] ?? char);
}

function displayValue(value: unknown, fallback = ""): string {
  if (value === null || value === undefined || value === "") return fallback;
  if (["string", "number", "boolean"].includes(typeof value)) return String(value);
  if (Array.isArray(value)) return value.map((item) => displayValue(item)).filter(Boolean).join(", ") || fallback;
  if (typeof value === "object") {
    const record = value as Record<string, unknown>;
    for (const key of ["name", "model", "dataset", "id", "path", "source"]) {
      const candidate = displayValue(record[key]);
      if (candidate) return candidate;
    }
    return Object.entries(record)
      .slice(0, 2)
      .map(([key, nestedValue]) => `${key}: ${displayValue(nestedValue, "n/a")}`)
      .join(", ") || fallback;
  }
  return fallback;
}

function metric(label: string, value: string | number): string {
  return `<div class="metric"><strong>${esc(value)}</strong><span>${esc(label)}</span></div>`;
}

function sourceButton(path: string | null | undefined, label = path): string {
  if (!path) return "";
  return `<md-text-button class="path-button" type="button" data-preview="${esc(path)}">${esc(label)}</md-text-button>`;
}

function chip(label: string): string {
  return `<md-assist-chip class="pill-chip" label="${esc(label)}"></md-assist-chip>`;
}

function shortPath(path: string): string {
  const parts = path.split("/");
  return parts.length > 3 ? `.../${parts.slice(-3).join("/")}` : path;
}

function isChartRow(row: ChartRow | null): row is ChartRow {
  return row !== null;
}

function routeFromHash(): RouteId {
  const rawRoute = window.location.hash.replace(/^#/, "");
  return validRouteIds.has(rawRoute as RouteId) ? rawRoute as RouteId : "overview";
}

function applyRoute(nextRoute = routeFromHash()): void {
  state.route = nextRoute;
  for (const page of document.querySelectorAll<HTMLElement>("[data-page]")) {
    page.hidden = page.dataset.page !== nextRoute;
  }
  for (const link of document.querySelectorAll<HTMLAnchorElement>("[data-route]")) {
    const isActive = link.dataset.route === nextRoute;
    link.classList.toggle("active", isActive);
    link.setAttribute("aria-current", isActive ? "page" : "false");
  }
  const routeTitle = routes.find((route) => route.id === nextRoute)?.title || "Overview";
  document.title = `${routeTitle} · AI Research Lab Cockpit`;
  window.scrollTo(0, 0);
}

async function loadOverview(): Promise<void> {
  const response = await fetch("/api/overview", { cache: "no-store" });
  if (!response.ok) throw new Error(`overview failed: ${response.status}`);
  state.data = await response.json() as OverviewData;
  render();
}

function render(): void {
  const data = state.data;
  if (!data) return;
  qs("#repoRoot").textContent = data.repoRoot;
  qs("#generatedAt").textContent = `Indexed ${data.generatedAt}`;
  qs("#metrics").innerHTML = [
    metric("tracks", data.metrics.tracks),
    metric("experiments", data.metrics.experiments),
    metric("papers", data.metrics.papers),
    metric("active specs", data.metrics.activeOpenSpecChanges),
    metric("benchmarks", data.metrics.benchmarks),
    metric("warnings", data.metrics.warnings),
  ].join("");
  renderTracks(data.tracks);
  renderOpenSpec(data.openSpecChanges);
  renderExperimentCharts(data.experiments);
  renderBenchmarkChart(data.benchmarks);
  renderExperiments(data.experiments);
  renderPaperCharts(data.papers);
  renderPapers(data.papers);
  renderGraph(data.graph);
  renderActions(data);
  bindPreviewButtons();
  applyRoute();
}

function renderBenchmarkChart(benchmarks: Benchmark[]): void {
  const correctnessRows = benchmarks
    .flatMap((benchmark) => (benchmark.controls ?? []).map((control) => {
      const value = control.passRate ?? control.meanScore;
      if (value === null || value === undefined) return null;
      return {
        label: `${control.name} · ${benchmark.id}`.slice(0, 72),
        value: Number(value),
        display: control.passRate !== null && control.passRate !== undefined ? pct(control.passRate) : String(control.meanScore?.toFixed?.(2) ?? "n/a"),
      };
    }))
    .filter(isChartRow);
  const strategyRows = benchmarks
    .flatMap((benchmark) => (benchmark.strategies ?? []).map((strategy) => ({
      label: `${strategy.name} · ${benchmark.id}`.slice(0, 72),
      value: Number(strategy.scenarioCount),
      display: `${strategy.scenarioCount} scenarios`,
    })))
    .filter((row) => Number(row.value));
  const rows = correctnessRows.length
    ? correctnessRows.sort((a, b) => Number(b.value) - Number(a.value)).slice(0, 12)
    : strategyRows.sort((a, b) => Number(b.value) - Number(a.value)).slice(0, 12);
  renderBarChart(qs("#benchmarkChart"), rows, { label: "benchmark signals", color: "var(--blue-3)" });
}

function renderTracks(tracks: Track[]): void {
  qs("#trackCount").textContent = `${tracks.length} tracks`;
  qs("#tracks").innerHTML = tracks.map((track) => `
    <article class="track">
      <div class="track-title">
        <strong>${esc(track.id)}</strong>
        ${sourceButton(track.readmePath || track.path, "open")}
      </div>
      <p class="note">${esc(track.summary || track.title)}</p>
      <div class="meta-line">
        ${chip(`${track.noteCount} notes`)}
        ${chip(`${track.experimentCount} experiments`)}
        ${chip(`${track.evidenceCount} evidence files`)}
      </div>
    </article>
  `).join("");
}

function renderOpenSpec(changes: OpenSpecChange[]): void {
  const active = changes.filter((change) => change.status !== "complete");
  qs("#openspecSummary").textContent = `${active.length} active of ${changes.length}`;
  qs("#openspec").innerHTML = changes.slice(0, 12).map((change) => {
    const total = Number(change.totalTasks) || 0;
    const completed = Number(change.completedTasks) || 0;
    const width = total ? Math.round((completed / total) * 100) : 0;
    return `
      <article class="change-row">
        <div class="row-title">
          <strong>${esc(change.name)}</strong>
          ${sourceButton(`${change.path}/tasks.md`, `${completed}/${total}`)}
        </div>
        <md-linear-progress value="${width / 100}" aria-label="${esc(change.name)} progress"></md-linear-progress>
        <div class="meta-line">
          ${chip(change.status)}
          ${chip(change.lastModified)}
        </div>
      </article>
    `;
  }).join("");
}

function flattenControlRows(experiments: Experiment[]): Array<{
  experiment: string;
  track: string;
  path: string;
  name: string;
  passRate?: NullableNumber;
  meanScore?: NullableNumber;
  caseCount?: NullableNumber;
}> {
  return experiments
    .flatMap((exp) => (exp.controls ?? []).map((control) => ({
      experiment: exp.id,
      track: exp.track,
      path: exp.path,
      name: control.name,
      passRate: control.passRate,
      meanScore: control.meanScore,
      caseCount: control.caseCount,
    })))
    .filter((row) => row.passRate !== null && row.passRate !== undefined || row.meanScore !== null && row.meanScore !== undefined);
}

function renderBarChart(container: Element, rows: ChartRow[], options: { label?: string; color?: string } = {}): void {
  const max = Math.max(1, ...rows.map((row) => Number(row.value) || 0));
  const color = options.color || "var(--blue)";
  if (!rows.length) {
    container.innerHTML = `<div class="empty-chart">No comparable data found.</div>`;
    return;
  }
  container.innerHTML = `
    <div class="bar-list" role="img" aria-label="${esc(options.label || "bar chart")}">
      ${rows.map((row) => {
        const width = Math.max(1, ((Number(row.value) || 0) / max) * 100);
        return `
          <div class="bar-row">
            <div class="bar-label" title="${esc(row.label)}">${esc(row.label)}</div>
            <div class="bar-track">
              <span style="width:${width}%; background:${color}"></span>
            </div>
            <div class="bar-value">${esc(row.display)}</div>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function renderExperimentCharts(experiments: Experiment[]): void {
  const controlRows = flattenControlRows(experiments)
    .map((row) => {
      const value = row.passRate ?? row.meanScore;
      if (value === null || value === undefined) return null;
      return {
        label: row.name,
        value: Number(value),
        display: row.passRate !== null && row.passRate !== undefined ? pct(row.passRate) : String(row.meanScore?.toFixed?.(2) ?? row.meanScore),
      };
    })
    .filter(isChartRow)
    .sort((a, b) => b.value - a.value)
    .slice(0, 12);
  renderBarChart(qs("#controlChart"), controlRows, { label: "control pass rates", color: "var(--blue)" });

  const caseRows = experiments
    .filter((exp) => Number(exp.caseCount))
    .sort((a, b) => Number(b.caseCount) - Number(a.caseCount))
    .slice(0, 12)
    .map((exp) => ({ label: exp.id, value: Number(exp.caseCount), display: `${exp.caseCount} cases` }));
  renderBarChart(qs("#caseChart"), caseRows, { label: "experiment case counts", color: "var(--blue-2)" });
}

function experimentMatches(exp: Experiment): boolean {
  const query = state.experimentFilter.trim().toLowerCase();
  if (!query) return true;
  return [exp.id, exp.track, displayValue(exp.dataset), displayValue(exp.model), displayValue(exp.decision), ...(exp.controls ?? []).map((control) => control.name)]
    .join(" ")
    .toLowerCase()
    .includes(query);
}

function renderExperiments(experiments: Experiment[]): void {
  const visible = experiments.filter(experimentMatches);
  qs("#experimentsTable").innerHTML = `
    <div class="collection-head">
      <div>
        <h3>Experiment Runs</h3>
        <span>${visible.length} visible of ${experiments.length}</span>
      </div>
      <span class="note">Filter by track, model, dataset, or control</span>
    </div>
    <div class="experiment-grid">
      ${visible.map((exp) => {
        const controls = (exp.controls ?? []).slice(0, 5);
        const warnings = (exp.warnings ?? []).slice(0, 3);
        return `
          <article class="experiment-card">
            <div class="card-kicker">${esc(exp.track)}</div>
            <div class="card-title-row">
              <h3>${esc(exp.title)}</h3>
              ${sourceButton(exp.readmePath || `${exp.path}/summary.json`, "Preview")}
            </div>
            <div class="path-note">${esc(shortPath(exp.path))}</div>
            <dl class="fact-grid">
              <div><dt>Model</dt><dd>${esc(displayValue(exp.model, "n/a"))}</dd></div>
              <div><dt>Dataset</dt><dd>${esc(displayValue(exp.dataset, "n/a"))}</dd></div>
              <div><dt>Cases</dt><dd>${esc(exp.caseCount ?? "n/a")}</dd></div>
            </dl>
            <div class="control-strip">
              ${controls.length ? controls.map((control) => chip(`${control.name} ${pct(control.passRate ?? control.meanScore)}`)).join("") : `<span class="note">No comparable controls indexed</span>`}
            </div>
            ${warnings.length ? `<div class="warning-box">${warnings.map((warning) => `<span>${esc(warning)}</span>`).join("")}</div>` : `<div class="clear-box">Research discipline checks clear</div>`}
          </article>
        `;
      }).join("")}
    </div>
  `;
  bindPreviewButtons();
}

function groupCounts<T>(items: T[], keyFn: (item: T) => unknown): Record<string, number> {
  return items.reduce<Record<string, number>>((acc, item) => {
    const rawKey = keyFn(item);
    const key = String(rawKey ?? "unknown") || "unknown";
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
}

function renderPaperCharts(papers: Paper[]): void {
  const yearCounts = groupCounts(papers, (paper) => paper.year);
  const yearRows = Object.entries(yearCounts)
    .sort(([a], [b]) => String(a).localeCompare(String(b)))
    .map(([label, value]) => ({ label, value, display: `${value}` }));
  renderBarChart(qs("#paperYearChart"), yearRows, { label: "papers by year", color: "var(--blue-3)" });

  const oaRows = Object.entries(groupCounts(papers, (paper) => paper.oaStatus))
    .map(([label, value]) => ({ label, value, display: `${value}` }));
  renderBarChart(qs("#oaChart"), oaRows, { label: "open access status", color: "var(--steel)" });
}

function renderPapers(papers: Paper[]): void {
  qs("#papersTable").innerHTML = `
    <div class="collection-head">
      <div>
        <h3>Evidence Anchors</h3>
        <span>${papers.length} harvested papers</span>
      </div>
      <span class="note">Metadata-first evidence, not full-text claims</span>
    </div>
    <div class="paper-list">
      ${papers.map((paper) => `
        <article class="paper-card">
          <div>
            <h3>${esc(paper.title || "Untitled")}</h3>
            <div class="meta-line">
              ${chip(String(paper.year || "n/a"))}
              ${chip(`OA ${paper.oaStatus || "unknown"}`)}
              ${chip(`PDF ${paper.pdfsDownloaded ? "yes" : "no"}`)}
            </div>
          </div>
          <div class="paper-meta">
            <span>${esc(paper.arxivId || "no arXiv id")}</span>
            <span>${esc(paper.openAlexId || "no OpenAlex id")}</span>
          </div>
          ${sourceButton(paper.sourcePath, `${paper.rawOutputCount} raw files`)}
        </article>
      `).join("")}
    </div>
  `;
  bindPreviewButtons();
}

function renderGraph(graph: Graph): void {
  const tracks = graph.nodes.filter((node) => node.type === "track");
  const experiments = graph.nodes.filter((node) => node.type === "experiment").slice(0, 28);
  const papers = graph.nodes.filter((node) => node.type === "paper").slice(0, 36);
  const width = 1040;
  const height = 520;
  const positions = new Map<string, { x: number; y: number }>();
  tracks.forEach((node, i) => positions.set(node.id, { x: 110, y: 80 + i * 95 }));
  experiments.forEach((node, i) => positions.set(node.id, { x: 470, y: 36 + (i % 14) * 34 }));
  papers.forEach((node, i) => positions.set(node.id, { x: 860, y: 40 + (i % 18) * 25 }));
  const edgeMarkup = graph.edges
    .map((edge) => {
      const a = positions.get(edge.source);
      const b = positions.get(edge.target);
      if (!a || !b) return "";
      return `<path d="M${a.x + 70},${a.y} C${a.x + 190},${a.y} ${b.x - 160},${b.y} ${b.x - 20},${b.y}" stroke="rgba(71,85,105,.32)" fill="none" />`;
    })
    .join("");
  const nodeMarkup = [...tracks, ...experiments, ...papers].map((node) => {
    const pos = positions.get(node.id);
    if (!pos) return "";
    const fill = node.type === "track" ? "var(--blue)" : node.type === "experiment" ? "var(--blue-2)" : "var(--steel)";
    return `
      <g>
        <circle cx="${pos.x}" cy="${pos.y}" r="${node.type === "track" ? 10 : 6}" fill="${fill}"></circle>
        <text x="${pos.x + 14}" y="${pos.y + 4}" class="chart-label">${esc(node.label).slice(0, 30)}</text>
      </g>
    `;
  }).join("");
  qs("#researchGraph").innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="track to evidence graph">${edgeMarkup}${nodeMarkup}</svg>`;
}

function renderActions(data: OverviewData): void {
  const latestExperiment = [...data.experiments].sort((a, b) => {
    const aTime = Date.parse(a.generatedAt || a.lastModified || "");
    const bTime = Date.parse(b.generatedAt || b.lastModified || "");
    return (Number.isFinite(bTime) ? bTime : 0) - (Number.isFinite(aTime) ? aTime : 0);
  })[0];
  const actionSummary = qs("#actionSummary");
  if (!latestExperiment) {
    actionSummary.innerHTML = `
      <div class="action-card">
        <div class="card-kicker">First action</div>
        <h3>Generate data visualization for latest experiment</h3>
        <p class="note">No experiment folders were indexed yet.</p>
      </div>
    `;
    qs<TextValueElement>("#agentPrompt").value = "No indexed experiment is available yet. Refresh the cockpit after adding an experiment folder.";
    return;
  }
  const targetPath = latestExperiment.path;
  const targetLabel = latestExperiment.title || latestExperiment.id;
  actionSummary.innerHTML = `
    <div class="action-card">
      <div class="card-kicker">First action</div>
      <h3>Generate data visualization for latest experiment</h3>
      <dl class="fact-grid">
        <div><dt>Experiment</dt><dd>${esc(targetLabel)}</dd></div>
        <div><dt>Track</dt><dd>${esc(latestExperiment.track)}</dd></div>
        <div><dt>Updated</dt><dd>${esc(latestExperiment.generatedAt || latestExperiment.lastModified || "n/a")}</dd></div>
      </dl>
      <p class="note">${esc(shortPath(targetPath))}</p>
    </div>
  `;
  qs<TextValueElement>("#agentPrompt").value = `Use the research-figures skill to generate paper-quality data visualizations for the latest indexed experiment.

Experiment: ${targetLabel}
Target path: ${targetPath}
Track: ${latestExperiment.track}
Model: ${displayValue(latestExperiment.model, "n/a")}
Dataset: ${displayValue(latestExperiment.dataset, "n/a")}

Please:
1. Define the figure claim in one sentence before plotting.
2. Inspect the target experiment artifacts, especially README.md, summary.json, case-metrics.json, failure-classifications.json, artifact-manifest.json, commands.md, and any raw result JSON.
3. Build a compact computed-data table from the experiment data before plotting.
4. Choose the right paper-style figure type for the available data: horizontal bars for control comparisons, grouped bars for methods x metrics, line plots for time/step axes, or heatmaps for matrix data.
5. Use Matplotlib's object-oriented API and the repo's research-figures workflow. Export SVG, PDF, and PNG from the same reproducible script.
6. Save the script and generated figures inside the experiment folder under a clear figures/ or visualization/ subdirectory.
7. Render and visually inspect the PNG before finalizing. Check for title, legend, tick, annotation, and label overlap.
8. Return exact output paths, the figure claim, the computed-data table summary, and any caveats about missing or weak experiment data.

Do not edit experiment measurements or make unsupported claims. If the latest experiment lacks enough plottable data, say what artifact is missing and create the smallest useful placeholder data table instead of inventing values.`;
}

async function previewPath(path: string): Promise<void> {
  const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
  const payload = await response.json() as { path?: string; text?: string; error?: string };
  qs("#previewTitle").textContent = payload.path || path;
  qs("#previewBody").textContent = payload.text || payload.error || "";
  qs<DialogElement>("#previewDialog").show();
}

function bindPreviewButtons(): void {
  document.querySelectorAll<HTMLElement>("[data-preview]").forEach((button) => {
    button.onclick = () => {
      const path = button.dataset.preview;
      if (path) void previewPath(path);
    };
  });
}

qs("#refreshButton").addEventListener("click", () => void loadOverview());
qs<ValueElement>("#experimentFilter").addEventListener("input", (event) => {
  state.experimentFilter = (event.target as ValueElement).value;
  if (state.data) renderExperiments(state.data.experiments);
});
qs("#copyPromptButton").addEventListener("click", async () => {
  await navigator.clipboard.writeText(qs<TextValueElement>("#agentPrompt").value);
  const copyButton = qs("#copyPromptButton");
  copyButton.textContent = "Copied";
  window.setTimeout(() => { copyButton.textContent = "Copy Prompt"; }, 1200);
});
qs("#closePreview").addEventListener("click", () => qs<DialogElement>("#previewDialog").close());
window.addEventListener("hashchange", () => applyRoute());

loadOverview().catch((error: unknown) => {
  const message = error instanceof Error ? error.stack || error.message : String(error);
  document.body.innerHTML = `<pre class="fatal">${esc(message)}</pre>`;
});
