# ChatBot with GTK and Transformers 🗣️💬

A simple AI chatbot application built using GTK for the Linux desktop environment. This chatbot utilizes the transformers library from Hugging Face to generate responses based on user input. The interface allows for a smooth conversational experience, with chat history being saved and loaded automatically.

## Features ✨

Interactive Chat Interface: Built with GTK, providing a clean and responsive UI.
AI-Powered Responses: Utilizes the transformers library for generating AI responses.
Chat History Management: Saves and loads chat history to and from a file.

## Requirements 📦

Python 3.7 or higher
```bash
Pip packages: packaging, torch, transformers, accelerate, PyGObject
```

## Installation 💻

### Clone the repository:
```bash
git clone https://github.com/yourusername/chatbot-gtk.git
cd chatbot-gtk
```

### Install the required packages:

Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate
```

### Install the dependencies:
```bash
pip install packaging torch transformers accelerate PyGObject
```

## Usage 🚀

Run the chatbot application:
```bash
python chatbot.py
```

Interface Overview:
    Text View: Displays chat history.
    Entry Field: Type your message here.
    Send Button: Click to send your message and receive a response.

Chat History:
    Chat history is automatically saved to chat_history.txt.
    The history is loaded each time the application starts.

## Customization ⚙️

    Model Selection: Change the model in the ChatWidget class by modifying the base_model_name variable to use a different transformer model.
    Chat History File: Update the path to the chat history file by modifying the chat_history_file variable in the load_chat_history and save_chat_history methods.

## Contributing 🤝

    Fork the repository and clone it to your local machine.
    Create a new branch for your changes.
    Make your changes and test them thoroughly.
    Submit a pull request with a clear description of your changes.

## License 📝

This project is licensed under the MIT License. See the LICENSE file for more details.
