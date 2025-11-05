# Getting Started with AI Insurance Claim Processing

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### Step 2: Configure API Key

```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your API key
# For OpenAI:
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# OR for Anthropic:
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Run Quick Start

```bash
# This will test the system and generate sample data
python quickstart.py
```

### Step 4: Launch Web App

```bash
# Start Streamlit application
streamlit run app.py
```

Open your browser to **http://localhost:8501**

---

## 📋 What You'll See

### 1. Home Screen
- Configuration status (API key check)
- Two tabs: "Use Sample Data" and "Upload Files"

### 2. Sample Data Tab
- Dropdown to select sample claims
- Dropdown to select sample policies
- Text area for optional medical report
- "Process Claim" button

### 3. Results Screen
- **Decision Status**: Approved/Rejected/Needs Review
- **Financial Metrics**: Billed, Approved, Insurance Payment, Your Responsibility
- **Four Tabs**:
  - Summary: Overview and explanation
  - Financial Details: Breakdown with charts
  - Validation: All checks performed
  - Full Report: Complete text report with download

---

## 🎯 Try These Examples

### Example 1: Simple Approved Claim

1. Select any sample claim
2. Select matching policy (same policy number)
3. Click "Process Claim"
4. Expected: **APPROVED** with financial breakdown

### Example 2: Upload Custom Claim

1. Go to "Upload Files" tab
2. Upload your JSON claim file
3. Upload your JSON policy file
4. Click "Process Uploaded Claim"

### Example 3: Add Medical Report

1. Select sample claim
2. In medical report field, add:
   ```
   Patient presents with acute lower back pain.
   Examination reveals muscle spasm.
   Treatment: Office visit and pain management.
   Medical necessity confirmed.
   ```
3. Process and see enhanced explanation

---

## 📁 Project Structure Overview

```
automated-insurance-claim-processing/
│
├── app.py                    # 👈 START HERE - Streamlit app
├── quickstart.py             # Quick test script
├── data_generator.py         # Generate sample data
│
├── agents/                   # Multi-agent system
│   ├── orchestrator.py       # Main coordinator
│   ├── extraction_agent.py   # Extract data
│   ├── validation_agent.py   # Validate claims
│   ├── decision_agent.py     # Make decisions
│   └── explanation_agent.py  # Generate reports
│
├── models/                   # Data models
│   ├── claim.py
│   ├── policy.py
│   └── decision.py
│
├── utils/                    # Utilities
│   ├── llm_provider.py       # LLM integration
│   ├── document_parser.py    # Parse documents
│   └── report_generator.py   # Generate PDFs
│
├── data/                     # Sample data (auto-generated)
│   ├── sample_claims/
│   ├── sample_policies/
│   └── sample_medical_reports/
│
└── tests/                    # Unit tests
    └── test_agents.py
```

---

## 🔧 Common Tasks

### Generate More Sample Data

```bash
python data_generator.py
```

This creates:
- 10 sample claims
- 5 sample policies
- 10 medical reports

### Run Tests

```bash
pytest tests/test_agents.py -v
```

### Process Claims Programmatically

```python
from agents.orchestrator import OrchestratorAgent
import json

# Load data
with open('data/sample_claims/CLM-2024-001.json') as f:
    claim = json.load(f)

with open('data/sample_policies/POL-10000.json') as f:
    policy = json.load(f)

# Process
orchestrator = OrchestratorAgent()
result = orchestrator.process({
    "claim_document": claim,
    "policy_data": policy
})

# View decision
print(result['final_output']['decision']['type'])
```

### Change LLM Model

Edit `.env`:

```bash
# Use GPT-3.5 (faster, cheaper)
OPENAI_MODEL=gpt-3.5-turbo

# Use GPT-4 (more accurate)
OPENAI_MODEL=gpt-4-turbo-preview

# Use Claude Sonnet (balanced)
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

---

## 🎓 Understanding the System

### How It Works

1. **Extraction Agent** reads your claim and extracts structured data
2. **Validation Agent** checks against policy rules
3. **Decision Agent** generates approval/rejection recommendation
4. **Explanation Agent** creates human-readable report

### Decision Types

- **APPROVED**: Claim meets all requirements
- **REJECTED**: Critical issues found
- **NEEDS_REVIEW**: Requires manual review
- **PARTIAL_APPROVAL**: Some items approved

### Confidence Scores

- **>95%**: High confidence, can auto-approve
- **85-95%**: Good confidence, minimal review
- **70-85%**: Medium confidence, needs review
- **<70%**: Low confidence, manual review required

---

## 📊 Sample Data Explained

### Claim JSON Structure

```json
{
  "claim_id": "CLM-2024-001",
  "policy_number": "POL-12345",
  "claimant_name": "John Doe",
  "total_billed_amount": 150.00,
  "primary_diagnosis": "M54.5",  // ICD-10 code
  "claim_items": [
    {
      "procedure_code": "99213",  // CPT code
      "procedure_description": "Office visit",
      "billed_amount": 150.00
    }
  ]
}
```

### Policy JSON Structure

```json
{
  "policy_number": "POL-12345",
  "annual_deductible": 1000.00,
  "deductible_met": 500.00,
  "coverages": [
    {
      "category": "outpatient",
      "copay_amount": 30.00,
      "coinsurance_percentage": 20
    }
  ]
}
```

---

## 🐛 Troubleshooting

### "API key not configured"

**Solution**: 
1. Make sure `.env` file exists
2. Check API key is correct
3. Restart the application

### "No sample data found"

**Solution**:
```bash
python data_generator.py
```

### "Module not found"

**Solution**:
```bash
pip install -r requirements.txt
```

### Processing takes too long

**Causes**:
- Large documents (>5 pages)
- Complex claims (many items)
- API rate limits

**Solutions**:
- Use GPT-3.5 for faster processing
- Break large documents into smaller parts
- Check API rate limits

### Low confidence scores

**Causes**:
- Missing information
- Ambiguous data
- Complex medical cases

**Solutions**:
- Provide complete information
- Add medical reports
- Use structured JSON format

---

## 💡 Tips for Best Results

### 1. Data Quality
- Use complete, accurate data
- Include all required fields
- Provide medical reports when available

### 2. Cost Optimization
- Use GPT-3.5 for simple claims
- Use GPT-4 for complex cases
- Cache policy documents

### 3. Accuracy
- Review low-confidence decisions
- Provide feedback for improvement
- Keep medical reports concise

### 4. Performance
- Process claims in batches
- Use async processing for high volume
- Monitor API usage

---

## 📚 Next Steps

### Learn More

1. **README.md** - Project overview
2. **SETUP_GUIDE.md** - Detailed setup
3. **USAGE_EXAMPLES.md** - Code examples
4. **architecture.md** - System design
5. **PROJECT_SUMMARY.md** - Complete summary

### Customize

1. **Add validation rules** in `agents/validation_agent.py`
2. **Modify prompts** in each agent's `get_system_prompt()`
3. **Add new agents** by extending `BaseAgent`
4. **Customize UI** in `app.py`

### Integrate

1. **API Integration** - Create REST API with Flask/FastAPI
2. **Database** - Add PostgreSQL for persistence
3. **Queue System** - Use Celery for async processing
4. **Monitoring** - Add logging and metrics

### Deploy

1. **Streamlit Cloud** - Free hosting for Streamlit apps
2. **Docker** - Containerize the application
3. **AWS/Azure/GCP** - Cloud deployment
4. **On-Premise** - Internal server deployment

---

## 🆘 Getting Help

### Documentation
- All `.md` files in project root
- Inline code comments
- Docstrings in all functions

### Common Questions

**Q: Can I use this in production?**
A: Yes, but ensure HIPAA compliance and proper security measures.

**Q: What's the cost per claim?**
A: $0.05-$0.60 depending on model and complexity.

**Q: Can it handle scanned documents?**
A: Not yet, but OCR integration is planned.

**Q: Is it HIPAA compliant?**
A: The code follows best practices, but full compliance requires proper deployment and policies.

**Q: Can I train custom models?**
A: Yes, you can fine-tune models on your historical data.

---

## ✅ Checklist

Before going live:

- [ ] API keys configured
- [ ] Sample data generated
- [ ] Quick start test passed
- [ ] Web app launches successfully
- [ ] Can process sample claims
- [ ] Results display correctly
- [ ] Can download reports
- [ ] Understand decision types
- [ ] Read all documentation
- [ ] Tested with your own data

---

## 🎉 Success!

You're now ready to use the AI Insurance Claim Processing system!

**What you can do:**
✓ Process insurance claims automatically
✓ Validate against policy rules
✓ Generate approval/rejection decisions
✓ Create detailed reports
✓ Save time and reduce errors

**Start processing claims now:**
```bash
streamlit run app.py
```

---

**Need help?** Check the documentation or review the code comments.

**Want to contribute?** Follow the contribution guidelines in README.md.

**Have feedback?** We'd love to hear from you!
