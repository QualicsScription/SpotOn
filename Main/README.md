# SpotOn - Advanced File Comparator (Beta 2.1.0)

SpotOn is a professional file comparison tool designed to compare files in various formats (SolidWorks, CAD, Documents, Images, etc.) with advanced similarity analysis.

> **Note:** This is a beta version. Some features may not be fully stable.

## Features
- Compare files based on metadata, hash, content, and structure.
- Visual analysis with pie charts for similarity distribution.
- Detailed analysis with file information and comparison details.
- Multi-language support (English, Turkish).
- Customizable dark theme UI.
- Export results to CSV or HTML reports.
- Sortable table columns for better data analysis.
- Improved tab display with better visibility.
- Enhanced language switching with full UI updates.

## Installation
1. Navigate to the `Main` directory:
   ```bash
   cd C:\SpotOn\Main
   ```

## Project Structure

- All modules are organized under the `src/` directory:
  - `src/core/`: Comparison logic
  - `src/ui/`: UI components
  - `src/resources/`: Color and style definitions
  - `src/languages/`: Language files and `LanguageManager`

## Installation and Running

1. Create and activate a virtual environment:
   ```powershell
   cd E:\Software\SpotOn\Main
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run the application:
   ```powershell
   python main.py
   ```

## Version History

- **2.1.0-beta**: Current beta version with improved UI and language support
- **2.0.0-alpha**: Initial alpha version with basic functionality

## Known Issues in Beta

- Some UI elements may not resize properly on different screen resolutions
- Performance may degrade with very large file sets

## Upcoming Features

- Advanced filtering options
- Batch processing capabilities
- Cloud storage integration