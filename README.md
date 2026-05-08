# 🔬 MatRisk AI: Enterprise Material Intelligence & Risk Analytics

[![Streamlit App](https://static.streamlit.io/badge_streamlit.svg)](https://matrisk-ai.streamlit.app)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**MatRisk AI** is a production-grade analytics platform designed to bridge the gap between physical material properties and institutional financial risk. By leveraging advanced machine learning and structural engineering models, the platform provides actionable insights for infrastructure management, commodity trading, and ESG compliance.

---

## 🚀 Key Modules

### 🧪 Material Intelligence
- **Property Explorer**: In-depth visualization of chemical and physical attributes.
- **ML Stability Engine**: Predictive modeling for material stability using Gradient Boosting.
- **Regression Suite**: Property estimation (Bulk Modulus, Melting Point) with Random Forest models.

### 🏗️ Infrastructure Analytics
- **Portfolio Monitoring**: Real-time risk scoring for bridge and industrial assets.
- **Financial Exposure**: Integration of asset replacement values with outstanding loan balances.
- **Failure History**: Statistical analysis of historical failure modes and severity.

### 📈 Commodity Markets
- **Market Signals**: Real-time tracking of critical material prices and technical indicators (RSI, Bollinger).
- **Monte Carlo Simulator**: Stochastic price forecasting for strategic procurement and risk hedging.

### 🌱 ESG & Sustainability
- **Footprint Analysis**: Granular tracking of carbon intensity and recycled content.
- **Rating Matrix**: Composite ESG scoring for material candidates and suppliers.

### 🎮 MatRisk Lab (Simulations)
- **Degradation Models**: Probabilistic corrosion simulation using time-to-failure (TTF) distributions.
- **Stress Testing**: Portfolio-wide impact analysis of extreme market and physical events.

---

## 🛠️ Technical Architecture

- **Engine**: [Streamlit](https://streamlit.io/) for high-fidelity interactive UI.
- **Data**: [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) for high-performance analytics.
- **Machine Learning**: [Scikit-learn](https://scikit-learn.org/) for predictive pipelines.
- **Visualization**: [Altair](https://altair-viz.github.io/) & [Plotly](https://plotly.com/python/) for declarative and interactive charting.
- **State Management**: Robust `st.session_state` architecture for cross-page persistence.

---

## 📁 Project Structure

```text
├── app.py                  # Main entry point & unified routing
├── modules/                # Domain-specific page modules
│   ├── 1_dashboard.py      # Executive overview
│   ├── 2_materials.py      # Material science intelligence
│   └── ...                 # Other domain modules
├── services/               # Business logic & ML pipelines
│   ├── ml_service.py       # Predictive model implementation
│   └── risk_service.py     # Infrastructure risk calculations
├── utils/                  # Core utilities
│   ├── data_loader.py      # Defensive data ingestion
│   └── state_manager.py    # Global session state initialization
├── components/             # Reusable UI components & chart wrappers
├── datasets/processed/     # Production-ready datasets (CSV)
└── tests/                  # Unit test suite
```

---

## 🚦 Getting Started

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/matrisk-ai.git
   cd matrisk-ai
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally
```bash
streamlit run app.py
```

---

## 🛡️ Production & Security
- **Data Sanitization**: No local filesystem paths are exposed in the UI.
- **Defensive Engineering**: Built-in schema validation ensures dataset integrity.
- **State Persistence**: User work is preserved across session reruns and navigation.

---

**© 2026 ZeTheta Advanced Agentic Coding Team**
*Disclaimer: This platform uses analytical models for educational and demonstrative purposes. Always consult professional engineering standards for critical infrastructure decisions.*
