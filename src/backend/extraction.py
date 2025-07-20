"""
Google Sheets Data Integration Module

This module provides secure connection to and extraction of data from Google Sheets
workout tracker using OAuth2 authentication and comprehensive error handling.
"""

import os
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json
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
    

    
    def _validate_sheet_structure(self, worksheet) -> List[str]:
        """
        Validate that required columns exist in the sheet.
        
        Args:
            worksheet: gspread worksheet object
            
        Returns:
            List of column headers
            
        Raises:
            ValueError: If required columns are missing
        """
        try:
            # Get the first row as headers
            headers = worksheet.row_values(1)
            
            if not headers:
                raise ValueError("Sheet appears to be empty or has no headers")
            
            # Define required columns for workout data
            required_columns = [
                'Workout Date',
                'Exercise Type',
                'Exercise Name',
                'Weight',
                'Sets',
                'Discrete Reps',
                'Alternating'
            ]
            
            missing_columns = [col for col in required_columns if col not in headers]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            logger.info(f"Sheet structure validated. Found columns: {headers}")
            return headers
            
        except Exception as e:
            logger.error(f"Error validating sheet structure: {e}")
            raise
    
    def _clean_and_validate_data(self, data: List[List], headers: List[str]) -> pd.DataFrame:
        """
        Clean and validate extracted data, handling empty cells and missing data.
        
        Args:
            data: Raw data from sheet
            headers: Column headers
            
        Returns:
            DataFrame with cleaned and validated records with proper data types
        """
        # Remove header row for processing
        data_rows = data[1:]    

        # Filter out rows missing workout date
        data_rows = [row for row in data_rows if len(row) > 0 and row[0].strip()]  # Assuming date is first column
        
        if not data_rows:
            raise ValueError("No valid data rows found after filtering missing dates")
        
        logger.info(f"Filtered {len(data[1:]) - len(data_rows)} rows with missing dates")

        cleaned_records = []
        errors = 0
        
        for row_idx, row in enumerate(data_rows, start=2):  # Start from 2 to account for header row
            try:
                # Pad row to match header length
                while len(row) < len(headers):
                    row.append("")
                
                # Create record dictionary
                record = dict(zip(headers, row))
                
                # Validate required fields
                required_fields = ['Workout Date', 'Exercise Name', 'Exercise Type', 'Weight', 'Sets', 'Discrete Reps']
                if any(not record.get(field) for field in required_fields):
                    logger.warning(f"Row {row_idx}: Missing required fields ({' or '.join(required_fields)})")
                    errors += 1
                    continue
                
                cleaned_records.append(record)
                
            except Exception as e:
                logger.error(f"Row {row_idx}: Error processing row: {e}")
                errors += 1
                continue
        
        self.stats.errors_found = errors
        
        # Create DataFrame
        df = pd.DataFrame(cleaned_records)
        
        if df.empty:
            return df
        
        # Convert data types
        try:
            # Convert date column
            if 'Workout Date' in df.columns:
                df['Workout Date'] = pd.to_datetime(df['Workout Date'], errors='coerce')
            
            # Convert numeric columns
            if 'Weight' in df.columns:
                df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')
            
            if 'Sets' in df.columns:
                df['Sets'] = pd.to_numeric(df['Sets'], errors='coerce').astype('Int64')  # nullable integer
            
            if 'Discrete Reps' in df.columns:
                df['Discrete Reps'] = pd.to_numeric(df['Discrete Reps'], errors='coerce').astype('Int64')  # nullable integer
            
            # Keep string columns as object type
            string_columns = ['Exercise Name', 'Exercise Type', 'Alternating']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].astype('string')
            
            logger.info(f"DataFrame created with {len(df)} records and proper data types")
            logger.info(f"DataFrame columns and types: {df.dtypes.to_dict()}")
            
        except Exception as e:
            logger.error(f"Error converting data types: {e}")
            # Return DataFrame with original data types if conversion fails
            pass
        
        return df
    
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
            
            # Validate sheet structure
            headers = self._validate_sheet_structure(worksheet)
            
            # Extract data
            if range_name:
                raw_data = worksheet.get(range_name)
            else:
                raw_data = worksheet.get_all_values()
            
            if not raw_data or len(raw_data) <= 1:
                raise ValueError("No data found in sheet or sheet is empty")
            
            # Clean and validate data
            df = self._clean_and_validate_data(raw_data, headers)
            
            # Update statistics
            self.stats.records_read = len(df)
            self.stats.extraction_time = time.time() - start_time
            self.stats.range_read = range_name or f"A1:{chr(65 + len(headers) - 1)}{len(raw_data)}"
            
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
    credentials_path = "C:/Users/jhqui/OneDrive/Desktop/exercise_mobile_app/google_sheets_service_account.json"
    spreadsheet_id = "1vC6qXrz-BmviRIEcI3uU9yfW0I44iYuZF_XzEyok2Es"
    sheet_name = "Fact Exercise 2"
    range_name = "A1:G1000"
    # Run example if executed directly
    """Example of how to use the GoogleSheetsExtractor."""
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
