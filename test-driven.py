import unittest
from datetime import datetime
import re
from datetime import datetime
from typing import List, Dict, Union


def clean_email_data(raw_data: List[str]) -> List[Dict[str, str]]:
    """
    Clean and structure raw staff email data from comma-separated strings.
    
    Args:
        raw_data: List of strings in format "email, birth_date, start_date, title"
        
    Returns:
        List of cleaned dictionaries with keys: email, birth_date, start_date, title
    """
    cleaned_data = []
    
    for record in raw_data:
        if not record:
            continue
        
        # Split by comma
        parts = [part.strip() for part in record.split(',')]
        
        if len(parts) < 4:
            continue
        
        email_raw, birth_date_raw, start_date_raw, title_raw = parts[0], parts[1], parts[2], parts[3]
        
        # Clean email
        email = _clean_email(email_raw)
        
        # Clean dates
        birth_date = _clean_date_string(birth_date_raw)
        start_date = _clean_date_string(start_date_raw)
        
        # Clean title
        title = _clean_title(title_raw)
        
        # Create cleaned record
        cleaned_record = {
            "email": email,
            "birth_date": birth_date,
            "start_date": start_date,
            "title": title
        }
        
        cleaned_data.append(cleaned_record)
    
    return cleaned_data


def generate_messages(structured_data: List[Dict[str, str]], today: datetime) -> List[str]:
    """
    Generate birthday and work anniversary messages based on the current date.
    
    Args:
        structured_data: List of cleaned staff data dictionaries
        today: Current date as datetime object
        
    Returns:
        List of message strings
    """
    messages = []
    
    for person in structured_data:
        email = person.get('email', '')
        birth_date_str = person.get('birth_date', '')
        start_date_str = person.get('start_date', '')
        
        # Extract name from email
        name = _extract_name_from_email(email)
        
        # Check for birthday
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
                if birth_date.month == today.month and birth_date.day == today.day:
                    messages.append(f"Happy Birthday, {name}! Have a fantastic day!")
            except ValueError:
                pass
        
        # Check for work anniversary
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                if start_date.month == today.month and start_date.day == today.day:
                    # Calculate years
                    years = today.year - start_date.year
                    # Adjust if anniversary hasn't occurred yet this year
                    if (today.month, today.day) < (start_date.month, start_date.day):
                        years -= 1
                    
                    # Only send if at least 1 year has passed
                    if years > 0:
                        messages.append(f"Happy Work Anniversary, {name}! {years} years at the company!")
            except ValueError:
                pass
    
    return messages


# Helper functions

def _clean_email(email_raw: str) -> str:
    """
    Clean email address by removing invalid characters and fixing common typos.
    """
    email = email_raw.strip().lower()
    
    # Fix double dots (..)
    email = re.sub(r'\.\.+', '.', email)
    
    # Fix double @ signs (@@)
    email = re.sub(r'@+', '@', email)
    
    # Replace # with @ if # appears where @ should be
    if '@' not in email and '#' in email:
        email = email.replace('#', '@')
    
    # Remove special characters at the end (like !!, **, @@)
    # Keep only valid email characters
    email = re.sub(r'[^a-z0-9@._-]', '', email)
    
    return email


def _clean_date_string(date_str: str) -> str:
    """
    Clean and validate date string. Returns the date in YYYY-MM-DD format.
    """
    date_str = date_str.strip()
    
    # Remove any non-date characters
    date_str = re.sub(r'[^0-9-]', '', date_str)
    
    try:
        # Validate it's a proper date
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        return date_str  # Return as-is if parsing fails


def _clean_title(title_raw: str) -> str:
    """
    Clean job title by removing special characters and extra spaces.
    """
    title = title_raw.strip()
    
    # Remove special characters at the end (like !!, **, @@)
    title = re.sub(r'[!@*#$%^&*]+$', '', title)
    
    # Remove extra spaces
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title


def _extract_name_from_email(email: str) -> str:
    """
    Extract and format a person's name from their email address.
    Converts john.doe or jane_doe to John Doe or Jane Doe.
    """
    if not email or '@' not in email:
        return ''
    
    # Get the part before @
    username = email.split('@')[0]
    
    # Replace dots and underscores with spaces
    name_parts = re.split(r'[._-]', username)
    
    # Capitalize each part
    formatted_name = ' '.join(part.capitalize() for part in name_parts if part)
    
    return formatted_name


# Run tests
if __name__ == '__main__':
    import unittest
    
    class TestStaffDataProcessing(unittest.TestCase):
        
        def test_clean_email_data(self):
            raw_data = [
                "john.doe@company..com, 1985-07-23, 2015-06-15, Software Engineer!!",
                "JANE_DOE@@company.com, 1990-12-05, 2018-09-01, Senior Manager**",
                "BOB.SMITH#company.com, 1975-04-17, 2000-03-12, CTO@@",
            ]
            expected_cleaned_data = [
                {"email": "john.doe@company.com", "birth_date": "1985-07-23", "start_date": "2015-06-15", "title": "Software Engineer"},
                {"email": "jane_doe@company.com", "birth_date": "1990-12-05", "start_date": "2018-09-01", "title": "Senior Manager"},
                {"email": "bob.smith@company.com", "birth_date": "1975-04-17", "start_date": "2000-03-12", "title": "CTO"},
            ]
            
            cleaned_data = clean_email_data(raw_data)
            self.assertEqual(cleaned_data, expected_cleaned_data)
        
        def test_generate_messages(self):
            structured_data = [
                {"email": "john.doe@company.com", "birth_date": "1985-07-23", "start_date": "2015-06-15", "title": "Software Engineer"},
                {"email": "jane_doe@company.com", "birth_date": "1990-12-05", "start_date": "2018-09-01", "title": "Senior Manager"},
                {"email": "bob.smith@company.com", "birth_date": "1975-04-17", "start_date": "2000-03-12", "title": "CTO"},
            ]
            today = datetime(2025, 7, 23)
            expected_messages = [
                "Happy Birthday, John Doe! Have a fantastic day!",
                "Happy Work Anniversary, John Doe! 10 years at the company!",
            ]
            
            messages = generate_messages(structured_data, today)
            
            for msg in expected_messages:
                self.assertIn(msg, messages)
        
        def test_no_messages_for_non_matching_dates(self):
            structured_data = [
                {"email": "john.doe@company.com", "birth_date": "1985-07-23", "start_date": "2015-06-15", "title": "Software Engineer"},
                {"email": "jane_doe@company.com", "birth_date": "1990-12-05", "start_date": "2018-09-01", "title": "Senior Manager"},
                {"email": "bob.smith@company.com", "birth_date": "1975-04-17", "start_date": "2000-03-12", "title": "CTO"},
            ]
            today = datetime(2025, 8, 15)
            messages = generate_messages(structured_data, today)
            self.assertEqual(messages, [])
    
    unittest.main()
class TestStaffDataProcessing(unittest.TestCase):
    
    def test_clean_email_data(self):
        raw_data = [
            "john.doe@company..com, 1985-07-23, 2015-06-15, Software Engineer!!",
            "JANE_DOE@@company.com, 1990-12-05, 2018-09-01, Senior Manager**",
            "BOB.SMITH#company.com, 1975-04-17, 2000-03-12, CTO@@",
        ]
        expected_cleaned_data = [
            {"email": "john.doe@company.com", "birth_date": "1985-07-23", "start_date": "2015-06-15", "title": "Software Engineer"},
            {"email": "jane_doe@company.com", "birth_date": "1990-12-05", "start_date": "2018-09-01", "title": "Senior Manager"},
            {"email": "bob.smith@company.com", "birth_date": "1975-04-17", "start_date": "2000-03-12", "title": "CTO"},
        ]
        
        cleaned_data = clean_email_data(raw_data)  # This function must be implemented
        self.assertEqual(cleaned_data, expected_cleaned_data)
    
    def test_generate_messages(self):
        structured_data = [
            {"email": "john.doe@company.com", "birth_date": "1985-07-23", "start_date": "2015-06-15", "title": "Software Engineer"},
            {"email": "jane_doe@company.com", "birth_date": "1990-12-05", "start_date": "2018-09-01", "title": "Senior Manager"},
            {"email": "bob.smith@company.com", "birth_date": "1975-04-17", "start_date": "2000-03-12", "title": "CTO"},
        ]
        today = datetime(2025, 7, 23)  # Simulated current date for testing
        expected_messages = [
            "Happy Birthday, John Doe! Have a fantastic day!",
            "Happy Work Anniversary, John Doe! 10 years at the company!",
        ]
        
        messages = generate_messages(structured_data, today)  # This function must be implemented
        
        for msg in expected_messages:
            self.assertIn(msg, messages)
    
    def test_no_messages_for_non_matching_dates(self):
        structured_data = [
            {"email": "john.doe@company.com", "birth_date": "1985-07-23", "start_date": "2015-06-15", "title": "Software Engineer"},
            {"email": "jane_doe@company.com", "birth_date": "1990-12-05", "start_date": "2018-09-01", "title": "Senior Manager"},
            {"email": "bob.smith@company.com", "birth_date": "1975-04-17", "start_date": "2000-03-12", "title": "CTO"},
        ]
        today = datetime(2025, 8, 15)  # A date that doesn't match any events
        messages = generate_messages(structured_data, today)
        self.assertEqual(messages, [])  # No messages should be generated

if __name__ == '__main__':
    unittest.main()