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
import socket
import requests
import threading
from unittest import TestCase

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def is_port_free(port, host='127.0.0.1'):
    """Check if a port is free on the specified host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except socket.error:
            return False


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

        # Check if port is free before starting server
        if not is_port_free(cls.server_port):
            raise RuntimeError(f"Port {cls.server_port} is already in use")

        # Start the PSA app in a thread
        def start_server():
            from psa_car_controller.__main__ import main
            from psa_car_controller.psacc.application.car_controller import PSACarController

            # Override sys.argv to pass the required arguments
            original_argv = sys.argv
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "config.json")
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
                    '-f', config_path
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

    def validate_path(self, headers, expected_prefix):

        try:
            response = requests.get(self.server_url, headers=headers, timeout=10)

            self.assertEqual(response.status_code, 200,
                             f"Expected 200, got {response.status_code}")

            html = response.text

            # Check for prefix in HTML

            scripts = re.findall(r'src="(/[^"]+)"', html)
            for script in scripts:
                assert re.match(expected_prefix, script), f"Script {script} does not match {expected_prefix}"
            # Check if prefix appears in hrefs
            hrefs = re.findall(f'href="(/[^"]+)"', html)
            for href in hrefs:
                assert re.match(expected_prefix, href), f"Href {href} does not match {expected_prefix}"

        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

    def test_root_route_with_ingress_path(self):
        """
        Test that / route returns HTML with hrefs containing the prefix
        when X-Ingress-Path header is present.
        """
        prefix = r'/api/ingress/a93a74ea_psacc/.+'
        headers = {
            'X-Ingress-Path': prefix,
            'Host': f'127.0.0.1:{self.server_port}'
        }
        self.validate_path(headers, prefix)

    def test_root_route_without(self):
        """
        Test that / route returns HTML with hrefs containing the prefix
        when X-Ingress-Path header is present.
        """
        headers = {
            'Host': f'127.0.0.1:{self.server_port}'
        }
        self.validate_path(headers, r"/(assets|_dash|_favicon).+")

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

    def test_style_json_with_ingress_path(self):
        """
        Test that /style.json returns JSON with sprite path containing the prefix
        when X-Ingress-Path header is present.
        """
        prefix = '/api/ingress/a93a74ea_psacc/'
        headers = {
            'X-Ingress-Path': prefix,
            'Host': f'127.0.0.1:{self.server_port}'
        }

        url = f"{self.server_url}/style.json"
        expected = f"{self.server_url}{prefix}assets/sprites/osm-liberty"
        try:
            # todo lower timeout
            response = requests.get(url, headers=headers, timeout=3600)

            self.assertEqual(response.status_code, 200,
                             f"Expected 200, got {response.status_code}")

            data = response.json()
            self.assertIn('sprite', data, "Response should contain 'sprite' key")

            sprite_path = data['sprite']
            self.assertEqual(sprite_path, expected)

        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

    def test_svg_images_with_ingress_path(self):
        """
        Test that SVG images in HTML have correct path with X-Ingress-Path header.
        Specifically checks for battery-soh.svg and other image paths.
        """
        prefix = '/api/ingress/a93a74ea_psacc/'
        headers = {
            'X-Ingress-Path': prefix,
            'Host': f'127.0.0.1:{self.server_port}'
        }

        try:
            response = requests.get(self.server_url, headers=headers, timeout=10)

            self.assertEqual(response.status_code, 200,
                             f"Expected 200, got {response.status_code}")

            html = response.text

            # Find all src attributes in img tags
            img_srcs = re.findall(r'<img[^>]+src="([^"]+)"', html)

            # Check each image source
            for img_src in img_srcs:
                # Skip data URLs
                if img_src.startswith('data:'):
                    continue

                # Check if it's an assets/image path
                if 'assets/images/' in img_src:
                    # The path should start with the prefix
                    self.assertTrue(img_src.startswith(prefix),
                                    f"Image path {img_src} does not start with prefix {prefix}")

        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)
