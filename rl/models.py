from stable_baselines3 import PPO, SAC

def create_ppo_model(env, learning_rate=0.0005, n_steps=4096):
    """
    Create a PPO model for the trading environment.
    
    Args:
        env: Gymnasium environment.
        learning_rate (float): Learning rate for the optimizer.
        n_steps (int): Number of steps to run per update.
    
    Returns:
        PPO: Configured PPO model.
    """
    return PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=learning_rate,
        n_steps=n_steps,
        batch_size=128,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        ent_coef=0.01,
        clip_range=0.3,
        verbose=1
    )

def create_sac_model(env, learning_rate=0.0003):
    """
    Create an SAC model for the trading environment.
    
    Args:
        env: Gymnasium environment.
        learning_rate (float): Learning rate for the optimizer.
    
    Returns:
        SAC: Configured SAC model.
    """
    return SAC(
        policy="MlpPolicy",
        env=env,
        learning_rate=learning_rate,
        buffer_size=100000,
        batch_size=256,
        tau=0.005,
        gamma=0.99,
        verbose=1
    )