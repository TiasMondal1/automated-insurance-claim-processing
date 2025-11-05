"""Policy data models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Coverage(BaseModel):
    """Coverage details for a specific service category."""
    category: str = Field(..., description="Service category (e.g., 'inpatient', 'outpatient')")
    annual_limit: Optional[float] = Field(None, description="Annual coverage limit")
    per_visit_limit: Optional[float] = Field(None, description="Per visit limit")
    copay_amount: float = Field(default=0.0, description="Copay amount")
    coinsurance_percentage: float = Field(default=0.0, ge=0, le=100, description="Coinsurance %")
    deductible_applies: bool = Field(default=True, description="Whether deductible applies")
    requires_preauth: bool = Field(default=False, description="Requires pre-authorization")
    covered_procedures: List[str] = Field(default_factory=list, description="List of covered CPT codes")


class Exclusion(BaseModel):
    """Policy exclusion."""
    exclusion_type: str = Field(..., description="Type of exclusion")
    description: str = Field(..., description="Detailed description")
    excluded_codes: List[str] = Field(default_factory=list, description="Excluded diagnosis/procedure codes")


class Policy(BaseModel):
    """Insurance policy data model."""
    policy_number: str = Field(..., description="Unique policy number")
    policy_holder_name: str = Field(..., description="Policy holder name")
    
    # Coverage Period
    effective_date: datetime = Field(..., description="Policy effective date")
    expiration_date: datetime = Field(..., description="Policy expiration date")
    
    # Financial Terms
    annual_deductible: float = Field(..., ge=0, description="Annual deductible amount")
    deductible_met: float = Field(default=0.0, ge=0, description="Amount of deductible already met")
    out_of_pocket_max: float = Field(..., ge=0, description="Out-of-pocket maximum")
    out_of_pocket_met: float = Field(default=0.0, ge=0, description="Amount of OOP already met")
    
    # Coverage Details
    coverages: List[Coverage] = Field(..., description="List of coverage categories")
    exclusions: List[Exclusion] = Field(default_factory=list, description="List of exclusions")
    
    # Policy Type
    policy_type: str = Field(..., description="Type of policy (e.g., 'PPO', 'HMO', 'EPO')")
    network_type: str = Field(..., description="Network type")
    
    # Additional Terms
    requires_referral: bool = Field(default=False, description="Requires referral for specialists")
    emergency_coverage: bool = Field(default=True, description="Emergency services covered")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def is_active(self) -> bool:
        """Check if policy is currently active."""
        now = datetime.now()
        return self.effective_date <= now <= self.expiration_date
    
    def get_coverage_for_category(self, category: str) -> Optional[Coverage]:
        """Get coverage details for a specific category."""
        for coverage in self.coverages:
            if coverage.category.lower() == category.lower():
                return coverage
        return None
    
    def is_procedure_excluded(self, procedure_code: str) -> bool:
        """Check if a procedure is excluded."""
        for exclusion in self.exclusions:
            if procedure_code in exclusion.excluded_codes:
                return True
        return False
    
    class Config:
        json_schema_extra = {
            "example": {
                "policy_number": "POL-12345",
                "policy_holder_name": "John Doe",
                "effective_date": "2024-01-01",
                "expiration_date": "2024-12-31",
                "annual_deductible": 1000.00,
                "deductible_met": 500.00,
                "out_of_pocket_max": 5000.00,
                "out_of_pocket_met": 1200.00,
                "policy_type": "PPO",
                "network_type": "In-Network"
            }
        }
