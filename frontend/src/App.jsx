import { useEffect, useState } from "react";
import { UserRound } from "lucide-react";
import {
  getCases,
  getCase,
  getEvidence,
  getTimeline,
  getGraph,
  getHypotheses,
  uploadEvidence,
  getFindings,
  getContradictions,
} from "./api/client";

import "./App.css";

function App() {
  const [caseData, setCaseData] = useState(null);

  const [cases, setCases] = useState([]);

  const [evidence, setEvidence] = useState([]);
  const [timeline, setTimeline] = useState([]);

  const [graph, setGraph] = useState({
    nodes: [],
    edges: [],
  });

  const [hypotheses, setHypotheses] = useState([]);

  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const [currentCaseId, setCurrentCaseId] = useState("CASE-548f9caa");
  const [caseStatus, setCaseStatus] = useState("active");
  const [showCaseSelector, setShowCaseSelector] = useState(false);
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  const [showCaseActions, setShowCaseActions] = useState(false);

  const [findings, setFindings] = useState([]);
  const [activePage, setActivePage] = useState("overview");

  const [contradictions, setContradictions] = useState([]);

  const activeHypotheses = hypotheses.filter(
    (hypothesis) =>
      hypothesis.confidence > 0 ||
      hypothesis.supporting_evidence?.length > 0
  );
  const [selectedFile, setSelectedFile] = useState(null);
  const [evidenceSource, setEvidenceSource] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [evidenceSearch, setEvidenceSearch] = useState("");

  const [selectedEvidence, setSelectedEvidence] = useState(null);

  const [timelineSearch, setTimelineSearch] = useState("");
  const [timelineAction, setTimelineAction] = useState("all");
  const [selectedEvent, setSelectedEvent] = useState(null);

  const [selectedGraphNode, setSelectedGraphNode] = useState(null);

  

  useEffect(() => {
    async function loadCases() {
      try {
        const data = await getCases();

        const normalizedCases = Array.isArray(data)
          ? data
          : Array.isArray(data?.cases)
          ? data.cases
          : [];

        setCases(normalizedCases);
      } catch (error) {
        console.error("Failed to load cases:", error);
      }
    }

    loadCases();
  }, []);

  useEffect(() => {
    async function loadDashboard() {
      setIsLoading(true);
      setLoadError("");

      setCaseData(null);
      setEvidence([]);
      setTimeline([]);
      setGraph({ nodes: [], edges: [] });
      setHypotheses([]);
      setFindings([]);
      setContradictions([]);

      try {
        const [
          caseInfo,
          evidenceData,
          timelineData,
          graphData,
          hypothesisData,
          findingsData,
          contradictionsData,
        ] = await Promise.all([
          getCase(currentCaseId),
          getEvidence(currentCaseId),
          getTimeline(currentCaseId),
          getGraph(currentCaseId),
          getHypotheses(currentCaseId),
          getFindings(currentCaseId),
          getContradictions(currentCaseId),
        ]);

        setCaseData(caseInfo);
        setEvidence(evidenceData);
        setTimeline(timelineData);
        setGraph(graphData);
        setHypotheses(hypothesisData);
        setFindings(findingsData);
        setContradictions(contradictionsData);
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
        setLoadError("Failed to load dashboard data.");
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, [currentCaseId]);

   async function handleEvidenceUpload() {
      if (!selectedFile) {
        setUploadMessage("Please select an evidence file.");
        return;
      }

      if (!evidenceSource.trim()) {
        setUploadMessage("Please enter the evidence source.");
        return;
      }

      try {
        setUploading(true);
        setUploadMessage("");

        const uploadedEvidence = await uploadEvidence(
          currentCaseId,
          evidenceSource.trim(),
          selectedFile
        );

        setEvidence((current) => [uploadedEvidence, ...current]);

        const updatedTimeline = await getTimeline(currentCaseId);
        setTimeline(updatedTimeline);

        const updatedGraph = await getGraph(currentCaseId);
        setGraph(updatedGraph);

        setSelectedFile(null);
        setEvidenceSource("");
        setUploadMessage("Evidence uploaded and processed successfully.");

        document.getElementById("evidence-file-input").value = "";
      } catch (error) {
        console.error(error);
        setUploadMessage(
          error.message || "Evidence upload failed. Please try again."
        );
      } finally {
        setUploading(false);
      }
    }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">C</div>
          <div>
            <div className="brand-name">COVEN</div>
            <div className="brand-subtitle">Digital Forensics</div>
          </div>
        </div>

        <nav className="navigation">
          <div className="nav-section">INVESTIGATION</div>

          <button
            className={`nav-item ${activePage === "overview" ? "active" : ""}`}
            onClick={() => setActivePage("overview")}
          >
            <span>◈</span>
            Overview
          </button>

          <button
            className={`nav-item ${activePage === "evidence" ? "active" : ""}`}
            onClick={() => setActivePage("evidence")}
          >
            <span>◫</span>
            Evidence
          </button>

          <button
            className={`nav-item ${activePage === "timeline" ? "active" : ""}`}
            onClick={() => setActivePage("timeline")}
          >
            <span>◷</span>
            Timeline
          </button>

          <button
            className={`nav-item ${activePage === "graph" ? "active" : ""}`}
            onClick={() => setActivePage("graph")}
          >
            <span>⌘</span>
            Evidence Graph
          </button>

          <div className="nav-section">ANALYSIS</div>

          <button
            className={`nav-item ${activePage === "findings" ? "active" : ""}`}
            onClick={() => setActivePage("findings")}
          >
            <span>△</span>
            Findings
          </button>

          <button
            className={`nav-item ${activePage === "hypotheses" ? "active" : ""}`}
            onClick={() => setActivePage("hypotheses")}
          >
            <span>◇</span>
            Hypotheses
          </button>

          <button
            className={`nav-item ${activePage === "contradictions" ? "active" : ""}`}
            onClick={() => setActivePage("contradictions")}
          >
            <span>!</span>
            Contradictions
          </button>
        </nav>
        <div className="sidebar-footer">
          <div className="system-status">
            <span className="status-dot" />
            Backend connected
          </div>
          <div className="version">COVEN v0.1</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="case-heading">

            <button
              className="case-selector"
              onClick={() => {
                setShowCaseSelector(!showCaseSelector);
                setShowStatusMenu(false);
                setShowCaseActions(false);
              }}
            >
              <span>CASES / {currentCaseId}</span>
              
              <span className="selector-arrow">▾</span>
            </button>

            {showCaseSelector && (
              <div className="case-selector-menu">
                <div className="menu-label">SELECT CASE</div>

                {cases.length > 0 ? (
                  cases.map((item) => (
                    <button
                      key={item.case_id}
                      className={`case-option ${
                        item.case_id === currentCaseId ? "active-case" : ""
                      }`}
                      onClick={() => {
                        setCurrentCaseId(item.case_id);
                        setShowCaseSelector(false);
                      }}
                    >
                      <span>
                        <strong>{item.case_id}</strong>
                        <small>{item.name}</small>
                      </span>

                      {item.case_id === currentCaseId && <span>✓</span>}
                    </button>
                  ))
                ) : (
                  <div className="empty-case-list">
                    No cases found.
                  </div>
                )}

                <div className="menu-divider" />

                <button
                  className="create-case-option"
                  onClick={() => {
                    setShowCaseSelector(false);
                    alert("Create Case will be connected next.");
                  }}
                >
                  + Create New Case
                </button>
              </div>
            )}

            <h1>{caseData?.name || "Investigation"}</h1>

          </div>

          <div className="topbar-actions">

            <div className="status-wrapper">
              <button
                className={`case-status ${caseStatus}`}
                onClick={() => {
                  setShowStatusMenu(!showStatusMenu);
                  setShowCaseSelector(false);
                  setShowCaseActions(false);
                }}
              >
                <span className="status-dot" />

                {caseStatus === "active" && "Active Investigation"}
                {caseStatus === "review" && "Under Review"}
                {caseStatus === "closed" && "Investigation Closed"}

                <span className="status-arrow">▾</span>
              </button>

              {showStatusMenu && (
                <div className="status-menu">

                  <div className="menu-label">CASE STATUS</div>

                  <button
                    className={caseStatus === "active" ? "selected" : ""}
                    onClick={() => {
                      setCaseStatus("active");
                      setShowStatusMenu(false);
                    }}
                  >
                    <span className="status-preview active-status" />
                    Active Investigation
                  </button>

                  <button
                    className={caseStatus === "review" ? "selected" : ""}
                    onClick={() => {
                      setCaseStatus("review");
                      setShowStatusMenu(false);
                    }}
                  >
                    <span className="status-preview review-status" />
                    Under Review
                  </button>

                  <button
                    className={caseStatus === "closed" ? "selected" : ""}
                    onClick={() => {
                      setCaseStatus("closed");
                      setShowStatusMenu(false);
                    }}
                  >
                    <span className="status-preview closed-status" />
                    Investigation Closed
                  </button>

                </div>
              )}
            </div>

            <div className="case-actions-wrapper">

              <button
                className="icon-button"
                title="Case actions"
                onClick={() => {
                  setShowCaseActions(!showCaseActions);
                  setShowStatusMenu(false);
                  setShowCaseSelector(false);
                }}
              >
                ⋮
              </button>

              {showCaseActions && (
                <div className="case-actions-menu">

                  <div className="menu-label">CASE ACTIONS</div>

                  <button onClick={() => alert("Edit Case will be connected later.")}>
                    Edit Case
                  </button>

                  <button onClick={() => alert("Export will be connected later.")}>
                    Export Case
                  </button>

                  <div className="menu-divider" />

                  <button
                    className="danger-option"
                    onClick={() => alert("Archive will be connected later.")}
                  >
                    Archive Case
                  </button>

                </div>
              )}

            </div>

            <div className="avatar" title="User profile">
              <UserRound size={16} strokeWidth={1.8} />
            </div>

          </div>
        </header>

        <section className="content">
          {isLoading ? (
            <div className="state-message">
              Loading case data...
            </div>
          ) : loadError ? (
            <div className="state-message error">
              <strong>Unable to load case data.</strong>
              <span>Please try again.</span>
            </div>
          ) : (
            <>
              
                {activePage === "overview" && (
                  <>
                    <div className="case-summary">
                      <div>
                        <span className="eyebrow">CASE OVERVIEW</span>
                        <p className="description">
                          {caseData?.description ||
                            "Investigation summary and evidence analysis."}
                        </p>
                      </div>

                      <div className="case-meta">
                        <div>
                          <span>INVESTIGATOR</span>
                          <strong>{caseData?.investigator || "—"}</strong>
                        </div>

                        <div>
                          <span>CASE ID</span>
                          <strong>{caseData?.case_id || "—"}</strong>
                        </div>

                        <div>
                          <span>CREATED</span>
                          <strong>
                            {caseData?.created_at
                              ? new Date(caseData.created_at).toLocaleDateString()
                              : "—"}
                          </strong>
                        </div>
                      </div>
                    </div>

                    <div className="stats-grid">
                      <StatCard
                        label="Evidence Items"
                        value={evidence.length}
                        detail="Collected sources"
                        icon="◫"
                        onClick={() => setActivePage("evidence")}
                      />

                      <StatCard
                        label="Timeline Events"
                        value={timeline.length}
                        detail="Normalized events"
                        icon="◷"
                        onClick={() => setActivePage("timeline")}
                      />

                      <StatCard
                        label="Hypotheses"
                        value={activeHypotheses.length}
                        detail="Under investigation"
                        icon="◇"
                        onClick={() => setActivePage("hypotheses")}
                      />

                      <StatCard
                        label="Integrity"
                        value={
                          evidence.length
                            ? `${Math.round(
                                (evidence.filter(
                                  (item) =>
                                    item.integrity_status === "verified"
                                ).length /
                                  evidence.length) *
                                  100
                              )}%`
                            : "—"
                        }
                        detail="Evidence verified"
                        icon="✓"
                        
                      />
                    </div>

                    <div className="dashboard-grid">
                      <section className="panel timeline-panel">
                        <PanelHeader
                          title="Investigation Timeline"
                          subtitle="Chronological reconstruction of observed events"
                          action="View timeline"
                          onAction={() => setActivePage("timeline")}
                        />

                        {timeline.length > 0 ? (
                          <div className="timeline">
                            {timeline.map((event) => (
                              <TimelineEvent
                                key={event.event_id}
                                event={event}
                                onClick={() => setActivePage("timeline")}
                              />
                            ))}
                          </div>
                        ) : (
                          <div className="timeline-empty">
                            <strong>No timeline events yet</strong>
                            <span>
                              Upload evidence to begin reconstructing the investigation timeline.
                            </span>
                          </div>
                        )}

                      </section>

                      <section className="panel">
                        <PanelHeader
                          title="Evidence"
                          subtitle="Collected and verified sources"
                          action="View all"
                          onAction={() => setActivePage("evidence")}
                        />

                        {evidence.length > 0 ? (
                          <div className="evidence-list">
                            {evidence.map((item) => (
                              <button
                                type="button"
                                className="evidence-item"
                                key={item.evidence_id}
                                onClick={() => {
                                  setSelectedEvidence(item);
                                  setActivePage("evidence");
                                }}
                              >
                                <div className="evidence-icon">
                                  {item.type === "log" ? "≋" : "□"}
                                </div>

                                <div className="evidence-info">
                                  <strong>{item.original_filename}</strong>
                                  <span>
                                    {item.source} · {item.evidence_id}
                                  </span>
                                </div>

                                <div className="verified">
                                  <span>✓</span>
                                  Verified
                                </div>
                              </button>
                            ))}
                          </div>
                        ) : (
                          <div className="evidence-empty">
                            <strong>No evidence collected yet</strong>
                            <span>Upload evidence to begin the investigation.</span>
                          </div>
                        )}
                      </section>
                    </div>

                    <section className="panel hypotheses-panel">
                      <PanelHeader
                        title="Active Hypotheses"
                        subtitle="Current investigative possibilities"
                        action="View analysis"
                        onAction={() => setActivePage("hypotheses")}
                      />

                      {activeHypotheses.length > 0 ? (
                        <div className="hypothesis-grid">
                          {activeHypotheses.map((hypothesis) => (
                            <button
                              type="button"
                              className="hypothesis-card"
                              key={hypothesis.hypothesis_id}
                              onClick={() => setActivePage("hypotheses")}
                            >
                              <div className="hypothesis-top">
                                <span className="hypothesis-id">
                                  {hypothesis.hypothesis_id}
                                </span>

                                <span className="confidence">
                                  {Math.round(hypothesis.confidence * 100)}% confidence
                                </span>
                              </div>

                              <h3>{hypothesis.description}</h3>

                              <p>{hypothesis.explanation}</p>

                              <div className="hypothesis-footer">
                                <span>
                                  Supporting: {hypothesis.supporting_evidence.length}
                                </span>

                                <span>
                                  Contradicting:{" "}
                                  {hypothesis.contradicting_evidence.length}
                                </span>
                              </div>
                            </button>
                          ))}
                        </div>
                      ) : (
                        <div className="hypotheses-empty">
                          <strong>No active hypotheses yet</strong>
                          <span>
                            Add evidence to generate evidence-backed investigative hypotheses.
                          </span>
                        </div>
                      )}

                    </section>
                  </>
                )}

                {activePage === "evidence" && (
                  <EvidencePage
                    evidence={evidence}
                    timeline={timeline}
                    currentCaseId={currentCaseId}
                    selectedFile={selectedFile}
                    setSelectedFile={setSelectedFile}
                    evidenceSource={evidenceSource}
                    setEvidenceSource={setEvidenceSource}
                    uploading={uploading}
                    uploadMessage={uploadMessage}
                    handleEvidenceUpload={handleEvidenceUpload}
                    evidenceSearch={evidenceSearch}
                    setEvidenceSearch={setEvidenceSearch}
                    selectedEvidence={selectedEvidence}
                    setSelectedEvidence={setSelectedEvidence}
                  />
                )}

                {activePage === "timeline" && (
                  <TimelinePage
                    timeline={timeline}
                    timelineSearch={timelineSearch}
                    setTimelineSearch={setTimelineSearch}
                    timelineAction={timelineAction}
                    setTimelineAction={setTimelineAction}
                    selectedEvent={selectedEvent}
                    setSelectedEvent={setSelectedEvent}
                  />
                )}

                {activePage === "graph" && (
                  <GraphPage
                    graph={graph}
                    timeline={timeline}
                    selectedGraphNode={selectedGraphNode}
                    setSelectedGraphNode={setSelectedGraphNode}
                  />
                )}

                {activePage === "findings" && (
                  <FindingsPage findings={findings} />
                )}

                {activePage === "hypotheses" && (
                  <HypothesesPage hypotheses={hypotheses} />
                )}

                {activePage === "contradictions" && (
                  <ContradictionsPage
                    contradictions={contradictions}
                  />
                )}
             
            </>
          )}
        </section>
      </main>
    </div>
  );
}

function StatCard({
  label,
  value,
  detail,
  icon,
  onClick,
}) {
  return (
    <button
      type="button"
      className={`stat-card ${onClick ? "clickable" : ""}`}
      onClick={onClick}
    >
      <div className="stat-icon">{icon}</div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
    </button>
  );
}

function PanelHeader({ title, subtitle, action, onAction }) {
  return (
    <div className="panel-header">
      <div>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>

      {action && (
        <button
          type="button"
          className={`panel-action ${
            onAction ? "clickable" : ""
          }`}
          onClick={onAction}
          disabled={!onAction}
        >
          {action} →
        </button>
      )}
    </div>
  );
}

function TimelineEvent({ event, onClick }) {
  return (
    <div className="timeline-event" onClick={onClick}>
      <div className="timeline-marker" />

      <div className="event-time">
        {new Date(event.timestamp).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })}
      </div>

      <div className="event-content">
        <strong>{event.action.replaceAll("_", " ")}</strong>
        <span>
          {event.actor} · {event.device}
          {event.object ? ` · ${event.object}` : ""}
        </span>
      </div>

      <div className="event-source">{event.source}</div>
    </div>
  );
}

function EvidencePage({
  evidence,
  timeline,
  currentCaseId,
  selectedFile,
  setSelectedFile,
  evidenceSource,
  setEvidenceSource,
  uploading,
  uploadMessage,
  handleEvidenceUpload,
  evidenceSearch,
  setEvidenceSearch,
  selectedEvidence,
  setSelectedEvidence,
}) {
  const filteredEvidence = evidence.filter((item) => {
    const search = evidenceSearch.toLowerCase();

    return (
      item.original_filename?.toLowerCase().includes(search) ||
      item.evidence_id?.toLowerCase().includes(search) ||
      item.source?.toLowerCase().includes(search)
    );
  });

  const verifiedCount = evidence.filter(
    (item) => item.integrity_status === "verified"
  ).length;

  if (selectedEvidence) {
  return (
    <EvidenceDetails
      evidence={selectedEvidence}
      timeline={timeline}
      onBack={() => setSelectedEvidence(null)}
    />
  );
}

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">INVESTIGATION EVIDENCE</span>
          <h2>Evidence Repository</h2>
          <p>
            Collect, process and inspect digital evidence associated with this
            investigation.
          </p>
        </div>
      </div>

      <div className="evidence-stats">
        <div className="evidence-stat">
          <span>Total Evidence</span>
          <strong>{evidence.length}</strong>
        </div>

        <div className="evidence-stat">
          <span>Verified</span>
          <strong>{verifiedCount}</strong>
        </div>

        <div className="evidence-stat">
          <span>Processing</span>
          <strong>0</strong>
        </div>

        <div className="evidence-stat">
          <span>Evidence Types</span>
          <strong>
            {new Set(evidence.map((item) => item.type)).size}
          </strong>
        </div>
      </div>

      <section className="vidence-upload-panel">
        <div className="panel-header">
          <div>
            <h2>Add Evidence</h2>
            <p>
              Upload a file to add it to the current investigation.
            </p>
          </div>
        </div>

        <div className="upload-form">
          <div className="upload-field">
            <label htmlFor="evidence-source">Evidence Source</label>

            <input
              id="evidence-source"
              type="text"
              placeholder="e.g. Server-01, Employee Laptop, Email Export"
              value={evidenceSource}
              onChange={(event) => setEvidenceSource(event.target.value)}
            />
          </div>

          <div className="upload-field">
            <label htmlFor="evidence-file-input">Evidence File</label>

            <input
              id="evidence-file-input"
              type="file"
              onChange={(event) =>
                setSelectedFile(event.target.files?.[0] || null)
              }
            />
          </div>

          <button
            className="upload-button"
            onClick={handleEvidenceUpload}
            disabled={uploading}
          >
            {uploading ? "Processing..." : "Upload Evidence"}
          </button>
        </div>

        {selectedFile && (
          <div className="selected-file">
            Selected: <strong>{selectedFile.name}</strong>
          </div>
        )}

        {uploadMessage && (
          <div className="upload-message">
            {uploadMessage}
          </div>
        )}
      </section>

      <section className="evidence-repository">
        <div className="panel-header">
          <div>
            <h2>Evidence Repository</h2>
            <p>
               All evidence collected for {currentCaseId}.
            </p>
          </div>

          <input
            className="evidence-search"
            type="text"
            placeholder="Search evidence..."
            value={evidenceSearch}
            onChange={(event) => setEvidenceSearch(event.target.value)}
          />
        </div>

        <div className="evidence-table">
          <div className="evidence-table-header">
            <span>Evidence</span>
            <span>Source</span>
            <span>Type</span>
            <span>Status</span>
          </div>

          {evidence.length === 0 ? (
            <div className="evidence-empty">
              <strong>No evidence collected yet</strong>
              <span>
                Upload evidence above to begin the investigation.
              </span>
            </div>
          ) : filteredEvidence.length === 0 ? (
            <div className="evidence-empty">
              No evidence matches your search.
            </div>
          ) : (
            filteredEvidence.map((item) => (
              <div
                className="evidence-table-row evidence-row-clickable"
                key={item.evidence_id}
                onClick={() => setSelectedEvidence(item)}
              >
                <div className="evidence-name">
                  <div className="evidence-icon">
                    {item.type === "log" ? "≋" : "□"}
                  </div>

                  <div>
                    <strong>{item.original_filename}</strong>
                    <span>{item.evidence_id}</span>
                  </div>
                </div>

                <span>{item.source || "—"}</span>

                <span>
                  {item.type || "unknown"}
                </span>

                <span
                  className={
                    item.integrity_status === "verified"
                      ? "evidence-status verified-status"
                      : "evidence-status"
                  }
                >
                  {item.integrity_status || "Processing"}
                </span>
              </div>
            ))
          )}
        </div>
      </section>
    </>
  );
}

function EvidenceDetails({ evidence, timeline, onBack }) {
  const evidenceEvents = timeline.filter(
  (event) => event.evidence_id === evidence.evidence_id
);
  return (
    <>
      <div className="details-navigation">
        <button className="back-button" onClick={onBack}>
          ← Back to Evidence
        </button>
      </div>

      <div className="page-heading">
        <span className="eyebrow">EVIDENCE DETAILS</span>

        <h2>{evidence.original_filename || "Evidence Item"}</h2>

        <p>
          Evidence ID: {evidence.evidence_id || "—"}
        </p>
      </div>

      <section className="evidence-details-panel">
        <div className="panel-header">
          <div>
            <h2>Evidence Information</h2>
            <p>Metadata and integrity information for this evidence item.</p>
          </div>

          <span
            className={
              evidence.integrity_status === "verified"
                ? "verified evidence-detail-status"
                : "evidence-detail-status"
            }
          >
            {evidence.integrity_status || "Processing"}
          </span>
        </div>

        <div className="details-grid">
          <DetailItem
            label="Evidence ID"
            value={evidence.evidence_id}
          />

          <DetailItem
            label="Filename"
            value={evidence.original_filename}
          />

          <DetailItem
            label="Source"
            value={evidence.source}
          />

          <DetailItem
            label="Type"
            value={evidence.type}
          />

          <DetailItem
            label="Integrity"
            value={evidence.integrity_status}
          />

          <DetailItem
            label="Created"
            value={
              evidence.created_at
                ? new Date(evidence.created_at).toLocaleString()
                : "—"
            }
          />

          <DetailItem
            label="SHA-256"
            value={
              evidence.sha256 ||
              evidence.file_hash ||
              evidence.hash ||
              "Hash available in backend record"
            }
            full
          />
        </div>
      </section>

      <section className="panel evidence-processing-panel">
        <div className="panel-header">
          <div>
            <h2>Provenance</h2>
            <p>Recorded transformations performed on this evidence.</p>
          </div>
        </div>

        <div className="processing-steps">
          {evidence.transformation_history?.length ? (
            evidence.transformation_history.map((transformation, index) => (
              <ProcessingStep
                key={`${transformation.timestamp}-${index}`}
                title={formatTransformationAction(transformation.action)}
                timestamp={transformation.timestamp}
              />
            ))
          ) : (
            <div className="provenance-empty">
              No transformation history recorded.
            </div>
          )}
        </div>
      </section>

      <section className="panel extracted-events-panel">
        <div className="panel-header">
          <div>
            <h2>Extracted Events</h2>
            <p>
              Events normalized from this evidence source.
            </p>
          </div>

          <span className="event-count">
            {evidenceEvents.length} events
          </span>
        </div>

        <div className="extracted-events">
          {evidenceEvents.length === 0 ? (
            <div className="events-empty">
              No events were extracted from this evidence.
            </div>
          ) : (
            evidenceEvents.map((event) => (
              <div
                className="extracted-event"
                key={event.event_id}
              >
                <div className="extracted-event-time">
                  {new Date(event.timestamp).toLocaleString()}
                </div>

                <div className="extracted-event-main">
                  <strong>
                    {event.action.replaceAll("_", " ")}
                  </strong>

                  <span>
                    {event.actor || "Unknown actor"}
                    {" · "}
                    {event.device || "Unknown device"}
                  </span>
                </div>

                <div className="extracted-event-object">
                  <span>OBJECT</span>
                  <strong>{event.object || "—"}</strong>
                </div>

                <div className="extracted-event-location">
                  <span>LOCATION</span>
                  <strong>{event.location || "—"}</strong>
                </div>

                <div className="extracted-event-confidence">
                  <span>CONFIDENCE</span>
                  <strong>
                    {Math.round((event.confidence ?? 0) * 100)}%
                  </strong>
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </>
  );
}

function DetailItem({ label, value, full = false }) {
  return (
    <div className={`detail-item ${full ? "detail-item-full" : ""}`}>
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function formatTransformationAction(action) {
  if (!action) {
    return "Unknown transformation";
  }

  return action
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function ProcessingStep({ title, timestamp }) {
  return (
    <div className="processing-step">
      <div className="processing-indicator">
        ✓
      </div>

      <div className="processing-step-content">
        <strong>{title}</strong>

        <span>
          {timestamp
            ? new Date(timestamp).toLocaleString()
            : "Timestamp unavailable"}
        </span>
      </div>
    </div>
  );
}

function TimelinePage({
  timeline,
  timelineSearch,
  setTimelineSearch,
  timelineAction,
  setTimelineAction,
  selectedEvent,
  setSelectedEvent,
}) {
  const actions = [
    ...new Set(
      timeline
        .map((event) => event.action)
        .filter(Boolean)
    ),
  ];

  const filteredTimeline = timeline
    .filter((event) => {
      const search = timelineSearch.toLowerCase();

      if (!search) {
        return true;
      }

      return (
        event.actor?.toLowerCase().includes(search) ||
        event.device?.toLowerCase().includes(search) ||
        event.action?.toLowerCase().includes(search) ||
        event.object?.toLowerCase().includes(search) ||
        event.location?.toLowerCase().includes(search) ||
        event.evidence_id?.toLowerCase().includes(search)
      );
    })
    .filter((event) => {
      if (timelineAction === "all") {
        return true;
      }

      return event.action === timelineAction;
    })
    .sort(
      (a, b) =>
        new Date(a.timestamp) - new Date(b.timestamp)
    );

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">INVESTIGATION TIMELINE</span>
          <h2>Event Timeline</h2>
          <p>
            Chronological reconstruction of events observed across
            the investigation evidence.
          </p>
        </div>
      </div>

      <div className="timeline-toolbar">
        <div className="timeline-search-wrapper">
          <input
            className="timeline-search"
            type="text"
            placeholder="Search actor, device, action, object..."
            value={timelineSearch}
            onChange={(event) =>
              setTimelineSearch(event.target.value)
            }
          />
        </div>

        <select
          className="timeline-filter"
          value={timelineAction}
          onChange={(event) =>
            setTimelineAction(event.target.value)
          }
        >
          <option value="all">All actions</option>

          {actions.map((action) => (
            <option key={action} value={action}>
              {formatEventAction(action)}
            </option>
          ))}
        </select>

        <div className="timeline-count">
          {filteredTimeline.length}{" "}
          {filteredTimeline.length === 1 ? "event" : "events"}
        </div>
      </div>

      <section className="panel timeline-workspace">
        <div className="panel-header">
          <div>
            <h2>Chronology</h2>
            <p>
              Events ordered from earliest to latest.
            </p>
          </div>
        </div>

        {timeline.length === 0 ? (
          <div className="timeline-empty">
            <strong>No timeline events yet</strong>
            <span>
              Upload evidence to begin reconstructing the investigation timeline.
            </span>
          </div>
        ) : filteredTimeline.length === 0 ? (
          <div className="timeline-empty">
            No events match the current filters.
          </div>
        ) : (
          <div className="investigation-timeline">
            {filteredTimeline.map((event) => (
              <TimelineEventCard
                key={event.event_id}
                event={event}
                selected={selectedEvent?.event_id === event.event_id}
                onClick={() => setSelectedEvent(event)}
              />
            ))}
          </div>
        )}
      </section>

      {selectedEvent && (
        <EventDetails
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}
    </>
  );
}

function TimelineEventCard({
  event,
  selected,
  onClick,
}) {
  return (
    <button
      type="button"
      className={`timeline-event-card ${
        selected ? "selected" : ""
      }`}
      onClick={onClick}
    >
      <div className="timeline-event-time">
        <strong>
          {new Date(event.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </strong>

        <span>
          {new Date(event.timestamp).toLocaleDateString()}
        </span>
      </div>

      <div className="timeline-line">
        <div className="timeline-node" />
      </div>

      <div className="timeline-event-content">
        <div className="timeline-event-header">
          <strong>
            {formatEventAction(event.action)}
          </strong>

          <span className="timeline-confidence">
            {Math.round((event.confidence ?? 0) * 100)}%
          </span>
        </div>

        <p>
          {event.actor || "Unknown actor"}
          {" · "}
          {event.device || "Unknown device"}
        </p>

        <div className="timeline-event-meta">
          <span>
            Object: {event.object || "—"}
          </span>

          <span>
            Location: {event.location || "—"}
          </span>

          <span>
            Evidence: {event.evidence_id || "—"}
          </span>
        </div>
      </div>
    </button>
  );
}

function EventDetails({ event, onClose }) {
  return (
    <section className="panel event-details-panel">
      <div className="panel-header">
        <div>
          <span className="eyebrow">EVENT DETAILS</span>

          <h2>
            {formatEventAction(event.action)}
          </h2>

          <p>
            Event ID: {event.event_id}
          </p>
        </div>

        <button
          type="button"
          className="event-close-button"
          onClick={onClose}
        >
          Close
        </button>
      </div>

      <div className="event-details-grid">
        <EventDetail
          label="Timestamp"
          value={
            event.timestamp
              ? new Date(event.timestamp).toLocaleString()
              : "—"
          }
        />

        <EventDetail
          label="Actor"
          value={event.actor}
        />

        <EventDetail
          label="Device"
          value={event.device}
        />

        <EventDetail
          label="Action"
          value={formatEventAction(event.action)}
        />

        <EventDetail
          label="Object"
          value={event.object}
        />

        <EventDetail
          label="Location"
          value={event.location}
        />

        <EventDetail
          label="Source"
          value={event.source}
        />

        <EventDetail
          label="Evidence ID"
          value={event.evidence_id}
        />

        <EventDetail
          label="Confidence"
          value={`${Math.round(
            (event.confidence ?? 0) * 100
          )}%`}
        />
      </div>
    </section>
  );
}

function EventDetail({ label, value }) {
  return (
    <div className="event-detail-item">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function formatEventAction(action) {
  if (!action) {
    return "Unknown event";
  }

  return action
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function GraphPage({
  graph,
  timeline,
  selectedGraphNode,
  setSelectedGraphNode,
}) {

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">INVESTIGATION GRAPH</span>

          <h2>Evidence Relationships</h2>

          <p>
            Relationships between evidence, events, actors,
            devices, and objects observed during the investigation.
          </p>
        </div>
      </div>

      <div className="graph-stats">
        <GraphStat
          label="Nodes"
          value={graph.nodes.length}
        />

        <GraphStat
          label="Relationships"
          value={graph.edges.length}
        />

        <GraphStat
          label="Events"
          value={timeline.length}
        />

        <GraphStat
          label="Evidence Sources"
          value={
            new Set(
              timeline
                .map((event) => event.evidence_id)
                .filter(Boolean)
            ).size
          }
        />
      </div>

      <section className="panel graph-panel">
        <div className="panel-header">
          <div>
            <h2>Relationship Map</h2>

            <p>
              Select a node to inspect its role in the investigation.
            </p>
          </div>

          <div className="graph-legend">
            <GraphLegend type="actor" label="Actor" />
            <GraphLegend type="device" label="Device" />
            <GraphLegend type="object" label="Object" />
            <GraphLegend type="evidence" label="Evidence" />
          </div>
        </div>

        <div className="graph-workspace">
          <InvestigationGraph
            graph={graph}
            selectedNode={selectedGraphNode}
            onSelectNode={setSelectedGraphNode}
          />
        </div>
      </section>

      {selectedGraphNode && (
        <GraphNodeDetails
          node={selectedGraphNode}
          graph={graph}
          onClose={() => setSelectedGraphNode(null)}
        />
      )}
    </>
  );
}

function GraphStat({ label, value }) {
  return (
    <div className="graph-stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function GraphLegend({ type, label }) {
  return (
    <span className="graph-legend-item">
      <span className={`graph-legend-dot ${type}`} />
      {label}
    </span>
  );
}

function buildInvestigationGraph(events) {
  const nodes = [];
  const edges = [];

  const nodeMap = new Map();

  function addNode(id, label, type, data = {}) {
    if (nodeMap.has(id)) {
      return;
    }

    const node = {
      id,
      label,
      type,
      data,
    };

    nodeMap.set(id, node);
    nodes.push(node);
  }

  function addEdge(source, target, label, event) {
    edges.push({
      id: `${source}-${target}-${event.event_id}`,
      source,
      target,
      label,
      event,
    });
  }

  events.forEach((event) => {
    const evidenceId = event.evidence_id;
    const eventId = event.event_id;

    if (evidenceId) {
      addNode(
        `evidence:${evidenceId}`,
        evidenceId,
        "evidence",
        {
          evidence_id: evidenceId,
        }
      );
    }

    addNode(
      `event:${eventId}`,
      formatEventAction(event.action),
      "event",
      event
    );

    if (evidenceId) {
      addEdge(
        `evidence:${evidenceId}`,
        `event:${eventId}`,
        "produced",
        event
      );
    }

    if (event.actor) {
      addNode(
        `actor:${event.actor}`,
        event.actor,
        "actor",
        {
          actor: event.actor,
        }
      );

      addEdge(
        `actor:${event.actor}`,
        `event:${eventId}`,
        "performed",
        event
      );
    }

    if (event.device) {
      addNode(
        `device:${event.device}`,
        event.device,
        "device",
        {
          device: event.device,
        }
      );

      addEdge(
        `device:${event.device}`,
        `event:${eventId}`,
        "involved",
        event
      );
    }

    if (event.object) {
      addNode(
        `object:${event.object}`,
        event.object,
        "object",
        {
          object: event.object,
        }
      );

      addEdge(
        `event:${eventId}`,
        `object:${event.object}`,
        event.action || "affected",
        event
      );
    }
  });

  return {
    nodes,
    edges,
  };
}

function InvestigationGraph({
  graph,
  selectedNode,
  onSelectNode,
}) {
  const positions = calculateGraphPositions(graph);

  return (
    <div className="investigation-graph">
      <svg
        className="graph-svg"
        viewBox="0 0 1100 620"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <marker
            id="graph-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path
              d="M 0 0 L 10 5 L 0 10 z"
              className="graph-arrow"
            />
          </marker>
        </defs>
        {(() => {
          const edgeGroups = new Map();

          graph.edges.forEach((edge) => {
            const key = `${edge.source}->${edge.target}`;

            if (!edgeGroups.has(key)) {
              edgeGroups.set(key, []);
            }

            edgeGroups.get(key).push(edge);
          });

          return graph.edges.map((edge) => {
            const source = positions[edge.source];
            const target = positions[edge.target];

            if (!source || !target) {
              return null;
            }

            const groupKey = `${edge.source}->${edge.target}`;
            const group = edgeGroups.get(groupKey);
            const edgeIndex = group.indexOf(edge);
            
            /*
            * Spread duplicate relationships around the
            * direct connection instead of stacking them.
            */

            const offset =
              group.length > 1
                ? (edgeIndex - (group.length - 1) / 2) * 45
                : 0;

            const dx = target.x - source.x;
            const dy = target.y - source.y;
            const length = Math.sqrt(dx * dx + dy * dy) || 1;

            const normalX = -dy / length;
            const normalY = dx / length;

            const midX = (source.x + target.x) / 2;
            const midY = (source.y + target.y) / 2;

            const controlX = midX + normalX * offset;
            const controlY = midY + normalY * offset;

            return (
              <g
                key={`${edge.source}-${edge.target}-${edge.relation}-${edgeIndex}`}
              >
                <path
                  d={`M ${source.x} ${source.y} Q ${controlX} ${controlY} ${target.x} ${target.y}`}
                  className="graph-edge"
                  fill="none"
                  markerEnd="url(#graph-arrow)"
                />

                <text
                  x={controlX}
                  y={controlY - 10}
                  className="graph-edge-label"
                  textAnchor="middle"
                >
                  {edge.label || edge.relation}
                </text>
              </g>
            );
          });
        })()}

        {graph.nodes.map((node) => {
          const position = positions[node.id];

          if (!position) {
            return null;
          }

          const isSelected =
            selectedNode?.id === node.id;

          return (
            <g
              key={node.id}
              className={`graph-node ${node.type} ${
                isSelected ? "selected" : ""
              }`}
              transform={`translate(${position.x}, ${position.y})`}
              onClick={() => onSelectNode(node)}
            >
              <circle r="31" />

              <text
                className="graph-node-type"
                y="-5"
              >
                {node.type.toUpperCase()}
              </text>

              <text
                className="graph-node-label"
                y="11"
              >
                {truncateGraphLabel(node.label)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function calculateGraphPositions(graph) {
  const positions = {};

  const positionByType = {
    person: { x: 180, y: 310 },
    actor: { x: 180, y: 310 },

    device: { x: 550, y: 310 },

    entity: { x: 550, y: 130 },

    file: { x: 900, y: 310 },
    object: { x: 900, y: 310 },

    event: { x: 550, y: 470 },
    evidence: { x: 180, y: 500 },
  };

  const counters = {};

  graph.nodes.forEach((node) => {
    const base = positionByType[node.type];

    if (!base) {
      return;
    }

    const count = counters[node.type] ?? 0;
    counters[node.type] = count + 1;

    positions[node.id] = {
      x: base.x,
      y: base.y + count * 110,
    };
  });

  return positions;
}

function GraphNodeDetails({
  node,
  graph,
  onClose,
}) {
  const relatedEdges = graph.edges.filter(
    (edge) =>
      edge.source === node.id ||
      edge.target === node.id
  );

  return (
    <section className="panel graph-node-details">
      <div className="panel-header">
        <div>
          <span className="eyebrow">
            GRAPH NODE
          </span>

          <h2>{node.label}</h2>

          <p>
            {node.type.charAt(0).toUpperCase() +
              node.type.slice(1)}
          </p>
        </div>

        <button
          type="button"
          className="event-close-button"
          onClick={onClose}
        >
          Close
        </button>
      </div>

      <div className="graph-node-information">
        <div className="graph-node-property">
          <span>Node ID</span>
          <strong>{node.id}</strong>
        </div>

        <div className="graph-node-property">
          <span>Connections</span>
          <strong>{relatedEdges.length}</strong>
        </div>
      </div>

      <div className="graph-connections">
        <span className="eyebrow">
          CONNECTIONS
        </span>

        {relatedEdges.map((edge) => {
          const otherNodeId =
            edge.source === node.id
              ? edge.target
              : edge.source;

          const otherNode = graph.nodes.find(
            (item) => item.id === otherNodeId
          );

          return (
            <div
              className="graph-connection"
              key={edge.id}
            >
              <strong>
                {otherNode?.label || otherNodeId}
              </strong>

              <span>
                {edge.label}
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
} 

function truncateGraphLabel(label) {
  if (!label) {
    return "—";
  }

  return label.length > 16
    ? `${label.slice(0, 15)}…`
    : label;
}

function FindingsPage({ findings }) {
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">ANALYSIS / FINDINGS</span>

          <h2>Investigation Findings</h2>

          <p>
            Evidence-backed observations generated from the
            investigation data.
          </p>
        </div>

        <div className="findings-count">
          {findings.length}{" "}
          {findings.length === 1 ? "finding" : "findings"}
        </div>
      </div>

      {findings.length === 0 ? (
        <section className="panel findings-empty">
          <h3>No findings available</h3>
          <p>
            The analysis engine has not produced any findings
            for this case yet.
          </p>
        </section>
      ) : (
        <div className="findings-list">
          {findings.map((finding) => (
            <FindingCard
              key={finding.finding_id}
              finding={finding}
            />
          ))}
        </div>
      )}
    </>
  );
}

function FindingCard({ finding }) {
  const confidence = Math.round(
    (finding.confidence ?? 0) * 100
  );

  const reliability = Math.round(
    (finding.reliability ?? 0) * 100
  );

  return (
    <section className="panel finding-card">
      <div className="finding-header">
        <div>
          <span className="finding-id">
            {finding.finding_id}
          </span>

          <h2>Investigation Finding</h2>
        </div>

        <div className="finding-confidence">
          <span>CONFIDENCE</span>
          <strong>{confidence}%</strong>
        </div>
      </div>

      <div className="finding-explanation">
        <span className="eyebrow">ANALYSIS</span>

        <p>
          {finding.explanation ||
            "No explanation provided."}
        </p>
      </div>

      <div className="finding-metrics">
        <FindingMetric
          label="Reliability"
          value={`${reliability}%`}
        />

        <FindingMetric
          label="Model"
          value={finding.model || "—"}
        />

        <FindingMetric
          label="Version"
          value={finding.model_version || "—"}
        />

        <FindingMetric
          label="Supporting Evidence"
          value={
            new Set(finding.supporting_evidence ?? []).size
          }
        />

        <FindingMetric
          label="Contradicting Evidence"
          value={
            new Set(finding.contradicting_evidence ?? []).size
          }
        />
      </div>

      <div className="finding-sections">
        <EvidenceReferenceList
          title="Supporting Evidence"
          items={finding.supporting_evidence}
          variant="supporting"
        />

        <EvidenceReferenceList
          title="Contradicting Evidence"
          items={finding.contradicting_evidence}
          variant="contradicting"
        />
      </div>

      <ReliabilityBreakdown
        breakdown={finding.reliability_breakdown}
      />
    </section>
  );
}

function FindingMetric({ label, value }) {
  return (
    <div className="finding-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function EvidenceReferenceList({
  title,
  items = [],
  variant,
}) {
  const uniqueItems = [...new Set(items)];

  return (
    <div className="evidence-reference-section">
      <div className="evidence-reference-header">
        <span>{title}</span>
        <strong>{uniqueItems.length}</strong>
      </div>

      {uniqueItems.length === 0 ? (
        <div className="evidence-reference-empty">
          None
        </div>
      ) : (
        <div className="evidence-reference-list">
          {uniqueItems.map((evidenceId) => (
            <div
              className={`evidence-reference ${variant}`}
              key={evidenceId}
            >
              <span>◈</span>
              {evidenceId}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ReliabilityBreakdown({ breakdown }) {
  if (!breakdown) {
    return null;
  }

  const metrics = [
    ["Model Confidence", breakdown.model_confidence],
    ["Evidence Integrity", breakdown.evidence_integrity],
    ["Source Reliability", breakdown.source_reliability],
    ["Cross-Source Agreement", breakdown.cross_source_agreement],
    ["Reproducibility", breakdown.reproducibility],
  ];

  return (
    <div className="reliability-breakdown">
      <div className="reliability-header">
        <div>
          <span className="eyebrow">
            RELIABILITY BREAKDOWN
          </span>

          <p>
            Factors contributing to the finding reliability.
          </p>
        </div>
      </div>

      <div className="reliability-grid">
        {metrics.map(([label, value]) => (
          <div
            className="reliability-item"
            key={label}
          >
            <div className="reliability-item-header">
              <span>{label}</span>

              <strong>
                {Math.round((value ?? 0) * 100)}%
              </strong>
            </div>

            <div className="reliability-bar">
              <div
                className="reliability-bar-fill"
                style={{
                  width: `${Math.max(
                    0,
                    Math.min(100, (value ?? 0) * 100)
                  )}%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function HypothesesPage({ hypotheses }) {
  const activeHypotheses = hypotheses.filter(
    (hypothesis) =>
      hypothesis.confidence > 0 ||
      hypothesis.supporting_evidence?.length > 0
  );

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">ANALYSIS / HYPOTHESES</span>

          <h2>Investigation Hypotheses</h2>

          <p>
            Competing explanations derived from the available
            evidence and analysis.
          </p>
        </div>

        <div className="hypotheses-count">
          {activeHypotheses.length}{" "}
          {activeHypotheses.length === 1 ? "hypothesis" : "hypotheses"}
        </div>
      </div>

      {activeHypotheses.length === 0 ? (
        <section className="panel hypotheses-empty">
          <h3>No active hypotheses yet</h3>

          <p>
            Add evidence to generate evidence-backed investigative
            hypotheses.
          </p>
        </section>
      ) : (
        <div className="analysis-hypothesis-grid">
          {activeHypotheses.map((hypothesis) => (
            <HypothesisAnalysisCard
              key={hypothesis.hypothesis_id}
              hypothesis={hypothesis}
            />
          ))}
        </div>
      )}
    </>
  );
}

function HypothesisAnalysisCard({ hypothesis }) {
  const confidence = Math.round(
    (hypothesis.confidence ?? 0) * 100
  );

  const reliability = Math.round(
    (hypothesis.reliability ?? 0) * 100
  );

  return (
    <section className="panel analysis-hypothesis-card">
      <div className="analysis-hypothesis-header">
        <div>
          <span className="hypothesis-analysis-id">
            {hypothesis.hypothesis_id}
          </span>

          <h2>{hypothesis.description}</h2>
        </div>

        <div className="hypothesis-confidence">
          <span>CONFIDENCE</span>

          <strong>{confidence}%</strong>
        </div>
      </div>

      <div className="hypothesis-analysis-body">
        <div className="hypothesis-explanation">
          <span className="eyebrow">ANALYSIS</span>

          <p>
            {hypothesis.explanation ||
              "No explanation provided."}
          </p>
        </div>

        <div className="hypothesis-metrics">
          <HypothesisMetric
            label="Confidence"
            value={`${confidence}%`}
          />

          <HypothesisMetric
            label="Reliability"
            value={`${reliability}%`}
          />

          <HypothesisMetric
            label="Supporting"
            value={
              hypothesis.supporting_evidence?.length ?? 0
            }
          />

          <HypothesisMetric
            label="Contradicting"
            value={
              hypothesis.contradicting_evidence?.length ?? 0
            }
          />

          <HypothesisMetric
            label="Missing"
            value={
              hypothesis.missing_evidence?.length ?? 0
            }
          />
        </div>

        <div className="hypothesis-evidence-columns">
          <HypothesisEvidence
            title="Supporting Evidence"
            items={hypothesis.supporting_evidence}
            type="supporting"
          />

          <HypothesisEvidence
            title="Contradicting Evidence"
            items={hypothesis.contradicting_evidence}
            type="contradicting"
          />

          <HypothesisEvidence
            title="Missing Evidence"
            items={hypothesis.missing_evidence}
            type="missing"
          />
        </div>
      </div>
    </section>
  );
}

function HypothesisMetric({ label, value }) {
  return (
    <div className="hypothesis-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function HypothesisEvidence({
  title,
  items = [],
  type,
}) {
  return (
    <div className="hypothesis-evidence-section">
      <div className="hypothesis-evidence-header">
        <span>{title}</span>

        <strong>{items.length}</strong>
      </div>

      {items.length === 0 ? (
        <div className="hypothesis-evidence-empty">
          None
        </div>
      ) : (
        <div className="hypothesis-evidence-list">
          {items.map((item, index) => (
            <div
              className={`hypothesis-evidence-item ${type}`}
              key={`${item}-${index}`}
            >
              <span>
                {type === "supporting"
                  ? "✓"
                  : type === "contradicting"
                    ? "!"
                    : "?"}
              </span>

              <strong>{item}</strong>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ContradictionsPage({ contradictions }) {
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            ANALYSIS / CONTRADICTIONS
          </span>

          <h2>Evidence Contradictions</h2>

          <p>
            Conflicts detected between evidence sources and
            observed events.
          </p>
        </div>

        <div className="contradictions-count">
          {contradictions.length}{" "}
          {contradictions.length === 1
            ? "contradiction"
            : "contradictions"}
        </div>
      </div>

      {contradictions.length === 0 ? (
        <ContradictionsEmptyState />
      ) : (
        <div className="contradictions-list">
          {contradictions.map((contradiction, index) => (
            <ContradictionCard
              key={
                contradiction.contradiction_id ||
                index
              }
              contradiction={contradiction}
            />
          ))}
        </div>
      )}
    </>
  );
}

function ContradictionsEmptyState() {
  return (
    <section className="panel contradictions-empty">
      <div className="contradiction-empty-icon">
        ✓
      </div>

      <h3>No contradictions detected</h3>

      <p>
        The contradiction analysis engine has not identified
        any conflicts between the available evidence and
        events for this case.
      </p>

      <span>
        This does not establish that no contradictions exist;
        it means none have been returned by the current
        analysis.
      </span>
    </section>
  );
}

function ContradictionCard({ contradiction }) {
  return (
    <section className="panel contradiction-card">
      <div className="contradiction-card-header">
        <div>
          <span className="eyebrow">
            CONTRADICTION
          </span>

          <h2>
            {contradiction.contradiction_id ||
              "Detected Conflict"}
          </h2>
        </div>
      </div>

      <pre className="contradiction-data">
        {JSON.stringify(
          contradiction,
          null,
          2
        )}
      </pre>
    </section>
  );
}

function PlaceholderPage({ title, description }) {
  return (
    <section className="panel page-placeholder">
      <div className="panel-header">
        <div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
      </div>

      <div className="placeholder-content">
        <span className="eyebrow">COVEN WORKSPACE</span>
        <h3>{title}</h3>
        <p>
          This workspace is ready to be connected to the COVEN investigation
          pipeline.
        </p>
      </div>
    </section>
  );
}

export default App;