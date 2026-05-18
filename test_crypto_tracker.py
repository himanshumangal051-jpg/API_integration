import unittest
from unittest.mock import Mock, patch

import crypto_tracker


class CryptoTrackerTests(unittest.TestCase):
    @patch("crypto_tracker.requests.get")
    def test_fetch_coin_ids_filters_by_query(self, mock_get: Mock) -> None:
        mock_response = Mock()
        mock_response.json.return_value = {
            "coins": [
                {"id": "bitcoin", "name": "Bitcoin", "symbol": "btc"},
                {"id": "ethereum", "name": "Ethereum", "symbol": "eth"},
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = crypto_tracker.fetch_coin_ids("bit")

        self.assertEqual(result, ["bitcoin"])

    def test_filter_market_data_with_market_cap_and_limit(self) -> None:
        rows = [
            {"name": "A", "market_cap": 100},
            {"name": "B", "market_cap": 200},
            {"name": "C", "market_cap": 300},
        ]

        filtered = crypto_tracker.filter_market_data(rows, min_market_cap=200, limit=1)

        self.assertEqual(filtered, [{"name": "B", "market_cap": 200}])

    @patch("crypto_tracker.requests.get")
    def test_fetch_market_data_raises_runtime_error_on_request_issue(
        self, mock_get: Mock
    ) -> None:
        mock_get.side_effect = crypto_tracker.requests.RequestException("timeout")

        with self.assertRaises(RuntimeError):
            crypto_tracker.fetch_market_data(["bitcoin"], "usd")


if __name__ == "__main__":
    unittest.main()
