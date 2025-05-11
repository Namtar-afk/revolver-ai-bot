import pytest
from reco.generator import generate_ideas, generate_timeline, generate_budget

def dummy(): return None  # placeholder

def test_generate_ideas_signature():
    ideas = generate_ideas(dummy, dummy)
    assert isinstance(ideas, list)

def test_generate_timeline_signature():
    timeline = generate_timeline(dummy, dummy)
    assert isinstance(timeline, list)

def test_generate_budget_signature():
    budget = generate_budget(dummy, dummy)
    assert isinstance(budget, list)
