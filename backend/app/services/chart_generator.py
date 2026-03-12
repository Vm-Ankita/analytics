"""
Auto-generates a base64 PNG chart from tabular data using matplotlib.
Returns None if matplotlib is unavailable or data has no numeric columns.
"""
import io
import base64
from typing import Optional


def generate_chart(headers: list, rows: list) -> Optional[str]:
    try:
        import pandas as pd
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        df = pd.DataFrame(rows)
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass

        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            return None

        num_cols = min(len(numeric.columns), 3)
        fig, axes = plt.subplots(1, num_cols, figsize=(num_cols * 4, 3), tight_layout=True)
        if num_cols == 1:
            axes = [axes]

        palette = ["#2563eb", "#16a34a", "#dc2626"]

        for ax, col, color in zip(axes, numeric.columns[:3], palette):
            data = numeric[col].dropna().reset_index(drop=True)
            if len(data) == 0:
                continue
            if len(data) <= 30:
                ax.bar(range(len(data)), data, color=color, alpha=0.85, width=0.7)
            else:
                ax.plot(data.values, color=color, linewidth=1.8)
                ax.fill_between(range(len(data)), data.values, alpha=0.12, color=color)
            ax.set_title(col, fontsize=10, fontweight="bold", pad=6)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.tick_params(labelsize=7)
            ax.grid(axis="y", alpha=0.3, linestyle="--")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                    facecolor="white", edgecolor="none")
        buf.seek(0)
        result = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        return result

    except Exception:
        return None
