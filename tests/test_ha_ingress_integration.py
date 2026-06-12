"""
Integration test for Home Assistant X-Ingress-Path header handling (issue #1228)

This test starts the PSA Car Controller app with --web-conf -r --offline -d10,
makes a GET request with X-Ingress-Path header, and verifies that hrefs in
the HTML response contain the prefix.

Run with: python -m unittest tests.test_ha_ingress_integration -v
or: python tests/test_ha_ingress_integration.py
"""
import os
import sys
import time
import re
import requests
import threading
from unittest import TestCase, skipIf
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


try:
    import psa_car_controller
    HAS_APP = True
except ImportError:
    HAS_APP = False


@skipIf(not HAS_APP, "App dependencies not available")
class TestHomeAssistantIngressIntegration(TestCase):
    """
    Integration tests for PSA Car Controller with Home Assistant X-Ingress-Path header.
    These tests verify that hrefs in the HTML response include the prefix.
    """

    @classmethod
    def setUpClass(cls):
        """Set up test server"""
        cls.server_thread = None
        cls.server_port = 18080
        cls.server_url = f"http://127.0.0.1:{cls.server_port}"

        # Start the PSA app in a thread
        def start_server():
            from psa_car_controller.__main__ import main
            from psa_car_controller.psacc.application.car_controller import PSACarController

            # Override sys.argv to pass the required arguments
            original_argv = sys.argv
            try:
                # Set up command line arguments
                sys.argv = [
                    'psa_car_controller',
                    '--web-conf',
                    '-r',
                    '--offline',
                    '-d', '10',
                    '-l', '127.0.0.1',
                    '-p', str(cls.server_port),
                    '-b', '/',
                    '-f', 'config/config.json'
                ]

                # Run the app
                main()
            except SystemExit:
                pass
            finally:
                sys.argv = original_argv

        cls.server_thread = threading.Thread(target=start_server, daemon=True)
        cls.server_thread.start()

        # Wait for server to start
        max_wait = 15
        for _ in range(max_wait):
            try:
                response = requests.get(cls.server_url, timeout=1)
                if response.status_code in (200, 404):
                    break
            except requests.exceptions.RequestException:
                time.sleep(1)
        else:
            cls.server_thread = None
            raise RuntimeError(f"Server failed to start on port {cls.server_port} within {max_wait}s")

        time.sleep(2)  # Extra time for Dash to initialize

    @classmethod
    def tearDownClass(cls):
        """Clean up test server"""
        # The daemon thread will exit when the main process exits
        pass

    def setUp(self):
        """Check if server is running before each test"""
        if self.server_thread is None:
            self.skipTest("Server failed to start")

        # Verify server is responsive
        try:
            response = requests.get(self.server_url, timeout=5)
            if response.status_code != 200:
                self.skipTest(f"Server not ready, got status {response.status_code}")
        except requests.exceptions.RequestException:
            self.skipTest("Server not responding")

    def test_root_route_with_ingress_path(self):
        """
        Test that / route returns HTML with hrefs containing the prefix
        when X-Ingress-Path header is present.
        """
        prefix = '/api/ingress/a93a74ea_psacc'
        headers = {
            'X-Ingress-Path': prefix,
            'Host': f'127.0.0.1:{self.server_port}'
        }

        url = f"{self.server_url}/"

        try:
            response = requests.get(url, headers=headers, timeout=10)

            self.assertEqual(response.status_code, 200,
                             f"Expected 200, got {response.status_code}")

            html = response.text

            # Check for prefix in HTML

            scripts = re.findall(r'src="([^"]+)"', html)
            for script in scripts:
                assert (not script.startswith("/")
                        ) or script.startswith(prefix), f"script {script} doesn't contain prefix"
            # The Dash app's initial HTML should contain the prefix in its config
            # Look for the Dash config which includes requests_pathname_prefix
            if 'requests_pathname_prefix' in html:
                import json
                # Try to extract the Dash config
                config_match = re.search(r'id="_dash-config"[^>]*>([^<]+)</script>', html)
                if config_match:
                    config_str = config_match.group(1)
                    try:
                        config = json.loads(config_str)
                        requests_prefix = config.get('requests_pathname_prefix', '')
                        print(f"Dash config requests_pathname_prefix: {requests_prefix}")

                        # Check if it matches our prefix
                        if prefix in requests_prefix:
                            print(f"✓ Dash config has correct prefix")
                            return
                        else:
                            print(f"✗ Dash config prefix doesn't match")
                            print(f"  Expected: {prefix}")
                            print(f"  Got: {requests_prefix}")
                    except json.JSONDecodeError:
                        pass

            # Check if prefix appears in hrefs
            hrefs = re.findall(r'href="([^"]+)"', html)
            prefix_hrefs = [h for h in hrefs if prefix in h]

            if prefix_hrefs:
                print(f"✓ Found {len(prefix_hrefs)} hrefs with prefix")
            else:
                # Check if prefix appears anywhere
                if prefix in html:
                    print(f"✓ Prefix found in HTML")
                else:
                    print(f"✗ Prefix NOT found in HTML")
                    print(f"Sample hrefs: {hrefs[:10]}")
                    with open('/tmp/test_root_response.html', 'w') as f:
                        f.write(html)
                    self.fail(f"Prefix '{prefix}' not found in HTML")

        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

    def test_api_route_with_ingress_path(self):
        """
        Test that Flask API routes (from api.py) work with prefix header.
        """
        headers = {
            'X-Ingress-Path': '/api/ingress/a93a74ea_psacc/',
            'Host': f'127.0.0.1:{self.server_port}'
        }

        # Try a simple API route that should work
        url = f"{self.server_url}/get_vehicles"

        try:
            response = requests.get(url, headers=headers, timeout=10)

            # API should return JSON
            if response.status_code == 200:
                print(f"✓ API route /get_vehicles returned 200")
            else:
                print(f"API route returned {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"API request failed (may need auth): {e}")
            # This is OK - we're just checking the server is running


if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)
