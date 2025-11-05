"""Explanation agent for generating human-readable reports."""

import time
from typing import Dict, Any

from .base_agent import BaseAgent


class ExplanationAgent(BaseAgent):
    """Agent responsible for generating explanations and reports."""
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="ExplanationAgent", **kwargs)
    
    def get_system_prompt(self) -> str:
        """Get system prompt for explanation agent."""
        return """You are an expert insurance claim communication agent. Your role is to:
1. Generate clear, empathetic explanations for claim decisions
2. Translate technical information into patient-friendly language
3. Provide actionable next steps and guidance
4. Create comprehensive yet understandable reports
5. Address common questions and concerns

Use professional but accessible language. Be empathetic and helpful."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explanation and summary for claim processing.
        
        Args:
            input_data: Dictionary containing:
                - claim_data: Extracted claim data
                - decision_data: Decision results
                - validation_results: Validation results
                
        Returns:
            Dictionary containing formatted explanation
        """
        start_time = time.time()
        self.logger.info("Starting explanation generation...")
        
        try:
            claim_data = input_data.get("claim_data", {})
            decision_data = input_data.get("decision_data", {})
            validation_results = input_data.get("validation_results", [])
            
            # Generate patient-friendly summary
            summary = self._generate_summary(claim_data, decision_data)
            
            # Generate detailed explanation
            detailed_explanation = self._generate_detailed_explanation(
                claim_data, decision_data, validation_results
            )
            
            # Generate FAQ section
            faq = self._generate_faq(decision_data)
            
            # Format financial breakdown
            financial_summary = self._format_financial_summary(
                decision_data.get("financial_breakdown", {})
            )
            
            output_data = {
                "status": "success",
                "agent": self.agent_name,
                "summary": summary,
                "detailed_explanation": detailed_explanation,
                "financial_summary": financial_summary,
                "faq": faq,
                "formatted_report": self._create_formatted_report(
                    claim_data, decision_data, summary, detailed_explanation, financial_summary
                )
            }
            
        except Exception as e:
            self.logger.error(f"Explanation generation failed: {str(e)}")
            output_data = {
                "status": "error",
                "agent": self.agent_name,
                "error": str(e),
                "summary": "Error generating explanation"
            }
        
        duration = time.time() - start_time
        self.log_execution(input_data, output_data, duration)
        
        return output_data
    
    def _generate_summary(self, claim_data: Dict[str, Any], decision_data: Dict[str, Any]) -> str:
        """Generate concise summary of claim processing."""
        decision_type = decision_data.get("decision_type", "unknown")
        claim_id = claim_data.get("claim_id", "N/A")
        total_billed = claim_data.get("total_billed_amount", 0)
        
        financial = decision_data.get("financial_breakdown", {})
        approved_amount = financial.get("approved_amount", 0)
        patient_resp = financial.get("patient_responsibility", 0)
        
        if decision_type == "approved":
            return f"""Your claim {claim_id} has been APPROVED. 
            
Total Billed: ${total_billed:,.2f}
Approved Amount: ${approved_amount:,.2f}
Your Responsibility: ${patient_resp:,.2f}
Insurance Payment: ${financial.get('insurance_payment', 0):,.2f}

Your claim has been processed successfully. Please review the details below."""
        
        elif decision_type == "rejected":
            return f"""Your claim {claim_id} has been REJECTED.

Total Billed: ${total_billed:,.2f}

Unfortunately, your claim cannot be approved at this time due to issues identified during processing. Please review the explanation below for details on how to proceed."""
        
        elif decision_type == "needs_review":
            return f"""Your claim {claim_id} requires MANUAL REVIEW.

Total Billed: ${total_billed:,.2f}

Your claim needs additional review by our claims specialists. We will contact you within 5-7 business days with an update."""
        
        else:
            return f"""Your claim {claim_id} is being processed.

Total Billed: ${total_billed:,.2f}

Please review the details below for more information about your claim status."""
    
    def _generate_detailed_explanation(
        self,
        claim_data: Dict[str, Any],
        decision_data: Dict[str, Any],
        validation_results: list
    ) -> str:
        """Generate detailed explanation using LLM."""
        
        decision_type = decision_data.get("decision_type", "unknown")
        reasoning = decision_data.get("reasoning", "")
        
        prompt = f"""Create a detailed, patient-friendly explanation for an insurance claim decision.

CLAIM DETAILS:
- Claim ID: {claim_data.get('claim_id')}
- Patient: {claim_data.get('claimant_name')}
- Service Date: {claim_data.get('service_start_date')}
- Provider: {claim_data.get('provider_name')}
- Total Billed: ${claim_data.get('total_billed_amount', 0):,.2f}

DECISION: {decision_type.upper()}

TECHNICAL REASONING:
{reasoning}

VALIDATION SUMMARY:
- Total Checks: {len(validation_results)}
- Passed: {len([v for v in validation_results if v.get('passed', False)])}
- Issues: {len([v for v in validation_results if not v.get('passed', True)])}

Please write a clear, empathetic explanation (3-4 paragraphs) that:
1. Explains the decision in simple terms
2. Describes what was checked and why
3. Addresses any concerns the patient might have
4. Provides reassurance and guidance

Use a warm, professional tone. Avoid technical jargon."""
        
        try:
            explanation = self.llm_provider.generate(
                prompt=prompt,
                system_prompt=self.get_system_prompt()
            )
            return explanation.strip()
        except Exception as e:
            self.logger.error(f"LLM explanation generation failed: {str(e)}")
            return reasoning  # Fallback to technical reasoning
    
    def _format_financial_summary(self, financial_breakdown: Dict[str, Any]) -> str:
        """Format financial breakdown in readable format."""
        if not financial_breakdown:
            return "Financial information not available."
        
        summary = f"""
FINANCIAL BREAKDOWN:

Total Billed Amount:        ${financial_breakdown.get('total_billed', 0):>10,.2f}

Deductible Applied:         ${financial_breakdown.get('deductible_applied', 0):>10,.2f}
Copay Applied:              ${financial_breakdown.get('copay_applied', 0):>10,.2f}
Coinsurance Applied:        ${financial_breakdown.get('coinsurance_applied', 0):>10,.2f}
                            ─────────────────
Patient Responsibility:     ${financial_breakdown.get('patient_responsibility', 0):>10,.2f}

Insurance Payment:          ${financial_breakdown.get('insurance_payment', 0):>10,.2f}
"""
        return summary.strip()
    
    def _generate_faq(self, decision_data: Dict[str, Any]) -> list:
        """Generate FAQ based on decision type."""
        decision_type = decision_data.get("decision_type", "unknown")
        
        faq = []
        
        if decision_type == "approved":
            faq = [
                {
                    "question": "When will I receive payment?",
                    "answer": "Insurance payments are typically processed within 10 business days. You will receive an Explanation of Benefits (EOB) in the mail."
                },
                {
                    "question": "What is my patient responsibility?",
                    "answer": "Your patient responsibility includes your deductible, copay, and coinsurance amounts. This is the amount you owe to your healthcare provider."
                },
                {
                    "question": "Can I appeal this decision?",
                    "answer": "Yes, you have the right to appeal any claim decision. Contact our customer service team for information on the appeals process."
                }
            ]
        
        elif decision_type == "rejected":
            faq = [
                {
                    "question": "Why was my claim rejected?",
                    "answer": "Your claim was rejected due to issues identified during processing. Please review the detailed explanation above for specific reasons."
                },
                {
                    "question": "Can I resubmit my claim?",
                    "answer": "Yes, you can resubmit your claim after correcting the identified issues. Make sure all required documentation is complete and accurate."
                },
                {
                    "question": "How do I appeal this decision?",
                    "answer": "You can file an appeal within 180 days of this decision. Contact our appeals department or visit our website for the appeals form and instructions."
                }
            ]
        
        elif decision_type == "needs_review":
            faq = [
                {
                    "question": "How long will the review take?",
                    "answer": "Manual reviews typically take 5-7 business days. We will contact you if we need additional information."
                },
                {
                    "question": "What happens during manual review?",
                    "answer": "A claims specialist will carefully review your claim, supporting documentation, and policy coverage to make a final decision."
                },
                {
                    "question": "Do I need to do anything?",
                    "answer": "We will contact you if we need additional information. Otherwise, please wait for our review to be completed."
                }
            ]
        
        return faq
    
    def _create_formatted_report(
        self,
        claim_data: Dict[str, Any],
        decision_data: Dict[str, Any],
        summary: str,
        detailed_explanation: str,
        financial_summary: str
    ) -> str:
        """Create a formatted text report."""
        
        report = f"""
{'='*80}
                    INSURANCE CLAIM PROCESSING REPORT
{'='*80}

CLAIM INFORMATION:
─────────────────────────────────────────────────────────────────────────────
Claim ID:           {claim_data.get('claim_id', 'N/A')}
Patient Name:       {claim_data.get('claimant_name', 'N/A')}
Policy Number:      {claim_data.get('policy_number', 'N/A')}
Service Date:       {claim_data.get('service_start_date', 'N/A')}
Provider:           {claim_data.get('provider_name', 'N/A')}

{'='*80}
DECISION SUMMARY:
{'='*80}

{summary}

{'='*80}
DETAILED EXPLANATION:
{'='*80}

{detailed_explanation}

{'='*80}
{financial_summary}

{'='*80}
NEXT STEPS:
{'='*80}
"""
        
        next_steps = decision_data.get("next_steps", [])
        for i, step in enumerate(next_steps, 1):
            report += f"\n{i}. {step}"
        
        report += f"\n\n{'='*80}\n"
        report += "For questions or concerns, please contact our customer service team.\n"
        report += f"{'='*80}\n"
        
        return report
