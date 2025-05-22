import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_decision_time_scatter(data_dir="data", output_path="plots/decision_time_scatter.png"):
    diagnostic_files = glob.glob(os.path.join(data_dir, "*_diagnostics.csv"))
    records = []

    for filepath in diagnostic_files:
        df = pd.read_csv(filepath)
        agent_name = os.path.basename(filepath).replace("_diagnostics.csv", "").capitalize()

        if "decision_time_sec" not in df.columns:
            continue

        df = df.copy()
        df["Agent"] = agent_name
        df["Game Number"] = range(1, len(df) + 1)
        records.append(df[["Game Number", "decision_time_sec", "Agent"]])

    if not records:
        print("No valid decision_time_sec data found.")
        return

    combined_df = pd.concat(records, ignore_index=True)

    # Plot
    plt.figure(figsize=(12, 6))
    sns.scatterplot(
        data=combined_df,
        x="Game Number",
        y="decision_time_sec",
        hue="Agent",
        alpha=0.6,
        s=30
    )

    plt.ylabel("Decision Time (seconds)")
    plt.title("Decision Time per Game by Agent")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()

# Example usage
if __name__ == "__main__":
    plot_decision_time_scatter()
