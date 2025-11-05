# Setup Guide

## Quick Start

Follow these steps to get the AI Insurance Claim Processing system up and running.

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key OR Anthropic API key

### Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and add your API key:

For OpenAI:
```
MODEL_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

For Anthropic:
```
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-opus-20240229
```

### Step 3: Generate Sample Data

Generate synthetic claims, policies, and medical reports for testing:

```bash
python data_generator.py
```

This will create:
- 10 sample insurance claims
- 5 sample insurance policies
- 10 medical reports

All data will be saved in the `data/` directory.

### Step 4: Run the Application

Start the Streamlit web application:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Using the Application

### Processing a Claim

1. **Select Sample Data Tab**
   - Choose a sample claim from the dropdown
   - Choose a matching policy
   - Optionally add a medical report
   - Click "Process Claim"

2. **Upload Files Tab**
   - Upload your own claim JSON file
   - Upload your own policy JSON file
   - Optionally add a medical report
   - Click "Process Uploaded Claim"

3. **View Results**
   - Review the decision (Approved/Rejected/Needs Review)
   - Check financial breakdown
   - Read detailed explanation
   - View validation results
   - Download the full report

## Testing the Agents Individually

You can test individual agents programmatically:

```python
from agents.extraction_agent import ExtractionAgent
from agents.validation_agent import ValidationAgent
from agents.decision_agent import DecisionAgent
from agents.explanation_agent import ExplanationAgent

# Test extraction
extraction_agent = ExtractionAgent()
result = extraction_agent.process({
    "claim_document": claim_data,
    "medical_report": report_text
})

# Test validation
validation_agent = ValidationAgent()
result = validation_agent.process({
    "claim_data": extracted_data,
    "policy_data": policy_data
})

# And so on...
```

## Troubleshooting

### API Key Issues

**Problem**: "OPENAI_API_KEY not found in environment variables"

**Solution**: 
1. Make sure you created the `.env` file
2. Verify your API key is correct
3. Restart the application after adding the key

### Import Errors

**Problem**: "ModuleNotFoundError: No module named 'streamlit'"

**Solution**:
```bash
pip install -r requirements.txt
```

### No Sample Data

**Problem**: "No sample data found"

**Solution**:
```bash
python data_generator.py
```

### Port Already in Use

**Problem**: "Port 8501 is already in use"

**Solution**:
```bash
streamlit run app.py --server.port 8502
```

## Advanced Configuration

### Changing LLM Models

Edit `.env` to use different models:

```
# For GPT-3.5 (faster, cheaper)
OPENAI_MODEL=gpt-3.5-turbo

# For GPT-4 (more accurate)
OPENAI_MODEL=gpt-4-turbo-preview

# For Claude 3 Sonnet (balanced)
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# For Claude 3 Opus (most capable)
ANTHROPIC_MODEL=claude-3-opus-20240229
```

### Adjusting Confidence Thresholds

Edit `.env`:

```
CONFIDENCE_THRESHOLD=0.85
AUTO_APPROVE_THRESHOLD=0.95
MANUAL_REVIEW_THRESHOLD=0.70
```

### Enabling Debug Logging

Edit `.env`:

```
LOG_LEVEL=DEBUG
```

## Production Deployment

### Security Considerations

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use environment variables** in production instead of `.env` file
3. **Implement authentication** for the Streamlit app
4. **Enable HTTPS** for secure communication
5. **Sanitize user inputs** to prevent injection attacks

### Scaling

For high-volume processing:

1. **Use async processing** with message queues (e.g., Celery + Redis)
2. **Deploy multiple agent instances** for parallel processing
3. **Cache policy documents** to reduce LLM calls
4. **Implement rate limiting** to manage API costs

### Monitoring

Set up monitoring for:

- API usage and costs
- Processing times
- Error rates
- Decision accuracy

## API Cost Estimates

Approximate costs per claim (as of 2024):

- **GPT-4 Turbo**: $0.30 - $0.50 per claim
- **GPT-3.5 Turbo**: $0.05 - $0.10 per claim
- **Claude 3 Opus**: $0.40 - $0.60 per claim
- **Claude 3 Sonnet**: $0.10 - $0.20 per claim

Costs vary based on:
- Document length
- Complexity of claim
- Number of validation checks
- Report detail level

## Support

For issues or questions:

1. Check the [README.md](README.md) for general information
2. Review [architecture.md](architecture.md) for system design
3. Check existing issues on GitHub
4. Create a new issue with detailed information

## Next Steps

1. **Customize the agents** - Modify prompts and logic for your use case
2. **Add more validation rules** - Implement domain-specific checks
3. **Integrate with existing systems** - Connect to EHR, billing systems
4. **Train custom models** - Use historical data for better accuracy
5. **Implement feedback loop** - Learn from manual reviews

## License

MIT License - See LICENSE file for details
