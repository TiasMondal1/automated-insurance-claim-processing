"""Report generation utilities."""

from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from models.claim import Claim
from models.policy import Policy
from models.decision import Decision, DecisionType


class ReportGenerator:
    """Generate PDF reports for claim processing."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Status style
        self.styles.add(ParagraphStyle(
            name='StatusApproved',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.green,
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='StatusRejected',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.red,
            alignment=TA_CENTER,
            spaceAfter=12
        ))
    
    def generate_claim_report(
        self,
        claim: Claim,
        policy: Policy,
        decision: Decision,
        output_path: str
    ) -> str:
        """
        Generate comprehensive claim processing report.
        
        Args:
            claim: Claim data
            policy: Policy data
            decision: Decision data
            output_path: Path to save PDF
            
        Returns:
            Path to generated PDF
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("Insurance Claim Processing Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Decision Status
        status_style = (
            'StatusApproved' if decision.decision_type == DecisionType.APPROVED 
            else 'StatusRejected'
        )
        story.append(Paragraph(
            f"<b>Status: {decision.decision_type.value.upper()}</b>",
            self.styles[status_style]
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Claim Information Section
        story.append(Paragraph("Claim Information", self.styles['SectionHeader']))
        claim_data = [
            ['Claim ID:', claim.claim_id],
            ['Claimant:', claim.claimant_name],
            ['Policy Number:', claim.policy_number],
            ['Claim Date:', claim.claim_date.strftime('%Y-%m-%d')],
            ['Service Date:', f"{claim.service_start_date.strftime('%Y-%m-%d')} to {claim.service_end_date.strftime('%Y-%m-%d')}"],
            ['Total Billed:', f"${claim.total_billed_amount:,.2f}"],
        ]
        story.append(self._create_table(claim_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Financial Summary Section
        story.append(Paragraph("Financial Summary", self.styles['SectionHeader']))
        financial_data = [
            ['Total Billed Amount:', f"${claim.total_billed_amount:,.2f}"],
            ['Approved Amount:', f"${decision.approved_amount:,.2f}"],
            ['Insurance Payment:', f"${decision.insurance_payment:,.2f}"],
            ['Patient Responsibility:', f"${decision.patient_responsibility:,.2f}"],
            ['', ''],
            ['Deductible Applied:', f"${decision.deductible_applied:,.2f}"],
            ['Copay Applied:', f"${decision.copay_applied:,.2f}"],
            ['Coinsurance Applied:', f"${decision.coinsurance_applied:,.2f}"],
        ]
        story.append(self._create_table(financial_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Policy Information Section
        story.append(Paragraph("Policy Information", self.styles['SectionHeader']))
        policy_data = [
            ['Policy Type:', policy.policy_type],
            ['Annual Deductible:', f"${policy.annual_deductible:,.2f}"],
            ['Deductible Met:', f"${policy.deductible_met:,.2f}"],
            ['Out-of-Pocket Max:', f"${policy.out_of_pocket_max:,.2f}"],
            ['Out-of-Pocket Met:', f"${policy.out_of_pocket_met:,.2f}"],
        ]
        story.append(self._create_table(policy_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Decision Reasoning Section
        story.append(Paragraph("Decision Reasoning", self.styles['SectionHeader']))
        story.append(Paragraph(decision.reasoning, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Validation Results Section
        if decision.validation_results:
            story.append(Paragraph("Validation Results", self.styles['SectionHeader']))
            validation_data = [['Check', 'Status', 'Message']]
            for result in decision.validation_results:
                status = '✓ Pass' if result.passed else '✗ Fail'
                validation_data.append([
                    result.check_name,
                    status,
                    result.message[:50] + '...' if len(result.message) > 50 else result.message
                ])
            story.append(self._create_table(validation_data, header=True))
            story.append(Spacer(1, 0.2 * inch))
        
        # Recommendations Section
        if decision.recommendations:
            story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
            for i, rec in enumerate(decision.recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Next Steps Section
        if decision.next_steps:
            story.append(Paragraph("Next Steps", self.styles['SectionHeader']))
            for i, step in enumerate(decision.next_steps, 1):
                story.append(Paragraph(f"{i}. {step}", self.styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Footer
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            f"Confidence Score: {decision.confidence_score:.2%} | Processing Time: {decision.processing_time_seconds:.2f}s",
            self.styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _create_table(self, data: list, header: bool = False) -> Table:
        """Create a formatted table."""
        table = Table(data, colWidths=[2.5 * inch, 4 * inch])
        
        style = [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]
        
        if header:
            style.extend([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ])
        
        table.setStyle(TableStyle(style))
        return table
