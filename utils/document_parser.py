"""Document parsing utilities."""

import json
from typing import Dict, Any, Optional
from pathlib import Path
import PyPDF2
import pdfplumber


class DocumentParser:
    """Utility class for parsing various document formats."""
    
    @staticmethod
    def parse_json(file_path: str) -> Dict[str, Any]:
        """
        Parse JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def parse_json_string(json_string: str) -> Dict[str, Any]:
        """
        Parse JSON string.
        
        Args:
            json_string: JSON string
            
        Returns:
            Parsed JSON data
        """
        return json.loads(json_string)
    
    @staticmethod
    def parse_text(file_path: str) -> str:
        """
        Parse text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            File contents as string
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def parse_pdf_pypdf2(file_path: str) -> str:
        """
        Parse PDF file using PyPDF2.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    @staticmethod
    def parse_pdf_pdfplumber(file_path: str) -> str:
        """
        Parse PDF file using pdfplumber (better for tables).
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    
    @staticmethod
    def parse_pdf(file_path: str, method: str = "pdfplumber") -> str:
        """
        Parse PDF file with specified method.
        
        Args:
            file_path: Path to PDF file
            method: Parsing method ('pypdf2' or 'pdfplumber')
            
        Returns:
            Extracted text
        """
        if method == "pypdf2":
            return DocumentParser.parse_pdf_pypdf2(file_path)
        else:
            return DocumentParser.parse_pdf_pdfplumber(file_path)
    
    @staticmethod
    def parse_document(file_path: str) -> str:
        """
        Auto-detect and parse document based on extension.
        
        Args:
            file_path: Path to document
            
        Returns:
            Extracted content (text or JSON string)
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.json':
            data = DocumentParser.parse_json(file_path)
            return json.dumps(data, indent=2)
        elif extension == '.txt':
            return DocumentParser.parse_text(file_path)
        elif extension == '.pdf':
            return DocumentParser.parse_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from text that may contain other content.
        
        Args:
            text: Text potentially containing JSON
            
        Returns:
            Extracted JSON data or None
        """
        # Try to find JSON in the text
        import re
        
        # Look for JSON object pattern
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        return None
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: list) -> tuple[bool, list]:
        """
        Validate JSON structure has required fields.
        
        Args:
            data: JSON data to validate
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, missing_fields)
        """
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
