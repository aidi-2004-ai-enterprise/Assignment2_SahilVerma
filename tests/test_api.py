from fastapi.testclient import TestClient
from app.main import app, PenguinFeatures, load_model_and_metadata
import pytest
import pandas as pd
import json

client = TestClient(app)

def test_predict_endpoint_valid_input():
    """Test prediction with valid penguin data"""
    sample_data = {
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750,
        "year": 2007,
        "sex": "male",
        "island": "Torgersen"
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200
    
    json_response = response.json()
    assert "predicted_species" in json_response
    assert "confidence" in json_response
    assert json_response["predicted_species"] in ["Adelie", "Chinstrap", "Gentoo"]
    assert 0.0 <= json_response["confidence"] <= 1.0

def test_predict_endpoint_different_valid_inputs():
    """Test prediction with different valid penguin data combinations"""
    test_cases = [
        {
            "bill_length_mm": 46.1,
            "bill_depth_mm": 13.2,
            "flipper_length_mm": 211,
            "body_mass_g": 4500,
            "year": 2008,
            "sex": "female",
            "island": "Biscoe"
        },
        {
            "bill_length_mm": 50.7,
            "bill_depth_mm": 19.7,
            "flipper_length_mm": 203,
            "body_mass_g": 4050,
            "year": 2009,
            "sex": "male",
            "island": "Dream"
        }
    ]
    
    for sample_data in test_cases:
        response = client.post("/predict", json=sample_data)
        assert response.status_code == 200
        json_response = response.json()
        assert "predicted_species" in json_response
        assert "confidence" in json_response
        assert json_response["predicted_species"] in ["Adelie", "Chinstrap", "Gentoo"]

def test_predict_endpoint_missing_required_field():
    """Test handling of missing required field (bill_length_mm omitted)"""
    sample_data = {
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750,
        "year": 2007,
        "sex": "male",
        "island": "Torgersen"
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 400
    
    json_response = response.json()
    assert "detail" in json_response
    assert "errors" in json_response
    
    # Check that bill_length_mm is mentioned in the error
    error_found = False
    for error in json_response["errors"]:
        if error["field"] == "bill_length_mm":
            error_found = True
            break
    assert error_found

def test_predict_endpoint_invalid_data_types():
    """Test handling of invalid data types (strings instead of floats)"""
    sample_data = {
        "bill_length_mm": "invalid_string",
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750,
        "year": 2007,
        "sex": "male",
        "island": "Torgersen"
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 400
    
    json_response = response.json()
    assert "detail" in json_response
    assert "errors" in json_response

def test_predict_endpoint_invalid_enum_values():
    """Test handling of invalid enum values for sex and island"""
    # Test invalid sex
    sample_data = {
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750,
        "year": 2007,
        "sex": "invalid_sex",
        "island": "Torgersen"
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 400
    
    json_response = response.json()
    assert "detail" in json_response
    assert "errors" in json_response
    
    # Test invalid island
    sample_data["sex"] = "male"
    sample_data["island"] = "invalid_island"
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 400

def test_predict_endpoint_out_of_range_values():
    """Test handling of out-of-range values (negative body_mass_g)"""
    sample_data = {
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": -1000,  # Negative body mass is unrealistic
        "year": 2007,
        "sex": "male",
        "island": "Torgersen"
    }
    # Note: The current model doesn't validate ranges, but it should still make a prediction
    # In a production system, you might want to add range validation
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200  # Model accepts the input but prediction might be unreliable

def test_predict_endpoint_extreme_values():
    """Test boundary conditions with extreme but technically valid values"""
    extreme_cases = [
        {
            "bill_length_mm": 0.1,  # Very small but positive
            "bill_depth_mm": 0.1,
            "flipper_length_mm": 1,
            "body_mass_g": 1,
            "year": 1900,
            "sex": "male",
            "island": "Torgersen"
        },
        {
            "bill_length_mm": 1000.0,  # Very large values
            "bill_depth_mm": 1000.0,
            "flipper_length_mm": 1000,
            "body_mass_g": 50000,
            "year": 2030,
            "sex": "female",
            "island": "Biscoe"
        }
    ]
    
    for sample_data in extreme_cases:
        response = client.post("/predict", json=sample_data)
        # Should return prediction even for extreme values
        assert response.status_code == 200
        json_response = response.json()
        assert "predicted_species" in json_response
        assert "confidence" in json_response

def test_predict_endpoint_empty_request():
    """Test handling of completely empty request"""
    response = client.post("/predict", json={})
    assert response.status_code == 400
    
    json_response = response.json()
    assert "detail" in json_response
    assert "errors" in json_response
    
    # Should have errors for all required fields
    required_fields = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "year", "sex", "island"]
    error_fields = [error["field"] for error in json_response["errors"]]
    
    for field in required_fields:
        assert field in error_fields

def test_predict_endpoint_null_values():
    """Test handling of null values in required fields"""
    sample_data = {
        "bill_length_mm": None,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750,
        "year": 2007,
        "sex": "male",
        "island": "Torgersen"
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 400

def test_root_endpoint():
    """Test that root endpoint is accessible (if it exists)"""
    response = client.get("/")
    # Since there's no root endpoint defined, expect 404
    assert response.status_code == 404

def test_predict_endpoint_response_structure():
    """Test that the prediction response has the correct structure"""
    sample_data = {
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750,
        "year": 2007,
        "sex": "male",
        "island": "Torgersen"
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200
    
    json_response = response.json()
    
    # Check response structure
    assert isinstance(json_response, dict)
    assert len(json_response) == 2  # Should have exactly 2 keys
    
    # Check data types
    assert isinstance(json_response["predicted_species"], str)
    assert isinstance(json_response["confidence"], (int, float))
    
    # Check confidence is a probability
    assert 0.0 <= json_response["confidence"] <= 1.0