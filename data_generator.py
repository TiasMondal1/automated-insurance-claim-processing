"""Generate synthetic data for testing the claim processing system."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class SyntheticDataGenerator:
    """Generate synthetic insurance claims, policies, and medical reports."""
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "sample_claims").mkdir(exist_ok=True)
        (self.output_dir / "sample_policies").mkdir(exist_ok=True)
        (self.output_dir / "sample_medical_reports").mkdir(exist_ok=True)
        (self.output_dir / "generated").mkdir(exist_ok=True)
    
    def generate_all(self, num_claims: int = 10, num_policies: int = 5):
        """Generate all synthetic data."""
        print("Generating synthetic data...")
        
        # Generate policies first
        policies = self.generate_policies(num_policies)
        print(f"✓ Generated {len(policies)} policies")
        
        # Generate claims
        claims = self.generate_claims(num_claims, policies)
        print(f"✓ Generated {len(claims)} claims")
        
        # Generate medical reports
        medical_reports = self.generate_medical_reports(claims)
        print(f"✓ Generated {len(medical_reports)} medical reports")
        
        print(f"\nData saved to: {self.output_dir.absolute()}")
        return policies, claims, medical_reports
    
    def generate_policies(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate synthetic insurance policies."""
        policy_types = ["PPO", "HMO", "EPO", "POS"]
        
        policies = []
        for i in range(count):
            policy_number = f"POL-{10000 + i}"
            
            policy = {
                "policy_number": policy_number,
                "policy_holder_name": self._random_name(),
                "effective_date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                "expiration_date": (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat(),
                "annual_deductible": random.choice([500, 1000, 1500, 2000, 2500, 3000]),
                "deductible_met": random.uniform(0, 1500),
                "out_of_pocket_max": random.choice([5000, 6000, 7000, 8000, 10000]),
                "out_of_pocket_met": random.uniform(0, 3000),
                "policy_type": random.choice(policy_types),
                "network_type": "In-Network",
                "requires_referral": random.choice([True, False]),
                "emergency_coverage": True,
                "coverages": [
                    {
                        "category": "outpatient",
                        "annual_limit": 50000,
                        "per_visit_limit": 5000,
                        "copay_amount": random.choice([20, 30, 40, 50]),
                        "coinsurance_percentage": random.choice([10, 20, 30]),
                        "deductible_applies": True,
                        "requires_preauth": False,
                        "covered_procedures": ["99213", "99214", "99215"]
                    },
                    {
                        "category": "inpatient",
                        "annual_limit": 100000,
                        "per_visit_limit": None,
                        "copay_amount": 0,
                        "coinsurance_percentage": 20,
                        "deductible_applies": True,
                        "requires_preauth": True,
                        "covered_procedures": []
                    },
                    {
                        "category": "emergency",
                        "annual_limit": None,
                        "per_visit_limit": None,
                        "copay_amount": 100,
                        "coinsurance_percentage": 0,
                        "deductible_applies": False,
                        "requires_preauth": False,
                        "covered_procedures": []
                    }
                ],
                "exclusions": [
                    {
                        "exclusion_type": "cosmetic",
                        "description": "Cosmetic procedures not medically necessary",
                        "excluded_codes": ["15780", "15781", "15782"]
                    }
                ],
                "metadata": {}
            }
            
            policies.append(policy)
            
            # Save individual policy
            output_file = self.output_dir / "sample_policies" / f"{policy_number}.json"
            with open(output_file, 'w') as f:
                json.dump(policy, f, indent=2)
        
        return policies
    
    def generate_claims(self, count: int = 10, policies: List[Dict] = None) -> List[Dict[str, Any]]:
        """Generate synthetic insurance claims."""
        if not policies:
            policies = self.generate_policies(5)
        
        diagnosis_codes = [
            ("M54.5", "Low back pain"),
            ("J06.9", "Acute upper respiratory infection"),
            ("E11.9", "Type 2 diabetes mellitus"),
            ("I10", "Essential hypertension"),
            ("M25.511", "Pain in right shoulder"),
            ("K21.9", "Gastro-esophageal reflux disease"),
            ("F41.9", "Anxiety disorder"),
            ("M79.3", "Panniculitis"),
        ]
        
        procedure_codes = [
            ("99213", "Office visit, established patient, level 3", 150),
            ("99214", "Office visit, established patient, level 4", 200),
            ("99215", "Office visit, established patient, level 5", 250),
            ("73030", "Shoulder X-ray", 120),
            ("80053", "Comprehensive metabolic panel", 85),
            ("85025", "Complete blood count", 45),
            ("93000", "Electrocardiogram", 95),
        ]
        
        claims = []
        for i in range(count):
            policy = random.choice(policies)
            claim_id = f"CLM-2024-{1000 + i}"
            
            service_date = datetime.now() - timedelta(days=random.randint(1, 60))
            diagnosis = random.choice(diagnosis_codes)
            
            # Generate 1-3 claim items
            num_items = random.randint(1, 3)
            claim_items = []
            total_billed = 0
            
            for _ in range(num_items):
                proc = random.choice(procedure_codes)
                units = random.randint(1, 2)
                amount = proc[2] * units
                total_billed += amount
                
                claim_items.append({
                    "procedure_code": proc[0],
                    "procedure_description": proc[1],
                    "diagnosis_code": diagnosis[0],
                    "service_date": service_date.isoformat(),
                    "provider_name": self._random_provider(),
                    "billed_amount": amount,
                    "units": units
                })
            
            claim = {
                "claim_id": claim_id,
                "policy_number": policy["policy_number"],
                "claimant_name": policy["policy_holder_name"],
                "claimant_dob": (datetime.now() - timedelta(days=random.randint(18*365, 70*365))).strftime("%Y-%m-%d"),
                "claimant_id": f"MEM-{random.randint(10000, 99999)}",
                "claim_date": datetime.now().isoformat(),
                "service_start_date": service_date.isoformat(),
                "service_end_date": service_date.isoformat(),
                "primary_diagnosis": diagnosis[0],
                "secondary_diagnoses": [],
                "claim_items": claim_items,
                "total_billed_amount": total_billed,
                "provider_name": claim_items[0]["provider_name"],
                "provider_npi": f"{random.randint(1000000000, 9999999999)}",
                "facility_name": random.choice([None, "City Medical Center", "Regional Hospital"]),
                "status": "pending",
                "metadata": {}
            }
            
            claims.append(claim)
            
            # Save individual claim
            output_file = self.output_dir / "sample_claims" / f"{claim_id}.json"
            with open(output_file, 'w') as f:
                json.dump(claim, f, indent=2)
        
        return claims
    
    def generate_medical_reports(self, claims: List[Dict]) -> List[Dict[str, Any]]:
        """Generate synthetic medical reports."""
        reports = []
        
        for claim in claims:
            claim_id = claim["claim_id"]
            diagnosis = claim["primary_diagnosis"]
            
            # Generate medical report text
            report_text = f"""MEDICAL REPORT

Patient: {claim['claimant_name']}
Date of Service: {claim['service_start_date'][:10]}
Provider: {claim['provider_name']}

CHIEF COMPLAINT:
Patient presents with symptoms related to diagnosis code {diagnosis}.

HISTORY OF PRESENT ILLNESS:
Patient reports onset of symptoms approximately {random.randint(1, 14)} days ago. 
Symptoms have been {random.choice(['gradually worsening', 'stable', 'improving with treatment'])}.

PHYSICAL EXAMINATION:
Vital signs stable. Examination findings consistent with diagnosis.

ASSESSMENT:
Primary diagnosis: {diagnosis}
{random.choice(['Condition is stable', 'Condition requires continued monitoring', 'Patient responding well to treatment'])}.

PLAN:
1. Continue current treatment plan
2. {random.choice(['Follow-up in 2 weeks', 'Follow-up as needed', 'Return if symptoms worsen'])}
3. {random.choice(['Prescribed medication', 'Ordered diagnostic tests', 'Referred to specialist'])}

MEDICAL NECESSITY:
The services provided were medically necessary for the diagnosis and treatment of the patient's condition.

Provider Signature: {claim['provider_name']}
NPI: {claim['provider_npi']}
Date: {claim['service_start_date'][:10]}
"""
            
            report = {
                "claim_id": claim_id,
                "report_text": report_text
            }
            
            reports.append(report)
            
            # Save individual report
            output_file = self.output_dir / "sample_medical_reports" / f"{claim_id}_report.txt"
            with open(output_file, 'w') as f:
                f.write(report_text)
        
        return reports
    
    def _random_name(self) -> str:
        """Generate random name."""
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", "William", "Mary"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _random_provider(self) -> str:
        """Generate random provider name."""
        titles = ["Dr.", "Dr.", "Dr."]
        first_names = ["James", "Jennifer", "Michael", "Sarah", "David", "Emily"]
        last_names = ["Anderson", "Thompson", "Wilson", "Moore", "Taylor", "Lee"]
        return f"{random.choice(titles)} {random.choice(first_names)} {random.choice(last_names)}"


if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    generator.generate_all(num_claims=10, num_policies=5)
    print("\n✓ Synthetic data generation complete!")
