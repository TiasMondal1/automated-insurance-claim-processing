"""Decision and validation result models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DecisionType(str, Enum):
    """Type of claim decision."""
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIAL_APPROVAL = "partial_approval"
    NEEDS_REVIEW = "needs_review"
    PENDING_INFO = "pending_information"


class ValidationResult(BaseModel):
    """Result of a validation check."""
    check_name: str = Field(..., description="Name of validation check")
    passed: bool = Field(..., description="Whether check passed")
    severity: str = Field(..., description="Severity: info, warning, error")
    message: str = Field(..., description="Detailed message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")


class Decision(BaseModel):
    """Claim decision data model."""
    claim_id: str = Field(..., description="Associated claim ID")
    decision_type: DecisionType = Field(..., description="Type of decision")
    decision_date: datetime = Field(default_factory=datetime.now, description="Decision timestamp")
    
    # Financial Calculations
    approved_amount: float = Field(default=0.0, ge=0, description="Approved claim amount")
    patient_responsibility: float = Field(default=0.0, ge=0, description="Patient responsibility")
    insurance_payment: float = Field(default=0.0, ge=0, description="Insurance payment amount")
    
    # Breakdown
    deductible_applied: float = Field(default=0.0, ge=0, description="Deductible amount applied")
    copay_applied: float = Field(default=0.0, ge=0, description="Copay amount applied")
    coinsurance_applied: float = Field(default=0.0, ge=0, description="Coinsurance amount applied")
    
    # Validation Results
    validation_results: List[ValidationResult] = Field(default_factory=list, description="All validation results")
    
    # Confidence and Reasoning
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Detailed reasoning for decision")
    
    # Flags and Issues
    flags: List[str] = Field(default_factory=list, description="Any flags raised")
    missing_information: List[str] = Field(default_factory=list, description="Missing information needed")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for claimant")
    next_steps: List[str] = Field(default_factory=list, description="Next steps to take")
    
    # Review Information
    requires_manual_review: bool = Field(default=False, description="Requires human review")
    review_reason: Optional[str] = Field(None, description="Reason for manual review")
    
    # Agent Information
    processing_agents: List[str] = Field(default_factory=list, description="Agents involved in processing")
    processing_time_seconds: float = Field(default=0.0, description="Total processing time")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def get_failed_validations(self) -> List[ValidationResult]:
        """Get all failed validation checks."""
        return [v for v in self.validation_results if not v.passed]
    
    def get_critical_issues(self) -> List[ValidationResult]:
        """Get critical validation issues."""
        return [v for v in self.validation_results if not v.passed and v.severity == "error"]
    
    def is_auto_approvable(self, threshold: float = 0.95) -> bool:
        """Check if decision can be auto-approved based on confidence."""
        return (
            self.decision_type == DecisionType.APPROVED
            and self.confidence_score >= threshold
            and not self.requires_manual_review
            and len(self.get_critical_issues()) == 0
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "CLM-2024-001",
                "decision_type": "approved",
                "approved_amount": 1200.00,
                "patient_responsibility": 300.00,
                "insurance_payment": 900.00,
                "confidence_score": 0.92,
                "reasoning": "Claim meets all policy requirements and coverage criteria.",
                "requires_manual_review": False
            }
        }
