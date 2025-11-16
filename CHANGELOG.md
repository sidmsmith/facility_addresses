# Changelog

All notable changes to the Site Identification Developer web application will be documented in this file.

## [2.0.0] - 2025-01-XX

### Major Release - Production Ready

This is the first major release (v2.0.0) of the web application, representing a complete migration from the Python desktop application with significant enhancements.

### Added
- **Complete Web Migration**: Full migration from Python CustomTkinter desktop app to web application
- **Auto-Load File Upload**: JSON files automatically load when selected (no button click required)
- **Comprehensive Input Validation**: Pre-API validation of facility input format
  - Validates each city/state pair before geocoding
  - Detects format errors (too many commas, missing parts, etc.)
  - Provides specific error messages with pair numbers
- **State Abbreviation Correction**: Automatically extracts and corrects state abbreviations from geocoding
  - Handles full state names (e.g., "Georgia" → "GA")
  - Uses reverse geocoding data to override user input
  - Includes US state name to abbreviation mapping
- **Real-Time Progress Updates**: Detailed progress messaging during geocoding
  - Shows current facility being geocoded: "Geocoding City, State (1/4)..."
  - Updates progress bar after each completion
  - Displays completion status for each facility
- **Improved Parsing Logic**: Robust parsing of city/state pairs
  - Handles semicolon-separated pairs: "City, State; City, State"
  - Supports multi-word cities and states (e.g., "New York, New York")
  - Validates format before processing
- **localStorage Persistence**: Saves user preferences
  - Facilities list saved automatically
  - Defaults to original Python app values on first use
  - Clear Saved button to reset preferences
- **Enhanced Error Handling**: 
  - File upload errors with automatic cleanup
  - JSON validation errors with clear messages
  - Geocoding errors per facility

### Changed
- **UI Simplification**: Removed output filename input (defaults to FacilityAddresses.json)
- **Button Text**: Changed "1. Generate & Open JSON" to "Generate JSON"
- **File Upload UX**: Removed "Use This File" button - files auto-load on selection
- **Layout Improvements**: Moved file upload section and Clear Saved button for better organization

### Fixed
- Fixed parsing bug where only first semicolon was replaced, causing incorrect pair splitting
- Fixed state abbreviation handling for full state names
- Fixed progress bar calculation to update after each completion
- Fixed validation to catch format errors before API calls

### Technical Details
- **Frontend**: HTML/JavaScript with Bootstrap 5.3.3
- **Backend**: Flask API deployed on Vercel serverless functions
- **Geocoding**: OpenStreetMap Nominatim API with rate limiting (1.1s delay)
- **API Integration**: Manhattan WMS Facility Bulk Import API
- **Environment Variables**: Same authentication as appointment app (MANHATTAN_PASSWORD, MANHATTAN_SECRET)

---

## [1.0.0] - 2025-01-XX

### Initial Release
- Basic web application structure
- Authentication with Manhattan API
- Facility geocoding and JSON generation
- File upload and download
- Upload to Manhattan WMS

