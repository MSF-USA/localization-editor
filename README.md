# Localization Editor for MSF AI Assistant

## Overview

This is a GUI-based localization editor designed to assist with creating and managing localization files for the [MSF AI Assistant website](https://github.com/MSF-USA/chatbot-ui). The tool simplifies the process of handling multiple language translations by providing an intuitive interface for editing, adding, and generating translations.

It is very ugly and works in a very narrow way currently. Code is also not well arranged and should be broken up considerably if use gets expanded in any way.

But it serves a very practical purpose, so publishing it anyway.

## Features

- **Locale Folder Management**: Easily open and manage the locales directory used by the MSF AI Assistant website.
- **File and Key Management**:
  - View all localization files and keys in a tree structure.
  - Add new localization files directly from the interface.
  - Add new keys to existing localization files.
- **Localization Value Editing**:
  - Edit values for each key across different locales.
  - Use AI-assisted translation generation powered by OpenAI, making use of structured output.
- **Statistics Display**:
  - View total keys, filled keys, empty keys, and completion percentage to track localization progress. The only work on a per-file basis
- **Keyboard Shortcuts**:
  - **Ctrl+O**: Open Locales Folder
  - **Ctrl+S**: Save Changes
  - **Ctrl+Q**: Exit the application
- **Context Menus and Navigation**:
  - Right-click context menus for tree and table views.
  - Keyboard navigation within the tables.

## Installation

### Prerequisites

- **Python 3.x** installed on your system.
- **OpenAI API Key**: Required for AI-assisted translation generation. You can obtain one from the [OpenAI website](https://platform.openai.com/account/api-keys).

### Clone the Repository

```bash
git clone https://github.com/YourUsername/localization-editor.git
cd localization-editor
```

### Install Dependencies

#### Using `pyproject.toml` (Recommended)

```bash
pip install --upgrade pip
```

Then install the project:

```bash
pip install .
```

#### Using `requirements.txt`

Alternatively, you can install dependencies directly:

```bash
pip install -r requirements.txt
```

### Set Up OpenAI API Key

Set the `OPENAI_API_KEY` environment variable with your OpenAI API key. Currently this is setup for the regular OpenAI. Because the localizations are for an open-source project, this doesn't cause any issues. OpenAI is used because it has structured responses, which provide more guarantees for getting the desired outputs in the required format.

**For Windows Command Prompt:**

```cmd
set OPENAI_API_KEY=your-api-key
```

**For Windows PowerShell:**

```powershell
$env:OPENAI_API_KEY="your-api-key"
```

**For Unix/Linux/MacOS:**

```bash
export OPENAI_API_KEY='your-api-key'
```

## Configuration

## Usage

Run the application:

```bash
python main.py
```

### Main Interface

- **File Menu**:
  - **Open Locales Folder (Ctrl+O)**: Select the directory containing your localization files.
  - **Save Changes (Ctrl+S)**: Save all modifications to the localization files.
  - **Exit (Ctrl+Q)**: Exit the application.

- **Files Treeview (Left Panel)**:
  - Displays all localization files.
  - **Add File**: Add a new localization file.
  - **Add Key**: Add a new key to the selected file.
  - Right-click for context menu options.

- **Localization Table (Right Panel)**:
  - Displays keys and their values across different locales.
  - Double-click or press **Enter** on a cell to edit its value.
  - Right-click for context menu options.

### Editing Values

- Select a key and double-click or press **Enter** to open the **Edit Value Dialog**.
- **Edit Value Dialog**:
  - **Key**: View or edit the key name.
  - **Locales**: Edit values for each locale.
  - **AI Localization Generation**:
    - **Use Custom Phrase for Generation**: Enable to use a custom phrase instead of the key for translation.
    - **Custom Phrase**: Provide a custom phrase to translate.
    - **Context (optional)**: Add context to improve translation accuracy.
    - **Generation Locale**: Specify the source language code (default is `'en'`).
    - **Overwrite Existing Values**: Choose whether to overwrite existing translations.
    - **Generate Translations**: Use OpenAI's GPT model to generate translations.
  - **Save**: Save the changes made to the key and values.

### Keyboard Shortcuts

- **Ctrl+O**: Open Locales Folder
- **Ctrl+S**: Save Changes
- **Ctrl+Q**: Exit the application
- **Up/Down Arrow Keys**: Navigate through items in lists and tables.
- **Enter**: Edit the selected key's value.

### Statistics Panel

- Located at the bottom of the right panel.
- Displays:
  - **Total Keys**: The total number of keys in the selected file.
  - **Filled Keys**: Number of keys that have translations in all locales.
  - **Empty Keys**: Number of keys missing translations in one or more locales.
  - **Completion**: The percentage of keys fully translated.

## Dependencies

- **Python Packages**:
  - `openai==1.52.0`
  - Other dependencies as listed in `requirements.txt`, though they we're all introduced as dependencies for openai.

- **Tkinter**: Standard Python interface to the Tk GUI toolkit (should be included with Python).

## Troubleshooting

- **OpenAI API Key Error**: If you encounter an error related to the OpenAI API key, ensure that the `OPENAI_API_KEY` environment variable is set correctly.
- **Other**: This is not a very well tested application at present, so I would expect there to be other issues.