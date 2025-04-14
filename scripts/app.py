import os
import shutil
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import random
import socket
import uuid

# Import the client functions from your backend
from client_backend import ls, get, put

# Generate a unique client ID and random color for this instance
CLIENT_ID = str(uuid.uuid4())[:8]
RANDOM_COLOR = "#{:06x}".format(random.randint(0, 0xFFFFFF))
HEADER_BG_COLOR = RANDOM_COLOR
TEXT_COLOR = "white" if sum(int(RANDOM_COLOR[i:i+2], 16) for i in (1, 3, 5)) < 384 else "black"

# --- Helper functions for the UI commands ---

def run_ls():
    """
    List remote files from the server.
    """
    try:
        args = {
            'host': entry_host.get(),
            'port': int(entry_port.get()),
            'key': entry_key.get(),
            'cipher': 'aes',
            'auth': False,
            'local': False,      # we want remote files
            'function': 'ls'     # explicitly set the function key
        }
        out_text.insert(tk.END, f"Client {CLIENT_ID}: Listing remote files...\n")
        remote_files = ls(args)
        if remote_files:
            pretty = "\n".join([f"{i}: {fname}" for i, fname in enumerate(remote_files)])
            out_text.insert(tk.END, pretty + "\n")
        else:
            out_text.insert(tk.END, "No files found or an error occurred.\n")
    except Exception as e:
        out_text.insert(tk.END, f"Error listing remote files: {e}\n")

def run_get():
    """
    Download (get) a file from the server.
    """
    filename = entry_get.get().strip()
    if not filename:
        messagebox.showerror("Error", "Please enter a filename to download.")
        return
    try:
        args = {
            'host': entry_host.get(),
            'port': int(entry_port.get()),
            'key': entry_key.get(),
            'cipher': 'aes',
            'auth': False,
            'filename': filename,
            'function': 'get'   # explicitly set the function key
        }
        out_text.insert(tk.END, f"Client {CLIENT_ID}: Downloading file: {filename}...\n")
        get(args)
        out_text.insert(tk.END, f"File '{filename}' downloaded successfully.\n")
    except Exception as e:
        out_text.insert(tk.END, f"Error downloading file: {e}\n")

def run_put():
    """
    Upload (put) a file to the server.
    """
    # Ask the user to select a file from disk (assumes client_files folder)
    file_path = filedialog.askopenfilename(initialdir="client_files", title="Select file to upload")
    if not file_path:
        return
    try:
        filename_only = os.path.basename(file_path)
        client_files_dir = "client_files"
        if not os.path.exists(client_files_dir):
            os.makedirs(client_files_dir)
        # Copy the file to the client_files folder if not already there
        dest = os.path.join(client_files_dir, filename_only)
        if os.path.abspath(file_path) != os.path.abspath(dest):
            shutil.copy(file_path, dest)
        args = {
            'host': entry_host.get(),
            'port': int(entry_port.get()),
            'key': entry_key.get(),
            'cipher': 'aes',
            'auth': False,
            'filename': filename_only,
            'function': 'put'  # explicitly set the function key
        }
        out_text.insert(tk.END, f"Client {CLIENT_ID}: Uploading file: {filename_only}...\n")
        put(args)
        out_text.insert(tk.END, f"File '{filename_only}' uploaded successfully.\n")
    except Exception as e:
        out_text.insert(tk.END, f"Error uploading file: {e}\n")

# --- Build the main Tkinter UI window ---
root = tk.Tk()
root.title(f"Secure File Transfer - Client {CLIENT_ID}")

# Client ID Banner at the top
frame_banner = tk.Frame(root, bg=HEADER_BG_COLOR, padx=10, pady=10)
frame_banner.pack(side=tk.TOP, fill=tk.X)
label_banner = tk.Label(frame_banner, 
                       text=f"CLIENT {CLIENT_ID}",
                       font=("Arial", 16, "bold"),
                       bg=HEADER_BG_COLOR,
                       fg=TEXT_COLOR)
label_banner.pack(side=tk.LEFT, padx=5)

# Top frame: Connection & encryption parameters
frame_top = tk.Frame(root, bg="#f0f0f0")
frame_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

tk.Label(frame_top, text="Host:", bg="#f0f0f0").pack(side=tk.LEFT)
entry_host = tk.Entry(frame_top, width=12)
entry_host.insert(0, "127.0.0.1")
entry_host.pack(side=tk.LEFT, padx=5)

tk.Label(frame_top, text="Port:", bg="#f0f0f0").pack(side=tk.LEFT)
entry_port = tk.Entry(frame_top, width=6)
entry_port.insert(0, "65432")
entry_port.pack(side=tk.LEFT, padx=5)

tk.Label(frame_top, text="Key:", bg="#f0f0f0").pack(side=tk.LEFT)
entry_key = tk.Entry(frame_top, width=70)
entry_key.insert(0, "c37ddfe20d88021bc66a06706ac9fbdd0bb2dc0b043cf4d22dbbbcda086f0f48")
entry_key.pack(side=tk.LEFT, padx=5)

# Middle frame: Buttons and input for Get command
frame_buttons = tk.Frame(root, bg="#e0e0e0")
frame_buttons.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

btn_ls = tk.Button(frame_buttons, text="List Remote Files", 
                   command=lambda: threading.Thread(target=run_ls).start(),
                   bg=HEADER_BG_COLOR, fg=TEXT_COLOR)
btn_ls.pack(side=tk.LEFT, padx=5)

tk.Label(frame_buttons, text="Get File:", bg="#e0e0e0").pack(side=tk.LEFT)
entry_get = tk.Entry(frame_buttons, width=30)
entry_get.pack(side=tk.LEFT, padx=5)

btn_get = tk.Button(frame_buttons, text="Download", 
                    command=lambda: threading.Thread(target=run_get).start(),
                    bg=HEADER_BG_COLOR, fg=TEXT_COLOR)
btn_get.pack(side=tk.LEFT, padx=5)

btn_put = tk.Button(frame_buttons, text="Upload File", 
                    command=lambda: threading.Thread(target=run_put).start(),
                    bg=HEADER_BG_COLOR, fg=TEXT_COLOR)
btn_put.pack(side=tk.LEFT, padx=5)

# Bottom frame: Output console with custom border
frame_output_container = tk.Frame(root, bg=HEADER_BG_COLOR, padx=3, pady=3)
frame_output_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

frame_output = tk.Frame(frame_output_container)
frame_output.pack(fill=tk.BOTH, expand=True)

out_text = scrolledtext.ScrolledText(frame_output, width=90, height=20)
out_text.pack(fill=tk.BOTH, expand=True)

# Add client ID identifier to the console
out_text.insert(tk.END, f"==== Client {CLIENT_ID} Initialized ====\n")
out_text.insert(tk.END, f"Window Color: {RANDOM_COLOR}\n\n")

# Set window size and position (slightly offset for each instance)
window_width = 800
window_height = 500
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Generate a position offset based on the client ID hash
offset_x = (int(CLIENT_ID, 16) % 10) * 30
offset_y = (int(CLIENT_ID, 16) % 8) * 30

x = (screen_width - window_width) // 2 + offset_x
y = (screen_height - window_height) // 2 + offset_y

root.geometry(f"{window_width}x{window_height}+{x}+{y}")

root.mainloop()
