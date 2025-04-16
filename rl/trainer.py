import numpy as np
from rl.environment import StockTradingEnv
from rl.models import create_ppo_model, create_sac_model
from stable_baselines3 import PPO
import os

def calculate_metrics(net_worths):
    """
    Calculate performance metrics for the trading strategy.
    
    Args:
        net_worths (list): List of net worths over time.
    
    Returns:
        tuple: Sharpe ratio, max drawdown.
    """
    returns = np.diff(net_worths) / net_worths[:-1]
    sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
    max_drawdown = (max(net_worths) - min(net_worths)) / max(net_worths) if max(net_worths) > 0 else 0
    return sharpe_ratio, max_drawdown

def train_model(ticker, months=12, total_timesteps=100000, save_path="models/ppo_model", algo="ppo"):
    """
    Train a model on the stock trading environment.
    """
    # Create environment
    env = StockTradingEnv(ticker, months=months, continuous=(algo == "sac"))
    
    # Create and train model
    if algo == "ppo":
        model = create_ppo_model(env)
    elif algo == "sac":
        model = create_sac_model(env)
    else:
        raise ValueError(f"Unsupported algorithm: {algo}")
    
    model.learn(total_timesteps=total_timesteps)
    
    # Save model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    
    # Evaluate
    obs, _ = env.reset()
    total_reward = 0
    actions = []
    net_worths = []
    print(f"Starting evaluation with obs shape: {obs.shape}")
    while True:
        action, _ = model.predict(obs, deterministic=True)  # Ensure deterministic prediction
        if isinstance(action, np.ndarray) and action.ndim == 0:
            action = action.item()  # Convert 0D array to scalar
        elif isinstance(action, np.ndarray) and action.ndim == 1:
            action = action[0]  # Take first element if 1D
        obs, reward, done, truncated, _ = env.step(action)
        total_reward += reward
        actions.append(action)
        net_worths.append(env.net_worth)
        
        print(f"Eval step: Action={action}, Net Worth={env.net_worth}")  # Debug
        if done or truncated:
            break
    
    sharpe_ratio, max_drawdown = calculate_metrics(net_worths)
    print(f"Evaluation complete. Actions: {len(actions)}, Net Worths: {len(net_worths)}, Max Net Worth: {max(net_worths)}")
    return actions, net_worths, total_reward, sharpe_ratio, max_drawdown

def evaluate_model(ticker, months=12, model_path="models/ppo_model", algo="ppo"):
    """
    Evaluate a trained model.
    
    Args:
        ticker (str): Stock ticker.
        months (int): Data range in months.
        model_path (str): Path to the trained model.
        algo (str): Algorithm used ("ppo" or "sac").
    
    Returns:
        tuple: Actions, net worths, total reward, Sharpe ratio, max drawdown.
    """
    env = StockTradingEnv(ticker, months=months, continuous=(algo == "sac"))
    if algo == "ppo":
        model = PPO.load(model_path)
    elif algo == "sac":
        from stable_baselines3 import SAC
        model = SAC.load(model_path)
    else:
        raise ValueError(f"Unsupported algorithm: {algo}")
    
    obs, _ = env.reset()
    total_reward = 0
    actions = []
    net_worths = []
    
    while True:
        action, _ = model.predict(obs)
        obs, reward, done, truncated, _ = env.step(action)
        total_reward += reward
        actions.append(action)
        net_worths.append(env.net_worth)
        if done or truncated:
            break
    print(f"Starting evaluation with obs shape: {obs.shape}")
    

    print(f"Total Reward: {total_reward}, Actions Taken: {len(actions)}, Net Worths Recorded: {len(net_worths)}")
    
    sharpe_ratio, max_drawdown = calculate_metrics(net_worths)
    return actions, net_worths, total_reward, sharpe_ratio, max_drawdown