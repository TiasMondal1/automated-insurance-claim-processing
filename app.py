"""Streamlit frontend for AI-powered insurance claim processing."""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import time

# Import agents and utilities
from agents.orchestrator import OrchestratorAgent
from utils.document_parser import DocumentParser
from utils.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="AI Insurance Claim Processor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .status-approved {
        color: #28a745;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .status-rejected {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .status-review {
        color: #ffc107;
        font-weight: bold;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'processing_results' not in st.session_state:
        st.session_state.processing_results = None
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None


def load_sample_data():
    """Load sample claims and policies."""
    data_dir = Path("data")
    
    sample_claims = []
    sample_policies = []
    
    # Load sample claims
    claims_dir = data_dir / "sample_claims"
    if claims_dir.exists():
        for file in claims_dir.glob("*.json"):
            with open(file, 'r') as f:
                sample_claims.append(json.load(f))
    
    # Load sample policies
    policies_dir = data_dir / "sample_policies"
    if policies_dir.exists():
        for file in policies_dir.glob("*.json"):
            with open(file, 'r') as f:
                sample_policies.append(json.load(f))
    
    return sample_claims, sample_policies


def render_sidebar():
    """Render sidebar with configuration."""
    st.sidebar.title("⚙️ Configuration")
    
    # Check if API key is configured
    api_key_configured = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    
    if api_key_configured:
        st.sidebar.success("✓ API Key Configured")
    else:
        st.sidebar.error("❌ API Key Not Configured")
        st.sidebar.info("Please set your API key in the .env file")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info(
        "AI-powered insurance claim processing system using multi-agent architecture."
    )
    
    return api_key_configured


def process_claim(claim_data, policy_data, medical_report=""):
    """Process claim using orchestrator agent."""
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Prepare input
        input_data = {
            "claim_document": claim_data,
            "policy_data": policy_data,
            "medical_report": medical_report
        }
        
        # Process
        with st.spinner("Processing claim... This may take a minute."):
            results = orchestrator.process(input_data)
        
        return results
    
    except Exception as e:
        st.error(f"Error processing claim: {str(e)}")
        return None


def render_results(results):
    """Render processing results."""
    if not results or results.get("status") != "completed":
        st.error("Processing failed or incomplete")
        return
    
    final_output = results.get("final_output", {})
    
    # Header
    st.markdown('<div class="main-header">📋 Claim Processing Results</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Decision Status
    decision = final_output.get("decision", {})
    decision_type = decision.get("type", "unknown")
    
    if decision_type == "approved":
        st.markdown('<div class="status-approved">✓ CLAIM APPROVED</div>', unsafe_allow_html=True)
    elif decision_type == "rejected":
        st.markdown('<div class="status-rejected">✗ CLAIM REJECTED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-review">⚠ NEEDS REVIEW</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    financial = final_output.get("financial", {})
    
    with col1:
        st.metric("Total Billed", f"${financial.get('total_billed', 0):,.2f}")
    
    with col2:
        st.metric("Approved Amount", f"${financial.get('approved_amount', 0):,.2f}")
    
    with col3:
        st.metric("Insurance Payment", f"${financial.get('insurance_payment', 0):,.2f}")
    
    with col4:
        st.metric("Your Responsibility", f"${financial.get('patient_responsibility', 0):,.2f}")
    
    st.markdown("---")
    
    # Tabs for detailed information
    tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Financial Details", "Validation", "Full Report"])
    
    with tab1:
        st.subheader("Claim Summary")
        st.write(final_output.get("summary", ""))
        
        st.subheader("Detailed Explanation")
        st.write(final_output.get("detailed_explanation", ""))
        
        if final_output.get("recommendations"):
            st.subheader("Recommendations")
            for rec in final_output.get("recommendations", []):
                st.write(f"• {rec}")
        
        if final_output.get("next_steps"):
            st.subheader("Next Steps")
            for step in final_output.get("next_steps", []):
                st.write(f"• {step}")
    
    with tab2:
        st.subheader("Financial Breakdown")
        st.code(final_output.get("financial_summary", ""), language="text")
        
        # Financial chart
        import pandas as pd
        financial_data = {
            "Category": ["Deductible", "Copay", "Coinsurance", "Insurance Payment"],
            "Amount": [
                financial.get("deductible_applied", 0),
                financial.get("copay_applied", 0),
                financial.get("coinsurance_applied", 0),
                financial.get("insurance_payment", 0)
            ]
        }
        df = pd.DataFrame(financial_data)
        st.bar_chart(df.set_index("Category"))
    
    with tab3:
        st.subheader("Validation Summary")
        validation = final_output.get("validation_summary", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Checks", validation.get("total_checks", 0))
        with col2:
            st.metric("Critical Issues", validation.get("critical_issues", 0))
        with col3:
            st.metric("Warnings", validation.get("warnings", 0))
        
        # Validation results
        if results.get("validation", {}).get("validation_results"):
            st.subheader("Validation Details")
            for result in results["validation"]["validation_results"]:
                status_icon = "✓" if result["passed"] else "✗"
                status_color = "green" if result["passed"] else "red"
                st.markdown(f"**{status_icon} {result['check_name']}** - {result['message']}")
    
    with tab4:
        st.subheader("Complete Processing Report")
        st.code(final_output.get("formatted_report", ""), language="text")
        
        # Download button
        st.download_button(
            label="Download Report (TXT)",
            data=final_output.get("formatted_report", ""),
            file_name=f"claim_report_{final_output.get('claim_id', 'unknown')}.txt",
            mime="text/plain"
        )


def main():
    """Main application."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🏥 AI Insurance Claim Processor</div>', unsafe_allow_html=True)
    st.markdown("### Automated claim processing using multi-agent AI")
    st.markdown("---")
    
    # Sidebar
    api_configured = render_sidebar()
    
    if not api_configured:
        st.warning("⚠️ Please configure your API key in the .env file to use this application.")
        st.info("Copy .env.example to .env and add your OpenAI or Anthropic API key.")
        return
    
    # Load sample data
    sample_claims, sample_policies = load_sample_data()
    
    # Upload section
    st.header("📄 Submit Claim")
    
    tab1, tab2 = st.tabs(["Use Sample Data", "Upload Files"])
    
    with tab1:
        if not sample_claims or not sample_policies:
            st.warning("No sample data found. Run data_generator.py first to generate sample data.")
            st.code("python data_generator.py", language="bash")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                claim_options = [f"{c['claim_id']} - {c['claimant_name']}" for c in sample_claims]
                selected_claim_idx = st.selectbox("Select Sample Claim", range(len(claim_options)), format_func=lambda i: claim_options[i])
                selected_claim = sample_claims[selected_claim_idx]
                
                st.json(selected_claim, expanded=False)
            
            with col2:
                policy_options = [f"{p['policy_number']} - {p['policy_holder_name']}" for p in sample_policies]
                selected_policy_idx = st.selectbox("Select Sample Policy", range(len(policy_options)), format_func=lambda i: policy_options[i])
                selected_policy = sample_policies[selected_policy_idx]
                
                st.json(selected_policy, expanded=False)
            
            medical_report = st.text_area("Medical Report (Optional)", height=100)
            
            if st.button("Process Claim", type="primary", use_container_width=True):
                results = process_claim(selected_claim, selected_policy, medical_report)
                if results:
                    st.session_state.processing_results = results
                    st.rerun()
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            claim_file = st.file_uploader("Upload Claim (JSON)", type=["json"])
        
        with col2:
            policy_file = st.file_uploader("Upload Policy (JSON)", type=["json"])
        
        medical_report_upload = st.text_area("Medical Report (Optional)", height=100, key="upload_medical")
        
        if st.button("Process Uploaded Claim", type="primary", use_container_width=True):
            if claim_file and policy_file:
                claim_data = json.load(claim_file)
                policy_data = json.load(policy_file)
                
                results = process_claim(claim_data, policy_data, medical_report_upload)
                if results:
                    st.session_state.processing_results = results
                    st.rerun()
            else:
                st.error("Please upload both claim and policy files")
    
    # Display results if available
    if st.session_state.processing_results:
        st.markdown("---")
        render_results(st.session_state.processing_results)
        
        if st.button("Process Another Claim"):
            st.session_state.processing_results = None
            st.rerun()


if __name__ == "__main__":
    main()
