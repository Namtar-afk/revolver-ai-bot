import inspect
from reco import generator


def test_signature_generate_insights():
    sig = inspect.signature(generator.generate_insights)
    assert list(sig.parameters) == ["brief", "trends"]


def test_signature_generate_hypotheses():
    sig = inspect.signature(generator.generate_hypotheses)
    assert list(sig.parameters) == ["brief", "trends"]


def test_signature_generate_kpis():
    sig = inspect.signature(generator.generate_kpis)
    assert list(sig.parameters) == ["brief", "trends"]


def test_signature_generate_executive_summary():
    sig = inspect.signature(generator.generate_executive_summary)
    assert list(sig.parameters) == ["brief", "trends"]


def test_signature_generate_recommendation():
    sig = inspect.signature(generator.generate_recommendation)
    assert list(sig.parameters) == ["brief", "trends"]
