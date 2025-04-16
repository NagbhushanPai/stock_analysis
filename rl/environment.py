import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces
from data.fetcher import fetch_historical_data
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
from ta.trend import MACD

class StockTradingEnv(gym.Env):
    def __init__(self, ticker, months=12, initial_balance=10000, continuous=False):
        super(StockTradingEnv, self).__init__()
        self.ticker = ticker
        self.months = months
        self.initial_balance = initial_balance
        self.continuous = continuous
        self.current_step = 0
        self.balance = initial_balance
        self.shares_held = 0
        self.net_worth = initial_balance
        
        # Fetch data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        self.data = fetch_historical_data(ticker, start_date, end_date, interval="1d", context="rl")
        if self.data.empty:
            raise ValueError(f"No data fetched for {ticker}")
        
        # Add technical indicators
        self.data['RSI'] = RSIIndicator(self.data['Close'], window=14).rsi()
        macd = MACD(self.data['Close'], window_slow=26, window_fast=12, window_sign=9)
        self.data['MACD'] = macd.macd()
        self.data['MACD_Signal'] = macd.macd_signal()
        
        # Handle NaN values
        self.data = self.data.bfill().ffill()
        
        # Drop initial rows with NaN indicators
        self.data = self.data.dropna()
        if len(self.data) < 20:
            raise ValueError(f"Insufficient valid data for {ticker} after cleaning: {len(self.data)} rows")
        
        # Normalize data for observation
        self.price_max = self.data['Close'].max()
        self.ma20_max = self.data['MA20'].max()
        self.ma50_max = self.data['MA50'].max()
        self.balance_max = initial_balance * 2
        self.shares_max = initial_balance / self.data['Close'].min()
        self.macd_max = max(abs(self.data['MACD'].max()), abs(self.data['MACD_Signal'].max())) or 1
        
        # Action space
        if self.continuous:
            self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)  # Position size
        else:
            self.action_space = spaces.Discrete(3)  # 0=hold, 1=buy, 2=sell
        
        # Observation space: [price, MA20, MA50, balance, shares_held, RSI, MACD, MACD_Signal]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, -1, -1]),
            high=np.array([1, 1, 1, 1, 1, 1, 1, 1]),
            shape=(8,),
            dtype=np.float32
        )
        
        self.max_steps = len(self.data) - 1
        self.current_step = min(self.current_step, self.max_steps)
        self.net_worths = []
    
    def reset(self, seed=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        self.net_worths = []
        return self._get_observation(), {}
    
    def step(self, action):
        current_price = self.data['Close'].iloc[self.current_step]
        
        # Execute action
        if self.continuous:
            position = action[0]  # -1 (full sell) to 1 (full buy)
            target_shares = (self.balance / current_price) * position
            shares_diff = target_shares - self.shares_held
            if shares_diff > 0:
                shares_to_buy = min(shares_diff, self.balance // current_price)
                cost = shares_to_buy * current_price
                self.balance -= cost
                self.shares_held += shares_to_buy
            elif shares_diff < 0:
                shares_to_sell = min(-shares_diff, self.shares_held)
                proceeds = shares_to_sell * current_price
                self.balance += proceeds
                self.shares_held -= shares_to_sell
        else:
            if action == 1:  # Buy
                shares_to_buy = self.balance // current_price
                cost = shares_to_buy * current_price
                self.balance -= cost
                self.shares_held += shares_to_buy
            elif action == 0:  # Hold
                pass
            elif action == 2:  # Sell
                proceeds = self.shares_held * current_price
                self.balance += proceeds
                self.shares_held = 0
        
        # Update net worth
        self.net_worth = self.balance + self.shares_held * current_price
        self.net_worths.append(self.net_worth)
        
        # Move to next step
        self.current_step += 1
        done = self.current_step >= self.max_steps
        truncated = False
        
        # Reward: Sharpe ratio or scaled net worth change
        if len(self.net_worths) > 20:
            returns = pd.Series(self.net_worths[-20:]).pct_change().dropna()
            reward = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            prev_net_worth = self.net_worths[0] if self.current_step == 1 else self.net_worths[-2]
            reward = (self.net_worth - prev_net_worth) / self.initial_balance * 100
        
        return self._get_observation(), reward, done, truncated, {}
    
    def _get_observation(self):
        obs = np.array([
            self.data['Close'].iloc[self.current_step] / self.price_max,
            self.data['MA20'].iloc[self.current_step] / self.ma20_max,
            self.data['MA50'].iloc[self.current_step] / self.ma50_max,
            self.balance / self.balance_max,
            self.shares_held / self.shares_max,
            self.data['RSI'].iloc[self.current_step] / 100,
            self.data['MACD'].iloc[self.current_step] / self.macd_max,
            self.data['MACD_Signal'].iloc[self.current_step] / self.macd_max
        ], dtype=np.float32)
        if not np.all(np.isfinite(obs)):
            raise ValueError(f"Non-finite observation at step {self.current_step}: {obs}")
        return obs