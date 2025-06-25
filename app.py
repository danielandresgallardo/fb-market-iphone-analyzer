import json
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# === Setup Directories ===
data_dir = "data"
output_data_dir = "output/data"
output_plots_dir = "output/plots"
os.makedirs(output_data_dir, exist_ok=True)
os.makedirs(output_plots_dir, exist_ok=True)

all_data = []

# === Load JSON files ===
for filename in os.listdir(data_dir):
    if filename.endswith(".json") and filename.startswith("marketplace"):
        with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
            try:
                file_data = json.load(f)
                all_data.extend(file_data)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

print(f"Loaded {len(all_data)} listings from {data_dir}")

# === Data Extraction Functions ===

def extract_model(title):
    title_clean = title.lower()

    # Normalize spacing and hyphens
    title_clean = re.sub(r"[\s\-]+", " ", title_clean)

    # Valid iPhone models
    valid_models = ["6", "6s", "7", "8", "se", "x", "xs", "11", "12", "13", "14", "15", "16", "16e"]

    # Regex pattern to match model and optional variant
    pattern = re.compile(
        r"iphone\s*(16e|xs|x|se|6s|6|7|8|11|12|13|14|15|16)\s*(pro max|promax|pro|plus|mini)?",
        re.IGNORECASE
    )

    matches = pattern.findall(title_clean)
    if not matches:
        return "Unknown"

    models = set()
    variant_map = {
        "promax": " Pro Max",
        "pro max": " Pro Max",
        "pro": " Pro",
        "plus": " Plus",
        "mini": " mini"
    }

    for model_raw, variant_raw in matches:
        model_raw = model_raw.lower()
        variant_raw = (variant_raw or "").replace(" ", "").lower()

        model_num = model_raw.upper()

        if model_num not in [m.upper() for m in valid_models]:
            continue

        if model_num == "16E":
            model_str = "iPhone 16E"
        else:
            variant = variant_map.get(variant_raw, "")
            model_str = f"iPhone {model_num}{variant}".strip()

        models.add(model_str)

    if len(models) == 1:
        return models.pop()
    elif len(models) > 1:
        return "Multiple"
    else:
        return "Unknown"


def extract_storage(title):
    # Accept only sane storage sizes with optional g/gb suffix
    match = re.search(r"\b(16|32|64|128|256|512)\s*g?b?\b", title.lower())
    if match:
        return int(match.group(1))
    
    # Match 1TB variants
    if re.search(r"\b1\s*t?b\b", title):
        return 1024  # in GB
    
    return "Unknown"

def parse_price(price_str):
    try:
        price_str = price_str.strip().lower()
        if price_str in ["free", "0", "nt$0", "nt$0.00"]:
            return 0
        return int(re.sub(r"[^\d]", "", price_str))
    except:
        return None

# === Normalize Data ===
for item in all_data:
    item["model"] = extract_model(item["title"])
    item["storage"] = extract_storage(item["title"])
    item["price_num"] = parse_price(item["price"])

# === DataFrame Creation ===
df = pd.DataFrame(all_data)
df_clean = df.dropna(subset=["price_num", "model", "storage"])
df_clean = df_clean[(df_clean["model"] != "Unknown") & (df_clean["storage"] != "Unknown")]

# === Outlier Detection ===
def detect_outliers(group):
    q1 = group["price_num"].quantile(0.25)
    q3 = group["price_num"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Treat price == 0 as an outlier explicitly
    return group[(group["price_num"] < lower_bound) |
                 (group["price_num"] > upper_bound) |
                 (group["price_num"] == 0)]

outliers = df_clean.groupby(["model", "storage"]).apply(detect_outliers).reset_index(drop=True)

# === Summary Stats ===
summary = df_clean[df_clean["price_num"] > 0].groupby(["model", "storage"]).agg(
    count=("price_num", "count"),
    min_price=("price_num", "min"),
    max_price=("price_num", "max"),
    avg_price=("price_num", "mean")
).reset_index()

# === Save Outputs ===
summary.to_csv(os.path.join(output_data_dir, "summary_stats.csv"), index=False)
df_clean.to_csv(os.path.join(output_data_dir, "all_data_clean.csv"), index=False)
outliers.to_csv(os.path.join(output_data_dir, "outliers.csv"), index=False)

print("=== Summary Stats ===")
print(summary)
print("\n=== Possible Outliers ===")
print(outliers[["title", "model", "storage", "price_num", "location"]])

# === Visualizations ===
sns.set(style="whitegrid")

# 1. Boxplot of prices by model & storage
plt.figure(figsize=(14, 6))
sns.boxplot(data=df_clean, x="model", y="price_num", hue="storage")
plt.xticks(rotation=45)
plt.title("Price Distribution by iPhone Model and Storage")
plt.ylabel("Price (NTD)")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "boxplot_model_storage.png"))
plt.close()

# 2. Barplot: Average price by model
avg_price_by_model = df_clean.groupby("model")["price_num"].mean().sort_values()
plt.figure(figsize=(12, 6))
avg_price_by_model.plot(kind="barh", color="skyblue")
plt.title("Average Price by iPhone Model")
plt.xlabel("Average Price (NTD)")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "avg_price_by_model.png"))
plt.close()

# 3. Barplot: Number of listings per model
model_counts = df_clean["model"].value_counts()
plt.figure(figsize=(12, 6))
model_counts.plot(kind="bar", color="orange")
plt.title("Number of Listings per iPhone Model")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "count_per_model.png"))
plt.close()

# 4. Histogram of prices
plt.figure(figsize=(10, 5))
sns.histplot(df_clean["price_num"], bins=30, kde=True)
plt.title("Histogram of iPhone Listing Prices")
plt.xlabel("Price (NTD)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "histogram_prices.png"))
plt.close()

# 5. Scatter plot of price vs storage (colored by model)
plt.figure(figsize=(14, 6))
sns.scatterplot(data=df_clean, x="storage", y="price_num", hue="model", alpha=0.6)
plt.title("Price vs Storage by iPhone Model")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "scatter_price_vs_storage.png"))
plt.close()

print(f"Saved summary CSV and outlier CSV to {output_data_dir}")
print(f"Saved 5 plots to {output_plots_dir}")