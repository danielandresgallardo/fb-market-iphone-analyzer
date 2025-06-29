# FB Market iPhone Analyzer

Analyze, visualize, and compare used iPhone prices on Facebook Marketplace in Taiwan against their official launch prices.

---

## 🔧 Features

- **📥 Data Extraction**  
  Parses JSON exports from Facebook Marketplace and normalizes messy, user-generated titles.

- **🔍 Model & Storage Recognition**  
  Regex-based extraction for all major iPhone models, including variants like Pro Max, Plus, SE, 16E, etc.

- **💵 Price Cleaning**  
  Standardizes price fields and filters out suspicious or missing entries.

- **📈 Launch Price Reference**  
  Includes a curated CSV of iPhone launch prices and storage options in Taiwan (NTD).

- **🚨 Outlier Detection**  
  Flags listings with abnormally high or low prices per model/storage group.

- **📊 Visualizations**  
  Generates plots:
  - Price distribution by model & storage
  - Average price by model
  - Top 20 models by avg. price
  - Histogram of price distribution
  - Scatterplot: storage vs. price
  - Heatmap: avg. price by model/storage
  - Used vs. launch price with % difference (red/green bars)

- **📤 Exclusion Tracking**  
  Clearly logs excluded listings (accessories, duplicates, zero price, etc.) for transparency.

---

## 🗂 Project Structure

```
fb-market-iphone-analyzer/
├── app.py                      # Main processing + visualization
├── used_vs_new_price.py        # Launch vs. used price comparison
├── data/
│   ├── launch_prices.csv       # Official Apple Taiwan launch prices
│   └── marketplace-YYYY-MM-DD.json  # Raw JSON input (not included)
├── output/
│   ├── data/
│   │   ├── all_data_clean.csv
│   │   ├── summary_stats.csv
│   │   ├── outliers.csv
│   │   ├── excluded_data.csv
│   │   └── output_verification.csv
│   └── plots/
│       └── *.png               # All auto-generated graphs
```

---

## 🚀 Usage

1. **Add Your Data:**
   - Place Facebook JSON exports into `data/`.
   - Make sure `launch_prices.csv` exists and is updated.

2. **Run Main Script:**
   ```bash
   python app.py
   ```

3. **Compare Used vs Launch Prices:**
   ```bash
   python used_vs_new_price.py
   ```

---

## 📦 Requirements

- Python 3.8+
- pandas
- matplotlib
- seaborn
- numpy

Install with:
```bash
pip install pandas matplotlib seaborn numpy
```

---

## 📁 Customization

- **Add new iPhones:**  
  Update `launch_prices.csv` and the regex in `extract_model()`.

- **Expand accessory filter rules:**  
  Edit `ACCESSORY_KEYWORDS` and the `is_probably_accessory()` function.

---

## 📄 Data Sources

- **Used Listings:** Facebook Marketplace (Taiwan region)
- **Launch Prices:** Apple Taiwan & reputable local sources

---

## ⚠️ Disclaimer

This project is for educational and research use only.  
It does not distribute or store any Facebook or Apple proprietary content.

---

## 👤 Author

Daniel Gallardo  
2024–2025
