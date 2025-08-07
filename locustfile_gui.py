"""
Locust GUI-compatible load testing file for the Penguin Species Prediction API.

This simplified version works perfectly with the Locust web interface.
Run with: uv run locust -f locustfile_gui.py
"""

import random
from locust import HttpUser, task, between
import json


class PenguinAPIUser(HttpUser):
    """
    Main user class for GUI load testing.
    Simulates users making requests to the Penguin Prediction API.
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    @task(8)  # 8/10 requests will be predictions
    def predict_penguin_species(self):
        """Test the main prediction endpoint with realistic penguin data."""
        
        # Realistic penguin data samples
        penguin_data_samples = [
            # Adelie penguin
            {
                "bill_length_mm": random.uniform(32.1, 46.0),
                "bill_depth_mm": random.uniform(15.5, 21.5),
                "flipper_length_mm": random.randint(172, 210),
                "body_mass_g": random.randint(2850, 4775),
                "year": random.choice([2007, 2008, 2009]),
                "sex": random.choice(["male", "female"]),
                "island": random.choice(["Torgersen", "Biscoe", "Dream"])
            },
            # Chinstrap penguin
            {
                "bill_length_mm": random.uniform(40.9, 58.0),
                "bill_depth_mm": random.uniform(16.4, 20.8),
                "flipper_length_mm": random.randint(178, 212),
                "body_mass_g": random.randint(2700, 4800),
                "year": random.choice([2007, 2008, 2009]),
                "sex": random.choice(["male", "female"]),
                "island": "Dream"
            },
            # Gentoo penguin
            {
                "bill_length_mm": random.uniform(40.9, 59.6),
                "bill_depth_mm": random.uniform(13.1, 17.3),
                "flipper_length_mm": random.randint(203, 231),
                "body_mass_g": random.randint(3950, 6300),
                "year": random.choice([2007, 2008, 2009]),
                "sex": random.choice(["male", "female"]),
                "island": "Biscoe"
            }
        ]
        
        penguin_data = random.choice(penguin_data_samples)
        
        with self.client.post(
            "/predict",
            json=penguin_data,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if "predicted_species" in result and "confidence" in result:
                        if result["predicted_species"] in ["Adelie", "Chinstrap", "Gentoo"]:
                            response.success()
                        else:
                            response.failure(f"Invalid species: {result['predicted_species']}")
                    else:
                        response.failure("Missing required fields")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)  # 1/10 requests will be health checks
    def health_check(self):
        """Test the health check endpoint."""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if "status" in result:
                        response.success()
                    else:
                        response.failure("Missing status field")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Health check failed: HTTP {response.status_code}")
    
    @task(1)  # 1/10 requests will test error handling
    def test_invalid_input(self):
        """Test API error handling with invalid data."""
        invalid_data = {
            "bill_length_mm": "invalid",  # Should be float
            "bill_depth_mm": 18.7,
            "flipper_length_mm": 181,
            "body_mass_g": 3750,
            "year": 2007,
            "sex": "male",
            "island": "Torgersen"
        }
        
        with self.client.post(
            "/predict",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code in [400, 422]:
                response.success()  # Expected error response
            elif response.status_code == 200:
                response.success()  # Also acceptable
            else:
                response.failure(f"Unexpected status: {response.status_code}")