from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.config.settings import get_settings
from app.models.schemas import AnalyzeStartupRequest, AnalyzeStartupResponse
from app.services.pipeline import run_analysis
from app.utils.logger import setup_logger


settings = get_settings()
logger = setup_logger()

app = FastAPI(title=settings.app_name, version="0.4.0")


UI_HTML = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>VentureLens AI</title>
  <style>
    :root {
      --bg0: #f4f7fb;
      --bg1: #e5edf7;
      --card: #ffffff;
      --text: #102033;
      --muted: #5f728a;
      --primary: #145da0;
      --primary-2: #0f3f6c;
      --border: #d5e0ec;
      --danger: #a61b1b;
      --ok: #1f7a3f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      color: var(--text);
      background: radial-gradient(circle at 15% 10%, var(--bg1), var(--bg0) 45%);
      min-height: 100vh;
      padding: 20px;
    }
    .layout {
      width: 100%;
      max-width: 1200px;
      margin: 0 auto;
      display: grid;
      gap: 16px;
    }
    .panel {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 14px 30px rgba(16, 32, 51, 0.06);
      overflow: hidden;
    }
    .header {
      padding: 20px;
      background: linear-gradient(110deg, #0f3f6c 0%, #145da0 65%, #2a7bc7 100%);
      color: #fff;
    }
    .header h1 { margin: 0; font-size: 24px; }
    .header p { margin: 8px 0 0; opacity: 0.95; font-size: 14px; }
    .content { padding: 20px; display: grid; gap: 16px; }

    form {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      align-items: end;
    }
    .field { display: grid; gap: 6px; }
    label {
      color: var(--muted);
      font-weight: 700;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }
    input {
      width: 100%;
      padding: 11px 12px;
      border: 1px solid var(--border);
      border-radius: 10px;
      font-size: 14px;
      color: var(--text);
      background: #fff;
    }
    input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(20, 93, 160, 0.12);
    }
    button {
      border: none;
      border-radius: 10px;
      padding: 11px 14px;
      background: var(--primary);
      color: #fff;
      font-weight: 700;
      cursor: pointer;
    }
    button:hover { background: var(--primary-2); }
    .status { min-height: 20px; color: var(--muted); font-size: 14px; }
    .status.error { color: var(--danger); }
    .status.ok { color: var(--ok); }

    .report { display: none; gap: 12px; }
    .report.visible { display: grid; }
    .topline {
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }
    .tile {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px;
      background: #fff;
    }
    .tile .k { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
    .tile .v { margin-top: 6px; font-size: 18px; font-weight: 700; }

    .grid {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }
    .section {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
      background: #fff;
    }
    .section h3 { margin: 0 0 8px; font-size: 16px; }
    .section .score { font-weight: 700; color: var(--primary-2); margin-bottom: 8px; }
    .section p { margin: 0 0 8px; color: #1b3149; }
    .evidence { margin: 0; padding-left: 16px; color: #29435f; font-size: 13px; }

    .risks { margin: 0; padding-left: 18px; }
    .risks li { margin-bottom: 6px; }

    details { border: 1px dashed var(--border); border-radius: 12px; padding: 10px; }
    pre {
      margin: 8px 0 0;
      padding: 10px;
      border-radius: 8px;
      background: #0b1b2b;
      color: #e9f1fb;
      overflow: auto;
      max-height: 260px;
      font-size: 12px;
      line-height: 1.4;
    }
  </style>
</head>
<body>
  <main class=\"layout\">
    <section class=\"panel\">
      <section class=\"header\">
        <h1>VentureLens AI</h1>
        <p>Investor-grade startup diligence view.</p>
      </section>
      <section class=\"content\">
        <form id=\"analyze-form\">
          <div class=\"field\">
            <label for=\"startup_name\">Startup Name</label>
            <input id=\"startup_name\" name=\"startup_name\" value=\"LangChain\" required />
          </div>
          <div class=\"field\">
            <label for=\"website_url\">Website URL</label>
            <input id=\"website_url\" name=\"website_url\" value=\"https://www.langchain.com\" required />
          </div>
          <div class=\"field\">
            <label for=\"max_news_articles\">Max News Articles</label>
            <input id=\"max_news_articles\" name=\"max_news_articles\" type=\"number\" min=\"0\" max=\"20\" value=\"2\" required />
          </div>
          <div class=\"field\">
            <button type=\"submit\" id=\"submit-btn\">Run Analysis</button>
          </div>
        </form>
        <div id=\"status\" class=\"status\"></div>

        <section id=\"report\" class=\"report\">
          <div class=\"topline\">
            <div class=\"tile\"><div class=\"k\">Startup</div><div id=\"t-startup\" class=\"v\">-</div></div>
            <div class=\"tile\"><div class=\"k\">Generated On</div><div id=\"t-date\" class=\"v\">-</div></div>
            <div class=\"tile\"><div class=\"k\">Recommendation</div><div id=\"t-rec\" class=\"v\">-</div></div>
            <div class=\"tile\"><div class=\"k\">Sources Indexed</div><div id=\"t-sources\" class=\"v\">-</div></div>
          </div>

          <div id=\"sections\" class=\"grid\"></div>

          <section class=\"section\">
            <h3>Key Risks</h3>
            <ul id=\"risk-list\" class=\"risks\"></ul>
          </section>

          <details>
            <summary>Debug JSON (optional)</summary>
            <pre id=\"raw\">No output yet</pre>
          </details>
        </section>
      </section>
    </section>
  </main>

  <script>
    const form = document.getElementById("analyze-form");
    const statusBox = document.getElementById("status");
    const submitBtn = document.getElementById("submit-btn");
    const report = document.getElementById("report");
    const raw = document.getElementById("raw");

    function escapeHtml(text) {
      return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }

    function renderSection(title, section) {
      const ev = (section.evidence || []).slice(0, 3);
      const evHtml = ev.length
        ? `<ul class=\"evidence\">${ev.map((e) => `<li>${escapeHtml(e.excerpt || "")}</li>`).join("")}</ul>`
        : `<p>No direct evidence extracted.</p>`;

      return `
        <article class=\"section\">
          <h3>${escapeHtml(title)}</h3>
          <div class=\"score\">Score: ${Number(section.score || 0).toFixed(2)} / 10</div>
          <p>${escapeHtml(section.summary || "")}</p>
          ${evHtml}
        </article>
      `;
    }

    function renderReport(data) {
      const r = data.report || {};
      document.getElementById("t-startup").textContent = r.startup_name || "-";
      document.getElementById("t-date").textContent = r.generated_on || "-";
      document.getElementById("t-rec").textContent = r.recommendation || "-";
      document.getElementById("t-sources").textContent = String(data.sources_indexed ?? "-");

      const sections = document.getElementById("sections");
      sections.innerHTML = [
        renderSection("Market", r.market || {}),
        renderSection("Competition", r.competition || {}),
        renderSection("Traction", r.traction || {}),
        renderSection("Business Model", r.business_model || {}),
        renderSection("Risk Assessment", r.risk_assessment || {}),
      ].join("");

      const riskList = document.getElementById("risk-list");
      const risks = r.key_risks || [];
      riskList.innerHTML = risks.length
        ? risks.map((x) => `<li>${escapeHtml(x)}</li>`).join("")
        : "<li>No explicit risks returned.</li>";

      raw.textContent = JSON.stringify(data, null, 2);
      report.classList.add("visible");
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const payload = {
        startup_name: document.getElementById("startup_name").value.trim(),
        website_url: document.getElementById("website_url").value.trim(),
        max_news_articles: Number(document.getElementById("max_news_articles").value),
        public_pdf_urls: []
      };

      statusBox.classList.remove("error", "ok");
      statusBox.textContent = "Running analysis...";
      submitBtn.disabled = true;

      try {
        const response = await fetch("/analyze_startup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "Request failed");
        }

        renderReport(data);
        statusBox.classList.add("ok");
        const verdict = data?.evaluation?.judge_verdict || "n/a";\n        const latency = data?.metrics?.latency_ms || 0;\n        const cost = data?.metrics?.estimated_cost_usd || 0;\n        statusBox.textContent = `Analysis complete. Verdict: ${verdict} | Latency: ${latency}ms | Est. Cost: ${Number(cost).toFixed(6)}`;
      } catch (err) {
        statusBox.classList.add("error");
        statusBox.textContent = "Failed.";
        raw.textContent = String(err);
      } finally {
        submitBtn.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/ui" />')


@app.get("/ui", response_class=HTMLResponse)
def ui() -> HTMLResponse:
    return HTMLResponse(UI_HTML)


@app.get("/status")
def status() -> dict:
    return {"status": "ok", "env": settings.app_env, "phase": "phase_3"}


@app.post("/analyze_startup", response_model=AnalyzeStartupResponse)
async def analyze_startup(payload: AnalyzeStartupRequest) -> AnalyzeStartupResponse:
    try:
        return await run_analysis(payload)
    except Exception as exc:
        logger.exception("Failed to analyze startup")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
