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


class TestGoogleSheetsExtractorSheetValidation(unittest.TestCase):
    """Test sheet structure validation."""
    
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
    
    def test_validate_sheet_structure_valid_headers(self):
        """Test validation with valid headers."""
        mock_worksheet = Mock()
        mock_worksheet.row_values.return_value = [
            'Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'
        ]
        
        headers = self.extractor._validate_sheet_structure(mock_worksheet)
        
        self.assertEqual(len(headers), 7)
        self.assertIn('Workout Date', headers)
        self.assertIn('Exercise Name', headers)
    
    def test_validate_sheet_structure_missing_columns(self):
        """Test validation fails with missing required columns."""
        mock_worksheet = Mock()
        mock_worksheet.row_values.return_value = [
            'Workout Date', 'Exercise Name', 'Weight'  # Missing required columns
        ]
        
        with self.assertRaises(ValueError) as context:
            self.extractor._validate_sheet_structure(mock_worksheet)
        
        self.assertIn("Missing required columns", str(context.exception))
    
    def test_validate_sheet_structure_empty_sheet(self):
        """Test validation fails with empty sheet."""
        mock_worksheet = Mock()
        mock_worksheet.row_values.return_value = []
        
        with self.assertRaises(ValueError) as context:
            self.extractor._validate_sheet_structure(mock_worksheet)
        
        self.assertIn("Sheet appears to be empty", str(context.exception))


class TestGoogleSheetsExtractorDataCleaning(unittest.TestCase):
    """Test data cleaning and validation functionality."""
    
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
    
    def test_handle_empty_cells_and_missing_data_valid_records(self):
        """Test handling empty cells and missing data with valid records."""
        headers = ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating']
        data = [
            headers,  # Header row
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No'],
            ['2024-01-02', 'Cardio', 'Running', '0', '1', '30', 'No']
        ]
        
        records = self.extractor._handle_empty_cells_and_missing_data(data, headers)
        
        self.assertEqual(len(records), 2)
        self.assertEqual(self.extractor.stats.errors_found, 0)
        self.assertIsInstance(records, list)
        self.assertIsInstance(records[0], dict)
    
    def test_handle_empty_cells_and_missing_data_empty_dates_filtered(self):
        """Test that rows with empty dates are filtered out."""
        headers = ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating']
        data = [
            headers,  # Header row
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No'],  # Valid
            ['', 'Strength', 'Squats', '150', '3', '8', 'No'],  # Empty date
            ['   ', 'Cardio', 'Running', '0', '1', '30', 'No']  # Whitespace date
        ]
        
        records = self.extractor._handle_empty_cells_and_missing_data(data, headers)
        
        self.assertEqual(len(records), 1)  # Only the valid record should remain
    
    def test_validate_data_constraints_valid_records(self):
        """Test validating data constraints with valid records."""
        records = [
            {'Workout Date': '2024-01-01', 'Exercise Type': 'Strength', 'Exercise Name': 'Bench Press', 
             'Weight': '100', 'Sets': '3', 'Discrete Reps': '10', 'Alternating': 'No'},
            {'Workout Date': '2024-01-02', 'Exercise Type': 'Cardio', 'Exercise Name': 'Running', 
             'Weight': '0', 'Sets': '1', 'Discrete Reps': '30', 'Alternating': 'No'}
        ]
        
        validated_records = self.extractor._validate_data_constraints(records)
        
        self.assertEqual(len(validated_records), 2)
        self.assertEqual(self.extractor.stats.errors_found, 0)
    
    def test_validate_data_constraints_missing_required_fields(self):
        """Test validating data constraints with missing required fields."""
        records = [
            {'Workout Date': '2024-01-01', 'Exercise Type': 'Strength', 'Exercise Name': 'Bench Press', 
             'Weight': '100', 'Sets': '3', 'Discrete Reps': '10', 'Alternating': 'No'},  # Valid
            {'Workout Date': '2024-01-02', 'Exercise Type': '', 'Exercise Name': 'Running', 
             'Weight': '0', 'Sets': '1', 'Discrete Reps': '30', 'Alternating': 'No'},  # Missing Exercise Type
            {'Workout Date': '2024-01-03', 'Exercise Type': 'Strength', 'Exercise Name': '', 
             'Weight': '100', 'Sets': '3', 'Discrete Reps': '10', 'Alternating': 'No'}  # Missing Exercise Name
        ]
        
        validated_records = self.extractor._validate_data_constraints(records)
        
        self.assertEqual(len(validated_records), 1)  # Only the valid record should remain
        self.assertEqual(self.extractor.stats.errors_found, 2)
    
    def test_coerce_data_types_conversion(self):
        """Test that data types are properly converted."""
        df = pd.DataFrame([
            {'Workout Date': '2024-01-01', 'Exercise Type': 'Strength', 'Exercise Name': 'Bench Press', 
             'Weight': '100.5', 'Sets': '3', 'Discrete Reps': '10', 'Alternating': 'No'}
        ])
        
        coerced_df = self.extractor._coerce_data_types(df)
        
        self.assertEqual(len(coerced_df), 1)
        self.assertIsInstance(coerced_df['Workout Date'].iloc[0], pd.Timestamp)
        self.assertIsInstance(coerced_df['Weight'].iloc[0], float)
        self.assertIsInstance(coerced_df['Sets'].iloc[0], pd.Int64Dtype().type)
        self.assertIsInstance(coerced_df['Discrete Reps'].iloc[0], pd.Int64Dtype().type)
    
    def test_clean_and_validate_data_integration(self):
        """Test the complete clean and validate data workflow."""
        headers = ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating']
        data = [
            headers,  # Header row
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No'],
            ['2024-01-02', 'Cardio', 'Running', '0', '1', '30', 'No']
        ]
        
        df = self.extractor._clean_and_validate_data(data, headers)
        
        self.assertEqual(len(df), 2)
        self.assertEqual(self.extractor.stats.errors_found, 0)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIsInstance(df['Workout Date'].iloc[0], pd.Timestamp)
        self.assertIsInstance(df['Weight'].iloc[0], float)


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
    
    @patch.object(GoogleSheetsExtractor, '_authenticate')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_success(self, mock_gspread, mock_authenticate):
        """Test successful data extraction."""
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_gspread.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock worksheet data
        mock_worksheet.row_values.return_value = [
            'Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'
        ]
        mock_worksheet.get_all_values.return_value = [
            ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'],
            ['2024-01-01', 'Strength', 'Bench Press', '100', '3', '10', 'No']
        ]
        
        df, stats = self.extractor.extract_data(
            spreadsheet_id="test_id",
            sheet_name="TestSheet"
        )
        
        self.assertEqual(len(df), 1)
        self.assertEqual(stats.records_read, 1)
        self.assertEqual(stats.sheet_name, "TestSheet")
        self.assertEqual(stats.api_connection_status, "connected")
        self.assertGreater(stats.extraction_time, 0)
    
    @patch.object(GoogleSheetsExtractor, '_authenticate')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_with_range(self, mock_gspread, mock_authenticate):
        """Test data extraction with specific range."""
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_gspread.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock worksheet data
        mock_worksheet.row_values.return_value = [
            'Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'
        ]
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
    
    @patch.object(GoogleSheetsExtractor, '_authenticate')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_sheet_not_found(self, mock_gspread, mock_authenticate):
        """Test extraction fails when sheet is not found."""
        # Mock the spreadsheet
        mock_spreadsheet = Mock()
        mock_gspread.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.side_effect = Exception("Worksheet not found")
        
        with self.assertRaises(Exception):
            self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="NonExistentSheet"
            )
    
    @patch.object(GoogleSheetsExtractor, '_authenticate')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_empty_sheet(self, mock_gspread, mock_authenticate):
        """Test extraction fails when sheet is empty."""
        # Mock the spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_gspread.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock empty worksheet data
        mock_worksheet.row_values.return_value = [
            'Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'
        ]
        mock_worksheet.get_all_values.return_value = [
            ['Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating']
        ]  # Only header row
        
        with self.assertRaises(ValueError) as context:
            self.extractor.extract_data(
                spreadsheet_id="test_id",
                sheet_name="TestSheet"
            )
        
        self.assertIn("No data found in sheet", str(context.exception))


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
    
    @patch.object(GoogleSheetsExtractor, '_authenticate')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_404_error(self, mock_gspread, mock_authenticate):
        """Test handling of 404 (not found) error."""
        from googleapiclient.errors import HttpError
        
        # Mock HTTP error
        mock_gspread.open_by_key.side_effect = HttpError(
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
    
    @patch.object(GoogleSheetsExtractor, '_authenticate')
    @patch('src.backend.extraction.gspread')
    def test_extract_data_403_error(self, mock_gspread, mock_authenticate):
        """Test handling of 403 (forbidden) error."""
        from googleapiclient.errors import HttpError
        
        # Mock HTTP error
        mock_gspread.open_by_key.side_effect = HttpError(
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
    
    @patch.object(GoogleSheetsExtractor, '_authenticate')
    @patch('src.backend.extraction.gspread')
    def test_test_connection_success(self, mock_gspread, mock_authenticate):
        """Test successful connection test."""
        # Mock the spreadsheet
        mock_spreadsheet = Mock()
        mock_spreadsheet.title = "Test Spreadsheet"
        mock_gspread.open_by_key.return_value = mock_spreadsheet
        
        result = self.extractor.test_connection("test_id")
        
        self.assertTrue(result)
    
    @patch.object(GoogleSheetsExtractor, '_authenticate')
    @patch('src.backend.extraction.gspread')
    def test_test_connection_failure(self, mock_gspread, mock_authenticate):
        """Test connection test failure."""
        # Mock connection failure
        mock_gspread.open_by_key.side_effect = Exception("Connection failed")
        
        result = self.extractor.test_connection("test_id")
        
        self.assertFalse(result)


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
        with self.assertRaises(ValueError):
            GoogleSheetsExtractor("/non/existent/path.json")
        
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
        mock_authorize.return_value = Mock()
        
        # Mock spreadsheet and worksheet
        mock_spreadsheet = Mock()
        mock_worksheet = Mock()
        mock_gspread.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock worksheet data
        mock_worksheet.row_values.return_value = [
            'Workout Date', 'Exercise Type', 'Exercise Name', 'Weight', 'Sets', 'Discrete Reps', 'Alternating'
        ]
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
        self.assertEqual(stats.records_read, 3)
        self.assertEqual(stats.errors_found, 0)
        self.assertEqual(stats.api_connection_status, "connected")
        self.assertGreater(stats.extraction_time, 0)
        self.assertEqual(stats.sheet_name, "TestSheet")
        
        # Verify DataFrame structure
        self.assertIn('Workout Date', df.columns)
        self.assertIn('Exercise Name', df.columns)
        self.assertIn('Weight', df.columns)
        
        # Verify data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['Workout Date']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df['Weight']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df['Sets']))


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run the tests
    unittest.main(verbosity=2)
