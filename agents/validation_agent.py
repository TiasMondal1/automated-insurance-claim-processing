"""Validation agent for checking claims against policy rules."""

import time
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from models.policy import Policy
from models.decision import ValidationResult


class ValidationAgent(BaseAgent):
    """Agent responsible for validating claims against policy rules."""
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="ValidationAgent", **kwargs)
    
    def get_system_prompt(self) -> str:
        """Get system prompt for validation agent."""
        return """You are an expert insurance policy validation agent. Your role is to:
1. Validate claims against policy coverage rules and limits
2. Check eligibility and coverage criteria
3. Verify diagnosis and procedure codes
4. Identify missing information or documentation
5. Flag policy violations or exclusions
6. Calculate deductibles, copays, and coinsurance

Be thorough and precise in your validation checks."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate claim against policy rules.
        
        Args:
            input_data: Dictionary containing:
                - claim_data: Extracted claim data
                - policy_data: Policy information
                
        Returns:
            Dictionary containing validation results
        """
        start_time = time.time()
        self.logger.info("Starting claim validation...")
        
        try:
            claim_data = input_data.get("claim_data", {})
            policy_data = input_data.get("policy_data", {})
            
            # Perform validation checks
            validation_results = []
            
            # 1. Policy Active Check
            validation_results.append(self._check_policy_active(policy_data, claim_data))
            
            # 2. Coverage Eligibility Check
            validation_results.append(self._check_coverage_eligibility(policy_data, claim_data))
            
            # 3. Coverage Limits Check
            validation_results.append(self._check_coverage_limits(policy_data, claim_data))
            
            # 4. Exclusions Check
            validation_results.append(self._check_exclusions(policy_data, claim_data))
            
            # 5. Pre-authorization Check
            validation_results.append(self._check_preauthorization(policy_data, claim_data))
            
            # 6. Diagnosis Code Validation
            validation_results.append(self._check_diagnosis_codes(claim_data))
            
            # 7. Procedure Code Validation
            validation_results.append(self._check_procedure_codes(claim_data))
            
            # 8. Amount Validation
            validation_results.append(self._check_amounts(claim_data))
            
            # Calculate financial breakdown
            financial_breakdown = self._calculate_financial_breakdown(policy_data, claim_data)
            
            # Determine overall validation status
            critical_failures = [v for v in validation_results if not v["passed"] and v["severity"] == "error"]
            overall_status = "passed" if len(critical_failures) == 0 else "failed"
            
            output_data = {
                "status": "success",
                "agent": self.agent_name,
                "validation_status": overall_status,
                "validation_results": validation_results,
                "financial_breakdown": financial_breakdown,
                "critical_issues_count": len(critical_failures),
                "warnings_count": len([v for v in validation_results if not v["passed"] and v["severity"] == "warning"])
            }
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            output_data = {
                "status": "error",
                "agent": self.agent_name,
                "error": str(e),
                "validation_results": []
            }
        
        duration = time.time() - start_time
        self.log_execution(input_data, output_data, duration)
        
        return output_data
    
    def _check_policy_active(self, policy_data: Dict[str, Any], claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if policy is active on service date."""
        try:
            effective_date = datetime.fromisoformat(str(policy_data.get("effective_date", "")))
            expiration_date = datetime.fromisoformat(str(policy_data.get("expiration_date", "")))
            service_date = datetime.fromisoformat(str(claim_data.get("service_start_date", "")))
            
            is_active = effective_date <= service_date <= expiration_date
            
            return {
                "check_name": "Policy Active Status",
                "passed": is_active,
                "severity": "error" if not is_active else "info",
                "message": "Policy is active on service date" if is_active else "Policy not active on service date",
                "details": {
                    "effective_date": effective_date.isoformat(),
                    "expiration_date": expiration_date.isoformat(),
                    "service_date": service_date.isoformat()
                }
            }
        except Exception as e:
            return {
                "check_name": "Policy Active Status",
                "passed": False,
                "severity": "error",
                "message": f"Unable to verify policy status: {str(e)}",
                "details": {}
            }
    
    def _check_coverage_eligibility(self, policy_data: Dict[str, Any], claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if services are covered under policy."""
        # Simplified check - in real system would check against coverage database
        has_coverage = len(policy_data.get("coverages", [])) > 0
        
        return {
            "check_name": "Coverage Eligibility",
            "passed": has_coverage,
            "severity": "error" if not has_coverage else "info",
            "message": "Services are eligible for coverage" if has_coverage else "No coverage found for services",
            "details": {"coverages_count": len(policy_data.get("coverages", []))}
        }
    
    def _check_coverage_limits(self, policy_data: Dict[str, Any], claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if claim amount exceeds coverage limits."""
        total_billed = float(claim_data.get("total_billed_amount", 0))
        
        # Check against first coverage limit (simplified)
        coverages = policy_data.get("coverages", [])
        if coverages and coverages[0].get("annual_limit"):
            annual_limit = float(coverages[0].get("annual_limit", 0))
            within_limit = total_billed <= annual_limit
            
            return {
                "check_name": "Coverage Limits",
                "passed": within_limit,
                "severity": "warning" if not within_limit else "info",
                "message": f"Claim amount within coverage limits" if within_limit else f"Claim exceeds annual limit",
                "details": {
                    "billed_amount": total_billed,
                    "annual_limit": annual_limit
                }
            }
        
        return {
            "check_name": "Coverage Limits",
            "passed": True,
            "severity": "info",
            "message": "No specific limits to check",
            "details": {}
        }
    
    def _check_exclusions(self, policy_data: Dict[str, Any], claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if any services are excluded."""
        exclusions = policy_data.get("exclusions", [])
        primary_diagnosis = claim_data.get("primary_diagnosis", "")
        
        # Check if diagnosis is excluded
        excluded = False
        for exclusion in exclusions:
            if primary_diagnosis in exclusion.get("excluded_codes", []):
                excluded = True
                break
        
        return {
            "check_name": "Exclusions Check",
            "passed": not excluded,
            "severity": "error" if excluded else "info",
            "message": "No exclusions apply" if not excluded else "Service is excluded under policy",
            "details": {"exclusions_count": len(exclusions)}
        }
    
    def _check_preauthorization(self, policy_data: Dict[str, Any], claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if pre-authorization was required and obtained."""
        # Simplified check
        coverages = policy_data.get("coverages", [])
        requires_preauth = any(c.get("requires_preauth", False) for c in coverages)
        
        if requires_preauth:
            # In real system, would check if preauth was obtained
            has_preauth = claim_data.get("metadata", {}).get("preauthorization_number") is not None
            
            return {
                "check_name": "Pre-authorization",
                "passed": has_preauth,
                "severity": "warning" if not has_preauth else "info",
                "message": "Pre-authorization obtained" if has_preauth else "Pre-authorization may be required",
                "details": {"requires_preauth": requires_preauth}
            }
        
        return {
            "check_name": "Pre-authorization",
            "passed": True,
            "severity": "info",
            "message": "Pre-authorization not required",
            "details": {}
        }
    
    def _check_diagnosis_codes(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate diagnosis codes format."""
        primary_diagnosis = claim_data.get("primary_diagnosis", "")
        
        # Basic ICD-10 format check (simplified)
        is_valid = len(primary_diagnosis) >= 3 and primary_diagnosis[0].isalpha()
        
        return {
            "check_name": "Diagnosis Code Validation",
            "passed": is_valid,
            "severity": "warning" if not is_valid else "info",
            "message": "Valid diagnosis code format" if is_valid else "Invalid or missing diagnosis code",
            "details": {"primary_diagnosis": primary_diagnosis}
        }
    
    def _check_procedure_codes(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate procedure codes format."""
        claim_items = claim_data.get("claim_items", [])
        
        if not claim_items:
            return {
                "check_name": "Procedure Code Validation",
                "passed": False,
                "severity": "error",
                "message": "No procedure codes found",
                "details": {}
            }
        
        # Check if all items have procedure codes
        all_valid = all(item.get("procedure_code") for item in claim_items)
        
        return {
            "check_name": "Procedure Code Validation",
            "passed": all_valid,
            "severity": "warning" if not all_valid else "info",
            "message": "All procedure codes present" if all_valid else "Some procedure codes missing",
            "details": {"items_count": len(claim_items)}
        }
    
    def _check_amounts(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate claim amounts."""
        total_billed = float(claim_data.get("total_billed_amount", 0))
        
        # Check if amount is reasonable (> 0 and < $1M)
        is_valid = 0 < total_billed < 1000000
        
        return {
            "check_name": "Amount Validation",
            "passed": is_valid,
            "severity": "error" if not is_valid else "info",
            "message": "Claim amount is valid" if is_valid else "Claim amount is invalid or unreasonable",
            "details": {"total_billed_amount": total_billed}
        }
    
    def _calculate_financial_breakdown(self, policy_data: Dict[str, Any], claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial breakdown of claim."""
        total_billed = float(claim_data.get("total_billed_amount", 0))
        
        # Get policy financial terms
        annual_deductible = float(policy_data.get("annual_deductible", 0))
        deductible_met = float(policy_data.get("deductible_met", 0))
        
        # Calculate remaining deductible
        remaining_deductible = max(0, annual_deductible - deductible_met)
        deductible_applied = min(remaining_deductible, total_billed)
        
        # Get coinsurance from first coverage (simplified)
        coverages = policy_data.get("coverages", [])
        coinsurance_pct = float(coverages[0].get("coinsurance_percentage", 20)) if coverages else 20
        copay = float(coverages[0].get("copay_amount", 0)) if coverages else 0
        
        # Calculate amounts
        amount_after_deductible = total_billed - deductible_applied
        coinsurance_applied = amount_after_deductible * (coinsurance_pct / 100)
        
        patient_responsibility = deductible_applied + coinsurance_applied + copay
        insurance_payment = total_billed - patient_responsibility
        
        return {
            "total_billed": round(total_billed, 2),
            "deductible_applied": round(deductible_applied, 2),
            "copay_applied": round(copay, 2),
            "coinsurance_applied": round(coinsurance_applied, 2),
            "patient_responsibility": round(patient_responsibility, 2),
            "insurance_payment": round(max(0, insurance_payment), 2),
            "approved_amount": round(total_billed, 2)
        }
