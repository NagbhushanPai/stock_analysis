import time
import numpy as np
from rl.environment import StockTradingEnv
from rl.models import create_ppo_model, create_sac_model
from stable_baselines3 import PPO
import os
from tqdm import tqdm # Ensure tqdm is imported
from stable_baselines3.common.callbacks import BaseCallback # Ensure BaseCallback is imported

def calculate_metrics(net_worths):
    """
    Calculate performance metrics for the trading strategy.
    
    Args:
        net_worths (list): List of net worths over time.
    
    Returns:
        tuple: Sharpe ratio, max drawdown.
    """
    if len(net_worths) < 2:
        return 0, 0 # Not enough data
    net_worths = np.array(net_worths) # Ensure numpy array for calculations
    returns = np.diff(net_worths) / net_worths[:-1]
    
    # Handle potential division by zero or NaN if returns are constant or net_worths are zero
    returns = returns[~np.isnan(returns) & ~np.isinf(returns)] # Filter out NaNs/Infs
    if len(returns) == 0:
        return 0, 0

    std_dev = np.std(returns)
    if std_dev == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = np.mean(returns) / std_dev * np.sqrt(252) # Annualized Sharpe

    # Calculate Max Drawdown
    peak = np.maximum.accumulate(net_worths)
    # Ensure peak is not zero to avoid division by zero
    peak[peak == 0] = 1 # Replace 0 peaks with 1 to avoid division error, drawdown will be 0 anyway
    drawdown = (peak - net_worths) / peak
    max_drawdown = np.max(drawdown)

    return sharpe_ratio, max_drawdown

# Global variables to track progress and ETA for the web UI
training_progress = 0
training_start_time = None
training_eta = None # Estimated time remaining as string "HH:MM:SS" or None

# Custom callback integrating tqdm for terminal and updating global vars for web UI
class TqdmCallback(BaseCallback):
    def __init__(self, total_timesteps, verbose=0):
        super(TqdmCallback, self).__init__(verbose)
        self.pbar = None
        self.total_timesteps = total_timesteps
        self.last_timestep = 0

    def _on_training_start(self):
        global training_start_time, training_progress, training_eta
        training_start_time = time.time()
        training_progress = 0
        training_eta = "Calculating..."
        # Initialize tqdm progress bar for the terminal
        self.pbar = tqdm(total=self.total_timesteps, desc="Training Progress", unit="step")
        self.last_timestep = 0

    def _on_step(self) -> bool:
        global training_progress, training_eta, training_start_time
        
        current_steps = self.num_timesteps
        # Update tqdm progress bar
        update_amount = current_steps - self.last_timestep
        if update_amount > 0: # Only update if steps increased
             self.pbar.update(update_amount)
             self.last_timestep = current_steps

        # Update global variables for web UI progress
        if self.total_timesteps > 0:
            progress = min(100.0, (current_steps / self.total_timesteps) * 100.0)
            training_progress = max(training_progress, int(progress)) # Use max to avoid decrease

            # Calculate ETA for web UI and tqdm description
            if training_start_time is not None and current_steps > 5:
                elapsed_time = time.time() - training_start_time
                if progress > 0:
                    total_estimated_time = (elapsed_time / progress) * 100
                    remaining_time_seconds = max(0, total_estimated_time - elapsed_time)
                    # Format ETA as HH:MM:SS
                    hours = int(remaining_time_seconds // 3600)
                    minutes = int((remaining_time_seconds % 3600) // 60)
                    seconds = int(remaining_time_seconds % 60)
                    training_eta = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    # Update tqdm description with ETA
                    self.pbar.set_description(f"Training Progress (ETA: {training_eta})")
                else:
                    training_eta = "Calculating..."
                    self.pbar.set_description(f"Training Progress (ETA: {training_eta})")
            elif training_start_time is not None:
                 training_eta = "Calculating..."
                 self.pbar.set_description(f"Training Progress (ETA: {training_eta})")

        return True # Continue training

    def _on_training_end(self):
        global training_progress, training_eta
        # Ensure progress bar reaches 100% and closes
        if self.pbar:
            # Ensure the bar visually completes if learn() finished slightly early
            update_amount = self.total_timesteps - self.pbar.n
            if update_amount > 0:
                self.pbar.update(update_amount)
            self.pbar.close()
            self.pbar = None
        # Update global state for web UI
        training_progress = 100
        training_eta = "00:00:00" # Training finished
        print("\nTrainer: Training finished.") # Add newline after tqdm


def train_model(ticker, months=12, total_timesteps=100000, save_path="models/ppo_model", algo="ppo"):
    # ... (rest of train_model function remains the same, using TqdmCallback) ...
    """
    Train a model with progress tracking (tqdm for terminal, globals for web UI).
    """
    global training_progress, training_start_time, training_eta # Ensure globals are accessible
    # Reset global state at the start of training attempt
    training_progress = 0
    training_start_time = None
    training_eta = None
    print(f"Trainer: Initializing training for {ticker} ({algo.upper()})...")

    # Create environment
    env = StockTradingEnv(ticker, months=months, continuous=(algo == "sac"))

    # Create model
    if algo == "ppo":
        model = create_ppo_model(env)
    elif algo == "sac":
        # Ensure SAC is imported if used
        from stable_baselines3 import SAC 
        model = create_sac_model(env) # Assumes create_sac_model exists
    else:
        raise ValueError(f"Unsupported algorithm: {algo}")

    # Create the callback instance
    tqdm_callback = TqdmCallback(total_timesteps=total_timesteps)

    print(f"Trainer: Starting model.learn for {total_timesteps} timesteps...")
    try:
        # Pass the callback to the learn method
        model.learn(total_timesteps=total_timesteps, callback=tqdm_callback, log_interval=1000) # Adjust log_interval
    except Exception as e:
        print(f"\nError during model.learn: {e}")
        # Ensure tqdm bar is closed on error
        if tqdm_callback.pbar:
            tqdm_callback.pbar.close()
        raise # Re-raise the exception
    # Note: _on_training_end in the callback handles final state updates

    # Save model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    print(f"Trainer: Model saved to {save_path}")

    # Evaluate
    print(f"Trainer: Starting evaluation...")
    obs, _ = env.reset()
    total_reward = 0
    actions = []
    net_worths = []

    while True:
        action, _ = model.predict(obs, deterministic=True)
        if isinstance(action, np.ndarray):
             action = action.item()

        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        actions.append(action)
        net_worths.append(env.net_worth)

        if done or truncated:
            print(f"Trainer: Evaluation loop finished. Done={done}, Truncated={truncated}")
            break

    sharpe_ratio, max_drawdown = calculate_metrics(net_worths)
    print(f"Trainer: Evaluation complete. Sharpe={sharpe_ratio:.2f}, Drawdown={max_drawdown:.2%}")

    # Final state already set by callback's _on_training_end
    print(f"Trainer: Training function finished.")
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
        action, _ = model.predict(obs, deterministic=True)
        if isinstance(action, np.ndarray):
             action = action.item()
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