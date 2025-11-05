# AI-Powered Automated Insurance Claim Processing System

## Overview
A multi-agent AI system that automates healthcare insurance claim processing using advanced language models and intelligent agents.

## Architecture

### Multi-Agent System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│              (User Interface & Visualization)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestrator Agent                          │
│         (Coordinates all agents and workflow)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Extraction  │ │  Validation  │ │   Decision   │ │ Explanation  │
│    Agent     │ │    Agent     │ │    Agent     │ │    Agent     │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
│              │ │              │ │              │ │              │
│ - Extract    │ │ - Validate   │ │ - Approve/   │ │ - Generate   │
│   claim data │ │   against    │ │   Reject     │ │   detailed   │
│ - Parse      │ │   policies   │ │ - Calculate  │ │   reports    │
│   medical    │ │ - Check      │ │   coverage   │ │ - Provide    │
│   reports    │ │   coverage   │ │ - Flag       │ │   next steps │
│ - Structure  │ │ - Identify   │ │   issues     │ │ - Explain    │
│   data       │ │   missing    │ │              │ │   decisions  │
│              │ │   info       │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Features

- **Intelligent Document Extraction**: Automatically extracts information from claim forms and medical reports
- **Policy Validation**: Validates claims against policy rules and coverage criteria
- **Automated Decision Making**: Generates approval/rejection recommendations with confidence scores
- **Detailed Explanations**: Provides clear explanations and next steps for claimants
- **Multi-Format Support**: Handles JSON, text, and PDF documents
- **Real-time Processing**: Streamlit interface for interactive claim processing

## Technology Stack

- **Frontend**: Streamlit
- **AI Models**: OpenAI GPT-4 / Anthropic Claude (configurable)
- **Agent Framework**: LangChain / Custom implementation
- **Data Processing**: Pandas, PyPDF2
- **Report Generation**: ReportLab (PDF generation)

## Installation

1. Clone the repository:
```bash
cd automated-insurance-claim-processing
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Configuration

Create a `.env` file with the following:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
MODEL_PROVIDER=openai  # or anthropic
MODEL_NAME=gpt-4-turbo-preview
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Upload claim documents through the web interface
3. Review the automated processing results
4. Download detailed reports

## Project Structure

```
automated-insurance-claim-processing/
├── app.py                          # Streamlit frontend
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── README.md                       # This file
├── architecture.md                 # Detailed architecture documentation
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py            # Main orchestrator agent
│   ├── extraction_agent.py        # Document extraction agent
│   ├── validation_agent.py        # Policy validation agent
│   ├── decision_agent.py          # Decision-making agent
│   └── explanation_agent.py       # Explanation generation agent
├── models/
│   ├── __init__.py
│   ├── claim.py                   # Claim data models
│   ├── policy.py                  # Policy data models
│   └── decision.py                # Decision data models
├── utils/
│   ├── __init__.py
│   ├── llm_provider.py            # LLM provider abstraction
│   ├── document_parser.py         # Document parsing utilities
│   └── report_generator.py        # PDF report generation
├── data/
│   ├── sample_claims/             # Sample claim forms
│   ├── sample_policies/           # Sample policy documents
│   ├── sample_medical_reports/    # Sample medical reports
│   └── generated/                 # Generated synthetic data
└── tests/
    ├── __init__.py
    └── test_agents.py             # Unit tests
```

## Data Requirements

### Input Data
1. **Claim Forms** (JSON format):
   - Claimant information
   - Policy number
   - Claim amount
   - Service dates
   - Diagnosis codes (ICD-10)
   - Procedure codes (CPT)

2. **Policy Documents** (Text/JSON):
   - Coverage limits
   - Deductibles
   - Co-payment rules
   - Exclusions
   - Pre-authorization requirements

3. **Medical Reports** (Text/PDF):
   - Diagnosis
   - Treatment details
   - Provider information
   - Medical necessity justification

### Output Data
- Claim processing summary
- Validation results
- Approval/rejection recommendation
- Coverage calculation
- Detailed explanation
- Next steps for claimant

## Sample Workflow

1. **Upload**: User uploads claim form and supporting documents
2. **Extraction**: Extraction agent parses and structures all data
3. **Validation**: Validation agent checks against policy rules
4. **Decision**: Decision agent generates recommendation
5. **Explanation**: Explanation agent creates detailed report
6. **Output**: User receives comprehensive processing summary

## License

MIT License

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.
