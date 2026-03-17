"""
Chart Generator

Creates automatic charts from tabular data.
Returns base64 PNG image.
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

        # Convert numeric columns
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                pass

        numeric = df.select_dtypes(include="number")

        if numeric.empty:
            return None

        num_cols = min(len(numeric.columns), 3)

        fig, axes = plt.subplots(
            1,
            num_cols,
            figsize=(num_cols * 4, 3),
            tight_layout=True
        )

        if num_cols == 1:
            axes = [axes]

        colors = ["#2563eb", "#16a34a", "#dc2626"]

        for ax, col, color in zip(axes, numeric.columns[:3], colors):

            data = numeric[col].dropna().reset_index(drop=True)

            if len(data) == 0:
                continue

            if len(data) <= 30:
                ax.bar(range(len(data)), data, color=color, alpha=0.85)
            else:
                ax.plot(data.values, color=color, linewidth=1.8)

            ax.set_title(col, fontsize=10, fontweight="bold")

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            ax.grid(axis="y", alpha=0.3, linestyle="--")

        buffer = io.BytesIO()

        plt.savefig(buffer, format="png", dpi=130, bbox_inches="tight")

        buffer.seek(0)

        result = base64.b64encode(buffer.read()).decode()

        plt.close(fig)

        return result

    except Exception:
        return None