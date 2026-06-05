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

interface ActionTarget {
  label: string;
  path: string;
  kind: "track" | "experiment" | "openspec";
}

interface AppState {
  data: OverviewData | null;
  experimentFilter: string;
  actionTargets: ActionTarget[];
}

interface ChartRow {
  label: string;
  value: number;
  display: string;
}

type ValueElement = HTMLElement & { value: string };
type TextValueElement = HTMLElement & { value: string; textContent: string };
type DialogElement = HTMLElement & { show: () => void; close: () => void };

const state: AppState = {
  data: null,
  experimentFilter: "",
  actionTargets: [],
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

function isChartRow(row: ChartRow | null): row is ChartRow {
  return row !== null;
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
  const width = 760;
  const rowH = 28;
  const height = Math.max(120, rows.length * rowH + 34);
  const max = Math.max(1, ...rows.map((row) => Number(row.value) || 0));
  const color = options.color || "var(--blue)";
  const labelWidth = 250;
  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(options.label || "bar chart")}">
      ${rows.map((row, index) => {
        const y = 18 + index * rowH;
        const barWidth = Math.max(2, ((Number(row.value) || 0) / max) * (width - labelWidth - 86));
        return `
          <text x="0" y="${y + 14}" class="chart-label">${esc(row.label).slice(0, 38)}</text>
          <rect x="${labelWidth}" y="${y}" width="${barWidth}" height="16" rx="3" fill="${color}"></rect>
          <text x="${labelWidth + barWidth + 8}" y="${y + 13}" class="chart-label">${esc(row.display)}</text>
        `;
      }).join("")}
    </svg>
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
    <table>
      <thead>
        <tr>
          <th>Experiment</th>
          <th>Track</th>
          <th>Model / Dataset</th>
          <th>Controls</th>
          <th>Warnings</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
        ${visible.map((exp) => `
          <tr>
            <td><strong>${esc(exp.title)}</strong><br><span class="note">${esc(exp.id)}</span></td>
            <td>${esc(exp.track)}</td>
            <td>${esc(displayValue(exp.model, "n/a"))}<br><span class="note">${esc(displayValue(exp.dataset))}</span></td>
            <td>${(exp.controls ?? []).slice(0, 4).map((control) => chip(`${control.name} ${pct(control.passRate)}`)).join(" ") || "n/a"}</td>
            <td>${(exp.warnings ?? []).slice(0, 3).map((warning) => `<span class="warning">${esc(warning)}</span>`).join("<br>") || "clear"}</td>
            <td>${sourceButton(exp.readmePath || `${exp.path}/summary.json`, "preview")}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
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
    <table>
      <thead>
        <tr>
          <th>Paper</th>
          <th>Year</th>
          <th>OA</th>
          <th>Identifiers</th>
          <th>Evidence</th>
        </tr>
      </thead>
      <tbody>
        ${papers.map((paper) => `
          <tr>
            <td><strong>${esc(paper.title || "Untitled")}</strong></td>
            <td>${esc(paper.year || "n/a")}</td>
            <td>${esc(paper.oaStatus || "unknown")}<br><span class="note">PDFs downloaded: ${paper.pdfsDownloaded ? "yes" : "no"}</span></td>
            <td>${esc(paper.arxivId || "")}<br><span class="note">${esc(paper.openAlexId || "")}</span></td>
            <td>${sourceButton(paper.sourcePath, `${paper.rawOutputCount} raw files`)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
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
  const targets: ActionTarget[] = [
    ...data.tracks.map((track) => ({ label: track.id, path: track.path, kind: "track" as const })),
    ...data.experiments.slice(0, 40).map((exp) => ({ label: exp.id, path: exp.path, kind: "experiment" as const })),
    ...data.openSpecChanges.slice(0, 30).map((change) => ({ label: change.name, path: change.path, kind: "openspec" as const })),
  ];
  state.actionTargets = targets;
  const actionTarget = qs<ValueElement>("#actionTarget");
  actionTarget.innerHTML = targets.map((target, index) => `
    <md-select-option value="${esc(target.path)}" ${index === 0 ? "selected" : ""}>
      <div slot="headline">${esc(target.label)}</div>
      <div slot="supporting-text">${esc(target.kind)}</div>
    </md-select-option>
  `).join("");
  actionTarget.value = targets[0]?.path || "";
  const actionKind = qs<ValueElement>("#actionKind");
  actionKind.value = actionKind.value || "refresh-track";
  updatePrompt();
}

function updatePrompt(): void {
  if (!state.data) return;
  const kind = qs<ValueElement>("#actionKind").value || "refresh-track";
  const targetPath = qs<ValueElement>("#actionTarget").value;
  const targetLabel = state.actionTargets.find((target) => target.path === targetPath)?.label || targetPath;
  const promptMap: Record<string, string> = {
    "refresh-track": `Use the repo research rules and refresh the status for ${targetLabel}.\n\nTarget path: ${targetPath}\n\nPlease inspect the README, recent notes, experiment folders, and relevant OpenSpec changes. Return: current state, strongest evidence, open risks, next useful action, and exact files you inspected. Do not make edits unless I explicitly ask after the status report.`,
    "summarize-failures": `Analyze experiment failures for ${targetLabel}.\n\nTarget path: ${targetPath}\n\nSeparate model weakness, prompt-protocol weakness, scorer brittleness, cache/session semantics, compatibility/position issues, and runtime/storage issues. Use source files and cite exact repo paths. Do not blend task families into one aggregate.`,
    "harvest-papers": `Use the repo-local pp-paper-harvester workflow for ${targetLabel}.\n\nTarget path: ${targetPath}\n\nFind paper anchors or prior-art claims in the target, collect metadata-first evidence with no PDFs by default, preserve raw provider outputs, and update only the relevant evidence note after verification.`,
    "draft-falsifying-test": `Draft the smallest falsifying test for ${targetLabel}.\n\nTarget path: ${targetPath}\n\nName the mainstream assumption, why the idea might work, why it might fail, baseline, controls, metrics, confounders, expected artifact, and stop rule. Use OpenSpec if this becomes implementation work.`,
  };
  qs<TextValueElement>("#agentPrompt").value = promptMap[kind] || promptMap["refresh-track"];
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
qs("#actionKind").addEventListener("change", updatePrompt);
qs("#actionTarget").addEventListener("change", updatePrompt);
qs("#copyPromptButton").addEventListener("click", async () => {
  await navigator.clipboard.writeText(qs<TextValueElement>("#agentPrompt").value);
  const copyButton = qs("#copyPromptButton");
  copyButton.textContent = "Copied";
  window.setTimeout(() => { copyButton.textContent = "Copy Prompt"; }, 1200);
});
qs("#closePreview").addEventListener("click", () => qs<DialogElement>("#previewDialog").close());

loadOverview().catch((error: unknown) => {
  const message = error instanceof Error ? error.stack || error.message : String(error);
  document.body.innerHTML = `<pre class="fatal">${esc(message)}</pre>`;
});
