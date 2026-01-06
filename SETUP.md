# DocOne - Quick Setup Guide

Follow these steps to get your DocOne document sharing platform up and running.

## Step 1: Install Dependencies

### Python Dependencies
```bash
pip install -r requirements.txt
```

### Node Dependencies (for Tailwind CSS)
```bash
npm install
```

## Step 2: Build Tailwind CSS

```bash
npm run build:css
```

For development with auto-rebuild:
```bash
npm run watch:css
```

## Step 3: Configure Database

Your `.env` file is already configured with your Neon database connection. Verify the `DATABASE_URL` is correct:

```env
DATABASE_URL=postgresql://neondb_owner:npg_Ib9uLdaeE5vi@ep-wispy-haze-a4bjv9hf-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

## Step 4: Initialize Database

```bash
# Initialize Flask-Migrate (creates migrations folder)
flask db init

# Create initial migration
flask db migrate -m "Initial models"

# Apply migration to database
flask db upgrade
```

## Step 5: Run the Application

```bash
python run.py
```

The application will be available at: **http://localhost:5000**

## Step 6: Create Your First Account

1. Navigate to http://localhost:5000/auth/register
2. Register with your email and password
3. Login and start uploading documents!

## Common Tasks

### Upload a Document
1. Login to your dashboard
2. Click "Upload Document"
3. Select PDF, DOCX, or PPTX file (up to 50MB)
4. Click "Upload Document"

### Create a Shareable Link
1. From your dashboard, click "Share" on any document
2. Click "Create New Link"
3. Configure settings:
   - Password protection (optional)
   - Email capture requirement (recommended)
   - Expiration date (optional)
   - View limit (optional)
   - Download permission
4. Click "Create Link"
5. Copy the generated link and share it!

### View Analytics
1. From your dashboard, click "Analytics" on any document
2. See:
   - Total views and unique viewers
   - Individual view sessions with duration
   - Pages viewed per session
   - Captured emails from viewers

## Document Conversion

### Windows/Mac (Development)
The app uses `docx2pdf` which works automatically.

### Linux (Production)
Install LibreOffice for document conversion:

```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# CentOS/RHEL
sudo yum install libreoffice
```

## Troubleshooting

### Database Connection Issues
- Verify your Neon database is active
- Check DATABASE_URL in .env file
- Ensure SSL is enabled (required by Neon)

### CSS Not Loading
```bash
npm run build:css
```

### Migration Errors
```bash
# Reset migrations (WARNING: This will delete all data)
rm -rf migrations
flask db init
flask db migrate -m "Initial models"
flask db upgrade
```

### File Upload Errors
- Check that `app/static/uploads/` directory exists
- Verify file size is under 50MB
- Ensure file type is PDF, DOCX, or PPTX

## Security Notes

- Change `SECRET_KEY` in production
- Use HTTPS in production (set `SESSION_COOKIE_SECURE=True`)
- Keep database credentials secure
- Regularly backup your database

## Next Steps

- Share documents with clients
- Track viewing analytics
- Monitor engagement metrics
- Collect leads through email capture

Need help? Check README.md for detailed documentation.
