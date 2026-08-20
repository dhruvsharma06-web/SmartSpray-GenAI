import pytest
from app.ai.pipeline import determine_spray_action
from app.ai.schemas import DetectionPipelineResult, ComponentResult, SeverityResult

def test_decision_engine_low_confidence_uncertain():
    res = DetectionPipelineResult(uncertain=True)
    decision = determine_spray_action(res, "AUTO")
    assert decision["recommendation"] == "NO_SPRAY"
    assert decision["reason"] == "UNCERTAIN"
    assert decision["auto_permitted"] is False

def test_decision_engine_no_disease():
    res = DetectionPipelineResult(disease="healthy")
    decision = determine_spray_action(res, "AUTO")
    assert decision["recommendation"] == "NO_SPRAY"
    assert decision["reason"] == "NO_DISEASE"

def test_decision_engine_no_severity():
    res = DetectionPipelineResult(disease="early_blight", severity=None)
    decision = determine_spray_action(res, "AUTO")
    assert decision["recommendation"] == "NO_SPRAY"
    assert decision["reason"] == "NO_VALID_SEVERITY"


import numpy as np
from app.ai.pipeline import extract_leaf_mask_hsv

def test_extract_leaf_mask_hsv_empty():
    crop = np.zeros((100, 100, 3), dtype=np.uint8)
    mask = extract_leaf_mask_hsv(crop)
    assert np.count_nonzero(mask) == 0

def test_extract_leaf_mask_hsv_valid():
    # Green image
    crop = np.zeros((100, 100, 3), dtype=np.uint8)
    crop[20:80, 20:80] = [0, 255, 0] # BGR Green
    mask = extract_leaf_mask_hsv(crop)
    assert np.count_nonzero(mask) > 0
