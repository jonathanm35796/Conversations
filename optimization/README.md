# Desktop File Organizer

A GUI-based tool for organizing files in directories based on their types and functions. This application helps you maintain a clean and organized file structure by automatically categorizing files into appropriate folders.

## Features

- Graphical user interface for easy file management
- Preview proposed file moves before applying changes
- Customizable file categories via JSON configuration
- Detailed logging of all file operations
- Support for common file types including programs, documents, images, and videos

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses standard library only)

## Usage

1. Run the application:
```bash
python file_organizer.py
```

2. Click "Browse" to select the directory you want to organize

3. Click "Analyze" to see the proposed file organization

4. Review the changes in the treeview:
   - File Name: Name of the file
   - Current Location: Current path of the file
   - Proposed Location: Where the file will be moved
   - Status: Current status of the operation (Pending/Done/Failed)

5. Click "Apply Changes" to execute the file moves after confirming

## Configuration

The application uses a configuration file (`organizer_config.json`) that defines file categories and their associated extensions. The default categories are:

- Development (.py, .java, .cpp, etc.)
- Documents (.pdf, .doc, .docx, etc.)
- Images (.jpg, .jpeg, .png, etc.)
- Videos (.mp4, .avi, .mov, etc.)
- Utilities (.exe, .msi, .bat, etc.)
- Archives (.zip, .rar, .7z, etc.)

You can modify this configuration file to customize the categorization rules.

## Log File

All file operations are logged in `file_organizer.log` for tracking and troubleshooting purposes.
