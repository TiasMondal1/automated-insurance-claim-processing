"""Claim data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ClaimStatus(str, Enum):
    """Claim processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class ClaimItem(BaseModel):
    """Individual claim item (service/procedure)."""
    procedure_code: str = Field(..., description="CPT procedure code")
    procedure_description: str = Field(..., description="Description of procedure")
    diagnosis_code: str = Field(..., description="ICD-10 diagnosis code")
    service_date: datetime = Field(..., description="Date of service")
    provider_name: str = Field(..., description="Healthcare provider name")
    billed_amount: float = Field(..., gt=0, description="Amount billed")
    units: int = Field(default=1, gt=0, description="Number of units")


class Claim(BaseModel):
    """Insurance claim data model."""
    claim_id: str = Field(..., description="Unique claim identifier")
    policy_number: str = Field(..., description="Insurance policy number")
    
    # Claimant Information
    claimant_name: str = Field(..., description="Name of claimant")
    claimant_dob: datetime = Field(..., description="Date of birth")
    claimant_id: str = Field(..., description="Claimant/Member ID")
    
    # Claim Details
    claim_date: datetime = Field(default_factory=datetime.now, description="Claim submission date")
    service_start_date: datetime = Field(..., description="Start date of service")
    service_end_date: datetime = Field(..., description="End date of service")
    
    # Medical Information
    primary_diagnosis: str = Field(..., description="Primary diagnosis code (ICD-10)")
    secondary_diagnoses: List[str] = Field(default_factory=list, description="Secondary diagnosis codes")
    claim_items: List[ClaimItem] = Field(..., description="List of claim items")
    
    # Financial
    total_billed_amount: float = Field(..., gt=0, description="Total amount billed")
    
    # Provider Information
    provider_name: str = Field(..., description="Primary provider name")
    provider_npi: str = Field(..., description="Provider NPI number")
    facility_name: Optional[str] = Field(None, description="Facility name if applicable")
    
    # Supporting Documents
    medical_report: Optional[str] = Field(None, description="Medical report text")
    additional_notes: Optional[str] = Field(None, description="Additional notes")
    
    # Processing Status
    status: ClaimStatus = Field(default=ClaimStatus.PENDING, description="Current status")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "CLM-2024-001",
                "policy_number": "POL-12345",
                "claimant_name": "John Doe",
                "claimant_dob": "1980-01-15",
                "claimant_id": "MEM-67890",
                "claim_date": "2024-01-20",
                "service_start_date": "2024-01-15",
                "service_end_date": "2024-01-15",
                "primary_diagnosis": "M54.5",
                "secondary_diagnoses": ["M25.511"],
                "total_billed_amount": 1500.00,
                "provider_name": "Dr. Jane Smith",
                "provider_npi": "1234567890",
                "status": "pending"
            }
        }
