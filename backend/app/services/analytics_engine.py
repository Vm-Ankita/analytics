"""
Analytics Engine

Runs BEFORE the LLM call.
Uses pandas to compute statistics and detect simple insights.

Benefits:
- Faster responses
- Deterministic numeric results
- Less LLM hallucination
"""

from __future__ import annotations
from typing import Dict, List


# -----------------------------------------------------
# Main analytics function
# -----------------------------------------------------

def build_summary(headers: List[str], rows: List[dict]) -> dict:
    """
    Compute column statistics using pandas.

    Returns structured dataset summary.
    """

    try:
        import pandas as pd

        df = pd.DataFrame(rows)

        # Convert numeric-looking columns
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "")
                )
            except Exception:
                pass

        column_stats: Dict = {}

        for col in df.columns:

            series = df[col]
            missing = int(series.isna().sum())

            # -------------------------
            # Numeric columns
            # -------------------------

            if pd.api.types.is_numeric_dtype(series):

                numeric = series.dropna()

                column_stats[col] = {
                    "type": "numeric",
                    "count": int(numeric.count()),
                    "missing": missing,
                    "min": round(float(numeric.min()), 4),
                    "max": round(float(numeric.max()), 4),
                    "avg": round(float(numeric.mean()), 4),
                    "median": round(float(numeric.median()), 4),
                    "std": round(float(numeric.std()), 4),
                    "sum": round(float(numeric.sum()), 4),
                }

            # -------------------------
            # Categorical columns
            # -------------------------

            else:

                freq = series.dropna().value_counts()

                column_stats[col] = {
                    "type": "categorical",
                    "count": int(series.count()),
                    "missing": missing,
                    "unique": int(series.nunique()),
                    "top": [[str(k), int(v)] for k, v in freq.head(8).items()],
                }

        insights = _auto_insights(df)

        return {
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "columns": column_stats,
            "auto_insights": insights,
        }

    except ImportError:
        # pandas unavailable fallback
        return _python_fallback(headers, rows)


# -----------------------------------------------------
# Automatic rule-based insights
# -----------------------------------------------------

def _auto_insights(df) -> List[str]:

    insights: List[str] = []

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    for col in numeric_cols:

        s = df[col].dropna()

        if len(s) < 2:
            continue

        # Trend detection
        if s.is_monotonic_increasing:
            insights.append(f"**{col}** shows a steady upward trend.")

        elif s.is_monotonic_decreasing:
            insights.append(f"**{col}** shows a steady downward trend.")

        # Outlier detection using IQR
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1

        if iqr > 0:
            outliers = s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)]

            if len(outliers) > 0:
                insights.append(
                    f"**{col}** has {len(outliers)} outlier(s) "
                    f"(range {round(float(s.min()),2)}–{round(float(s.max()),2)})."
                )

        # Missing data warning
        null_pct = df[col].isna().mean()

        if null_pct > 0.2:
            insights.append(
                f"**{col}** has {round(null_pct*100)}% missing values."
            )

    # Correlation detection
    if len(numeric_cols) >= 2:

        try:
            corr = df[numeric_cols].corr()

            for i, c1 in enumerate(numeric_cols):
                for c2 in numeric_cols[i + 1:]:

                    val = corr.loc[c1, c2]

                    if abs(val) > 0.8:
                        direction = "positive" if val > 0 else "negative"

                        insights.append(
                            f"Strong {direction} correlation "
                            f"({round(val,2)}) between **{c1}** and **{c2}**."
                        )

        except Exception:
            pass

    return insights[:8]


# -----------------------------------------------------
# Pure Python fallback if pandas missing
# -----------------------------------------------------

def _python_fallback(headers: List[str], rows: List[dict]) -> dict:

    columns = {}

    for h in headers:

        values = [r.get(h, "") for r in rows if r.get(h, "") not in ("", None)]

        missing = len(rows) - len(values)

        freq = {}

        for v in values:
            freq[str(v)] = freq.get(str(v), 0) + 1

        columns[h] = {
            "type": "categorical",
            "count": len(values),
            "missing": missing,
            "unique": len(freq),
            "top": [[k, v] for k, v in sorted(freq.items(), key=lambda x: -x[1])[:8]],
        }

    return {
        "total_rows": len(rows),
        "total_cols": len(headers),
        "columns": columns,
        "auto_insights": [],
    }