ANALYSIS_SYSTEM = (
    "You are a concise data analyst. "
    "Use markdown (## headers, bullet points). "
    "Be specific with numbers. Keep response under 300 words."
)

QA_SYSTEM = (
    "You are a data analyst assistant. "
    "Answer concisely using data from the context. "
    "Cite specific numbers. Keep response under 200 words."
)


def build_analysis_prompt(
    file_info: dict,
    raw_text: str = "",
    summary: dict = None,
    rows: list = None,
) -> str:
    name     = file_info["name"]
    label    = file_info["label"]
    category = file_info.get("category", "unknown")

    if category == "image":
        return "Briefly describe: what is shown, any visible text/data, and 2-3 key insights."

    if summary:
        cols   = dict(list(summary["columns"].items())[:5])
        sample = str((rows or [])[:3])
        auto   = "\n".join(f"- {i}" for i in summary.get("auto_insights", []))
        return (
            f'Analyze "{name}": {summary["total_rows"]} rows, {summary["total_cols"]} cols.\n\n'
            f'Pre-computed insights:\n{auto or "none"}\n\n'
            f'Column stats (top 5):\n{cols}\n\n'
            f'Sample (3 rows):\n{sample}\n\n'
            f'Provide: ## Key Stats, ## Trends & Patterns, ## Top 3 Actionable Insights'
        )

    snippet = raw_text[:2000] + ("..." if len(raw_text) > 2000 else "")
    return (
        f'Analyze this {label} file "{name}":\n\n{snippet}\n\n'
        f'Provide: ## Summary, ## Key Points, ## Insights'
    )
