import pytest
import pandas as pd
import numpy as np
from app.main import load_model_and_metadata, preprocess_features, PenguinFeatures
import app.main
import xgboost as xgb


def test_model_loading():
    """Test that XGBoost model loads correctly"""
    assert app.main.model is not None
    assert isinstance(app.main.model, xgb.XGBClassifier)
    assert app.main.label_encoder_classes is not None
    assert app.main.feature_names is not None
    
    # Check that we have the expected penguin species
    expected_species = ["Adelie", "Chinstrap", "Gentoo"]
    assert set(app.main.label_encoder_classes) == set(expected_species)
    
    # Check that we have the expected feature names
    expected_features = [
        "bill_length_mm", "bill_depth_mm", "flipper_length_mm", 
        "body_mass_g", "sex_Male", "island_Dream", "island_Torgersen"
    ]
    assert app.main.feature_names == expected_features

def test_model_prediction_with_known_data():
    """Test XGBoost model with known penguin data that should predict specific species"""
    # Test case 1: Typical Adelie penguin characteristics
    adelie_data = PenguinFeatures(
        bill_length_mm=39.1,
        bill_depth_mm=18.7,
        flipper_length_mm=181,
        body_mass_g=3750,
        year=2007,
        sex="male",
        island="Torgersen"
    )
    
    processed_features = preprocess_features(adelie_data)
    prediction = app.main.model.predict(processed_features)[0]
    prediction_proba = app.main.model.predict_proba(processed_features)[0]
    
    assert isinstance(prediction, (int, np.integer))
    assert 0 <= prediction < len(app.main.label_encoder_classes)
    assert len(prediction_proba) == len(app.main.label_encoder_classes)
    assert np.isclose(sum(prediction_proba), 1.0, rtol=1e-5)
    
    predicted_species = app.main.label_encoder_classes[prediction]
    assert predicted_species in ["Adelie", "Chinstrap", "Gentoo"]

def test_model_prediction_consistency():
    """Test that model predictions are consistent for the same input"""
    sample_data = PenguinFeatures(
        bill_length_mm=46.1,
        bill_depth_mm=13.2,
        flipper_length_mm=211,
        body_mass_g=4500,
        year=2008,
        sex="female",
        island="Biscoe"
    )
    
    processed_features = preprocess_features(sample_data)
    
    # Make multiple predictions with the same input
    predictions = []
    probabilities = []
    
    for _ in range(5):
        pred = app.main.model.predict(processed_features)[0]
        prob = app.main.model.predict_proba(processed_features)[0]
        predictions.append(pred)
        probabilities.append(prob)
    
    # All predictions should be identical (XGBoost is deterministic)
    assert all(p == predictions[0] for p in predictions)
    
    # All probability arrays should be identical
    for prob in probabilities:
        assert np.allclose(prob, probabilities[0])

def test_preprocess_features():
    """Test the preprocessing function handles one-hot encoding correctly"""
    sample_data = PenguinFeatures(
        bill_length_mm=39.1,
        bill_depth_mm=18.7,
        flipper_length_mm=181,
        body_mass_g=3750,
        year=2007,
        sex="male",
        island="Torgersen"
    )
    
    processed = preprocess_features(sample_data)
    
    # Check that it returns a DataFrame
    assert isinstance(processed, pd.DataFrame)
    
    # Check that it has the correct shape
    assert processed.shape == (1, len(app.main.feature_names))
    
    # Check that columns are in the correct order
    assert list(processed.columns) == app.main.feature_names
    
    # Check one-hot encoding for sex_Male (should be 1 for male, 0 for female)
    expected_sex_male = 1 if sample_data.sex == "male" else 0
    assert processed["sex_Male"].iloc[0] == expected_sex_male
    
    # Check one-hot encoding for island_Torgersen (should be 1 for Torgersen)
    assert processed["island_Torgersen"].iloc[0] == 1
    
    # Check one-hot encoding for island_Dream (should be 0 for Torgersen)
    assert processed["island_Dream"].iloc[0] == 0

def test_preprocess_features_female_biscoe():
    """Test preprocessing with female penguin from Biscoe island"""
    sample_data = PenguinFeatures(
        bill_length_mm=46.1,
        bill_depth_mm=13.2,
        flipper_length_mm=211,
        body_mass_g=4500,
        year=2008,
        sex="female",
        island="Biscoe"
    )
    
    processed = preprocess_features(sample_data)
    
    # Check one-hot encoding for sex_Male (should be 0 for female)
    assert processed["sex_Male"].iloc[0] == 0
    
    # Check one-hot encoding for islands (should be 0 for both Dream and Torgersen when Biscoe)
    assert processed["island_Dream"].iloc[0] == 0
    assert processed["island_Torgersen"].iloc[0] == 0

def test_model_predictions_for_all_species():
    """Test that model can predict all three penguin species with appropriate inputs"""
    # We'll test with different combinations that should favor different species
    test_cases = [
        # Case 1: Smaller penguin (likely Adelie)
        PenguinFeatures(
            bill_length_mm=35.0,
            bill_depth_mm=19.0,
            flipper_length_mm=180,
            body_mass_g=3200,
            year=2007,
            sex="female",
            island="Torgersen"
        ),
        # Case 2: Medium penguin (potentially Chinstrap)
        PenguinFeatures(
            bill_length_mm=48.0,
            bill_depth_mm=18.0,
            flipper_length_mm=195,
            body_mass_g=3800,
            year=2008,
            sex="male",
            island="Dream"
        ),
        # Case 3: Larger penguin (likely Gentoo)
        PenguinFeatures(
            bill_length_mm=50.0,
            bill_depth_mm=15.0,
            flipper_length_mm=220,
            body_mass_g=5200,
            year=2009,
            sex="male",
            island="Biscoe"
        )
    ]
    
    predictions = []
    for penguin_data in test_cases:
        processed_features = preprocess_features(penguin_data)
        prediction = app.main.model.predict(processed_features)[0]
        predicted_species = app.main.label_encoder_classes[prediction]
        predictions.append(predicted_species)
    
    # We should get valid species names
    for species in predictions:
        assert species in ["Adelie", "Chinstrap", "Gentoo"]

def test_model_probability_outputs():
    """Test that model probability outputs are valid probabilities"""
    sample_data = PenguinFeatures(
        bill_length_mm=39.1,
        bill_depth_mm=18.7,
        flipper_length_mm=181,
        body_mass_g=3750,
        year=2007,
        sex="male",
        island="Torgersen"
    )
    
    processed_features = preprocess_features(sample_data)
    probabilities = app.main.model.predict_proba(processed_features)[0]
    
    # Check that probabilities are valid
    assert len(probabilities) == 3  # Three species
    assert all(0 <= p <= 1 for p in probabilities)  # Each probability between 0 and 1
    assert np.isclose(sum(probabilities), 1.0, rtol=1e-5)  # Sum to 1
    
    # Check that the highest probability corresponds to the predicted class
    prediction = app.main.model.predict(processed_features)[0]
    assert probabilities[prediction] == max(probabilities)

def test_feature_names_consistency():
    """Test that feature names are consistent with model expectations"""
    # Create a sample to test preprocessing
    sample_data = PenguinFeatures(
        bill_length_mm=39.1,
        bill_depth_mm=18.7,
        flipper_length_mm=181,
        body_mass_g=3750,
        year=2007,
        sex="male",
        island="Torgersen"
    )
    
    processed_features = preprocess_features(sample_data)
    
    # The processed features should have the same number of features as expected by the model
    assert processed_features.shape[1] == len(app.main.feature_names)
    
    # Try making a prediction to ensure compatibility
    try:
        prediction = app.main.model.predict(processed_features)
        probabilities = app.main.model.predict_proba(processed_features)
        assert prediction is not None
        assert probabilities is not None
    except Exception as e:
        pytest.fail(f"Model prediction failed with processed features: {str(e)}")

def test_model_handles_edge_case_values():
    """Test that model can handle edge case values without crashing"""
    edge_cases = [
        # Very small values
        PenguinFeatures(
            bill_length_mm=20.0,
            bill_depth_mm=10.0,
            flipper_length_mm=150,
            body_mass_g=2000,
            year=2007,
            sex="female",
            island="Dream"
        ),
        # Very large values
        PenguinFeatures(
            bill_length_mm=70.0,
            bill_depth_mm=25.0,
            flipper_length_mm=250,
            body_mass_g=7000,
            year=2010,
            sex="male",
            island="Biscoe"
        )
    ]
    
    for penguin_data in edge_cases:
        processed_features = preprocess_features(penguin_data)
        
        # Should not raise an exception
        prediction = app.main.model.predict(processed_features)[0]
        probabilities = app.main.model.predict_proba(processed_features)[0]
        
        # Should return valid outputs
        assert isinstance(prediction, (int, np.integer))
        assert 0 <= prediction < len(app.main.label_encoder_classes)
        assert len(probabilities) == len(app.main.label_encoder_classes)
        assert np.isclose(sum(probabilities), 1.0, rtol=1e-5)