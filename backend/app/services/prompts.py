"""
Prompt templates used by the AI system.

All prompts for the LLM are centralized here.
This makes behavior easy to tune without touching other code.
"""


# -----------------------------------------------------
# System Prompts
# -----------------------------------------------------

ANALYSIS_SYSTEM = (
    "You are a concise data analyst. "
    "Use markdown formatting (## headers and bullet points). "
    "Be specific with numbers. "
    "Keep the response under 300 words."
)


QA_SYSTEM = (
    "You are a data analyst assistant. "
    "Answer using only the provided dataset context. "
    "Cite specific numbers where possible. "
    "Keep responses under 200 words."
)


# Maximum raw text snippet passed to the model
MAX_PROMPT_SNIPPET = 2000


# -----------------------------------------------------
# Build analysis prompt
# -----------------------------------------------------

def build_analysis_prompt(
    file_info: dict,
    raw_text: str = "",
    summary: dict | None = None,
    rows: list | None = None,
) -> str:
    """
    Create the prompt used for dataset analysis.
    """

    name = file_info["name"]
    label = file_info["label"]
    category = file_info.get("category", "unknown")

    # -------------------------------------------------
    # Image analysis prompt
    # -------------------------------------------------

    if category == "image":

        return (
            "Describe the image and extract useful information.\n\n"
            "Include:\n"
            "- What is visible\n"
            "- Any text or numbers\n"
            "- 2–3 key insights"
        )

    # -------------------------------------------------
    # Tabular dataset prompt
    # -------------------------------------------------

    if summary:

        column_stats = dict(list(summary["columns"].items())[:5])

        sample_rows = str((rows or [])[:3])

        auto_insights = "\n".join(
            f"- {i}" for i in summary.get("auto_insights", [])
        )

        return (
            f'Analyze dataset "{name}".\n\n'
            f'Rows: {summary["total_rows"]}\n'
            f'Columns: {summary["total_cols"]}\n\n'

            f'Pre-computed insights:\n'
            f'{auto_insights or "None"}\n\n'

            f'Column statistics (first 5 columns):\n'
            f'{column_stats}\n\n'

            f'Sample rows (3):\n'
            f'{sample_rows}\n\n'

            "Provide:\n"
            "## Key Statistics\n"
            "## Trends & Patterns\n"
            "## Top 3 Actionable Insights"
        )

    # -------------------------------------------------
    # Text file prompt
    # -------------------------------------------------

    snippet = raw_text[:MAX_PROMPT_SNIPPET]

    if len(raw_text) > MAX_PROMPT_SNIPPET:
        snippet += "..."

    return (
        f'Analyze this {label} file "{name}".\n\n'
        f'{snippet}\n\n'
        "Provide:\n"
        "## Summary\n"
        "## Key Points\n"
        "## Insights"
    )