# view/preprocessing_page.py
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk

class PreprocessingPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- ADDED: StringVars to trace changes in Entry widgets ---
        self.lowcut_var = tk.StringVar(value="0.05")
        self.highcut_var = tk.StringVar(value="3.0")
        self.start_time_var = tk.StringVar(value="0")
        self.end_time_var = tk.StringVar(value="") # Empty means 'end of signal'

        # Trace changes on these variables and link to the controller
        self.lowcut_var.trace_add("write", self.controller.on_parameters_changed)
        self.highcut_var.trace_add("write", self.controller.on_parameters_changed)
        self.start_time_var.trace_add("write", self.controller.on_parameters_changed)
        self.end_time_var.trace_add("write", self.controller.on_parameters_changed)

        # --- Configure top-level grid ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Top Controls Frame ---
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)

        stream_label = ctk.CTkLabel(top_frame, text="Select Stream:")
        stream_label.grid(row=0, column=0, padx=10, pady=10)

        # The command is triggered whenever the user selects a new item.
        self.stream_dropdown = ctk.CTkComboBox(
            top_frame,
            values=["- No file loaded -"],
            command=self.controller.on_stream_selected
        )
        self.stream_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        back_button = ctk.CTkButton(top_frame, text="Back to Home", command=self.controller.show_home_page)
        back_button.grid(row=0, column=2, padx=10, pady=10)

        # --- Plot Area ---
        plot_frame = ctk.CTkFrame(self) # No color needed now
        plot_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- ADDED: Matplotlib Figure and Canvas ---
        # Create a matplotlib Figure. We'll set a dark background to match the app theme.
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor="#2b2b2b")
        self.ax = self.fig.add_subplot(111)

        # Style the axes to be visible against the dark theme
        self.ax.set_facecolor("#2b2b2b")
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        # `FigureCanvasTkAgg` is the bridge between matplotlib and tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        # get_tk_widget() returns the tkinter-compatible widget, which we can pack
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        # --- End of Matplotlib Setup ---

        # --- Bottom Controls Frame ---
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        bottom_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1) # Make columns responsive

        # Create a sub-frame for parameters for better organization
        params_frame = ctk.CTkFrame(bottom_frame)
        params_frame.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="ew")
        params_frame.grid_columnconfigure((1, 3, 5, 7), weight=1) # Make entry widgets expand

        # Cleaning Method
        ctk.CTkLabel(params_frame, text="Cleaning Method:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.cleaning_method_dropdown = ctk.CTkComboBox(
            params_frame, 
            values=["khodadad2018", "BioSPPy"],
            command=self.controller.on_parameters_changed
        )
        self.cleaning_method_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Lowcut
        ctk.CTkLabel(params_frame, text="Lowcut (Hz):").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.lowcut_entry = ctk.CTkEntry(params_frame, textvariable=self.lowcut_var)
        self.lowcut_entry.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        # Find Peaks Method
        ctk.CTkLabel(params_frame, text="Find Peaks Method:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.find_peaks_dropdown = ctk.CTkComboBox(
            params_frame, 
            values=["khodadad2018", "scipy", "biosppy"],
            command=self.controller.on_parameters_changed # Also connect this for future use
        )
        self.find_peaks_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Highcut
        ctk.CTkLabel(params_frame, text="Highcut (Hz):").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.highcut_entry = ctk.CTkEntry(params_frame, textvariable=self.highcut_var)
        self.highcut_entry.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        # Time Range
        ctk.CTkLabel(params_frame, text="Start Time (s):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.start_time_entry = ctk.CTkEntry(params_frame, textvariable=self.start_time_var)
        self.start_time_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(params_frame, text="End Time (s):").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.end_time_entry = ctk.CTkEntry(params_frame, placeholder_text="end", textvariable=self.end_time_var)
        self.end_time_entry.grid(row=2, column=3, padx=10, pady=5, sticky="ew")
        
        # --- Save Button ---
        self.save_button = ctk.CTkButton(
            bottom_frame,
            text="Save Preprocessing Settings",
            command=self.controller.on_save_settings_click # Connect to the controller
        )
        self.save_button.grid(row=1, column=4, padx=10, pady=10, sticky="e")
        
        self.load_button = ctk.CTkButton(
            bottom_frame,
            text="Load Preprocessing Settings",
            command=self.controller.on_load_settings_click # Connect to controller
        )
        self.load_button.grid(row=1, column=3, padx=10, pady=10, sticky="e")
        
        self.analysis_button = ctk.CTkButton(
            bottom_frame,
            text="Go to Analysis ->",
            command=self.controller.navigate_to_analysis_page
        )
        self.analysis_button.grid(row=1, column=5, padx=20, pady=10, sticky="e")
        
    def update_stream_dropdown(self, channel_names):
        """Updates the values in the stream selection combobox."""
        self.stream_dropdown.configure(values=channel_names)
        if channel_names:
            self.stream_dropdown.set(channel_names[0])
            # --- ADDED: Automatically plot the first stream ---
            self.controller.on_stream_selected(channel_names[0])
        else:
            self.stream_dropdown.set("- No channels found -")

    # --- ADDED: Method to handle plotting ---
    def plot_signal(self, time_x, signal_y, peaks=None, signal_name=""):
        """
        Clears the plot and draws the new signal from its raw components.

        Args:
            time_x (np.array): The time vector for the x-axis.
            signal_y (np.array): The signal amplitude vector for the y-axis.
            peaks (np.array, optional): Indices of detected peaks.
            signal_name (str, optional): The name of the signal for the title.
        """
        self.ax.clear() # Clear the previous plot

        # Check if we have valid data to plot
        if time_x is not None and signal_y is not None:
            # Plot the main signal waveform
            self.ax.plot(time_x, signal_y, color="#1f6aa5", label="Signal")
            
            # Plot the peaks if they exist
            if peaks is not None and len(peaks) > 0:
                # Use the relative peak indices to get the corresponding time and amplitude
                peak_times = time_x[peaks]
                peak_amplitudes = signal_y[peaks]
                
                # Plot peaks as red scatter points
                self.ax.scatter(peak_times, peak_amplitudes, color="red", zorder=10, label="Peaks")

            self.ax.set_xlabel("Time (s)", color="white")
            self.ax.set_ylabel("Amplitude", color="white")
            self.ax.set_title(f"Displaying: {signal_name}", color="white")
            self.ax.legend(facecolor="#2b2b2b", labelcolor="white", frameon=False)
        else:
            self.ax.set_title("No data to display", color="white")
        
        # Redraw the canvas to show the changes
        self.canvas.draw()
        
    def get_processing_parameters(self):
        """
        Retrieves all current settings from the UI widgets.
        
        Returns:
            dict: A dictionary of all processing parameters.
        """
        params = {}
        try:
            params['cleaning_method'] = self.cleaning_method_dropdown.get()
            params['find_peaks_method'] = self.find_peaks_dropdown.get()
            params['lowcut'] = float(self.lowcut_var.get())
            params['highcut'] = float(self.highcut_var.get())
            params['start_time'] = float(self.start_time_var.get())
            
            # Handle empty end time entry
            end_time_str = self.end_time_var.get()
            params['end_time'] = float(end_time_str) if end_time_str else None

        except (ValueError, TypeError):
            # If a float conversion fails (e.g., user types text), use safe defaults
            # This prevents crashes during typing. A more advanced solution would show an error icon.
            params.setdefault('lowcut', 0.05)
            params.setdefault('highcut', 3.0)
            params.setdefault('start_time', 0.0)
            params.setdefault('end_time', None)
            
        return params
    
    def set_processing_parameters(self, settings):
        """
        Updates all the UI widgets based on a loaded settings dictionary.

        Args:
            settings (dict): The dictionary of parameters loaded from a file.
        """
        # Use .get(key, default) to safely access values that might be missing
        self.cleaning_method_dropdown.set(settings.get("cleaning_method", "khodadad2018"))
        self.find_peaks_dropdown.set(settings.get("find_peaks_method", "khodadad2018"))
        
        # Update the StringVars, which will in turn update the Entry widgets
        self.lowcut_var.set(str(settings.get("lowcut", "0.05")))
        self.highcut_var.set(str(settings.get("highcut", "3.0")))
        self.start_time_var.set(str(settings.get("start_time", "0")))
        
        # Handle the end time, which could be None
        end_time = settings.get("end_time")
        self.end_time_var.set(str(end_time) if end_time is not None else "")
    