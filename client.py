from clientThread import ClientThread

import tkinter as tk
import re

WIDTH = 400
HEIGHT = 400
PADDING_Y = 5
PADDING_X = 10
BACKGROUND = "snow3"
INPUTBOX_HEIGHT = 8

class UsernamePrompt(tk.Frame):
    """Prompts the user for a username"""
    def __init__(self, master=None):
        super().__init__(master, bg=BACKGROUND)
        self.username = None
        self.create_elements()        
    
    def create_elements(self):
        """Creates widgets for the prompt"""
        self.frame = tk.Frame(self, bg=BACKGROUND)
        self.frame.pack(fill=tk.X, expand=True, padx=PADDING_X)

        self.label = tk.Label(self.frame, text="Enter an username", bg=BACKGROUND)
        self.label.pack(fill=tk.X, pady=PADDING_Y)

        self.prompt = tk.Entry(self.frame)
        self.prompt.pack(fill=tk.X, pady=PADDING_Y)
        self.prompt.bind("<Return>", lambda _: self.choose_username())

        self.button = tk.Button(self.frame, text="Confirm", command=self.choose_username)
        self.button.pack(fill=tk.X, pady=PADDING_Y)
        
        self.pack(fill=tk.BOTH, expand=True)
        
    def choose_username(self):
        """
        Callback for the confirm button. Checks if the username
        is valid, if that is true saves it and closes the prompt.
        """
        username = self.prompt.get()        
        # Don't allow an empty username or with only blank characters
        if re.match(r"\S", username):            
            self.username = username
            self.pack_forget()
            self.quit()
            
    def get_username(self):
        """Returns the chosen username"""
        return self.username


class ClientApp(tk.Frame):
    """The chat client GUI"""

    def __init__(self, master=None, username=None):
        """
        Parameters:
        username (str): Name of the user
        """        
        super().__init__(master, bg=BACKGROUND)
        self.client = ClientThread(username)
        self.client.add_observer(self)
        self.create_elements()

    def start(self):
        """Starts the client thread and the GUI"""         
        self.client.start()
        self.mainloop()

    def stop(self):
        """ Stops the client thread and closes the program"""
        self.client.stop()
        self.master.destroy()

    def create_elements(self):
        """Creates widgets for the chat GUI"""
        chat_group = tk.Frame(self, bg=BACKGROUND)
        chat_group.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=PADDING_X, pady=PADDING_Y)  

        input_group = tk.Frame(self, bg=BACKGROUND)
        input_group.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=PADDING_X, pady=PADDING_Y)

        self.chat = tk.Text(chat_group, bg="white", state=tk.DISABLED,                                
                            wrap=tk.WORD)
        self.chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)        

        self.scrollbar = tk.Scrollbar(chat_group, orient=tk.VERTICAL,
                                      command=self.chat.yview)                
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat.configure(yscrollcommand=self.scrollbar.set)

        self.input_box = tk.Text(input_group, height=INPUTBOX_HEIGHT)
        self.input_box.pack(side=tk.TOP, fill=tk.BOTH, pady=PADDING_Y)

        def input_box_enter_handler(_):
            self.post_message()
            return "break"
        self.input_box.bind("<Return>", input_box_enter_handler)        

        self.post_button = tk.Button(input_group, text="Send", command=self.post_message)
        self.post_button.pack(side=tk.BOTTOM, fill=tk.BOTH, pady=5)
 
        self.pack(fill=tk.BOTH, expand=True)

    def clear_input_box(self):        
        self.input_box.delete("1.0", tk.END)

    def post_message(self):
        """Post the typed message to chat"""

        # Read input from line 1, character 0 (1.0) until the END (tk.END) and subtracting
        # the last newline character (-1c)
        message = self.input_box.get("1.0", tk.END + "-1c")
        self.clear_input_box()
        self.client.send_message(message)

    def notify(self, messages):
        """
        Function used by the ClientThread to pass new messages to the display
        
        Parameters:
        messages (list): List of strings containing the new chat messages
        """
        self.chat.configure(state=tk.NORMAL)
        for message in messages:
            self.chat.insert(tk.END, message + "\n")
        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("Chat client")
    root.minsize(WIDTH, HEIGHT)

    username_prompt = UsernamePrompt(root)
    username_prompt.mainloop()
    username = username_prompt.get_username()
    
    if username:
        app = ClientApp(root, username)
        root.protocol("WM_DELETE_WINDOW", app.stop)
        app.start()

    