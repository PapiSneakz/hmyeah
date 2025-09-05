# Overview

This is an AI trading bot designed for educational purposes that supports both backtesting and paper trading functionality. The system implements a modular architecture with separate components for trading strategies, risk management, data sourcing, and order execution. The bot can simulate trading using historical data for backtesting or run live paper trading with real market data through the CCXT library integration.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Components

The application follows a modular design pattern with clear separation of concerns:

**Strategy Engine**: Implements a base strategy interface with concrete implementations like SMA crossover with RSI filtering and scalping strategies. Strategies generate buy/sell signals based on technical indicators using the `ta` library.

**Risk Management**: Handles position sizing based on equity percentage limits and implements stop-loss/take-profit mechanisms. The risk manager calculates appropriate position sizes and exit levels for each trade.

**Data Sources**: Dual-mode data handling supporting both historical data for backtesting and live data feeds for paper trading. Uses CCXT for real exchange data with fallback to synthetic random-walk data for testing.

**Broker Simulation**: Paper broker implementation that simulates order execution, fee calculation, and position tracking without real money. Maintains equity and position state with realistic fee and slippage modeling.

**Backtesting Engine**: Processes historical data through the strategy and risk management components to generate performance metrics, trade logs, and equity curve visualizations.

## Configuration Management

Uses YAML-based configuration files with environment variable support for sensitive data like API keys. Configuration covers market settings, strategy parameters, risk limits, and exchange credentials.

## File Structure

- `/bot/` - Core trading system modules
- `/artifacts/` - Output directory for backtest results, charts, and state files
- Configuration files at root level
- Execution scripts for backtesting and paper trading modes

## Data Flow

1. Data source fetches market data (historical or live)
2. Strategy component analyzes data and generates signals
3. Risk manager validates and sizes positions
4. Broker component executes trades and tracks state
5. Results are logged and visualized

## Keep-Alive System

Includes a Flask-based keep-alive server for deployment on platforms like Replit that require active HTTP endpoints to prevent sleeping.

# External Dependencies

**Market Data**: CCXT library for connecting to cryptocurrency exchanges (Binance, Kraken, Coinbase, etc.) to fetch both historical and live market data.

**Technical Analysis**: TA-Lib Python library for calculating technical indicators like moving averages, RSI, and other trading signals.

**Data Processing**: Pandas for data manipulation and NumPy for numerical computations.

**Visualization**: Matplotlib for generating equity curve charts and performance visualizations.

**Configuration**: PyYAML for configuration file parsing and python-dotenv for environment variable management.

**Scheduling**: Schedule library for timing live trading operations.

**Web Framework**: Flask for the keep-alive server functionality.

**Validation**: Pydantic for configuration validation and type checking.

The system is designed to work without real exchange connections by using synthetic data, making it safe for educational testing and development.