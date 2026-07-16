import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import git
import os
import subprocess
import threading
from datetime import datetime

class GitSimplifiedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Simplified - One-Click Git Commands")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.repo_path = tk.StringVar(value=os.getcwd())
        self.clone_url = tk.StringVar()
        self.commit_message = tk.StringVar()
        self.branch_name = tk.StringVar()
        self.remote_name = tk.StringVar(value="origin")
        self.status_text = tk.StringVar(value="Ready")
        self.repo = None
        
        self.create_widgets()
        self.check_git_repo()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(main_frame, text="🚀 Git Simplified", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=10, sticky=tk.W)
        
        path_frame = ttk.LabelFrame(main_frame, text="Repository Location", padding="10")
        path_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        ttk.Label(path_frame, text="Path:").grid(row=0, column=0, sticky=tk.W)
        path_entry = ttk.Entry(path_frame, textvariable=self.repo_path, width=60)
        path_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Button(path_frame, text="Browse...", command=self.browse_repo).grid(row=0, column=2, padx=5)
        ttk.Button(path_frame, text="Refresh", command=self.check_git_repo).grid(row=0, column=3)
        
        clone_frame = ttk.LabelFrame(main_frame, text="Clone Repository", padding="10")
        clone_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        clone_frame.columnconfigure(1, weight=1)
        
        ttk.Label(clone_frame, text="URL:").grid(row=0, column=0, sticky=tk.W)
        url_entry = ttk.Entry(clone_frame, textvariable=self.clone_url, width=60)
        url_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Button(clone_frame, text="📥 Clone", command=self.clone_repo).grid(row=0, column=2, padx=5)
        
        action_frame = ttk.LabelFrame(main_frame, text="Quick Actions", padding="10")
        action_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        action_frame.columnconfigure(0, weight=1)
        
        button_frame1 = ttk.Frame(action_frame)
        button_frame1.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(button_frame1, text="📊 Status", command=self.show_status, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame1, text="➕ Add All", command=self.add_all, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame1, text="📝 Commit", command=self.commit_changes, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame1, text="⬆️ Push", command=self.push_changes, width=15).pack(side=tk.LEFT, padx=2)
        
        button_frame2 = ttk.Frame(action_frame)
        button_frame2.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(button_frame2, text="⬇️ Pull", command=self.pull_changes, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame2, text="🌿 New Branch", command=self.create_branch, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame2, text="🔄 Switch Branch", command=self.switch_branch, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame2, text="📋 Log", command=self.show_log, width=15).pack(side=tk.LEFT, padx=2)
        
        msg_frame = ttk.LabelFrame(main_frame, text="Commit Message", padding="10")
        msg_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        msg_frame.columnconfigure(1, weight=1)
        
        ttk.Label(msg_frame, text="Message:").grid(row=0, column=0, sticky=tk.W)
        msg_entry = ttk.Entry(msg_frame, textvariable=self.commit_message, width=60)
        msg_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(msg_frame, text="Commit & Push", command=self.commit_and_push).grid(row=0, column=2, padx=5)
        
        output_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="10")
        output_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = tk.Text(output_frame, height=10, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.output_text['yscrollcommand'] = scrollbar.set
        
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=5)
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_text, 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        main_frame.rowconfigure(5, weight=1)
        
    def browse_repo(self):
        directory = filedialog.askdirectory(title="Select Git Repository")
        if directory:
            self.repo_path.set(directory)
            self.check_git_repo()
    
    def check_git_repo(self):
        path = self.repo_path.get()
        try:
            self.repo = git.Repo(path)
            branch = self.repo.active_branch.name
            self.status_text.set(f"✅ Git repository found - Branch: {branch}")
            self.log_output(f"📁 Repository at: {path}\n🌿 Current branch: {branch}")
            return True
        except (git.InvalidGitRepositoryError, ValueError):
            self.repo = None
            self.status_text.set("⚠️ Not a git repository")
            self.log_output(f"⚠️ {path} is not a git repository")
            return False
    
    def log_output(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
    
    def run_git_command(self, command_func, success_msg, error_msg):
        if not self.repo and command_func.__name__ != 'clone_repo':
            messagebox.showerror("Error", "No git repository found. Please select a valid git repo.")
            return
        
        def execute():
            try:
                self.status_text.set(f"⏳ Running {command_func.__name__}...")
                self.root.config(cursor="watch")
                result = command_func()
                self.log_output(f"✅ {success_msg}")
                self.status_text.set(f"✅ {success_msg}")
                return result
            except Exception as e:
                error_message = str(e)
                self.log_output(f"❌ {error_msg}: {error_message}")
                self.status_text.set(f"❌ {error_msg}")
                messagebox.showerror("Error", f"{error_msg}\n{error_message}")
            finally:
                self.root.config(cursor="")
        
        threading.Thread(target=execute, daemon=True).start()
    
    def clone_repo(self):
        url = self.clone_url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a repository URL")
            return
        
        path = self.repo_path.get()
        
        def clone():
            try:
                self.status_text.set("⏳ Cloning repository...")
                self.log_output(f"📥 Cloning from: {url}")
                self.repo = git.Repo.clone_from(url, path)
                self.status_text.set("✅ Repository cloned successfully")
                self.log_output("✅ Repository cloned successfully")
                messagebox.showinfo("Success", "Repository cloned successfully!")
                return True
            except Exception as e:
                self.status_text.set("❌ Clone failed")
                self.log_output(f"❌ Clone failed: {str(e)}")
                messagebox.showerror("Error", f"Clone failed:\n{str(e)}")
                return False
        
        threading.Thread(target=clone, daemon=True).start()
    
    def show_status(self):
        if not self.repo:
            return
        
        def status():
            try:
                status_output = self.repo.git.status()
                self.log_output(f"📊 Status:\n{status_output}")
                return True
            except Exception as e:
                self.log_output(f"❌ Status failed: {str(e)}")
                return False
        
        self.run_git_command(status, "Status shown", "Status failed")
    
    def add_all(self):
        if not self.repo:
            return
        
        def add():
            self.repo.git.add('.')
            self.log_output("➕ Added all changes")
            return True
        
        self.run_git_command(add, "All changes added", "Add all failed")
    
    def commit_changes(self):
        if not self.repo:
            return
        
        msg = self.commit_message.get().strip()
        if not msg:
            messagebox.showerror("Error", "Please enter a commit message")
            return
        
        def commit():
            self.repo.index.commit(msg)
            self.log_output(f"📝 Committed: {msg}")
            self.commit_message.set("")
            return True
        
        self.run_git_command(commit, f"Committed: {msg}", "Commit failed")
    
    def push_changes(self):
        if not self.repo:
            return
        
        def push():
            origin = self.repo.remote(name=self.remote_name.get())
            origin.push()
            branch = self.repo.active_branch.name
            self.log_output(f"⬆️ Pushed to {self.remote_name.get()}/{branch}")
            return True
        
        self.run_git_command(push, "Changes pushed successfully", "Push failed")
    
    def pull_changes(self):
        if not self.repo:
            return
        
        def pull():
            origin = self.repo.remote(name=self.remote_name.get())
            origin.pull()
            branch = self.repo.active_branch.name
            self.log_output(f"⬇️ Pulled from {self.remote_name.get()}/{branch}")
            return True
        
        self.run_git_command(pull, "Changes pulled successfully", "Pull failed")
    
    def commit_and_push(self):
        if not self.repo:
            return
        
        msg = self.commit_message.get().strip()
        if not msg:
            messagebox.showerror("Error", "Please enter a commit message")
            return
        
        def commit_push():
            self.repo.index.commit(msg)
            self.log_output(f"📝 Committed: {msg}")
            
            origin = self.repo.remote(name=self.remote_name.get())
            origin.push()
            branch = self.repo.active_branch.name
            self.log_output(f"⬆️ Pushed to {self.remote_name.get()}/{branch}")
            
            self.commit_message.set("")
            return True
        
        self.run_git_command(commit_push, "Committed and pushed", "Commit and push failed")
    
    def create_branch(self):
        if not self.repo:
            return
        
        branch_name = self.branch_name.get().strip()
        if not branch_name:
            branch_name = tk.simpledialog.askstring("New Branch", "Enter branch name:")
            if not branch_name:
                return
        
        def create():
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            self.log_output(f"🌿 Created and switched to branch: {branch_name}")
            self.branch_name.set("")
            return True
        
        self.run_git_command(create, f"Created branch: {branch_name}", "Branch creation failed")
    
    def switch_branch(self):
        if not self.repo:
            return
        
        branches = [b.name for b in self.repo.heads]
        if not branches:
            messagebox.showerror("Error", "No branches found")
            return
        
        branch_name = tk.simpledialog.askstring("Switch Branch", 
                                               f"Available branches:\n{', '.join(branches)}\n\nEnter branch name:")
        if not branch_name:
            return
        
        if branch_name not in branches:
            messagebox.showerror("Error", f"Branch '{branch_name}' not found")
            return
        
        def switch():
            self.repo.git.checkout(branch_name)
            self.log_output(f"🔄 Switched to branch: {branch_name}")
            return True
        
        self.run_git_command(switch, f"Switched to branch: {branch_name}", "Branch switch failed")
    
    def show_log(self):
        if not self.repo:
            return
        
        def log():
            log_output = self.repo.git.log('--oneline', '-n', '10')
            self.log_output(f"📋 Recent commits:\n{log_output}")
            return True
        
        self.run_git_command(log, "Log shown", "Log failed")

def main():
    root = tk.Tk()
    app = GitSimplifiedApp(root)
    
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
