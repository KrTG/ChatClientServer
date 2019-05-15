from serverThread import ServerThread
import tkinter as tk

WIDTH = 300
HEIGHT = 500

class ServerApp(tk.Frame):
    """ 
    The chat server GUI. Starts the server and displays connected users.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.server = ServerThread()
        self.server.add_observer(self)
        self.create_elements()

    def start(self):
        """Starts the server thread and the GUI"""
        self.server.start()
        self.mainloop()

    def stop(self):
        """ Stops the client thread and closes the program"""
        self.server.stop()
        self.master.destroy()

    def create_elements(self):
        """Initializes all the widgets"""
        client_list_label = tk.Label(self, text="List of connected clients")
        client_list_label.pack(side=tk.TOP)
        self.client_list = tk.Listbox(self)
        self.client_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL,
                                      command=self.client_list.yview)        
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.client_list.config(yscrollcommand=self.scrollbar.set)

        self.pack(fill=tk.BOTH, expand=True)

    def notify(self, clients):
        """
        Function used by the ServerThread to pass the usernames
        of the connected users after connection/disconnections.
        
        Parameters:
        clients (list): List of strings with usernames
        """
        self.client_list.delete(0, tk.END)
        for client in clients:
            self.client_list.insert(tk.END, client)
                
if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("Chat server")
    root.minsize(WIDTH, HEIGHT)
    
    app = ServerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    app.start()
        