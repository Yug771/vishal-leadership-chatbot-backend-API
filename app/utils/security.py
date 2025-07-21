import re
from email_validator import validate_email as validate_email_lib, EmailNotValidError

def validate_email(email):
    """
    Validate an email address.
    
    Args:
        email (str): The email address to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Validate and normalize the email
        valid = validate_email_lib(email)
        # Update with the normalized email
        return True, valid.email
    except EmailNotValidError as e:
        # Email is not valid
        return False, str(e)

def validate_password(password):
    """
    Validate a password.
    
    Requirements:
    - At least 8 characters
    - Contains at least one digit
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one special character
    
    Args:
        password (str): The password to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    
    return True, "Password is valid."

def sanitize_input(input_str):
    """
    Sanitize input to prevent XSS and SQL injection.
    
    Args:
        input_str (str): The input string to sanitize
        
    Returns:
        str: The sanitized input
    """
    if not input_str:
        return input_str
    
    # Remove potentially dangerous HTML tags
    input_str = re.sub(r'<script.*?>.*?</script>', '', input_str, flags=re.DOTALL)
    input_str = re.sub(r'<.*?>', '', input_str)
    
    # Remove SQL injection patterns
    input_str = re.sub(r'\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE)?|INSERT|SELECT|UPDATE)\b', '', input_str, flags=re.IGNORECASE)
    input_str = re.sub(r'(\b(OR|AND)\b\s+\w+\s*=\s*\w+\s*($|\b))', '', input_str, flags=re.IGNORECASE)
    
    return input_str 