import streamlit as st, tempfile, json
from schema import AuditReport
from report import build_html

st.set_page_config(page_title="MDR Auditor", layout="wide")
st.title("🩺 The Auditor — EU MDR Compliance Checker")

mode = st.radio("Data source",
                ["Use sample data (no API needed)", "Run real audit"], horizontal=True)
report = None

if mode.startswith("Use sample"):
    if st.button("Load sample report"):
        with open("sample_report.json") as f:
            report = AuditReport(**json.load(f))
else:
    cer_file = st.file_uploader("Clinical Evaluation Report (PDF)", type="pdf")
    mdr_file = st.file_uploader("MDR Guideline (PDF)", type="pdf")
    quick = st.checkbox("Quick demo (first 8 sections only)", value=True)
    if st.button("Run Audit") and cer_file and mdr_file:
        from ingest import extract_text, chunk_text
        from retriever import Retriever
        from auditor import audit_section, readiness_score
        def save(f):
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            t.write(f.read()); t.close(); return t.name
        with st.spinner("Reading & embedding documents..."):
            cer_chunks = chunk_text(extract_text(save(cer_file)))
            mdr_chunks = chunk_text(extract_text(save(mdr_file)))
            retriever = Retriever(mdr_chunks)
        if quick:
            cer_chunks = cer_chunks[:8]
        findings, bar = [], st.progress(0.0)
        for i, sec in enumerate(cer_chunks):
            clauses = "\n---\n".join(retriever.search(sec, k=3))
            findings.extend(audit_section(sec, clauses))
            bar.progress((i + 1) / len(cer_chunks))
        report = AuditReport(document_name="Double J Stent CER", findings=findings,
                             readiness_score=readiness_score(findings),
                             summary=f"{len(findings)} potential MDR compliance issues identified.")

if report:
    c1, c2 = st.columns(2)
    c1.metric("Regulatory Readiness Score", f"{report.readiness_score}/100")
    c2.metric("Findings", len(report.findings))
    st.dataframe([f.model_dump() for f in report.findings], use_container_width=True)
    st.download_button("⬇ Download HTML report", build_html(report),
                       "audit_report.html", "text/html")