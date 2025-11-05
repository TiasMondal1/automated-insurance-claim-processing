"""Orchestrator agent that coordinates all other agents."""

import time
from typing import Dict, Any, Optional
from datetime import datetime

from .base_agent import BaseAgent
from .extraction_agent import ExtractionAgent
from .validation_agent import ValidationAgent
from .decision_agent import DecisionAgent
from .explanation_agent import ExplanationAgent

from models.claim import Claim, ClaimStatus
from models.policy import Policy
from models.decision import Decision, DecisionType, ValidationResult


class OrchestratorAgent(BaseAgent):
    """Main orchestrator that coordinates all agents in the claim processing workflow."""
    
    def __init__(self, **kwargs):
        super().__init__(agent_name="OrchestratorAgent", **kwargs)
        
        # Initialize all sub-agents
        self.extraction_agent = ExtractionAgent(llm_provider=self.llm_provider)
        self.validation_agent = ValidationAgent(llm_provider=self.llm_provider)
        self.decision_agent = DecisionAgent(llm_provider=self.llm_provider)
        self.explanation_agent = ExplanationAgent(llm_provider=self.llm_provider)
        
        self.logger.info("OrchestratorAgent initialized with all sub-agents")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the complete claim processing workflow.
        
        Args:
            input_data: Dictionary containing:
                - claim_document: Claim form data (JSON or text)
                - medical_report: Optional medical report
                - policy_data: Policy information
                
        Returns:
            Complete processing results from all agents
        """
        start_time = time.time()
        self.logger.info("="*80)
        self.logger.info("Starting claim processing workflow...")
        self.logger.info("="*80)
        
        workflow_results = {
            "workflow_id": f"WF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "status": "processing"
        }
        
        try:
            # Step 1: Extraction
            self.logger.info("\n[STEP 1/4] Running Extraction Agent...")
            extraction_input = {
                "claim_document": input_data.get("claim_document"),
                "medical_report": input_data.get("medical_report", "")
            }
            extraction_result = self.extraction_agent.process(extraction_input)
            workflow_results["extraction"] = extraction_result
            
            if extraction_result.get("status") != "success":
                raise Exception(f"Extraction failed: {extraction_result.get('error')}")
            
            claim_data = extraction_result.get("extracted_data", {})
            self.logger.info(f"✓ Extraction completed - Claim ID: {claim_data.get('claim_id')}")
            
            # Step 2: Validation
            self.logger.info("\n[STEP 2/4] Running Validation Agent...")
            validation_input = {
                "claim_data": claim_data,
                "policy_data": input_data.get("policy_data", {})
            }
            validation_result = self.validation_agent.process(validation_input)
            workflow_results["validation"] = validation_result
            
            if validation_result.get("status") != "success":
                raise Exception(f"Validation failed: {validation_result.get('error')}")
            
            validation_status = validation_result.get("validation_status")
            critical_issues = validation_result.get("critical_issues_count", 0)
            self.logger.info(f"✓ Validation completed - Status: {validation_status}, Critical Issues: {critical_issues}")
            
            # Step 3: Decision
            self.logger.info("\n[STEP 3/4] Running Decision Agent...")
            decision_input = {
                "claim_data": claim_data,
                "validation_results": validation_result.get("validation_results", []),
                "validation_status": validation_status,
                "financial_breakdown": validation_result.get("financial_breakdown", {})
            }
            decision_result = self.decision_agent.process(decision_input)
            workflow_results["decision"] = decision_result
            
            if decision_result.get("status") != "success":
                raise Exception(f"Decision failed: {decision_result.get('error')}")
            
            decision_type = decision_result.get("decision_type")
            confidence = decision_result.get("confidence_score", 0)
            self.logger.info(f"✓ Decision completed - Type: {decision_type}, Confidence: {confidence:.2%}")
            
            # Step 4: Explanation
            self.logger.info("\n[STEP 4/4] Running Explanation Agent...")
            explanation_input = {
                "claim_data": claim_data,
                "decision_data": decision_result,
                "validation_results": validation_result.get("validation_results", [])
            }
            explanation_result = self.explanation_agent.process(explanation_input)
            workflow_results["explanation"] = explanation_result
            
            if explanation_result.get("status") != "success":
                raise Exception(f"Explanation failed: {explanation_result.get('error')}")
            
            self.logger.info("✓ Explanation completed")
            
            # Compile final results
            workflow_results["status"] = "completed"
            workflow_results["end_time"] = datetime.now().isoformat()
            workflow_results["total_processing_time"] = time.time() - start_time
            
            # Create structured output
            final_output = self._compile_final_output(
                claim_data,
                validation_result,
                decision_result,
                explanation_result,
                workflow_results
            )
            
            workflow_results["final_output"] = final_output
            
            self.logger.info("\n" + "="*80)
            self.logger.info(f"Workflow completed successfully in {workflow_results['total_processing_time']:.2f}s")
            self.logger.info(f"Decision: {decision_type.upper()} (Confidence: {confidence:.2%})")
            self.logger.info("="*80)
            
        except Exception as e:
            self.logger.error(f"\n❌ Workflow failed: {str(e)}")
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            workflow_results["end_time"] = datetime.now().isoformat()
            workflow_results["total_processing_time"] = time.time() - start_time
        
        duration = time.time() - start_time
        self.log_execution(input_data, workflow_results, duration)
        
        return workflow_results
    
    def _compile_final_output(
        self,
        claim_data: Dict[str, Any],
        validation_result: Dict[str, Any],
        decision_result: Dict[str, Any],
        explanation_result: Dict[str, Any],
        workflow_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile all results into a structured final output."""
        
        financial = decision_result.get("financial_breakdown", {})
        
        return {
            "claim_id": claim_data.get("claim_id"),
            "workflow_id": workflow_results.get("workflow_id"),
            "processing_timestamp": workflow_results.get("end_time"),
            "processing_time_seconds": workflow_results.get("total_processing_time"),
            
            # Claim Information
            "claim_info": {
                "claimant_name": claim_data.get("claimant_name"),
                "policy_number": claim_data.get("policy_number"),
                "service_date": claim_data.get("service_start_date"),
                "provider": claim_data.get("provider_name"),
                "total_billed": claim_data.get("total_billed_amount")
            },
            
            # Decision
            "decision": {
                "type": decision_result.get("decision_type"),
                "confidence_score": decision_result.get("confidence_score"),
                "requires_manual_review": decision_result.get("requires_manual_review"),
                "flags": decision_result.get("flags", [])
            },
            
            # Financial
            "financial": {
                "total_billed": financial.get("total_billed", 0),
                "approved_amount": financial.get("approved_amount", 0),
                "insurance_payment": financial.get("insurance_payment", 0),
                "patient_responsibility": financial.get("patient_responsibility", 0),
                "deductible_applied": financial.get("deductible_applied", 0),
                "copay_applied": financial.get("copay_applied", 0),
                "coinsurance_applied": financial.get("coinsurance_applied", 0)
            },
            
            # Validation Summary
            "validation_summary": {
                "status": validation_result.get("validation_status"),
                "total_checks": len(validation_result.get("validation_results", [])),
                "critical_issues": validation_result.get("critical_issues_count", 0),
                "warnings": validation_result.get("warnings_count", 0)
            },
            
            # Explanations
            "summary": explanation_result.get("summary", ""),
            "detailed_explanation": explanation_result.get("detailed_explanation", ""),
            "financial_summary": explanation_result.get("financial_summary", ""),
            
            # Actions
            "recommendations": decision_result.get("recommendations", []),
            "next_steps": decision_result.get("next_steps", []),
            "missing_information": decision_result.get("missing_information", []),
            
            # FAQ
            "faq": explanation_result.get("faq", []),
            
            # Full Report
            "formatted_report": explanation_result.get("formatted_report", "")
        }
    
    def create_claim_object(self, claim_data: Dict[str, Any]) -> Claim:
        """Convert extracted data to Claim model object."""
        try:
            return Claim(**claim_data)
        except Exception as e:
            self.logger.error(f"Failed to create Claim object: {str(e)}")
            raise
    
    def create_decision_object(
        self,
        claim_id: str,
        decision_result: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Decision:
        """Convert decision data to Decision model object."""
        try:
            financial = decision_result.get("financial_breakdown", {})
            
            # Convert validation results to ValidationResult objects
            validation_results = []
            for v in validation_result.get("validation_results", []):
                validation_results.append(ValidationResult(**v))
            
            decision = Decision(
                claim_id=claim_id,
                decision_type=DecisionType(decision_result.get("decision_type")),
                confidence_score=decision_result.get("confidence_score", 0),
                reasoning=decision_result.get("reasoning", ""),
                approved_amount=financial.get("approved_amount", 0),
                patient_responsibility=financial.get("patient_responsibility", 0),
                insurance_payment=financial.get("insurance_payment", 0),
                deductible_applied=financial.get("deductible_applied", 0),
                copay_applied=financial.get("copay_applied", 0),
                coinsurance_applied=financial.get("coinsurance_applied", 0),
                validation_results=validation_results,
                flags=decision_result.get("flags", []),
                missing_information=decision_result.get("missing_information", []),
                recommendations=decision_result.get("recommendations", []),
                next_steps=decision_result.get("next_steps", []),
                requires_manual_review=decision_result.get("requires_manual_review", False),
                review_reason=decision_result.get("review_reason"),
                processing_agents=["ExtractionAgent", "ValidationAgent", "DecisionAgent", "ExplanationAgent"]
            )
            
            return decision
        except Exception as e:
            self.logger.error(f"Failed to create Decision object: {str(e)}")
            raise
