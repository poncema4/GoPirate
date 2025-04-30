# Chat-Bot
Interactive Chat Bot that allows the user to communicate with the bot which is able to handle any questions that is stored in the JSON database

## Prerequisites
  
- **pip install pytest**

## Installation

1. **Install Dependencies**

Make sure you are using the latest python version in your IDE and the latest versions of the prerequisites/requirements.txt

2. **Usage**

Run the chat_bot.py file in the specified path that it is located on

```Command Prompt
   cd C:\path\to\folder
```

For example:

```Command Prompt
   cd C:\PYTHON\Chat-Bot
```

Most of the time though when you run this program, the IDE will automatically be able to retrive the correct file where you are trying to access the program from

3. **UML Diagram**

If you want to see the UML Diagram completely or create one of your own using a similar Java structure language, then follow these steps

   - Install VSCode
   - Go to extensions and install Plant UML
   - Create a file with ending .wsd 
   - Begin the UML diagram with @startuml "your_project_name"
   - End the UML diagram with @enduml
   - Click the book with a magnifying glass in the top right corner to see the full UML diagram

## Run Program

To make the chat bot more visually appealing for the user we want them to hide all the backend code that was implemented, so using the batch file attached
click on it or follow these steps:

1. **Notepad** -> (Skip this step if you already have the batch file)

```Notepad
@echo off
:: Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

:: Run the Python script from its original directory
cd /d "%SCRIPT_DIR%"
python chat_bot.py
```

This is what is in the batch file and should be in the same directory as the chat_bot.py, naming the batch file something like chat_bot.bat, already done by me.

2. **Open up Command Prompt** 

```Command Prompt -> Step 1
 cd C:\path\to\folder 
```

Then

```Command Prompt -> Step 2
chat_bot
```

After following these steps and typing step 1 and 2 into Command Prompt you should see get the chat bot working in the terminal without having to be in any IDE

![image](https://github.com/user-attachments/assets/bdb494b1-cc4e-40de-9d2c-6f73d098fd18)