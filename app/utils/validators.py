import re
from email_validator import validate_email, EmailNotValidError

def is_valid_email(email):
    """Validate email address format"""
    try:
        valid = validate_email(email)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)

def is_valid_password(password):
    """Validate password strength

    Requirements:
    - At least 8 characters
    - At least one letter
    - At least one number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, "Valid password"

def is_allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
