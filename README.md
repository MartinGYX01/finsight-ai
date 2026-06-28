# FinSight AI V7

FinSight AI is a modern Finance + AI research application created as a FinTech
student portfolio project. It turns a global stock ticker into a currency-aware
dashboard, transparent risk screen, recent-news view, and detailed educational
research report.

The interface uses a restrained editorial finance design with warm off-white
surfaces, refined typography, quiet borders, and a single charcoal accent.
It does not copy Apple branding, assets, or layouts.
Users can switch the full interface and research report between English and
simplified Chinese.

> This report is generated for educational purposes only and does not constitute
> financial advice.

## Version 7 highlights

- Premium responsive Streamlit interface with restrained editorial styling,
  cleaner typography, balanced spacing, subtle borders, and lightweight motion
- English / 中文 language switch remembered for the current session
- Bilingual OpenAI reports and bilingual local template fallback reports
- Professional simplified-Chinese financial terminology throughout the report
- Dedicated desktop, tablet, mobile, and small-phone breakpoints at 1024px,
  768px, and 480px
- Mobile-first stacking for the search form, metric cards, financial cards, and
  content columns, with horizontally scrollable tabs
- Higher-contrast mobile text, touch-safe controls, reduced visual effects,
  Safari bottom spacing, and a compact article reading layout on phones
- Lightweight mobile chart with no Plotly toolbar, no chart animation, fixed
  zoom, and weekly close resampling for 5-year or longer periods
- Hero badge: **Designed by a UCSI FinTech Student**
- Global currency handling for prices, charts, market cap, and statements
- Detailed 13-part analytical report plus a news and sentiment section
- Optional OpenAI-powered report of approximately 900–1,500 words
- Useful 900+ word local template report when no API key is available
- Return on equity and current ratio when statement data is available
- Six-category risk breakdown and Low / Moderate / High risk badge
- Volatility Outlook with historical-volatility cards, investor action plan,
  and forward-looking scenario analysis
- Five-item investor watchlist and educational suitability analysis
- Recent Yahoo Finance headlines with publisher, date, link, and transparent
  keyword-based sentiment
- Language-aware Markdown downloads such as
  `finsight_ai_report_AAPL_en.md` and `finsight_ai_report_AAPL_zh.md`

## Dashboard tabs

1. **Overview** — profile, business summary, website, sector, and industry
2. **Financials** — annual metrics, ratios, health score, and explanations
3. **Risk Analysis** — risk badge, six-part breakdown, and investor watchlist
4. **Volatility Outlook** — historical volatility, drawdown, trend, action plan,
   and scenario analysis
5. **News** — available Yahoo headlines and rule-based sentiment
6. **Research Report** — full article-style report and download button

## Report sections

Both AI and template reports cover:

1. Executive Summary
2. Company Overview
3. Business Model Analysis
4. Stock Price Performance
5. Financial Performance
6. Key Financial Ratios
7. Risk Analysis
8. Volatility Outlook
9. Investor Action Plan
10. Forward-Looking Scenarios
11. News / Market Sentiment
12. Bullish Case
13. Bearish Case
14. Investor Watchlist
15. Suitability Analysis
16. Final Neutral View
17. Disclaimer

FinSight never provides personalized trading recommendations.

When **中文** is selected, every template section is generated directly in
simplified Chinese even when no OpenAI key is configured. Company names, stock
tickers, financial values, and currency codes remain unchanged.

## Project structure

```text
finsight_ai/
├── .env.example
├── .gitignore
├── app.py
├── requirements.txt
├── README.md
└── modules/
    ├── __init__.py
    ├── ai_report.py
    ├── data_fetcher.py
    ├── financial_ratios.py
    ├── i18n.py
    ├── news_analysis.py
    ├── report_generator.py
    └── risk_analysis.py
```

## Run locally

Python 3.10 or newer is recommended.

```bash
cd finsight_ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

Streamlit usually opens the app at `http://localhost:8501`.

## OpenAI reports and secrets

AI reporting is optional. The dashboard and detailed template report work
without an API key.

1. Copy the example file:

   ```bash
   cp .env.example .env
   ```

2. Add your key:

   ```dotenv
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-5.5
   ```

3. Restart Streamlit.

Alternatively, create `.streamlit/secrets.toml` for local Streamlit-style
secrets:

```toml
OPENAI_API_KEY = "your_openai_api_key_here"
OPENAI_MODEL = "gpt-5.5"
```

Both `.env` and `.streamlit/secrets.toml` are ignored by Git. Never commit,
paste into source code, print, or share a real API key. OpenAI API use may incur
charges. If the key is missing or an API request fails, FinSight automatically
keeps the full local template report.

FinSight checks credentials in this order:

1. Existing environment variables
2. Values loaded from `.env`
3. Top-level Streamlit secrets
4. Template fallback when no key is available

## Deploy with GitHub

The repository root should be the `finsight_ai` folder so that `app.py`,
`requirements.txt`, and `README.md` are together.

1. Create a new empty repository on GitHub. Do not add a README or `.gitignore`
   on GitHub if you plan to push this existing project.
2. From the project folder, review the files and push them:

   ```bash
   cd finsight_ai
   git init
   git add .
   git status
   git commit -m "Prepare FinSight AI for deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   git push -u origin main
   ```

3. Confirm that GitHub does **not** contain `.env`,
   `.streamlit/secrets.toml`, generated reports, data folders, or ZIP archives.

## Deploy on Streamlit Community Cloud

1. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) and
   connect your GitHub account.
2. Select **Create app**, then choose the existing GitHub repository.
3. Set:

   - **Repository:** your FinSight AI repository
   - **Branch:** `main`
   - **Main file path:** `app.py`

4. Open **Advanced settings** if you want to select a supported Python version
   or add optional secrets.
5. Select **Deploy**. Community Cloud installs the packages from
   `requirements.txt` and runs `app.py`.

Changes pushed to the selected GitHub branch are reflected in the deployed app.

## Configure Community Cloud secrets

OpenAI is optional. To enable AI reports:

1. Open the app's **Settings** in Streamlit Community Cloud.
2. Open **Secrets**.
3. Add TOML with your real key:

   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   OPENAI_MODEL = "gpt-5.5"
   ```

4. Save the settings and let the app restart.

Do not put these values in GitHub. If you leave the Secrets field empty,
FinSight remains fully functional and uses the detailed template report.

## Deployment checklist

- `app.py` is the main entry file.
- `requirements.txt` is committed beside `app.py`.
- `.env` and `.streamlit/secrets.toml` are not committed.
- `streamlit run app.py` works locally.
- The app works without `OPENAI_API_KEY`.
- Optional secrets are configured only in Streamlit Community Cloud settings.
- AAPL, `1155.KL`, and `0700.HK` return data in their correct currencies.

## How the analysis works

### Financial health score

The explainable score starts at 50 and adjusts for:

- net profit margin
- debt relative to assets
- annual revenue growth
- operating cash flow
- selected-period price direction

The interface maps the score to the requested screening bands:

- 75–100: Low Risk
- 50–74: Moderate Risk
- Below 50: High Risk

This is a simple portfolio-project screen—not a probability of loss, credit
rating, valuation model, or recommendation.

### News sentiment

The non-AI fallback checks headline words against small visible positive and
negative keyword lists. It labels each headline Positive, Neutral, or Negative
and summarizes the set as Positive, Neutral, Negative, or Mixed. It does not
claim to understand full articles.

## Data limitations

Data comes from Yahoo Finance through `yfinance`. Some companies, funds,
international securities, or newly listed stocks may have incomplete profiles,
statements, ratios, valuation fields, or news. FinSight shows `N/A` or a clear
availability message instead of fabricating values.

Price and market-cap currency comes from Yahoo's ticker profile. Examples tested
by the project include:

- `AAPL` — USD
- `1155.KL` — MYR
- `0700.HK` — HKD

If a trading currency is unavailable, the chart uses the neutral label `Price`
and does not assume USD.

## Mobile performance notes

- The Plotly modebar and scroll zoom are disabled.
- The chart uses a simple high-contrast line and a compact phone layout.
- Five-year, ten-year, and maximum histories are reduced to weekly closing
  prices for display, while the underlying research calculations continue to
  use the fetched historical data.
- Mobile CSS removes expensive blur effects, reduces shadows and spacing,
  disables touch hover lifts, and adds bottom padding for mobile Safari.
