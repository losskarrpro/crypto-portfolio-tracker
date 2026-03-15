import unittest
import json
import os
from unittest.mock import patch, MagicMock, mock_open
import requests
from portfolio import Portfolio


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        self.config_path = 'test_config.json'
        self.test_config = {
            "coins": {
                "bitcoin": {"quantity": 1.0, "purchase_price": 50000.0},
                "ethereum": {"quantity": 10.0, "purchase_price": 3000.0}
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
        self.portfolio = Portfolio(self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_load_config(self):
        loaded_config = self.portfolio.config
        self.assertEqual(loaded_config, self.test_config)

    @patch('requests.get')
    def test_fetch_prices_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bitcoin": {"usd": 60000.0},
            "ethereum": {"usd": 4000.0}
        }
        mock_get.return_value = mock_response

        prices = self.portfolio.fetch_prices()
        self.assertEqual(prices['bitcoin'], 60000.0)
        self.assertEqual(prices['ethereum'], 4000.0)
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_fetch_prices_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        prices = self.portfolio.fetch_prices()
        self.assertEqual(prices, {})

    def test_calculate_total_value(self):
        self.portfolio.prices = {'bitcoin': 60000.0, 'ethereum': 4000.0}
        total_value = self.portfolio.calculate_total_value()
        expected = (1.0 * 60000.0) + (10.0 * 4000.0)
        self.assertEqual(total_value, expected)

    def test_calculate_total_value_no_prices(self):
        self.portfolio.prices = {}
        total_value = self.portfolio.calculate_total_value()
        self.assertEqual(total_value, 0.0)

    def test_calculate_purchase_value(self):
        purchase_value = self.portfolio.calculate_purchase_value()
        expected = (1.0 * 50000.0) + (10.0 * 3000.0)
        self.assertEqual(purchase_value, expected)

    def test_calculate_pnl(self):
        self.portfolio.prices = {'bitcoin': 60000.0, 'ethereum': 4000.0}
        pnl = self.portfolio.calculate_pnl()
        purchase_value = self.portfolio.calculate_purchase_value()
        total_value = self.portfolio.calculate_total_value()
        expected_pnl = total_value - purchase_value
        self.assertEqual(pnl, expected_pnl)

    def test_calculate_pnl_no_prices(self):
        self.portfolio.prices = {}
        pnl = self.portfolio.calculate_pnl()
        self.assertEqual(pnl, 0.0)

    def test_calculate_evolution_percent(self):
        self.portfolio.prices = {'bitcoin': 60000.0, 'ethereum': 4000.0}
        evolution_percent = self.portfolio.calculate_evolution_percent()
        purchase_value = self.portfolio.calculate_purchase_value()
        pnl = self.portfolio.calculate_pnl()
        expected = (pnl / purchase_value) * 100 if purchase_value > 0 else 0.0
        self.assertAlmostEqual(evolution_percent, expected, places=2)

    def test_calculate_evolution_percent_no_purchase(self):
        empty_config = {"coins": {}}
        with open(self.config_path, 'w') as f:
            json.dump(empty_config, f)
        portfolio = Portfolio(self.config_path)
        portfolio.prices = {'bitcoin': 60000.0}
        evolution = portfolio.calculate_evolution_percent()
        self.assertEqual(evolution, 0.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)