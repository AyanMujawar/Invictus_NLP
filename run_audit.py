import json

from ingest import extract_text, chunk_text
from retriever import Retriever
from auditor import audit_section, readiness_score
from schema import AuditReport


def run(
    protocol_path="data/source_file.pdf",
    guideline_path="data/guideline.pdf",
    max_sections=2
):

    print("Reading PDFs...")

    protocol_text = extract_text(protocol_path)
    guideline_text = extract_text(guideline_path)

    protocol_chunks = chunk_text(protocol_text)

    guideline_chunks = chunk_text(guideline_text)

    print(
        f"Protocol chunks: {len(protocol_chunks)} | "
        f"Guideline chunks: {len(guideline_chunks)}"
    )

    print("Creating embeddings...")

    retriever = Retriever(guideline_chunks)

    all_findings = []

    protocol_chunks = protocol_chunks[:max_sections]

    for idx, section in enumerate(protocol_chunks):

        print(
            f"Auditing section {idx + 1}/{len(protocol_chunks)}"
        )

        relevant_clauses = retriever.search(
            section,
            k=3
        )

        clause_text = "\n\n".join(relevant_clauses)

        findings = audit_section(
            section,
            clause_text
        )

        all_findings.extend(findings)

    score = readiness_score(all_findings)

    report = AuditReport(
        document_name="Clinical Study Protocol",
        findings=all_findings,
        readiness_score=score,
        summary=f"{len(all_findings)} potential compliance issues found."
    )

    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(
            report.model_dump(),
            f,
            indent=2
        )

    print("\nAudit Complete")
    print(f"Findings: {len(all_findings)}")
    print(f"Readiness Score: {score}/100")

    return report


if __name__ == "__main__":
    run()