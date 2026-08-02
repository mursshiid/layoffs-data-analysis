# Global Tech Layoffs: End-to-End Data Analysis

An end-to-end analytics project on global tech layoffs from 2020-2026 — cleaning messy real-world data, exploring it for patterns, and building an interactive dashboard around it. Built entirely in Python.

**Live dashboard:** https://layoffs-data-analysis-murshid.streamlit.app

## Why I built this

I wanted a project that covered the full workflow a data analyst actually deals with — not just a clean CSV and a couple of charts, but real messiness: inconsistent date formats, missing values that don't have an obvious fix, duplicate labels hiding under different spellings. This dataset had all of that. It also gave me a reason to move past static notebooks and actually deploy something people can use, not just look at.

## The data

Around 4,500 rows of layoff records — company, location, headcount laid off, date, percentage of workforce cut, industry, funding stage, funds raised, country. Raw file is in `data/raw/`, the cleaned version I built is in `data/cleaned/`.

## What's in this repo

- `notebooks/01_cleaning.ipynb` — cleaning process: fixing mixed date formats (`7/23/2026` vs `07-12-2026` showing up in the same column), merging duplicate labels like "UAE" and "United Arab Emirates," deciding what to do with nulls
- `notebooks/02_eda_viz.ipynb` — exploring the data and building charts to answer specific questions (which industries got hit hardest, how layoffs trended over time, whether funding stage predicts severity, etc.)
- `app.py` — the Streamlit dashboard, with filters and live charts
- `visuals/` — exported chart images

## What I found

The US accounts for a huge share of the layoffs in this dataset — more than 9x India, the next highest country, which makes sense given the dataset leans heavily toward US tech companies. Layoffs spiked hard in early 2020 (COVID) and again around early 2023, which lines up with the well-known tech layoffs wave. One pattern I didn't expect going in: earlier-stage companies (Seed, Series A) tend to have much more severe layoffs — often over half the workforce — while later-stage and public companies do smaller, more routine cuts. That tracks with early layoffs often meaning a company is struggling to survive, versus later ones being more like cost-cutting. I also checked whether funding raised predicts layoff size, and it basically doesn't (correlation around 0.12) — how much money a company raised doesn't tell you much about how big its layoffs will be.

## A note on the missing data

About a third of the rows are missing `total_laid_off` or `percentage_laid_off`. I left these as null instead of guessing at values, since there's no reliable way to estimate a company's headcount or layoff percentage without data I don't have. Filling them in would have just been fabricating numbers. Also worth noting: 17% of rows have "Unknown" listed as the funding stage — I kept those in the dashboard but separated them visually so they don't get mistaken for a real funding category.

## Dashboard

Four tabs — Overview, Geography, Companies & Stages, and Raw Data — with filters for date range, industry, and country that update every chart live. You can also download the filtered data as a CSV directly from the sidebar.

## Built with

Python, pandas, matplotlib, seaborn, Plotly, Streamlit. Deployed on Streamlit Community Cloud.

## Running it locally

```bash
git clone https://github.com/mursshiid/layoffs-data-analysis.git
cd layoffs-data-analysis
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---
Murshid — Data Analytics Intern, working on becoming a data analyst.
[LinkedIn](www.linkedin.com/in/muhammed-murshidm) · [GitHub](https://github.com/mursshiid)
