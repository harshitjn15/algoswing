# AlgoSwing

Production-grade algorithmic swing trading platform.

## Architecture

- **Frontend**: Next.js 15 (App Router) + TypeScript + Tailwind CSS + ShadCN
- **Backend**: FastAPI + Python 3.12
- **Database**: MongoDB Atlas
- **Auth**: Clerk
- **Notifications**: Telegram + Email
- **Deployment**: Frontend → Vercel | Backend → Render

## Quick Start

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# Run development server
python -m app.main
# or
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend (Phase 2)

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `backend/.env.example` for all required variables.

## Project Structure

```
algo/
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── core/     # Config, DB, Scheduler, Logging
│   │   ├── scanners/ # Chartink scanner engine
│   │   ├── strategies/ # Strategy plugin system
│   │   ├── market_data/ # Upstox OHLCV provider
│   │   ├── alerts/   # Telegram + Email alerts
│   │   ├── models/   # Pydantic models
│   │   ├── repositories/ # MongoDB data access
│   │   └── api/      # FastAPI routes
│   └── tests/
└── frontend/         # Next.js frontend (Phase 2)
```

## Trading Strategies

### IPO ATH Retest (v1.0.0)
Identifies IPO stocks that broke their all-time high and are now retesting the breakout zone.

**Rules:**
1. Stock within ±5% of ATH
2. Volume ≥ 1.5x 20-day average
3. Valid ATH breakout detected in history
4. Retest of breakout zone (volume contraction + support held)
5. Bullish entry trigger candle (volume expansion + close above retest high)

**Risk Management:**
- SL = nearest swing low (max 15%)
- TP1 = +10%, TP2 = +15%, TP3 = +20%
- Trail SL: after TP1 → move to entry; after TP2 → move to TP1

## Adding New Strategies

1. Create `backend/app/strategies/<name>/strategy.py`
2. Decorate class with `@register_strategy`
3. Implement `BaseStrategy` interface
4. Add module to `load_all_strategies()` in `registry.py`

No core engine changes required.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/health/detailed` | Full health with DB + Telegram |
| GET | `/api/v1/signals` | Active signals |
| GET | `/api/v1/signals/today` | Today's signals |
| GET | `/api/v1/watchlist` | Watchlist |
| GET | `/api/v1/watchlist/near-ath` | Near-ATH stocks |
| POST | `/api/v1/scanner/run` | Trigger manual scan |
| GET | `/api/v1/scanner/status` | Scheduler status |
| GET | `/api/v1/scanner/strategies` | Available strategies |

## Development Phases

- **Phase 1** ✅ Scanner + Strategy + Alerts (current)
- **Phase 2** 🔄 Dashboard + Paper Trading (Next.js)
- **Phase 3** 📋 Backtesting Engine
- **Phase 4** 📋 Zerodha + Upstox Live Trading
- **Phase 5** 📋 Additional Strategies
