import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_agent_summary_table(data_dir="data"):
    diagnostic_files = glob.glob(os.path.join(data_dir, "*_diagnostics.csv"))
    rows = []

    for filepath in diagnostic_files:
        df = pd.read_csv(filepath)
        agent_name = os.path.basename(filepath).replace("_diagnostics.csv", "").capitalize()

        rows.append({
            "Agent": agent_name,
            "Avg. Bankroll": round(df["bankroll"].mean(), 2),
            "Volatility": round(df["bankroll"].std(), 2)
        })

    return pd.DataFrame(rows)

def render_table_to_png(df, output_path="plots/diagnostic_summary.png"):
    import matplotlib.pyplot as plt
    import os

    # Create figure with no extra height
    n_rows = len(df) + 1
    fig = plt.figure(figsize=(4.2, 0.38 * n_rows))  # Shrink vertical space

    # Manually fill entire figure area
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])  # [left, bottom, width, height]
    ax.axis('off')

    # Create and format table
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='center',
        cellLoc='center',
        colColours=["#f5f5f5"] * len(df.columns)
    )

    table.scale(1.0, 1.15)         # Adjust row height
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    # Save with hard-cropped bounding box and no padding
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches='tight',
        pad_inches=0.0   # 🔥 No extra margin
    )
    plt.close()



summary_df = compute_agent_summary_table("data")
render_table_to_png(summary_df)
print(summary_df)