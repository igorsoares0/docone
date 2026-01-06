# DocOne - Document Sharing WebApp

A Flask-based document sharing platform similar to Docsend and Papermark. Share documents securely with analytics, password protection, and email capture.

## Features

- Upload and share documents (PDF, DOCX, PPTX)
- Generate secure shareable links
- Password protection for documents
- Email capture before viewing
- View analytics (who opened, when, duration)
- Page-by-page tracking
- Session-based authentication

## Tech Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL (Neon)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Document Processing**: PyPDF2, python-docx, python-pptx
- **Authentication**: Flask-Login (session-based)

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+ (for Tailwind CSS)
- PostgreSQL database (Neon recommended)
- LibreOffice (for document conversion in production)

### 1. Clone and Setup Virtual Environment

```bash
cd docone
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Node Dependencies (Tailwind CSS)

```bash
npm install
```

### 4. Configure Environment Variables

Edit the `.env` file and update the following:

```env
# Database - Replace with your Neon PostgreSQL connection string
DATABASE_URL=postgresql://username:password@ep-xxx.neon.tech/dbname?sslmode=require

# Keep the generated SECRET_KEY or generate a new one
# SECRET_KEY=...
```

To generate a new secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Build Tailwind CSS

```bash
npm run build:css
```

For development with auto-rebuild:
```bash
npm run watch:css
```

### 6. Initialize Database

```bash
# Initialize Flask-Migrate
flask db init

# Create initial migration
flask db migrate -m "Initial models"

# Apply migration
flask db upgrade
```

### 7. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
docone/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration
│   ├── models/               # Database models
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── link.py
│   │   ├── analytics.py
│   │   └── email_capture.py
│   ├── routes/               # Route blueprints
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── links.py
│   │   ├── viewer.py
│   │   └── analytics.py
│   ├── services/             # Business logic
│   ├── utils/                # Utilities
│   ├── static/               # Static files
│   └── templates/            # HTML templates
├── migrations/               # Database migrations
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── package.json              # Node dependencies
└── run.py                    # Application entry point
```

## Database Models

- **User**: Document owners with email/password authentication
- **Document**: Uploaded files with metadata
- **ShareableLink**: Secure links with access control settings
- **DocumentView**: Viewing session analytics
- **CapturedEmail**: Emails collected from viewers

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

After modifying models, create and apply migrations:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Tailwind Development

Keep Tailwind watching for changes during development:

```bash
npm run watch:css
```

## Document Conversion

### Development (Windows/Mac)
The application uses `docx2pdf` which works on Windows and Mac.

### Production (Linux)
Install LibreOffice for document conversion:

```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# CentOS/RHEL
sudo yum install libreoffice
```

## Usage

1. **Register/Login**: Create an account at `/auth/register`
2. **Upload Document**: Navigate to `/upload` and upload PDF, DOCX, or PPTX
3. **Create Share Link**: Configure link settings (password, email requirement, expiration)
4. **Share**: Copy the generated link and share with viewers
5. **Track Analytics**: View who opened your document and for how long

## Security Features

- Session-based authentication with secure cookies
- Password hashing with Werkzeug
- CSRF protection
- Secure link generation with 128-bit entropy
- File type validation
- SQL injection protection via SQLAlchemy ORM

## License

MIT

## Support

For issues and questions, please open an issue on the GitHub repository.
