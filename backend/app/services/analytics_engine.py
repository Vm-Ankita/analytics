"""
Pure-pandas analytics — runs BEFORE the LLM call.
Returns structured stats + auto-detected insights (trends, outliers, correlations).
No LLM cost for the numbers part.
"""
from __future__ import annotations


def build_summary(headers: list, rows: list) -> dict:
    """Compute column-level statistics using pandas."""
    try:
        import pandas as pd

        df = pd.DataFrame(rows)
        # Coerce numeric columns
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""))
            except (ValueError, TypeError):
                pass
            except Exception:
                pass

        columns = {}
        for col in df.columns:
            s       = df[col]
            missing = int(s.isna().sum())

            if pd.api.types.is_numeric_dtype(s):
                numeric = s.dropna()
                columns[col] = {
                    "type":    "numeric",
                    "count":   int(numeric.count()),
                    "missing": missing,
                    "min":     round(float(numeric.min()), 4),
                    "max":     round(float(numeric.max()), 4),
                    "avg":     round(float(numeric.mean()), 4),
                    "median":  round(float(numeric.median()), 4),
                    "std":     round(float(numeric.std()), 4),
                    "sum":     round(float(numeric.sum()), 4),
                }
            else:
                freq = s.dropna().value_counts()
                columns[col] = {
                    "type":    "categorical",
                    "count":   int(s.count()),
                    "missing": missing,
                    "unique":  int(s.nunique()),
                    "top":     [[str(k), int(v)] for k, v in freq.head(8).items()],
                }

        auto_insights = _auto_insights(df)

        return {
            "total_rows":    len(df),
            "total_cols":    len(df.columns),
            "columns":       columns,
            "auto_insights": auto_insights,
        }

    except ImportError:
        return _python_fallback(headers, rows)


def _auto_insights(df) -> list:
    """Rule-based insight detection — fast, no LLM needed."""
    import pandas as pd
    insights = []
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

        # Outlier detection via IQR
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr     = q3 - q1
        if iqr > 0:
            outliers = s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)]
            if len(outliers) > 0:
                insights.append(
                    f"**{col}** has {len(outliers)} outlier(s) "
                    f"(range {round(float(s.min()), 2)}–{round(float(s.max()), 2)})."
                )

        # Missing value warning
        null_pct = df[col].isna().mean()
        if null_pct > 0.2:
            insights.append(f"**{col}** has {round(null_pct * 100)}% missing values — review data quality.")

    # Correlation detection
    if len(numeric_cols) >= 2:
        try:
            corr = df[numeric_cols].corr()
            for i, c1 in enumerate(numeric_cols):
                for c2 in numeric_cols[i + 1:]:
                    v = corr.loc[c1, c2]
                    if abs(v) > 0.8:
                        direction = "positive" if v > 0 else "negative"
                        insights.append(
                            f"Strong {direction} correlation ({round(v, 2)}) "
                            f"between **{c1}** and **{c2}**."
                        )
        except Exception:
            pass

    return insights[:8]


def _python_fallback(headers: list, rows: list) -> dict:
    """No-pandas fallback — pure Python stats."""
    columns: dict = {}
    for h in headers:
        vals    = [r.get(h, "") for r in rows if r.get(h, "") not in ("", None)]
        missing = len(rows) - len(vals)
        try:
            nums = [float(str(v).replace(",", "")) for v in vals]
            if len(nums) >= len(vals) * 0.6 and nums:
                s   = sorted(nums)
                mid = len(s) // 2
                columns[h] = {
                    "type":    "numeric",
                    "count":   len(nums),
                    "missing": missing,
                    "min":     round(min(nums), 4),
                    "max":     round(max(nums), 4),
                    "avg":     round(sum(nums) / len(nums), 4),
                    "median":  round(s[mid] if len(s) % 2 != 0 else (s[mid - 1] + s[mid]) / 2, 4),
                    "sum":     round(sum(nums), 4),
                }
                continue
        except Exception:
            pass
        freq: dict = {}
        for v in vals:
            freq[str(v)] = freq.get(str(v), 0) + 1
        columns[h] = {
            "type":    "categorical",
            "count":   len(vals),
            "missing": missing,
            "unique":  len(freq),
            "top":     [[k, v] for k, v in sorted(freq.items(), key=lambda x: -x[1])[:8]],
        }
    return {
        "total_rows":    len(rows),
        "total_cols":    len(headers),
        "columns":       columns,
        "auto_insights": [],
    }
