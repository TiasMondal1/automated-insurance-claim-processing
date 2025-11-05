"""Quick start script to test the insurance claim processing system."""

import json
from pathlib import Path
from agents.orchestrator import OrchestratorAgent
from data_generator import SyntheticDataGenerator


def check_setup():
    """Check if the system is properly set up."""
    print("Checking system setup...")
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Please copy .env.example to .env and add your API key")
        return False
    
    # Check for API key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ API key not configured")
        print("   Please add your API key to the .env file")
        return False
    
    print("✓ Environment configured")
    return True


def generate_sample_data():
    """Generate sample data if not exists."""
    data_dir = Path("data/sample_claims")
    
    if data_dir.exists() and list(data_dir.glob("*.json")):
        print("✓ Sample data already exists")
        return True
    
    print("Generating sample data...")
    try:
        generator = SyntheticDataGenerator()
        generator.generate_all(num_claims=5, num_policies=3)
        print("✓ Sample data generated")
        return True
    except Exception as e:
        print(f"❌ Failed to generate sample data: {e}")
        return False


def run_test_claim():
    """Run a test claim through the system."""
    print("\n" + "="*80)
    print("RUNNING TEST CLAIM")
    print("="*80 + "\n")
    
    # Load sample claim and policy
    claims_dir = Path("data/sample_claims")
    policies_dir = Path("data/sample_policies")
    
    claim_files = list(claims_dir.glob("*.json"))
    policy_files = list(policies_dir.glob("*.json"))
    
    if not claim_files or not policy_files:
        print("❌ No sample data found")
        return False
    
    # Load first claim and policy
    with open(claim_files[0]) as f:
        claim_data = json.load(f)
    
    with open(policy_files[0]) as f:
        policy_data = json.load(f)
    
    print(f"Processing Claim: {claim_data['claim_id']}")
    print(f"Claimant: {claim_data['claimant_name']}")
    print(f"Total Billed: ${claim_data['total_billed_amount']:,.2f}")
    print(f"Policy: {policy_data['policy_number']}")
    print("\nProcessing... (this may take 30-60 seconds)\n")
    
    try:
        # Initialize orchestrator and process
        orchestrator = OrchestratorAgent()
        
        results = orchestrator.process({
            "claim_document": claim_data,
            "policy_data": policy_data,
            "medical_report": "Patient presents with symptoms consistent with diagnosis."
        })
        
        # Display results
        if results.get("status") == "completed":
            final_output = results["final_output"]
            
            print("="*80)
            print("RESULTS")
            print("="*80)
            print(f"\nDecision: {final_output['decision']['type'].upper()}")
            print(f"Confidence: {final_output['decision']['confidence_score']:.2%}")
            print(f"\nFinancial Summary:")
            print(f"  Total Billed:           ${final_output['financial']['total_billed']:>10,.2f}")
            print(f"  Approved Amount:        ${final_output['financial']['approved_amount']:>10,.2f}")
            print(f"  Insurance Payment:      ${final_output['financial']['insurance_payment']:>10,.2f}")
            print(f"  Patient Responsibility: ${final_output['financial']['patient_responsibility']:>10,.2f}")
            
            print(f"\nProcessing Time: {results['total_processing_time']:.2f} seconds")
            
            print("\n" + "="*80)
            print("✓ Test completed successfully!")
            print("="*80)
            
            return True
        else:
            print(f"❌ Processing failed: {results.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main quick start function."""
    print("\n" + "="*80)
    print("AI INSURANCE CLAIM PROCESSING - QUICK START")
    print("="*80 + "\n")
    
    # Step 1: Check setup
    if not check_setup():
        print("\n❌ Setup incomplete. Please follow the instructions above.")
        return
    
    # Step 2: Generate sample data
    if not generate_sample_data():
        print("\n❌ Failed to generate sample data.")
        return
    
    # Step 3: Run test claim
    if not run_test_claim():
        print("\n❌ Test claim processing failed.")
        return
    
    # Success message
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Run the Streamlit app:")
    print("   streamlit run app.py")
    print("\n2. Open your browser to http://localhost:8501")
    print("\n3. Try processing different claims and policies")
    print("\n4. Review the documentation:")
    print("   - README.md - Overview and features")
    print("   - SETUP_GUIDE.md - Detailed setup instructions")
    print("   - USAGE_EXAMPLES.md - Code examples and use cases")
    print("   - architecture.md - System architecture details")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
