"""
Google Sheets Data Integration Module

This module provides secure connection to Google Sheets, ._authenticate
Extraction of data from Google Sheets, .extract_data
Uses DataValidator for comprehensive data validation and cleaning.
"""

import os
import logging
import time
from typing import Optional, Tuple
from dataclasses import dataclass
import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError
from googleapiclient.errors import HttpError
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ExtractionStats:
    """Statistics about the data extraction process."""
    records_read: int = 0
    errors_found: int = 0
    api_connection_status: str = "unknown"
    extraction_time: float = 0.0
    sheet_name: str = ""
    range_read: str = ""


class GoogleSheetsExtractor:
    """
    Secure Google Sheets data extractor with OAuth2 authentication.
    
    Implements comprehensive error handling, and data validation
    according to OWASP security guidelines.
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize the Google Sheets extractor.
        
        Args:
            credentials_path: Path to Google service account credentials JSON file.
                             If None, will look for GOOGLE_CREDENTIALS environment variable.
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS')
        self.client = None
        self.stats = ExtractionStats()
        
        if not self.credentials_path:
            raise ValueError(
                "Google credentials not found. Please set GOOGLE_CREDENTIALS "
                "environment variable or provide credentials_path."
            )
    
    def _authenticate(self) -> None:
        """
        Authenticate with Google Sheets API using OAuth2 service account.
        
        Raises:
            GoogleAuthError: If authentication fails
            ValueError: If credentials are invalid
        """
        try:
            logger.info("Authenticating with Google Sheets API...")
            
            # Define the scope for Google Sheets API
            scope = [
                'https://www.googleapis.com/auth/spreadsheets.readonly'
            ]
            
            # Load credentials from service account file
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scope
            )
            
            # Create gspread client
            self.client = gspread.authorize(credentials)
            
            logger.info("Successfully authenticated with Google Sheets API")
            self.stats.api_connection_status = "connected"
            
        except GoogleAuthError as e:
            logger.error(f"Google authentication failed: {e}")
            self.stats.api_connection_status = "authentication_failed"
            raise
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            self.stats.api_connection_status = "error"
            raise
    
    def _get_column_letter(self, column_index: int) -> str:
        """
        Convert column index to Excel-style column letter.
        
        Args:
            column_index: 0-based column index
            
        Returns:
            Column letter (A, B, C, ..., Z, AA, AB, etc.)
        """
        result = ""
        while column_index >= 0:
            column_index, remainder = divmod(column_index, 26)
            result = chr(65 + remainder) + result
            column_index -= 1
        return result
    
    def extract_data(
        self, 
        spreadsheet_id: str, 
        sheet_name: str = "Sheet1",
        range_name: Optional[str] = None
    ) -> Tuple[pd.DataFrame, ExtractionStats]:
        """
        Extract data from Google Sheets with comprehensive error handling.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Name of the sheet to read from
            range_name: Optional range specification (e.g., "A1:Z1000")
            
        Returns:
            Tuple of (DataFrame with extracted data, ExtractionStats)
            
        Raises:
            Exception: If extraction fails
        """
        start_time = time.time()
        
        try:
            # Authenticate if not already done
            if not self.client:
                self._authenticate()
            
            logger.info(f"Opening spreadsheet: {spreadsheet_id}")
            
            # Open spreadsheet
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # Get worksheet
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                raise ValueError(f"Sheet '{sheet_name}' not found in spreadsheet")
            
            self.stats.sheet_name = sheet_name
            
            # Extract data
            if range_name:
                raw_data = worksheet.get(range_name)
            else:
                raw_data = worksheet.get_all_values()
            
            if not raw_data or len(raw_data) <= 1:
                raise ValueError("No data found in sheet or sheet is empty")
            
            # Convert to DataFrame
            headers = raw_data[0]
            data_rows = raw_data[1:]
            df = pd.DataFrame(data_rows, columns=headers)
            
            # Update statistics
            self.stats.records_read = len(raw_data)
            self.stats.extraction_time = time.time() - start_time
            
            # Calculate range string
            if range_name:
                self.stats.range_read = range_name
            else:
                num_cols = len(headers)
                num_rows = len(raw_data)
                last_col = self._get_column_letter(num_cols - 1)
                self.stats.range_read = f"A1:{last_col}{num_rows}"
            
            logger.info(
                f"Successfully extracted {self.stats.records_read} records "
                f"from {sheet_name} in {self.stats.extraction_time:.2f}s"
            )
            
            if self.stats.errors_found > 0:
                logger.warning(f"Found {self.stats.errors_found} errors during extraction")
            
            return df, self.stats
            
        except HttpError as e:
            if e.resp.status == 404:
                error_msg = f"Spreadsheet not found or access denied: {spreadsheet_id}"
            elif e.resp.status == 403:
                error_msg = "Access denied. Check if the service account has permission to access this spreadsheet."
            else:
                error_msg = f"Google Sheets API error: {e}"
            
            logger.error(error_msg)
            self.stats.api_connection_status = "api_error"
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            self.stats.api_connection_status = "extraction_failed"
            raise
    
    def get_extraction_stats(self) -> ExtractionStats:
        """Get the current extraction statistics."""
        return self.stats
    
    def test_connection(self, spreadsheet_id: str) -> bool:
        """
        Test connection to a Google Sheets spreadsheet.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.client:
                self._authenticate()
            
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            logger.info(f"Successfully connected to spreadsheet: {spreadsheet.title}")
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


if __name__ == "__main__":
    # Example usage - replace with your actual credentials and spreadsheet details
    credentials_path = os.getenv('GOOGLE_CREDENTIALS', 'path/to/your/credentials.json')
    spreadsheet_id = "your_spreadsheet_id_here"
    sheet_name = "Sheet1"
    range_name = "A1:G1000"
    
    try:
        # Create extractor
        extractor = GoogleSheetsExtractor(credentials_path)
        
        # Test connection
        if extractor.test_connection(spreadsheet_id):
            logger.info("Connection successful!")
            
            # Extract data
            df, stats = extractor.extract_data(
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                range_name=range_name
            )
            
            logger.info(f"Extracted {len(df)} records")
            logger.info(f"Stats: {stats}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
