# Site Identification Developer - Web Application

**Version 2.0.0** - Production Ready Release

Web version of the Site Identification Developer (SID) tool, deployed on Vercel. This is a complete migration from the Python desktop application (`facilityaddress.py`) with enhanced features and improved user experience. This tool generates facility address data from city/state pairs and uploads it to Manhattan WMS.

## Setup Instructions

### 1. Environment Variables in Vercel

Add the following environment variables in your Vercel project settings:

#### Required:
- `MANHATTAN_PASSWORD` - Manhattan API password
- `MANHATTAN_SECRET` - Manhattan API client secret

### 2. Local Development

1. Install dependencies:
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. Set environment variables locally (create a `.env` file or export them):
   ```bash
   export MANHATTAN_PASSWORD="your_password"
   export MANHATTAN_SECRET="your_secret"
   ```

3. Run the development server:
   ```bash
   npm run dev
   # or
   vercel dev
   ```

### 3. Deployment

1. Connect your repository to Vercel
2. Add all environment variables in Vercel dashboard
3. Deploy!

## Features

### Core Functionality
- ✅ Authenticate with Manhattan API
- ✅ Enter facilities as "City, State; City, State" pairs
- ✅ Geocode addresses using OpenStreetMap Nominatim API
- ✅ Generate structured JSON with facility data
- ✅ Download generated JSON file
- ✅ Upload JSON to Manhattan WMS via bulk import API
- ✅ Upload existing JSON files (bypass generation step)

### User Experience
- ✅ Modern dark theme UI
- ✅ localStorage persistence for preferences (facilities list)
- ✅ Auto-load JSON files on selection (no button click needed)
- ✅ Real-time progress updates during geocoding
- ✅ Comprehensive input validation before API calls
- ✅ Editable JSON before upload
- ✅ Error handling and validation
- ✅ Default values for first-time users

### Validation & Error Handling
- ✅ Pre-API validation of facility input format
- ✅ State abbreviation auto-correction (handles "Georgia" → "GA")
- ✅ Multi-word city/state support ("New York, New York")
- ✅ Specific error messages with pair numbers
- ✅ File upload error handling

### Default Values
- **Facilities**: `Atlanta, GA;Jonestown, PA;Toronto, ON;Sydney, NSW`
- **Output Filename**: `FacilityAddresses.json` (automatic)

## API Endpoints

- `POST /api/app_opened` - Track app open event
- `POST /api/auth` - Authenticate with Manhattan API
- `POST /api/geocode` - Geocode a single city/state pair
- `POST /api/generate` - Generate facility addresses JSON from city/state pairs
- `POST /api/upload` - Upload facility addresses JSON to Manhattan WMS

## Project Structure

```
facility_addresses/
├── api/
│   ├── index.py          # Flask API endpoints
│   └── vercel.json       # Vercel configuration
├── index.html            # Frontend UI
├── server.js             # Express server (for local dev)
├── package.json          # Node.js dependencies
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── CHANGELOG.md         # Version history and release notes
```

## Workflow

1. **Authenticate**: Enter ORG and authenticate
2. **Enter Facilities**: Input city/state pairs (e.g., "Atlanta, GA;Jonestown, PA")
   - Format: `"City, State; City, State"`
   - Supports multi-word cities/states: `"New York, New York"`
   - Validation occurs before geocoding
3. **Generate**: Click "Generate JSON" to geocode addresses and create JSON
   - Shows real-time progress for each facility
   - Automatically corrects state abbreviations
4. **Review/Edit**: Review and edit the generated JSON if needed
5. **Download** (optional): Download the JSON file (defaults to FacilityAddresses.json)
6. **Upload**: Click "Upload to WM" to import to Manhattan WMS
   - Or upload an existing JSON file (auto-loads on selection)

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

**Current Version:** 2.0.0 (Major Release)

## Notes

- Geocoding uses OpenStreetMap Nominatim API with rate limiting (1.1s delay between requests)
- Generated JSON follows Manhattan WMS facility import format
- State abbreviations are automatically corrected from geocoding data
- Preferences (facilities list) are saved in browser localStorage
- ORG is never saved (security)
- File uploads automatically load into the editor (no button click required)

