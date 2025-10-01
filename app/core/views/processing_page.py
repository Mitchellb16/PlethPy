import tkinter as tk
from tkinter import ttk, messagebox

class ProcessingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        """Setup all UI elements for the processing page"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        self.setup_header()
        self.setup_plot_options()
        self.setup_plot_area()
        self.setup_action_buttons()
        self.setup_navigation()
    
    def setup_header(self):
        """Setup page header"""
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", pady=20)
        
        tk.Label(header_frame, text="Data Processing & Analysis", font=("Arial", 16, "bold")).pack()
        tk.Label(header_frame, text="Generate plots and export analysis results", 
                font=("Arial", 10), fg="gray").pack()
    
    def setup_plot_options(self):
        """Setup plot selection checkboxes"""
        options_frame = tk.LabelFrame(self, text="Plot Options", padx=10, pady=10)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        checkbox_frame = tk.Frame(options_frame)
        checkbox_frame.pack(fill="x")
        
        self.plot_vars = {}
        plot_options = [
            ("Raw Signal", "raw_signal"),
            ("Filtered Signal", "filtered_signal"),
            ("Peak Detection", "peak_detection"),
            ("Breathing Rate", "breathing_rate"),
            ("Volume Analysis", "volume_analysis"),
            ("Frequency Analysis", "frequency_analysis")
        ]
        
        for i, (display_name, var_name) in enumerate(plot_options):
            row = i // 2
            col = i % 2
            
            self.plot_vars[var_name] = tk.BooleanVar()
            tk.Checkbutton(checkbox_frame, text=display_name, variable=self.plot_vars[var_name],
                          command=self.on_plot_option_changed).grid(row=row, column=col, sticky="w", padx=20, pady=2)
        
        checkbox_frame.columnconfigure(0, weight=1)
        checkbox_frame.columnconfigure(1, weight=1)
    
    def setup_plot_area(self):
        """Setup plot display area"""
        plot_frame = tk.LabelFrame(self, text="Plots", padx=10, pady=10)
        plot_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(plot_frame, bg="white", height=300)
        scrollbar = tk.Scrollbar(plot_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.plot_canvas = canvas
        self.plot_frame = scrollable_frame
        
        tk.Label(scrollable_frame, text="Select plot options and click 'Generate Plots' to view results",
                font=("Arial", 12), fg="gray").pack(expand=True, pady=50)
    
    def setup_action_buttons(self):
        """Setup main action buttons"""
        action_frame = tk.Frame(self)
        action_frame.pack(fill="x", padx=20, pady=10)
        
        plot_btn_frame = tk.Frame(action_frame)
        plot_btn_frame.pack(side="left", fill="x", expand=True)
        
        self.plot_btn = tk.Button(plot_btn_frame, text="Generate Plots",
                                  command=self.controller.on_generate_plots_click,
                                  font=("Arial", 12, "bold"), bg="lightgreen", state="disabled")
        self.plot_btn.pack(fill="x")
        
        export_frame = tk.Frame(action_frame)
        export_frame.pack(side="right", padx=(20, 0))
        
        tk.Button(export_frame, text="Save / Export Results",
                 command=self.controller.on_export_results_click,
                 font=("Arial", 10), bg="lightblue").pack()
        
        self.export_format = tk.StringVar(value="PNG")
        format_frame = tk.Frame(export_frame)
        format_frame.pack(pady=(5, 0))
        
        tk.Label(format_frame, text="Format:").pack(side="left")
        ttk.Combobox(format_frame, textvariable=self.export_format,
                    values=["PNG", "PDF", "SVG", "CSV Data"], width=10, state="readonly").pack(side="right", padx=(5, 0))
    
    def setup_navigation(self):
        """Setup navigation buttons"""
        nav_frame = tk.Frame(self)
        nav_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Button(nav_frame, text="← Preprocessing",
                 command=lambda: self.controller.show_frame("PreprocessingPage")).pack(side="left")
        
        tk.Button(nav_frame, text="Home",
                 command=lambda: self.controller.show_frame("HomePage")).pack(side="right")
        
        self.status_label = tk.Label(nav_frame, text="Ready to generate plots", font=("Arial", 10), fg="blue")
        self.status_label.pack()
    
    def on_plot_option_changed(self):
        """Handle plot option checkbox changes"""
        any_selected = any(var.get() for var in self.plot_vars.values())
        self.plot_btn.config(state="normal" if any_selected else "disabled")
        
        if any_selected:
            selected_count = sum(var.get() for var in self.plot_vars.values())
            self.update_status(f"{selected_count} plot(s) selected", "blue")
        else:
            self.update_status("Select plot options to generate", "gray")
    
    def get_selected_plots(self):
        """Get list of currently selected plot options"""
        return [name for name, var in self.plot_vars.items() if var.get()]
    
    def update_status(self, message, color="blue"):
        """Update the status message"""
        self.status_label.config(text=message, fg=color)
    
    def clear_plots(self):
        """Clear the plot display area"""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
    
    def add_plot_placeholder(self, plot_name):
        """Add a placeholder for a plot"""
        plot_placeholder = tk.Frame(self.plot_frame, relief="ridge", bd=2, bg="lightgray")
        plot_placeholder.pack(fill="x", pady=5, padx=10)
        
        tk.Label(plot_placeholder, text=f"{plot_name} Plot", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(plot_placeholder, text=f"[{plot_name} visualization would appear here]",
                bg="white", relief="sunken", bd=1, height=8).pack(fill="x", padx=10, pady=(0, 10))
    
    def display_plots(self, plot_names):
        """Display the generated plots"""
        self.clear_plots()
        
        if not plot_names:
            tk.Label(self.plot_frame, text="No plots generated", 
                    font=("Arial", 12), fg="gray").pack(expand=True, pady=50)
            return
        
        for plot_name in plot_names:
            self.add_plot_placeholder(plot_name.replace("_", " ").title())
        
        self.plot_frame.update_idletasks()
        self.plot_canvas.configure(scrollregion=self.plot_canvas.bbox("all"))
    
    def show_error(self, message):
        """Display error message"""
        messagebox.showerror("Processing Error", message)
        self.update_status("Error occurred during processing", "red")
    
    def show_success(self, message):
        """Display success message"""
        messagebox.showinfo("Success", message)
        self.update_status("Processing completed successfully", "green")
    
    def get_export_settings(self):
        """Get current export settings"""
        return {
            'format': self.export_format.get(),
            'selected_plots': self.get_selected_plots()
        }
 
# =============================================================================
# Test Script to run this page independently from the project root
# =============================================================================
if __name__ == "__main__":
    from app.core.Controller import Controller
    from app.core.Model import Model
    
    root = tk.Tk()
    root.title("ProcessingPage Test (Running from Root)")
    root.geometry("900x800")
    
    model = Model()
    controller = Controller(app=root, model=model)
    
    # Mock the frames dict so controller.show_frame works
    root.frames = {"ProcessingPage": None, "PreprocessingPage": None, "HomePage": None}
    
    processing_page = ProcessingPage(parent=root, controller=controller)
    processing_page.pack(fill="both", expand=True)
    
    root.mainloop()