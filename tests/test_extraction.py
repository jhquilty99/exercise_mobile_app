"""
Test suite for Google Sheets Data Integration Module

Tests the GoogleSheetsExtractor class functionality including:
- OAuth2 authentication with Google Sheets API
- Data extraction from specified sheet ranges
- Error handling and validation
- Security compliance
- Extraction statistics and logging
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import json
import pandas as pd
from datetime import datetime
import logging
import time
import gspread

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.backend.extraction import GoogleSheetsExtractor, ExtractionStats


class TestExtractionStats(unittest.TestCase):
    """Test the ExtractionStats dataclass."""
    
    def test_extraction_stats_default_values(self):
        """Test that ExtractionStats has correct default values."""
        stats = ExtractionStats()
        
        self.assertEqual(stats.records_read, 0)
        self.assertEqual(stats.errors_found, 0)
        self.assertEqual(stats.api_connection_status, "unknown")
        self.assertEqual(stats.extraction_time, 0.0)
        self.assertEqual(stats.sheet_name, "")
        self.assertEqual(stats.range_read, "")
    
    def test_extraction_stats_custom_values(self):
        """Test that ExtractionStats can be initialized with custom values."""
        stats = ExtractionStats(
            records_read=100,
            errors_found=5,
            api_connection_status="connected",
            extraction_time=2.5,
            sheet_name="TestSheet",
            range_read="A1:G100"
        )
        
        self.assertEqual(stats.records_read, 100)
        self.assertEqual(stats.errors_found, 5)
        self.assertEqual(stats.api_connection_status, "connected")
        self.assertEqual(stats.extraction_time, 2.5)
        self.assertEqual(stats.sheet_name, "TestSheet")
        self.assertEqual(stats.range_read, "A1:G100")


class TestGoogleSheetsExtractorInitialization(unittest.TestCase):
    """Test the GoogleSheetsExtractor initialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_credentials_file.write('{"type": "service_account", "project_id": "test"}')
        self.temp_credentials_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_credentials_file.name):
            os.unlink(self.temp_credentials_file.name)
    
    def test_init_with_credentials_path(self):
        """Test initialization with valid credentials path."""
        extractor = GoogleSheetsExtractor(self.temp_credentials_file.name)
        
        self.assertEqual(extractor.credentials_path, self.temp_credentials_file.name)
        self.assertIsNone(extractor.client)
        self.assertIsInstance(extractor.stats, ExtractionStats)
    
    def test_init_with_environment_variable(self):
        """Test initialization using GOOGLE_CREDENTIALS environment variable."""
        with patch.dict(os.environ, {'GOOGLE_CREDENTIALS': self.temp_credentials_file.name}):
            extractor = GoogleSheetsExtractor()
            
            self.assertEqual(extractor.credentials_path, self.temp_credentials_file.name)
    
    def test_init_without_credentials(self):
        """Test initialization fails when no credentials are provided."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                GoogleSheetsExtractor()
            
            self.assertIn("Google credentials not found", str(context.exception))
    
    def test_init_with_none_credentials_path(self):
        """Test initialization with None credentials path falls back to environment variable."""
        with patch.dict(os.environ, {'GOOGLE_CREDENTIALS': self.temp_credentials_file.name}):
            extractor = GoogleSheetsExtractor(None)
            
            self.assertEqual(extractor.credentials_path, self.temp_credentials_file.name)


class TestGoogleSheetsExtractorAuthentication(unittest.TestCase):
    """Test the authentication functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_credentials_file.write('{"type": "service_account", "project_id": "test"}')
        self.temp_credentials_file.close()
        self.extractor = GoogleSheetsExtractor(self.temp_credentials_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_credentials_file.name):
            os.unlink(self.temp_credentials_file.name)
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    def test_authenticate_success(self, mock_authorize, mock_credentials):
        """Test successful authentication."""
        mock_credentials.return_value = Mock()
        mock_authorize.return_value = Mock()
        
        self.extractor._authenticate()
        
        self.assertIsNotNone(self.extractor.client)
        self.assertEqual(self.extractor.stats.api_connection_status, "connected")
        mock_credentials.assert_called_once()
        mock_authorize.assert_called_once()
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    def test_authenticate_google_auth_error(self, mock_credentials):
        """Test authentication failure with GoogleAuthError."""
        from google.auth.exceptions import GoogleAuthError
        mock_credentials.side_effect = GoogleAuthError("Invalid credentials")
        
        with self.assertRaises(GoogleAuthError):
            self.extractor._authenticate()
        
        self.assertEqual(self.extractor.stats.api_connection_status, "authentication_failed")
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    def test_authenticate_unexpected_error(self, mock_credentials):
        """Test authentication failure with unexpected error."""
        mock_credentials.side_effect = Exception("Unexpected error")
        
        with self.assertRaises(Exception):
            self.extractor._authenticate()
        
        self.assertEqual(self.extractor.stats.api_connection_status, "error")


class TestGoogleSheetsExtractorColumnLetterConversion(unittest.TestCase):
    """Test the _get_column_letter method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_credentials_file.write('{"type": "service_account", "project_id": "test"}')
        self.temp_credentials_file.close()
        self.extractor = GoogleSheetsExtractor(self.temp_credentials_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_credentials_file.name):
            os.unlink(self.temp_credentials_file.name)
    
    def test_get_column_letter_single_letters(self):
        """Test conversion of single letter columns (A-Z)."""
        self.assertEqual(self.extractor._get_column_letter(0), "A")
        self.assertEqual(self.extractor._get_column_letter(25), "Z")
    
    def test_get_column_letter_double_letters(self):
        """Test conversion of double letter columns (AA-ZZ)."""
        self.assertEqual(self.extractor._get_column_letter(26), "AA")
        self.assertEqual(self.extractor._get_column_letter(27), "AB")
        self.assertEqual(self.extractor._get_column_letter(51), "AZ")
        self.assertEqual(self.extractor._get_column_letter(52), "BA")
        self.assertEqual(self.extractor._get_column_letter(701), "ZZ")
    
    def test_get_column_letter_triple_letters(self):
        """Test conversion of triple letter columns (AAA-ZZZ)."""
        self.assertEqual(self.extractor._get_column_letter(702), "AAA")
        self.assertEqual(self.extractor._get_column_letter(703), "AAB")
    
    def test_get_column_letter_edge_cases(self):
        """Test edge cases for column letter conversion."""
        self.assertEqual(self.extractor._get_column_letter(1), "B")
        self.assertEqual(self.extractor._get_column_letter(2), "C")
        self.assertEqual(self.extractor._get_column_letter(25), "Z")
        self.assertEqual(self.extractor._get_column_letter(26), "AA")


class TestGoogleSheetsExtractorDataExtraction(unittest.TestCase):
    """Test the main data extraction functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_credentials_file.write('{"type": "service_account", "project_id": "test"}')
        self.temp_credentials_file.close()
        self.extractor = GoogleSheetsExtractor(self.temp_credentials_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_credentials_file.name):
            os.unlink(self.temp_credentials_file.name)
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_success(self, mock_gspread, mock_authorize, mock_credentials):
        """Test successful data extraction."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock worksheet data - return actual list instead of Mock
        mock_worksheet.get_all_values.return_value = [
            ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'],
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No']
        ]
        
        df, stats = self.extractor.extract_data(
            spreadsheet_id="test_id",
            sheet_name="TestSheet"
        )
        
        self.assertEqual(len(df), 1)
        self.assertEqual(stats.records_read, 2)  # Including header row
        self.assertEqual(stats.sheet_name, "TestSheet")
        self.assertEqual(stats.api_connection_status, "connected")
        # In mocked environment, extraction time might be 0, so check it's a number
        self.assertIsInstance(stats.extraction_time, float)
        self.assertEqual(stats.range_read, "A1:G2")
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_with_range(self, mock_gspread, mock_authorize, mock_credentials):
        """Test data extraction with specific range."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock worksheet data - return actual list instead of Mock
        mock_worksheet.get.return_value = [
            ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'],
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No']
        ]
        
        df, stats = self.extractor.extract_data(
            spreadsheet_id="test_id",
            sheet_name="TestSheet",
            range_name="A1:G10"
        )
        
        self.assertEqual(len(df), 1)
        self.assertEqual(stats.range_read, "A1:G10")
        mock_worksheet.get.assert_called_once_with("A1:G10")
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_worksheet_not_found(self, mock_gspread, mock_authorize, mock_credentials):
        """Test extraction fails when worksheet is not found."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet
        mock_spreadsheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        
        # Create a proper exception class for WorksheetNotFound
        class WorksheetNotFound(Exception):
            pass
        
        mock_spreadsheet.worksheet.side_effect = WorksheetNotFound("Worksheet not found")
        
        with self.assertRaises(ValueError) as context:
            self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="NonExistentSheet"
            )
        
        self.assertIn("Sheet 'NonExistentSheet' not found in spreadsheet", str(context.exception))
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_sheet_not_found(self, mock_gspread, mock_authorize, mock_credentials):
        """Test extraction fails when sheet is not found."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet
        mock_spreadsheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.side_effect = Exception("Worksheet not found")
        
        with self.assertRaises(Exception):
            self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="NonExistentSheet"
            )
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_empty_sheet(self, mock_gspread, mock_authorize, mock_credentials):
        """Test extraction fails when sheet is empty."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock empty worksheet data - return actual list instead of Mock
        mock_worksheet.get_all_values.return_value = [
            ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating']
        ]  # Only header row
        
        with self.assertRaises(ValueError) as context:
            self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="TestSheet"
            )
        
        self.assertIn("No data found in sheet", str(context.exception))
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_no_data(self, mock_gspread, mock_authorize, mock_credentials):
        """Test extraction fails when no data is returned."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock empty worksheet data - return actual list instead of Mock
        mock_worksheet.get_all_values.return_value = []
        
        with self.assertRaises(ValueError) as context:
            self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="TestSheet"
            )
        
        self.assertIn("No data found in sheet", str(context.exception))
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_with_errors_found(self, mock_gspread, mock_authorize, mock_credentials):
        """Test extraction with errors found triggers warning log."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock worksheet data - return actual list instead of Mock
        mock_worksheet.get_all_values.return_value = [
            ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'],
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No']
        ]
        
        # Set errors_found to trigger warning
        self.extractor.stats.errors_found = 5
        
        with self.assertLogs('src.backend.extraction', level='WARNING') as log:
            df, stats = self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="TestSheet"
            )
        
        # Check that warning was logged
        self.assertTrue(any("Found 5 errors during extraction" in record.message for record in log.records))
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_large_dataset(self, mock_gspread, mock_authorize, mock_credentials):
        """Test extraction with large dataset for performance validation."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Create large dataset (1000 rows) - return actual list instead of Mock
        headers = ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating']
        large_data = [headers]
        for i in range(1000):
            large_data.append([
                f'2024-01-{i+1:02d}',
                'Strength',
                f'Exercise {i}',
                str(100 + i),
                '3',
                '10',
                'No'
            ])
        
        mock_worksheet.get_all_values.return_value = large_data
        
        start_time = time.time()
        df, stats = self.extractor.extract_data(
            spreadsheet_id="test_id",
            sheet_name="TestSheet"
        )
        extraction_time = time.time() - start_time
        
        self.assertEqual(len(df), 1000)
        self.assertEqual(stats.records_read, 1001)  # Including header
        self.assertLess(extraction_time, 5.0)  # Should complete within 5 seconds
        self.assertEqual(stats.range_read, "A1:G1001")


class TestGoogleSheetsExtractorErrorHandling(unittest.TestCase):
    """Test error handling functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_credentials_file.write('{"type": "service_account", "project_id": "test"}')
        self.temp_credentials_file.close()
        self.extractor = GoogleSheetsExtractor(self.temp_credentials_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_credentials_file.name):
            os.unlink(self.temp_credentials_file.name)
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_404_error(self, mock_gspread, mock_authorize, mock_credentials):
        """Test handling of 404 (not found) error."""
        from googleapiclient.errors import HttpError
        
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock HTTP error - this should be raised when opening the spreadsheet
        mock_client.open_by_key.side_effect = HttpError(
            resp=Mock(status=404),
            content=b'Not found'
        )
        
        with self.assertRaises(Exception) as context:
            self.extractor.extract_data(
                spreadsheet_id="invalid_id",
                sheet_name="TestSheet"
            )
        
        self.assertIn("Spreadsheet not found or access denied", str(context.exception))
        self.assertEqual(self.extractor.stats.api_connection_status, "api_error")
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_403_error(self, mock_gspread, mock_authorize, mock_credentials):
        """Test handling of 403 (forbidden) error."""
        from googleapiclient.errors import HttpError
        
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock HTTP error - this should be raised when opening the spreadsheet
        mock_client.open_by_key.side_effect = HttpError(
            resp=Mock(status=403),
            content=b'Forbidden'
        )
        
        with self.assertRaises(Exception) as context:
            self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="TestSheet"
            )
        
        self.assertIn("Access denied", str(context.exception))
        self.assertEqual(self.extractor.stats.api_connection_status, "api_error")
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_other_http_error(self, mock_gspread, mock_authorize, mock_credentials):
        """Test handling of other HTTP errors."""
        from googleapiclient.errors import HttpError
        
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock HTTP error - this should be raised when opening the spreadsheet
        mock_client.open_by_key.side_effect = HttpError(
            resp=Mock(status=500),
            content=b'Internal Server Error'
        )
        
        with self.assertRaises(Exception) as context:
            self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="TestSheet"
            )
        
        self.assertIn("Google Sheets API error", str(context.exception))
        self.assertEqual(self.extractor.stats.api_connection_status, "api_error")
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_general_exception(self, mock_gspread, mock_authorize, mock_credentials):
        """Test handling of general exceptions during extraction."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock general exception - this should be raised when opening the spreadsheet
        mock_client.open_by_key.side_effect = Exception("Network timeout")
        
        with self.assertRaises(Exception) as context:
            self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="TestSheet"
            )
        
        # The error message should contain the original exception
        self.assertIn("Network timeout", str(context.exception))
        self.assertEqual(self.extractor.stats.api_connection_status, "extraction_failed")


class TestGoogleSheetsExtractorConnectionTest(unittest.TestCase):
    """Test connection testing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_credentials_file.write('{"type": "service_account", "project_id": "test"}')
        self.temp_credentials_file.close()
        self.extractor = GoogleSheetsExtractor(self.temp_credentials_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_credentials_file.name):
            os.unlink(self.temp_credentials_file.name)
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_test_connection_success(self, mock_gspread, mock_authorize, mock_credentials):
        """Test successful connection test."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet
        mock_spreadsheet = Mock()
        mock_spreadsheet.title = "Test Spreadsheet"
        mock_client.open_by_key.return_value = mock_spreadsheet
        
        result = self.extractor.test_connection("test_id")
        
        self.assertTrue(result)
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_test_connection_failure(self, mock_gspread, mock_authorize, mock_credentials):
        """Test connection test failure."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock connection failure - this should be raised when opening the spreadsheet
        mock_client.open_by_key.side_effect = Exception("Connection failed")
        
        result = self.extractor.test_connection("test_id")
        
        self.assertFalse(result)
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    def test_test_connection_authentication_failure(self, mock_authorize, mock_credentials):
        """Test connection test when authentication fails."""
        # Mock authentication failure
        mock_credentials.side_effect = Exception("Auth failed")
        
        result = self.extractor.test_connection("test_id")
        
        self.assertFalse(result)


class TestGoogleSheetsExtractorStats(unittest.TestCase):
    """Test the get_extraction_stats method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_credentials_file.write('{"type": "service_account", "project_id": "test"}')
        self.temp_credentials_file.close()
        self.extractor = GoogleSheetsExtractor(self.temp_credentials_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_credentials_file.name):
            os.unlink(self.temp_credentials_file.name)
    
    def test_get_extraction_stats_initial_state(self):
        """Test get_extraction_stats returns initial stats."""
        stats = self.extractor.get_extraction_stats()
        
        self.assertIsInstance(stats, ExtractionStats)
        self.assertEqual(stats.records_read, 0)
        self.assertEqual(stats.errors_found, 0)
        self.assertEqual(stats.api_connection_status, "unknown")
        self.assertEqual(stats.extraction_time, 0.0)
        self.assertEqual(stats.sheet_name, "")
        self.assertEqual(stats.range_read, "")
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_get_extraction_stats_after_extraction(self, mock_gspread, mock_authorize, mock_credentials):
        """Test get_extraction_stats returns updated stats after extraction."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock worksheet data - return actual list instead of Mock
        mock_worksheet.get_all_values.return_value = [
            ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'],
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No']
        ]
        
        # Perform extraction
        self.extractor.extract_data(
            spreadsheet_id="test_id",
            sheet_name="TestSheet"
        )
        
        # Get stats
        stats = self.extractor.get_extraction_stats()
        
        self.assertEqual(stats.records_read, 2)
        self.assertEqual(stats.sheet_name, "TestSheet")
        self.assertEqual(stats.api_connection_status, "connected")
        # Extraction time might be very small, so just check it's a number
        self.assertIsInstance(stats.extraction_time, float)
        self.assertEqual(stats.range_read, "A1:G2")


class TestGoogleSheetsExtractorSecurity(unittest.TestCase):
    """Test security compliance requirements."""
    
    def test_no_external_data_storage(self):
        """Test that no data is stored externally."""
        # This test verifies that the extractor doesn't create any external files
        # beyond the temporary credentials file which is expected
        
        temp_dir = tempfile.mkdtemp()
        credentials_path = os.path.join(temp_dir, "credentials.json")
        
        with open(credentials_path, 'w') as f:
            json.dump({"type": "service_account", "project_id": "test"}, f)
        
        try:
            extractor = GoogleSheetsExtractor(credentials_path)
            
            # Verify no additional files were created
            files_before = set(os.listdir(temp_dir))
            
            # Perform some operations
            extractor.get_extraction_stats()
            
            files_after = set(os.listdir(temp_dir))
            
            # Should only have the credentials file
            self.assertEqual(files_before, files_after)
            
        finally:
            # Clean up
            os.unlink(credentials_path)
            os.rmdir(temp_dir)
    
    def test_credentials_validation(self):
        """Test that invalid credentials are properly handled."""
        # Test with non-existent credentials file
        # The module doesn't validate file existence during initialization
        # It only validates during authentication
        extractor = GoogleSheetsExtractor("/non/existent/path.json")
        self.assertIsNotNone(extractor)
        
        # Test with empty credentials file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.write('{}')
        temp_file.close()
        
        try:
            # Should not raise error during initialization, but during authentication
            extractor = GoogleSheetsExtractor(temp_file.name)
            self.assertIsNotNone(extractor)
        finally:
            os.unlink(temp_file.name)
    
    def test_malicious_input_handling(self):
        """Test handling of potentially malicious input."""
        # Test with malicious spreadsheet ID
        temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_credentials_file.write('{"type": "service_account", "project_id": "test"}')
        temp_credentials_file.close()
        
        try:
            extractor = GoogleSheetsExtractor(temp_credentials_file.name)
            
            # Test with SQL injection attempt
            malicious_id = "'; DROP TABLE users; --"
            
            # Should not crash or expose sensitive information
            # The test_connection method should handle this gracefully
            result = extractor.test_connection(malicious_id)
            self.assertFalse(result)  # Should fail gracefully
            
        finally:
            os.unlink(temp_credentials_file.name)
    
    def test_sensitive_data_not_logged(self):
        """Test that sensitive data is not logged."""
        # This test verifies that credentials and sensitive data are not logged
        temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_credentials_file.write('{"type": "service_account", "project_id": "test", "private_key": "secret_key"}')
        temp_credentials_file.close()
        
        try:
            # Create extractor (this should trigger some logging)
            extractor = GoogleSheetsExtractor(temp_credentials_file.name)
            
            # Try to authenticate to trigger logging
            with self.assertLogs('src.backend.extraction', level='INFO') as log:
                try:
                    extractor.test_connection("test_id")
                except:
                    pass  # Expected to fail
                
                # Check that sensitive data is not in logs
                log_text = '\n'.join(log.output)
                self.assertNotIn("secret_key", log_text)
                self.assertNotIn("private_key", log_text)
                
        finally:
            os.unlink(temp_credentials_file.name)


class TestGoogleSheetsExtractorIntegration(unittest.TestCase):
    """Integration tests for the complete extraction workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_credentials_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_credentials_file.write('{"type": "service_account", "project_id": "test"}')
        self.temp_credentials_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_credentials_file.name):
            os.unlink(self.temp_credentials_file.name)
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_complete_extraction_workflow(self, mock_gspread, mock_authorize, mock_credentials):
        """Test the complete extraction workflow from authentication to data extraction."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock worksheet data - return actual list instead of Mock
        mock_worksheet.get_all_values.return_value = [
            ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'],
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No'],
            ['2024-01-02', 'Strength', 'Squats', '150', '3', '8', 'No'],
            ['2024-01-03', 'Cardio', 'Running', '0', '1', '30', 'No']
        ]
        
        # Create extractor and perform extraction
        extractor = GoogleSheetsExtractor(self.temp_credentials_file.name)
        
        # Test connection first
        connection_result = extractor.test_connection("test_id")
        self.assertTrue(connection_result)
        
        # Extract data
        df, stats = extractor.extract_data(
            spreadsheet_id="test_id",
            sheet_name="TestSheet"
        )
        
        # Verify results
        self.assertEqual(len(df), 3)
        self.assertEqual(stats.records_read, 4)  # Including header
        self.assertEqual(stats.errors_found, 0)
        self.assertEqual(stats.api_connection_status, "connected")
        # Extraction time might be very small, so just check it's a number
        self.assertIsInstance(stats.extraction_time, float)
        self.assertEqual(stats.sheet_name, "TestSheet")
        
        # Verify DataFrame structure
        self.assertIn('Workout Date', df.columns)
        self.assertIn('Exercise Name', df.columns)
        self.assertIn('Weight', df.columns)
        
        # Verify data types
        self.assertTrue(pd.api.types.is_object_dtype(df['Workout Date']))
        self.assertTrue(pd.api.types.is_object_dtype(df['Weight']))
        self.assertTrue(pd.api.types.is_object_dtype(df['Sets']))
    
    @patch('src.backend.extraction.Credentials.from_service_account_file')
    @patch('src.backend.extraction.gspread.authorize')
    @patch('src.backend.extraction.gspread')
    def test_extraction_with_range_specification(self, mock_gspread, mock_authorize, mock_credentials):
        """Test extraction workflow with range specification."""
        # Mock authentication
        mock_credentials.return_value = Mock()
        mock_client = Mock()
        mock_authorize.return_value = mock_client
        
        # Mock spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock worksheet data with range - return actual list instead of Mock
        mock_worksheet.get.return_value = [
            ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'],
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No'],
            ['2024-01-02', 'Strength', 'Squats', '150', '3', '8', 'No']
        ]
        
        # Create extractor and perform extraction
        extractor = GoogleSheetsExtractor(self.temp_credentials_file.name)
        
        # Extract data with range
        df, stats = extractor.extract_data(
            spreadsheet_id="test_id",
            sheet_name="TestSheet",
            range_name="A1:G10"
        )
        
        # Verify results
        self.assertEqual(len(df), 2)
        self.assertEqual(stats.range_read, "A1:G10")
        self.assertEqual(stats.records_read, 3)  # Including header
        
        # Verify that get() was called with the range
        mock_worksheet.get.assert_called_once_with("A1:G10")


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run the tests
    unittest.main(verbosity=2)
