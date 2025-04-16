import unittest
import numpy as np
from rl.environment import StockTradingEnv

class TestRLComponents(unittest.TestCase):
    def test_environment(self):
        env = StockTradingEnv(ticker="NVDA", months=3)
        obs, _ = env.reset()
        print(f"Observation: {obs}")  # Debug output
        self.assertEqual(len(obs), 8, f"Expected 8 elements, got {len(obs)}")
        self.assertTrue(np.all(np.isfinite(obs)), f"Observation contains non-finite values: {obs}")
        self.assertGreater(obs[0], 0, "Price should be positive")
        self.assertGreaterEqual(obs[3], 0, "Balance should be non-negative")
        self.assertEqual(obs[4], 0, "Shares_held should be 0 at reset")
        self.assertTrue(0 <= obs[5] <= 100, f"RSI out of range: {obs[5]}")
        action = env.action_space.sample()
        next_obs, reward, done, truncated, _ = env.step(action)
        print(f"Next observation: {next_obs}")  # Debug output
        self.assertEqual(len(next_obs), 8)
        self.assertIsInstance(reward, float)
        self.assertIsInstance(done, bool)
        self.assertIsInstance(truncated, bool)

if __name__ == '__main__':
    unittest.main()