"""Decision agent for generating claim approval/rejection recommendations."""

import time
from typing import Dict, Any
from datetime import datetime

from .base_agent import BaseAgent
from models.decision import DecisionType


class DecisionAgent(BaseAgent):
    """Agent responsible for making claim decisions."""
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="DecisionAgent", **kwargs)
    
    def get_system_prompt(self) -> str:
        """Get system prompt for decision agent."""
        return """You are an expert insurance claim decision agent. Your role is to:
1. Analyze validation results and claim data
2. Generate approval or rejection recommendations
3. Calculate coverage amounts and patient responsibility
4. Assign confidence scores to decisions
5. Flag claims that require manual review
6. Provide clear reasoning for all decisions

Consider all factors including policy compliance, medical necessity, and risk factors."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate claim decision based on validation results.
        
        Args:
            input_data: Dictionary containing:
                - claim_data: Extracted claim data
                - validation_results: Results from validation agent
                - financial_breakdown: Financial calculations
                
        Returns:
            Dictionary containing decision and reasoning
        """
        start_time = time.time()
        self.logger.info("Starting decision generation...")
        
        try:
            claim_data = input_data.get("claim_data", {})
            validation_results = input_data.get("validation_results", [])
            financial_breakdown = input_data.get("financial_breakdown", {})
            validation_status = input_data.get("validation_status", "failed")
            
            # Analyze validation results
            critical_issues = [v for v in validation_results if not v["passed"] and v["severity"] == "error"]
            warnings = [v for v in validation_results if not v["passed"] and v["severity"] == "warning"]
            
            # Determine decision type
            if len(critical_issues) > 0:
                decision_type = DecisionType.REJECTED
                confidence = 0.95
            elif len(warnings) > 2:
                decision_type = DecisionType.NEEDS_REVIEW
                confidence = 0.70
            elif len(warnings) > 0:
                decision_type = DecisionType.PARTIAL_APPROVAL
                confidence = 0.85
            else:
                decision_type = DecisionType.APPROVED
                confidence = 0.95
            
            # Generate reasoning using LLM
            reasoning = self._generate_reasoning(
                claim_data, validation_results, decision_type, critical_issues, warnings
            )
            
            # Determine if manual review is needed
            requires_manual_review = (
                len(critical_issues) > 0 or
                len(warnings) > 2 or
                confidence < 0.80 or
                financial_breakdown.get("approved_amount", 0) > 50000
            )
            
            # Generate recommendations and next steps
            recommendations = self._generate_recommendations(decision_type, critical_issues, warnings)
            next_steps = self._generate_next_steps(decision_type, critical_issues, warnings)
            
            # Compile flags
            flags = []
            if requires_manual_review:
                flags.append("MANUAL_REVIEW_REQUIRED")
            if financial_breakdown.get("approved_amount", 0) > 50000:
                flags.append("HIGH_VALUE_CLAIM")
            if len(critical_issues) > 0:
                flags.append("CRITICAL_ISSUES_FOUND")
            
            # Identify missing information
            missing_info = []
            for result in validation_results:
                if not result["passed"] and "missing" in result["message"].lower():
                    missing_info.append(result["check_name"])
            
            output_data = {
                "status": "success",
                "agent": self.agent_name,
                "decision_type": decision_type.value,
                "confidence_score": confidence,
                "reasoning": reasoning,
                "financial_breakdown": financial_breakdown,
                "requires_manual_review": requires_manual_review,
                "review_reason": "Critical issues or high-value claim" if requires_manual_review else None,
                "flags": flags,
                "missing_information": missing_info,
                "recommendations": recommendations,
                "next_steps": next_steps,
                "validation_summary": {
                    "total_checks": len(validation_results),
                    "passed": len([v for v in validation_results if v["passed"]]),
                    "critical_issues": len(critical_issues),
                    "warnings": len(warnings)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Decision generation failed: {str(e)}")
            output_data = {
                "status": "error",
                "agent": self.agent_name,
                "error": str(e),
                "decision_type": DecisionType.NEEDS_REVIEW.value
            }
        
        duration = time.time() - start_time
        self.log_execution(input_data, output_data, duration)
        
        return output_data
    
    def _generate_reasoning(
        self,
        claim_data: Dict[str, Any],
        validation_results: list,
        decision_type: DecisionType,
        critical_issues: list,
        warnings: list
    ) -> str:
        """Generate detailed reasoning for the decision using LLM."""
        
        prompt = f"""Analyze the following insurance claim and provide detailed reasoning for the decision.

CLAIM INFORMATION:
- Claim ID: {claim_data.get('claim_id')}
- Total Billed Amount: ${claim_data.get('total_billed_amount', 0):,.2f}
- Primary Diagnosis: {claim_data.get('primary_diagnosis')}
- Service Date: {claim_data.get('service_start_date')}

VALIDATION RESULTS:
Total Checks: {len(validation_results)}
Passed: {len([v for v in validation_results if v['passed']])}
Critical Issues: {len(critical_issues)}
Warnings: {len(warnings)}

CRITICAL ISSUES:
{self._format_issues(critical_issues)}

WARNINGS:
{self._format_issues(warnings)}

DECISION: {decision_type.value.upper()}

Provide a clear, professional explanation (2-3 paragraphs) for why this decision was made. 
Focus on the key factors that influenced the decision. Be specific about policy compliance and any issues found."""
        
        try:
            reasoning = self.llm_provider.generate(
                prompt=prompt,
                system_prompt=self.get_system_prompt()
            )
            return reasoning.strip()
        except Exception as e:
            self.logger.error(f"LLM reasoning generation failed: {str(e)}")
            # Fallback to rule-based reasoning
            return self._generate_fallback_reasoning(decision_type, critical_issues, warnings)
    
    def _format_issues(self, issues: list) -> str:
        """Format issues for prompt."""
        if not issues:
            return "None"
        
        formatted = []
        for issue in issues:
            formatted.append(f"- {issue['check_name']}: {issue['message']}")
        return "\n".join(formatted)
    
    def _generate_fallback_reasoning(
        self,
        decision_type: DecisionType,
        critical_issues: list,
        warnings: list
    ) -> str:
        """Generate fallback reasoning without LLM."""
        if decision_type == DecisionType.APPROVED:
            return "The claim has passed all validation checks and meets policy requirements. All diagnosis and procedure codes are valid, and the claim amount is within coverage limits. The claim is approved for processing."
        
        elif decision_type == DecisionType.REJECTED:
            issues_text = ", ".join([issue["check_name"] for issue in critical_issues])
            return f"The claim has been rejected due to critical issues: {issues_text}. These issues prevent the claim from being processed and must be resolved before resubmission."
        
        elif decision_type == DecisionType.NEEDS_REVIEW:
            return "The claim requires manual review due to multiple warnings or potential issues. While no critical errors were found, the complexity of the claim necessitates human oversight before a final decision can be made."
        
        else:
            return "The claim has been partially approved. Some services may be covered while others require additional review or documentation."
    
    def _generate_recommendations(
        self,
        decision_type: DecisionType,
        critical_issues: list,
        warnings: list
    ) -> list:
        """Generate recommendations based on decision."""
        recommendations = []
        
        if decision_type == DecisionType.REJECTED:
            recommendations.append("Review and correct all critical issues identified in the validation results")
            recommendations.append("Ensure all required documentation is complete and accurate")
            recommendations.append("Verify policy coverage and eligibility before resubmitting")
        
        elif decision_type == DecisionType.NEEDS_REVIEW:
            recommendations.append("Provide additional documentation to support the claim")
            recommendations.append("Contact the insurance provider for clarification on coverage")
            recommendations.append("Consider appealing if you believe the claim should be covered")
        
        elif decision_type == DecisionType.APPROVED:
            recommendations.append("Review the approved amount and patient responsibility")
            recommendations.append("Keep all documentation for your records")
            recommendations.append("Payment will be processed according to policy terms")
        
        # Add specific recommendations based on issues
        for issue in critical_issues + warnings:
            if "diagnosis" in issue["check_name"].lower():
                recommendations.append("Verify diagnosis codes with healthcare provider")
            elif "procedure" in issue["check_name"].lower():
                recommendations.append("Confirm procedure codes match services rendered")
            elif "authorization" in issue["check_name"].lower():
                recommendations.append("Obtain required pre-authorization before services")
        
        return list(set(recommendations))[:5]  # Return unique, max 5
    
    def _generate_next_steps(
        self,
        decision_type: DecisionType,
        critical_issues: list,
        warnings: list
    ) -> list:
        """Generate next steps based on decision."""
        next_steps = []
        
        if decision_type == DecisionType.REJECTED:
            next_steps.append("Correct identified issues and resubmit claim")
            next_steps.append("Contact provider for missing information")
            next_steps.append("Appeal decision if you disagree with rejection")
        
        elif decision_type == DecisionType.NEEDS_REVIEW:
            next_steps.append("Wait for manual review by claims specialist")
            next_steps.append("Provide additional documentation if requested")
            next_steps.append("Expected review time: 5-7 business days")
        
        elif decision_type == DecisionType.APPROVED:
            next_steps.append("Payment will be processed within 10 business days")
            next_steps.append("You will receive an Explanation of Benefits (EOB)")
            next_steps.append("Pay any patient responsibility amounts to provider")
        
        return next_steps
