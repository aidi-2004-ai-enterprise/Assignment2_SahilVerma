"""
Locust load testing file for the Penguin Species Prediction API.

This file defines load testing scenarios to validate the performance and
scalability of the FastAPI application both locally and in Cloud Run.

To run tests:
1. Install locust: uv add locust
2. Run tests: uv run locust
3. Open web interface: http://localhost:8089

Test Scenarios:
- Baseline: 1 user, 60 seconds
- Normal: 10 users, 5 minutes  
- Stress: 50 users, 2 minutes
- Spike: 1 to 100 users over 1 minute
"""

import random
from locust import HttpUser, task, between
import json


class PenguinAPIUser(HttpUser):
    """
    Simulates a user making requests to the Penguin Prediction API.
    
    Each simulated user will make requests with realistic penguin data
    and wait between 1-3 seconds between requests to simulate real usage.
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts. Can be used for login, setup, etc."""
        pass
    
    @task(8)  # Weight: 8/10 requests will be predictions
    def predict_penguin_species(self):
        """
        Test the main prediction endpoint with realistic penguin data.
        
        Uses a variety of realistic penguin measurements to test the model
        with different species characteristics.
        """
        
        # Define realistic penguin data ranges for each species
        penguin_data_samples = [
            # Adelie penguin characteristics (smaller, shorter bills)
            {
                "bill_length_mm": random.uniform(32.1, 46.0),
                "bill_depth_mm": random.uniform(15.5, 21.5),
                "flipper_length_mm": random.randint(172, 210),
                "body_mass_g": random.randint(2850, 4775),
                "year": random.choice([2007, 2008, 2009]),
                "sex": random.choice(["male", "female"]),
                "island": random.choice(["Torgersen", "Biscoe", "Dream"])
            },
            # Chinstrap penguin characteristics (medium size, longer bills)
            {
                "bill_length_mm": random.uniform(40.9, 58.0),
                "bill_depth_mm": random.uniform(16.4, 20.8),
                "flipper_length_mm": random.randint(178, 212),
                "body_mass_g": random.randint(2700, 4800),
                "year": random.choice([2007, 2008, 2009]),
                "sex": random.choice(["male", "female"]),
                "island": "Dream"  # Chinstrap penguins are mainly on Dream island
            },
            # Gentoo penguin characteristics (larger, distinctive features)
            {
                "bill_length_mm": random.uniform(40.9, 59.6),
                "bill_depth_mm": random.uniform(13.1, 17.3),
                "flipper_length_mm": random.randint(203, 231),
                "body_mass_g": random.randint(3950, 6300),
                "year": random.choice([2007, 2008, 2009]),
                "sex": random.choice(["male", "female"]),
                "island": "Biscoe"  # Gentoo penguins are mainly on Biscoe island
            }
        ]
        
        # Randomly select one of the penguin data samples
        penguin_data = random.choice(penguin_data_samples)
        
        # Make the prediction request
        with self.client.post(
            "/predict",
            json=penguin_data,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Validate response structure
                    if "predicted_species" not in result or "confidence" not in result:
                        response.failure("Response missing required fields")
                    elif result["predicted_species"] not in ["Adelie", "Chinstrap", "Gentoo"]:
                        response.failure(f"Invalid species prediction: {result['predicted_species']}")
                    elif not (0.0 <= result["confidence"] <= 1.0):
                        response.failure(f"Invalid confidence score: {result['confidence']}")
                    else:
                        # Success case
                        response.success()
                        
                except json.JSONDecodeError:
                    response.failure("Response is not valid JSON")
            else:
                response.failure(f"HTTP {response.status_code}: {response.text}")
    
    @task(1)  # Weight: 1/10 requests will be health checks
    def health_check(self):
        """
        Test the health check endpoint.
        
        This simulates monitoring systems checking if the service is healthy.
        """
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if "status" in result:
                        response.success()
                    else:
                        response.failure("Health check response missing status field")
                except json.JSONDecodeError:
                    response.failure("Health check response is not valid JSON")
            else:
                response.failure(f"Health check failed: HTTP {response.status_code}")
    
    @task(1)  # Weight: 1/10 requests will test invalid inputs
    def test_invalid_input_handling(self):
        """
        Test how the API handles invalid inputs.
        
        This helps ensure the API is robust and handles errors gracefully
        under load conditions.
        """
        
        invalid_data_samples = [
            # Missing required field
            {
                "bill_depth_mm": 18.7,
                "flipper_length_mm": 181,
                "body_mass_g": 3750,
                "year": 2007,
                "sex": "male",
                "island": "Torgersen"
                # Missing bill_length_mm
            },
            # Invalid data types
            {
                "bill_length_mm": "not_a_number",
                "bill_depth_mm": 18.7,
                "flipper_length_mm": 181,
                "body_mass_g": 3750,
                "year": 2007,
                "sex": "male",
                "island": "Torgersen"
            },
            # Invalid enum values
            {
                "bill_length_mm": 39.1,
                "bill_depth_mm": 18.7,
                "flipper_length_mm": 181,
                "body_mass_g": 3750,
                "year": 2007,
                "sex": "invalid_sex",
                "island": "Torgersen"
            },
            # Empty request
            {}
        ]
        
        invalid_data = random.choice(invalid_data_samples)
        
        with self.client.post(
            "/predict",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            
            # We expect error responses (400, 422) for invalid inputs
            if response.status_code in [400, 422]:
                try:
                    result = response.json()
                    # Should have error details
                    if "detail" in result or "errors" in result:
                        response.success()
                    else:
                        response.failure("Error response missing detail/errors field")
                except json.JSONDecodeError:
                    response.failure("Error response is not valid JSON")
            elif response.status_code == 200:
                # If it somehow returns 200, that's also acceptable
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")


class StressTestUser(PenguinAPIUser):
    """
    Extended user class for stress testing scenarios.
    
    This class has more aggressive timing and behavior patterns
    to simulate high-stress conditions.
    """
    
    wait_time = between(0.5, 2)  # Shorter wait times for stress testing
    
    @task(10)  # Higher weight for prediction requests during stress test
    def rapid_predictions(self):
        """Make rapid prediction requests with minimal delays."""
        self.predict_penguin_species()


class SpikeTestUser(PenguinAPIUser):
    """
    User class for spike testing scenarios.
    
    Simulates sudden bursts of traffic with very little wait time.
    """
    
    wait_time = between(0.1, 0.5)  # Very short wait times for spike testing


# Define different test scenarios
class WebsiteUser(HttpUser):
    """
    Realistic user simulation combining different usage patterns.
    
    This user class simulates a more realistic usage pattern where
    users might browse, make predictions, check health, etc.
    """
    
    wait_time = between(2, 5)  # More realistic user behavior
    
    def on_start(self):
        """User starts by checking if the service is healthy."""
        self.client.get("/")
    
    @task
    def predict_and_analyze(self):
        """
        Simulate a user making a prediction and potentially making
        multiple requests as they analyze different penguins.
        """
        
        # Make 1-3 predictions in a session
        num_predictions = random.randint(1, 3)
        
        for _ in range(num_predictions):
            # Use the prediction method from PenguinAPIUser
            penguin_user = PenguinAPIUser()
            penguin_user.client = self.client
            penguin_user.predict_penguin_species()
            
            # Brief pause between predictions in the same session
            self.wait()


# Custom Locust configuration for different test scenarios
class BaselineTest(PenguinAPIUser):
    """Baseline test: 1 user for 60 seconds"""
    wait_time = between(2, 4)


class NormalLoadTest(PenguinAPIUser):
    """Normal load test: 10 users for 5 minutes"""
    wait_time = between(1, 3)


class StressTest(StressTestUser):
    """Stress test: 50 users for 2 minutes"""
    pass


class SpikeTest(SpikeTestUser):
    """Spike test: 1 to 100 users over 1 minute"""
    pass