# Usage Examples

This document provides practical examples of using the AI Insurance Claim Processing system.

## Example 1: Processing a Simple Claim

### Input: Claim Data

```json
{
  "claim_id": "CLM-2024-001",
  "policy_number": "POL-12345",
  "claimant_name": "John Doe",
  "claimant_dob": "1980-01-15",
  "claimant_id": "MEM-67890",
  "claim_date": "2024-01-20T10:00:00",
  "service_start_date": "2024-01-15T09:00:00",
  "service_end_date": "2024-01-15T09:30:00",
  "primary_diagnosis": "M54.5",
  "secondary_diagnoses": [],
  "claim_items": [
    {
      "procedure_code": "99213",
      "procedure_description": "Office visit, established patient, level 3",
      "diagnosis_code": "M54.5",
      "service_date": "2024-01-15T09:00:00",
      "provider_name": "Dr. Jane Smith",
      "billed_amount": 150.00,
      "units": 1
    }
  ],
  "total_billed_amount": 150.00,
  "provider_name": "Dr. Jane Smith",
  "provider_npi": "1234567890",
  "status": "pending"
}
```

### Input: Policy Data

```json
{
  "policy_number": "POL-12345",
  "policy_holder_name": "John Doe",
  "effective_date": "2024-01-01T00:00:00",
  "expiration_date": "2024-12-31T23:59:59",
  "annual_deductible": 1000.00,
  "deductible_met": 500.00,
  "out_of_pocket_max": 5000.00,
  "out_of_pocket_met": 1200.00,
  "policy_type": "PPO",
  "network_type": "In-Network",
  "coverages": [
    {
      "category": "outpatient",
      "annual_limit": 50000,
      "copay_amount": 30.00,
      "coinsurance_percentage": 20,
      "deductible_applies": true,
      "requires_preauth": false
    }
  ],
  "exclusions": []
}
```

### Expected Output

```
Decision: APPROVED
Confidence: 95%

Financial Breakdown:
- Total Billed: $150.00
- Deductible Applied: $150.00
- Copay Applied: $30.00
- Coinsurance Applied: $0.00
- Patient Responsibility: $180.00
- Insurance Payment: $0.00

Reasoning: The claim meets all policy requirements. The service is covered under 
the outpatient category. The full amount applies to the remaining deductible.
```

## Example 2: Claim with Missing Information

### Input: Incomplete Claim

```json
{
  "claim_id": "CLM-2024-002",
  "policy_number": "POL-12345",
  "claimant_name": "Jane Smith",
  "total_billed_amount": 500.00,
  "provider_name": "City Medical Center"
}
```

### Expected Output

```
Decision: PENDING_INFORMATION
Confidence: 60%

Missing Information:
- Claimant date of birth
- Service dates
- Diagnosis codes
- Procedure codes
- Provider NPI

Next Steps:
1. Provide complete claimant information
2. Include service dates and diagnosis codes
3. Add detailed procedure information
4. Resubmit claim once complete
```

## Example 3: Claim Exceeding Coverage Limits

### Input: High-Value Claim

```json
{
  "claim_id": "CLM-2024-003",
  "policy_number": "POL-12345",
  "claimant_name": "John Doe",
  "total_billed_amount": 75000.00,
  "primary_diagnosis": "I21.9",
  "claim_items": [
    {
      "procedure_code": "33533",
      "procedure_description": "Coronary artery bypass",
      "billed_amount": 75000.00,
      "units": 1
    }
  ]
}
```

### Expected Output

```
Decision: NEEDS_REVIEW
Confidence: 70%

Flags:
- HIGH_VALUE_CLAIM
- MANUAL_REVIEW_REQUIRED

Reasoning: This claim exceeds the automatic approval threshold due to its high 
value. The procedure requires pre-authorization and manual review by a claims 
specialist. All documentation should be reviewed for medical necessity.

Next Steps:
1. Claim will be reviewed by specialist within 5-7 business days
2. Additional documentation may be requested
3. Pre-authorization verification required
```

## Example 4: Using the Python API

### Basic Usage

```python
from agents.orchestrator import OrchestratorAgent
import json

# Load claim and policy data
with open('data/sample_claims/CLM-2024-001.json') as f:
    claim_data = json.load(f)

with open('data/sample_policies/POL-12345.json') as f:
    policy_data = json.load(f)

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Process claim
results = orchestrator.process({
    "claim_document": claim_data,
    "policy_data": policy_data,
    "medical_report": "Patient presents with lower back pain..."
})

# Access results
final_output = results['final_output']
print(f"Decision: {final_output['decision']['type']}")
print(f"Confidence: {final_output['decision']['confidence_score']:.2%}")
print(f"Patient Responsibility: ${final_output['financial']['patient_responsibility']:.2f}")
```

### Processing Multiple Claims

```python
from agents.orchestrator import OrchestratorAgent
from pathlib import Path
import json

orchestrator = OrchestratorAgent()

# Process all claims in a directory
claims_dir = Path('data/sample_claims')
results_list = []

for claim_file in claims_dir.glob('*.json'):
    with open(claim_file) as f:
        claim_data = json.load(f)
    
    # Find matching policy
    policy_file = Path(f'data/sample_policies/{claim_data["policy_number"]}.json')
    with open(policy_file) as f:
        policy_data = json.load(f)
    
    # Process
    result = orchestrator.process({
        "claim_document": claim_data,
        "policy_data": policy_data
    })
    
    results_list.append(result)
    print(f"Processed {claim_data['claim_id']}: {result['final_output']['decision']['type']}")

# Summary statistics
approved = sum(1 for r in results_list if r['final_output']['decision']['type'] == 'approved')
rejected = sum(1 for r in results_list if r['final_output']['decision']['type'] == 'rejected')
review = sum(1 for r in results_list if r['final_output']['decision']['type'] == 'needs_review')

print(f"\nSummary: {approved} approved, {rejected} rejected, {review} need review")
```

### Generating PDF Reports

```python
from agents.orchestrator import OrchestratorAgent
from utils.report_generator import ReportGenerator
from models.claim import Claim
from models.policy import Policy
from models.decision import Decision
import json

# Process claim
orchestrator = OrchestratorAgent()
results = orchestrator.process({
    "claim_document": claim_data,
    "policy_data": policy_data
})

# Create model objects
claim = orchestrator.create_claim_object(
    results['extraction']['extracted_data']
)
policy = Policy(**policy_data)
decision = orchestrator.create_decision_object(
    claim.claim_id,
    results['decision'],
    results['validation']
)

# Generate PDF report
report_gen = ReportGenerator()
pdf_path = f"reports/{claim.claim_id}_report.pdf"
report_gen.generate_claim_report(claim, policy, decision, pdf_path)
print(f"Report saved to {pdf_path}")
```

## Example 5: Custom Validation Rules

### Adding Custom Validation

```python
from agents.validation_agent import ValidationAgent

class CustomValidationAgent(ValidationAgent):
    
    def process(self, input_data):
        # Call parent process
        result = super().process(input_data)
        
        # Add custom validation
        claim_data = input_data.get("claim_data", {})
        
        # Example: Check if claim is from preferred provider
        custom_check = self._check_preferred_provider(claim_data)
        result["validation_results"].append(custom_check)
        
        return result
    
    def _check_preferred_provider(self, claim_data):
        """Custom check for preferred provider."""
        preferred_providers = ["Dr. Jane Smith", "Dr. John Johnson"]
        provider = claim_data.get("provider_name", "")
        
        is_preferred = provider in preferred_providers
        
        return {
            "check_name": "Preferred Provider Check",
            "passed": is_preferred,
            "severity": "info",
            "message": "Provider is in preferred network" if is_preferred else "Provider not in preferred network",
            "details": {"provider": provider}
        }

# Use custom agent
custom_agent = CustomValidationAgent()
result = custom_agent.process({
    "claim_data": claim_data,
    "policy_data": policy_data
})
```

## Example 6: Batch Processing with Progress Tracking

```python
from agents.orchestrator import OrchestratorAgent
from pathlib import Path
import json
from tqdm import tqdm

def batch_process_claims(claims_dir, policies_dir, output_dir):
    """Process multiple claims with progress tracking."""
    orchestrator = OrchestratorAgent()
    
    claim_files = list(Path(claims_dir).glob('*.json'))
    results = []
    
    # Process with progress bar
    for claim_file in tqdm(claim_files, desc="Processing claims"):
        try:
            # Load claim
            with open(claim_file) as f:
                claim_data = json.load(f)
            
            # Load policy
            policy_file = Path(policies_dir) / f"{claim_data['policy_number']}.json"
            with open(policy_file) as f:
                policy_data = json.load(f)
            
            # Process
            result = orchestrator.process({
                "claim_document": claim_data,
                "policy_data": policy_data
            })
            
            results.append(result)
            
            # Save individual result
            output_file = Path(output_dir) / f"{claim_data['claim_id']}_result.json"
            with open(output_file, 'w') as f:
                json.dump(result['final_output'], f, indent=2)
        
        except Exception as e:
            print(f"Error processing {claim_file}: {e}")
    
    return results

# Run batch processing
results = batch_process_claims(
    'data/sample_claims',
    'data/sample_policies',
    'data/generated/results'
)
```

## Example 7: Integration with External Systems

### Webhook Integration

```python
from flask import Flask, request, jsonify
from agents.orchestrator import OrchestratorAgent

app = Flask(__name__)
orchestrator = OrchestratorAgent()

@app.route('/api/process-claim', methods=['POST'])
def process_claim_api():
    """API endpoint for claim processing."""
    try:
        data = request.json
        
        # Process claim
        result = orchestrator.process({
            "claim_document": data['claim'],
            "policy_data": data['policy'],
            "medical_report": data.get('medical_report', '')
        })
        
        # Return simplified response
        return jsonify({
            "success": True,
            "claim_id": result['final_output']['claim_id'],
            "decision": result['final_output']['decision']['type'],
            "confidence": result['final_output']['decision']['confidence_score'],
            "financial": result['final_output']['financial']
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5000)
```

## Tips and Best Practices

1. **Always validate input data** before processing
2. **Handle errors gracefully** with try-except blocks
3. **Log all processing steps** for audit trails
4. **Cache policy documents** to reduce API calls
5. **Implement rate limiting** to manage costs
6. **Monitor confidence scores** to improve accuracy
7. **Review manual review cases** to train the system
8. **Keep medical reports concise** to reduce token usage
9. **Use batch processing** for high volumes
10. **Test with edge cases** before production use
