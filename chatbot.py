import os
import importlib
import subprocess

from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig, BitsAndBytesConfig
from accelerate import init_empty_weights
import torch

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf




class ChatWidget(Gtk.Window):
    def __init__(self):
        super(ChatWidget, self).__init__()
        global MODEL_NAME, MODEL_FILE, PROMPT_INSTRUCTION
        self.set_default_size(1280, 720)  # Set window size to 1280x720
        self.connect("destroy", Gtk.main_quit)
        self.set_title("ChatBot")
        
        # Load the ICO icon
        #icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file("app.ico")  # Replace with your ICO file path
        #self.set_icon(icon_pixbuf)

        # Create a grid to arrange elements horizontally
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        
        # Create a scrolled text view for displaying messages
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_cursor_visible(False)
        
        # Create a text buffer for the text view
        self.buffer = self.textview.get_buffer()
        
        # Create a scrolled window to contain the text view
        scrolled_window = Gtk.ScrolledWindow()
        # Make the text view expand both vertically and horizontally
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.textview)
        
        # Create an entry for entering text
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Type your message here...")
        
        # Create a send button
        self.button = Gtk.Button(label="Send")
        self.button.connect("clicked", self.on_send_button_clicked)

        # Connect the "delete-event" signal to close the window properly
        self.connect("delete-event", self.on_window_closed)      

        # Add elements to the grid
        grid.attach(scrolled_window, 0, 0, 1, 1)
        grid.attach(self.entry, 0, 1, 1, 1)
        grid.attach(self.button, 0, 2, 1, 1)
        
        # Add the grid to the window
        self.add(grid)

        # Initialize 
        self.device = "cuda"
        self.max_new_tokens = 1024
        self.cache_dir = None # set optional cache directory
        self.base_model_name = 'FelixChao/WestSeverus-7B-DPO-v2'  #'NousResearch/Yarn-Mistral-7b-128k'
        self.instruction = """
Chain of Thought: Process the information thoroughly. Understand the user's query in its entirety before formulating a response. Think step-by-step, ensuring a logical flow in the conversation.
Positivity: Maintain a friendly and positive demeanor throughout the conversation. Even in challenging situations, approach problems with a solution-oriented mindset.
Confidentiality: Respect user privacy. Do not ask for or disclose sensitive information. If users share sensitive data, avoid acknowledging it and gently guide the conversation to a safer topic.
Safety First: Prioritize the safety and well-being of users and others. Refrain from providing instructions that could cause harm or pose a risk.
Role: Your name is ChatBot. You are a friendly AI chat assistant. Be safe. Be smart. This concludes your primary instruction. You will now be continue to the User's Request.
"""

        self.llm = None
        with init_empty_weights(): 
            self.llm = AutoModelForCausalLM.from_pretrained(self.base_model_name,  
                load_in_4bit=True, cache_dir=self.cache_dir)
        self.context_length: int = 32 * 1000 
        self.model_config = AutoConfig.from_pretrained(self.base_model_name, context_length=self.context_length, cache_dir=self.cache_dir) 
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name, config=self.model_config, cache_dir=self.cache_dir) 
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "right"  # Fix weird overflow issue with fp16 training
            self.tokenizer.truncation_side = "right"

        self.load_chat_history()

    def generate_output(self, user_input: str = '', eos_tags=[], eos_token=''):
        prompt_len: int = len(user_input) + 3 # + amount of line breaks
        inputs = self.tokenizer(str(user_input), truncation=True, padding=True, max_length=self.max_new_tokens, return_tensors='pt').to(self.device)
        with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False):
            output_token_ids = self.llm.generate(**inputs, max_new_tokens=self.max_new_tokens, temperature=0.7, 
                eos_token_id=self.tokenizer.convert_tokens_to_ids(self.tokenizer.eos_token), repetition_penalty=1.2, do_sample=True)
        output_result = self.tokenizer.decode(output_token_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=False) 
        filtered_result = ''
        if str(eos_tags[0]) in str(output_result):
            filtered_result = output_result.split(str(eos_tags[0])).pop()
        else:
            filtered_result = output_result[:prompt_len]
        for a in eos_tags:
            if a in filtered_result:
                filtered_result = filtered_result.replace(a, "")
        num_tokens_used = len(output_token_ids[0])
        return filtered_result

    def fill_template_mistral(self, prompt_with_context, input_prompt):
        full_prompt = f"<s>[INST]<<SYS>>\n{prompt_with_context}\n<</SYS>>\n\n [User_Prompt]: \n {input_prompt} \n\n [/INST][AI_Response]:\n"
        eos_tags = ["[AI_Response]:\n", "[/INST]", "[/AI_Response]"]
        eos_token = "</s>"
        return full_prompt, eos_tags, eos_token

    def generate_llm_response(self, user_input):
        filled_temp, eos_tags, eos_token = self.fill_template_mistral(self.instruction, user_input)
        ai_response = self.generate_output(filled_temp, eos_tags, eos_token)
        return ai_response



    def on_send_button_clicked(self, widget):
        # Get the text from the entry
        text = self.entry.get_text()
        
        if text:
            print(f"Input Recieved: {text}")
            # Append user's message to the text view
            end_iter = self.buffer.get_end_iter()
            self.buffer.insert(end_iter, f"You: {text}\n")
            
            # Generate a response using the LLM model
            response = self.generate_llm_response(text)
            print(f"Response Recieved: {response}")
            
            # Append LLM's response to the text view
            end_iter = self.buffer.get_end_iter()
            self.buffer.insert(end_iter, f"AI: {response}\n")
            
            # Save the chat history to a file
            self.save_chat_history()
            
            # Clear the entry field
            self.entry.set_text("")

    def on_window_closed(self, widget, event):
        # Save chat history to a file before closing the window
        self.save_chat_history()
        Gtk.main_quit()

    def load_chat_history(self):
        chat_history_file = "chat_history.txt"  # Replace with the path to your chat history file
        if os.path.exists(chat_history_file):
            with open(chat_history_file, "r") as file:
                chat_history = file.read()
                self.buffer.set_text(chat_history)
                
    def save_chat_history(self):
        chat_history_file = "chat_history.txt"  # Replace with the path to your chat history file
        chat_history = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), False)
        with open(chat_history_file, "w") as file:
            file.write(chat_history)

# Create an instance 
widget = ChatWidget()

# Show all elements in the window
widget.show_all()

# Start the GTK main loop
Gtk.main()
