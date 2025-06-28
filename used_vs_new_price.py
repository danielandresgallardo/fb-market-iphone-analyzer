import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# === Load data ===
used_df = pd.read_csv("output/data/all_data_clean.csv")
launch_df = pd.read_csv("data/launch_prices.csv")

# === Clean used data ===
used_df = used_df[used_df["model"] != "Unknown"]
used_df = used_df[used_df["storage"].notna()]
used_df["storage"] = used_df["storage"].astype(str).str.extract(r"(\d+)").astype(float)
used_df["model"] = used_df["model"].str.strip()

# === Reshape launch prices ===
launch_df = pd.melt(
    launch_df,
    id_vars=["model"],
    var_name="storage",
    value_name="launch_price"
)
launch_df["storage"] = pd.to_numeric(launch_df["storage"].str.replace("GB", ""), errors="coerce")
launch_df = launch_df.dropna(subset=["launch_price"])

# === Compute average used prices ===
used_avg = (
    used_df
    .groupby(["model", "storage"])["price_num"]
    .mean()
    .reset_index()
    .rename(columns={"price_num": "used_price"})
)

# === Merge ===
merged = pd.merge(used_avg, launch_df, how="inner", on=["model", "storage"])

# === Calculate price difference percentage ===
merged["pct_diff"] = ((merged["used_price"] - merged["launch_price"]) / merged["launch_price"]) * 100
merged["pct_diff_fmt"] = merged["pct_diff"].apply(lambda x: f"({x:+.0f}%)")

# === Labels ===
merged["label"] = merged["model"] + " " + merged["storage"].astype(int).astype(str) + "GB"
merged = merged.sort_values(["model", "storage"])

# === Plot setup ===
labels = merged["label"]
x = np.arange(len(labels))
bar_width = 0.4

plt.figure(figsize=(12, len(labels) * 0.35))

# Launch price bars (green)
plt.barh(x - bar_width / 2, merged["launch_price"], height=bar_width, color="green", label="Launch Price")

# Used price bars (red)
plt.barh(x + bar_width / 2, merged["used_price"], height=bar_width, color="red", label="Used Price")

# === Annotate bars ===
for i, row in merged.iterrows():
    # Launch price
    plt.text(
        row["launch_price"] + 200,
        x[i] - bar_width / 2,
        f"{int(row['launch_price'])} NTD",
        va="center",
        ha="left",
        fontsize=8
    )
    # Used price + percentage
    plt.text(
        row["used_price"] + 200,
        x[i] + bar_width / 2,
        f"{int(row['used_price'])} NTD {row['pct_diff_fmt']}",
        va="center",
        ha="left",
        fontsize=8
    )

# === Final touches ===
plt.yticks(x, labels)
plt.xlabel("Price (NTD)")
plt.title("Used iPhone Prices vs Launch Prices")
plt.legend(loc="lower right")
plt.tight_layout()

# === Save ===
os.makedirs("output/plots", exist_ok=True)
plt.savefig("output/plots/used_vs_launch_bars_labeled_pct.png")
plt.show()