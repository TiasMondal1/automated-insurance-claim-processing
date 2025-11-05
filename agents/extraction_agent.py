"""Extraction agent for parsing and structuring claim data."""

import json
from typing import Dict, Any
from datetime import datetime
import time

from .base_agent import BaseAgent
from models.claim import Claim, ClaimItem


class ExtractionAgent(BaseAgent):
    """Agent responsible for extracting structured data from claim documents."""
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="ExtractionAgent", **kwargs)
    
    def get_system_prompt(self) -> str:
        """Get system prompt for extraction agent."""
        return """You are an expert medical claim data extraction agent. Your role is to:
1. Extract all relevant information from claim forms and medical reports
2. Identify and extract diagnosis codes (ICD-10), procedure codes (CPT), and other medical codes
3. Parse dates, amounts, and provider information accurately
4. Structure the extracted data in a standardized JSON format
5. Flag any missing or ambiguous information

Be precise and thorough. If information is unclear or missing, note it explicitly."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from claim documents.
        
        Args:
            input_data: Dictionary containing:
                - claim_document: Raw claim document text/JSON
                - medical_report: Optional medical report text
                
        Returns:
            Dictionary containing extracted claim data
        """
        start_time = time.time()
        self.logger.info("Starting claim data extraction...")
        
        try:
            claim_document = input_data.get("claim_document", "")
            medical_report = input_data.get("medical_report", "")
            
            # Try to parse as JSON first
            if isinstance(claim_document, dict):
                extracted_data = self._extract_from_structured(claim_document)
            elif claim_document.strip().startswith('{'):
                try:
                    claim_json = json.loads(claim_document)
                    extracted_data = self._extract_from_structured(claim_json)
                except json.JSONDecodeError:
                    extracted_data = self._extract_from_unstructured(claim_document, medical_report)
            else:
                extracted_data = self._extract_from_unstructured(claim_document, medical_report)
            
            # Add medical report if provided
            if medical_report:
                extracted_data["medical_report"] = medical_report
            
            output_data = {
                "status": "success",
                "agent": self.agent_name,
                "extracted_data": extracted_data,
                "missing_fields": self._identify_missing_fields(extracted_data),
                "confidence": self._calculate_confidence(extracted_data)
            }
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {str(e)}")
            output_data = {
                "status": "error",
                "agent": self.agent_name,
                "error": str(e),
                "extracted_data": {}
            }
        
        duration = time.time() - start_time
        self.log_execution(input_data, output_data, duration)
        
        return output_data
    
    def _extract_from_structured(self, claim_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from structured JSON."""
        self.logger.info("Extracting from structured JSON data")
        
        # Map JSON fields to our standard format
        extracted = {
            "claim_id": claim_json.get("claim_id", claim_json.get("claimId", f"CLM-{datetime.now().strftime('%Y%m%d%H%M%S')}")),
            "policy_number": claim_json.get("policy_number", claim_json.get("policyNumber", "")),
            "claimant_name": claim_json.get("claimant_name", claim_json.get("patientName", "")),
            "claimant_dob": claim_json.get("claimant_dob", claim_json.get("dateOfBirth", "")),
            "claimant_id": claim_json.get("claimant_id", claim_json.get("memberId", "")),
            "claim_date": claim_json.get("claim_date", datetime.now().isoformat()),
            "service_start_date": claim_json.get("service_start_date", claim_json.get("serviceDate", "")),
            "service_end_date": claim_json.get("service_end_date", claim_json.get("serviceDate", "")),
            "primary_diagnosis": claim_json.get("primary_diagnosis", claim_json.get("diagnosisCode", "")),
            "secondary_diagnoses": claim_json.get("secondary_diagnoses", []),
            "total_billed_amount": float(claim_json.get("total_billed_amount", claim_json.get("totalAmount", 0))),
            "provider_name": claim_json.get("provider_name", claim_json.get("providerName", "")),
            "provider_npi": claim_json.get("provider_npi", claim_json.get("npi", "")),
            "facility_name": claim_json.get("facility_name"),
        }
        
        # Extract claim items
        items = claim_json.get("claim_items", claim_json.get("services", []))
        extracted["claim_items"] = []
        
        for item in items:
            claim_item = {
                "procedure_code": item.get("procedure_code", item.get("cptCode", "")),
                "procedure_description": item.get("procedure_description", item.get("description", "")),
                "diagnosis_code": item.get("diagnosis_code", extracted["primary_diagnosis"]),
                "service_date": item.get("service_date", extracted["service_start_date"]),
                "provider_name": item.get("provider_name", extracted["provider_name"]),
                "billed_amount": float(item.get("billed_amount", item.get("amount", 0))),
                "units": int(item.get("units", 1))
            }
            extracted["claim_items"].append(claim_item)
        
        return extracted
    
    def _extract_from_unstructured(self, claim_text: str, medical_report: str = "") -> Dict[str, Any]:
        """Extract data from unstructured text using LLM."""
        self.logger.info("Extracting from unstructured text using LLM")
        
        prompt = f"""Extract all relevant information from the following insurance claim document and medical report.

CLAIM DOCUMENT:
{claim_text}

MEDICAL REPORT:
{medical_report}

Extract and structure the following information in JSON format:
- claim_id (generate if not present using format CLM-YYYYMMDDHHMMSS)
- policy_number
- claimant_name
- claimant_dob (format: YYYY-MM-DD)
- claimant_id
- claim_date (format: YYYY-MM-DD)
- service_start_date (format: YYYY-MM-DD)
- service_end_date (format: YYYY-MM-DD)
- primary_diagnosis (ICD-10 code)
- secondary_diagnoses (array of ICD-10 codes)
- total_billed_amount (number)
- provider_name
- provider_npi
- facility_name (if mentioned)
- claim_items (array of objects with: procedure_code, procedure_description, diagnosis_code, service_date, provider_name, billed_amount, units)

If any information is missing or unclear, use null for that field."""
        
        try:
            extracted_json = self.llm_provider.generate_structured(
                prompt=prompt,
                system_prompt=self.get_system_prompt(),
                response_format={"type": "json_object"}
            )
            return extracted_json
        except Exception as e:
            self.logger.error(f"LLM extraction failed: {str(e)}")
            # Return minimal structure
            return {
                "claim_id": f"CLM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "error": "Extraction failed",
                "raw_text": claim_text[:500]
            }
    
    def _identify_missing_fields(self, extracted_data: Dict[str, Any]) -> list:
        """Identify missing or null fields."""
        required_fields = [
            "claim_id", "policy_number", "claimant_name", "claimant_dob",
            "primary_diagnosis", "total_billed_amount", "provider_name"
        ]
        
        missing = []
        for field in required_fields:
            if not extracted_data.get(field):
                missing.append(field)
        
        return missing
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on completeness."""
        total_fields = 15  # Total important fields
        filled_fields = sum(1 for v in extracted_data.values() if v not in [None, "", [], {}])
        
        confidence = filled_fields / total_fields
        return round(confidence, 2)
