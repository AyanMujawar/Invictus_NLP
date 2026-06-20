SEV_COLOR = {"Critical": "#b00020", "High": "#e65100",
             "Medium": "#f9a825", "Low": "#2e7d32"}

def build_html(report) -> str:
    rows = ""
    for f in sorted(report.findings,
                    key=lambda x: ["Critical","High","Medium","Low"].index(x.severity)):
        rows += f"""
        <tr>
          <td><span style="background:{SEV_COLOR[f.severity]};color:#fff;
              padding:3px 8px;border-radius:4px;">{f.severity}</span></td>
          <td>{f.violating_statement}</td>
          <td><b>{f.guideline_clause}</b></td>
          <td>{f.explanation}</td>
          <td>{f.confidence:.0%}</td>
          <td>{f.suggested_correction}</td>
        </tr>"""
    return f"""<html><head><meta charset="utf-8"><style>
      body{{font-family:Arial;margin:32px;color:#222}}
      table{{border-collapse:collapse;width:100%}}
      td,th{{border:1px solid #ddd;padding:8px;font-size:13px;vertical-align:top}}
      th{{background:#0d2b6b;color:#fff}}
      .score{{font-size:42px;font-weight:bold;color:#0d2b6b}}
    </style></head><body>
      <h1>Regulatory Compliance Audit Report</h1>
      <p><b>Document:</b> {report.document_name}</p>
      <p><b>Regulatory Readiness Score:</b> <span class="score">{report.readiness_score}/100</span></p>
      <p>{report.summary}</p>
      <table>
        <tr><th>Severity</th><th>Violating Statement</th><th>MDR Clause</th>
            <th>Explanation</th><th>Confidence</th><th>Suggested Correction</th></tr>
        {rows}
      </table>
    </body></html>"""