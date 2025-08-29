from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Trading System API", description="DCA Trading with Risk Management")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class TradingConfig(BaseModel):
    symbol: str = "BTC/USD"
    dca_amount: float = 100.0
    dca_interval: int = 24  # hours
    hedge_ratio: float = 0.3
    risk_limit: float = 0.1  # 10% max loss
    take_profit: float = 0.15  # 15% profit target

class TradeExecution(BaseModel):
    config: TradingConfig
    simulate: bool = True

class Portfolio(BaseModel):
    total_value: float
    positions: List[Dict[str, Any]]
    pnl: float
    trades: List[Dict[str, Any]]

# In-memory storage (in production, use a real database)
current_config = TradingConfig()
portfolio_data = Portfolio(
    total_value=10000.0,
    positions=[],
    pnl=0.0,
    trades=[]
)

# Trading Algorithm Engine
class TradingEngine:
    @staticmethod
    def calculate_dca_position(config: TradingConfig, current_price: float = 50000.0) -> Dict[str, Any]:
        """Calculate DCA position based on configuration"""
        position_size = config.dca_amount / current_price
        return {
            "type": "DCA_BUY",
            "symbol": config.symbol,
            "size": position_size,
            "price": current_price,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def calculate_hedge(config: TradingConfig, position_value: float) -> Dict[str, Any]:
        """Calculate hedge position to manage risk"""
        hedge_size = position_value * config.hedge_ratio
        return {
            "type": "HEDGE",
            "symbol": f"{config.symbol}_HEDGE",
            "size": hedge_size,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def assess_risk(portfolio: Portfolio, config: TradingConfig) -> Dict[str, Any]:
        """Assess current portfolio risk"""
        risk_percentage = abs(portfolio.pnl) / portfolio.total_value if portfolio.total_value > 0 else 0
        return {
            "current_risk": risk_percentage,
            "risk_limit": config.risk_limit,
            "within_limits": risk_percentage <= config.risk_limit,
            "recommendation": "REDUCE_POSITION" if risk_percentage > config.risk_limit else "CONTINUE"
        }

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Trading System API", "status": "active"}

@app.get("/config")
def get_config():
    """Get current trading configuration"""
    return current_config

@app.post("/config")
def update_config(config: TradingConfig):
    """Update trading configuration"""
    global current_config
    current_config = config
    return {"message": "Configuration updated", "config": current_config}

@app.post("/execute")
def execute_trade(execution: TradeExecution):
    """Execute trading strategy"""
    global portfolio_data
    
    # Simulate market price (in production, get from real API)
    current_price = 50000.0 + (hash(str(datetime.now())) % 10000 - 5000)  # Mock price variation
    
    # Calculate DCA position
    dca_trade = TradingEngine.calculate_dca_position(execution.config, current_price)
    
    # Calculate hedge if needed
    hedge_trade = TradingEngine.calculate_hedge(execution.config, execution.config.dca_amount)
    
    # Update portfolio (simplified simulation)
    portfolio_data.positions.append(dca_trade)
    portfolio_data.trades.extend([dca_trade, hedge_trade])
    
    # Calculate P&L (simplified)
    price_change = (current_price - 50000) / 50000  # Assume 50k baseline
    portfolio_data.pnl = portfolio_data.total_value * price_change * 0.1  # 10% exposure
    
    # Risk assessment
    risk_assessment = TradingEngine.assess_risk(portfolio_data, execution.config)
    
    return {
        "execution_result": "SUCCESS" if execution.simulate else "EXECUTED",
        "trades": [dca_trade, hedge_trade],
        "portfolio": portfolio_data,
        "risk_assessment": risk_assessment,
        "current_price": current_price
    }

@app.get("/portfolio")
def get_portfolio():
    """Get current portfolio status"""
    return portfolio_data

@app.get("/risk-analysis")
def get_risk_analysis():
    """Get detailed risk analysis"""
    risk_assessment = TradingEngine.assess_risk(portfolio_data, current_config)
    return risk_assessment

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/ui")
def serve_ui():
    """Serve the trading UI"""
    return FileResponse("static/index.html")