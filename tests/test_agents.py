"""Unit tests for agents."""

import pytest
import json
from datetime import datetime
from pathlib import Path

from agents.extraction_agent import ExtractionAgent
from agents.validation_agent import ValidationAgent
from agents.decision_agent import DecisionAgent
from agents.explanation_agent import ExplanationAgent
from agents.orchestrator import OrchestratorAgent


@pytest.fixture
def sample_claim_data():
    """Sample claim data for testing."""
    return {
        "claim_id": "CLM-TEST-001",
        "policy_number": "POL-TEST-001",
        "claimant_name": "Test Patient",
        "claimant_dob": "1980-01-01",
        "claimant_id": "MEM-TEST-001",
        "claim_date": datetime.now().isoformat(),
        "service_start_date": datetime.now().isoformat(),
        "service_end_date": datetime.now().isoformat(),
        "primary_diagnosis": "M54.5",
        "secondary_diagnoses": [],
        "claim_items": [
            {
                "procedure_code": "99213",
                "procedure_description": "Office visit",
                "diagnosis_code": "M54.5",
                "service_date": datetime.now().isoformat(),
                "provider_name": "Dr. Test",
                "billed_amount": 150.00,
                "units": 1
            }
        ],
        "total_billed_amount": 150.00,
        "provider_name": "Dr. Test",
        "provider_npi": "1234567890",
        "status": "pending"
    }


@pytest.fixture
def sample_policy_data():
    """Sample policy data for testing."""
    return {
        "policy_number": "POL-TEST-001",
        "policy_holder_name": "Test Patient",
        "effective_date": "2024-01-01T00:00:00",
        "expiration_date": "2024-12-31T23:59:59",
        "annual_deductible": 1000.00,
        "deductible_met": 0.00,
        "out_of_pocket_max": 5000.00,
        "out_of_pocket_met": 0.00,
        "policy_type": "PPO",
        "network_type": "In-Network",
        "coverages": [
            {
                "category": "outpatient",
                "annual_limit": 50000,
                "copay_amount": 30.00,
                "coinsurance_percentage": 20,
                "deductible_applies": True,
                "requires_preauth": False
            }
        ],
        "exclusions": []
    }


class TestExtractionAgent:
    """Test extraction agent."""
    
    def test_extraction_from_structured_data(self, sample_claim_data):
        """Test extraction from structured JSON."""
        agent = ExtractionAgent()
        
        result = agent.process({
            "claim_document": sample_claim_data,
            "medical_report": ""
        })
        
        assert result["status"] == "success"
        assert result["extracted_data"]["claim_id"] == "CLM-TEST-001"
        assert result["extracted_data"]["total_billed_amount"] == 150.00
    
    def test_extraction_confidence_calculation(self, sample_claim_data):
        """Test confidence score calculation."""
        agent = ExtractionAgent()
        
        result = agent.process({
            "claim_document": sample_claim_data,
            "medical_report": ""
        })
        
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1


class TestValidationAgent:
    """Test validation agent."""
    
    def test_validation_with_valid_claim(self, sample_claim_data, sample_policy_data):
        """Test validation with valid claim."""
        agent = ValidationAgent()
        
        result = agent.process({
            "claim_data": sample_claim_data,
            "policy_data": sample_policy_data
        })
        
        assert result["status"] == "success"
        assert "validation_results" in result
        assert len(result["validation_results"]) > 0
    
    def test_financial_breakdown_calculation(self, sample_claim_data, sample_policy_data):
        """Test financial breakdown calculation."""
        agent = ValidationAgent()
        
        result = agent.process({
            "claim_data": sample_claim_data,
            "policy_data": sample_policy_data
        })
        
        financial = result["financial_breakdown"]
        assert "total_billed" in financial
        assert "patient_responsibility" in financial
        assert "insurance_payment" in financial


class TestDecisionAgent:
    """Test decision agent."""
    
    def test_decision_generation(self, sample_claim_data):
        """Test decision generation."""
        agent = DecisionAgent()
        
        validation_results = [
            {
                "check_name": "Test Check",
                "passed": True,
                "severity": "info",
                "message": "Test passed"
            }
        ]
        
        result = agent.process({
            "claim_data": sample_claim_data,
            "validation_results": validation_results,
            "validation_status": "passed",
            "financial_breakdown": {
                "total_billed": 150.00,
                "approved_amount": 150.00,
                "patient_responsibility": 30.00,
                "insurance_payment": 120.00
            }
        })
        
        assert result["status"] == "success"
        assert "decision_type" in result
        assert "confidence_score" in result
        assert 0 <= result["confidence_score"] <= 1


class TestExplanationAgent:
    """Test explanation agent."""
    
    def test_explanation_generation(self, sample_claim_data):
        """Test explanation generation."""
        agent = ExplanationAgent()
        
        decision_data = {
            "decision_type": "approved",
            "confidence_score": 0.95,
            "reasoning": "Claim approved based on policy compliance",
            "financial_breakdown": {
                "total_billed": 150.00,
                "approved_amount": 150.00,
                "patient_responsibility": 30.00,
                "insurance_payment": 120.00
            },
            "recommendations": ["Review EOB"],
            "next_steps": ["Payment in 10 days"]
        }
        
        result = agent.process({
            "claim_data": sample_claim_data,
            "decision_data": decision_data,
            "validation_results": []
        })
        
        assert result["status"] == "success"
        assert "summary" in result
        assert "detailed_explanation" in result
        assert "formatted_report" in result


class TestOrchestratorAgent:
    """Test orchestrator agent."""
    
    @pytest.mark.skipif(
        not (Path.cwd() / ".env").exists(),
        reason="API key not configured"
    )
    def test_full_workflow(self, sample_claim_data, sample_policy_data):
        """Test complete workflow through orchestrator."""
        orchestrator = OrchestratorAgent()
        
        result = orchestrator.process({
            "claim_document": sample_claim_data,
            "policy_data": sample_policy_data,
            "medical_report": "Test medical report"
        })
        
        assert result["status"] == "completed"
        assert "final_output" in result
        assert "extraction" in result
        assert "validation" in result
        assert "decision" in result
        assert "explanation" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
