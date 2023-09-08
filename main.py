# import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import adbutils
import os
# import requests
# import platform
# import time
import utils
import threading
from adbutils._utils import adb_path


# create a folder for this. Please find another method for this code
try:
    os.mkdir(f'{utils.platform_home_folder}/.ethos-group')
except:
    pass
try:
    os.mkdir(f'{utils.platform_home_folder}/.ethos-group/gabb-adb-gui')
except:
    pass
try:
    os.mkdir(f'{utils.platform_home_folder}/.ethos-group/gabb-adb-gui/logs')
except:
    pass
try:
    os.mkdir(f'{utils.platform_home_folder}/.ethos-group/gabb-adb-gui/apk')
except:
    pass


# set up client

adb = adbutils.AdbClient(host='127.0.0.1', port=5037)
for info in adb.list():
    print(info.serial, info.state)


class ConnectionWaiterApp:

    def update_adb_status(self):

        try:

            state = adb.list()[0].state

        except IndexError:

            state = 'Disconnected'

        if 'no permission' in state:
            state = 'Please accept file transfer on your phone'

        if 'unauthorized' in state:
            state = 'Please disconnect your phone and try again.'

        self.adb_status_label.config(text=f'Status:\n\n{state}')

        self.root.after(500, self.update_adb_status)

    def show_connected_notification(self):
        messagebox.showinfo("Phone Connected", "Your Gabb Z2 has been connected!\n\nYou may now close this window.")

    def center_window(self):
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the center position
        center_x = (screen_width - 1000) // 2
        center_y = (screen_height - 600) // 2

        # Set the window's initial geometry to center it on the screen
        self.root.geometry(f"{1000}x{600}+{center_x}+{center_y}")

    def __init__(self, root):
        self.root = root

        # Set the initial size of the window
        root.minsize(400, 300)
        root.geometry("1000x600")
        self.center_window()

        self.root.title("Eth0s Group's Gabb Phone Z2 Hacker")
        self.server_thread = True

        self.device_id = 0
        self.should_continue = False

        # Create a frame for the navigation bar
        nav_bar = tk.Frame(root, height=30, bg="gray")
        nav_bar.pack(side="bottom", fill="x")

        # Create a label to display the name (left-aligned)
        name_label = tk.Label(nav_bar, text="The Eth0s Group", fg="white", bg="gray")
        name_label.pack(side="left", padx=10, pady=5)

        # Create a label to display text on the right (right-aligned)
        right_label = tk.Label(nav_bar, text="Created by Keagan Peterson (Kasherpete)", fg="white", bg="gray")
        right_label.pack(side="right", padx=10, pady=5)

        # Create a label to display the status
        self.status_label = tk.Label(root,
                                     text="Please follow the steps on the guide at gabbhackguide.netlify.app,\n connect your phone, and press the button below.")
        self.status_label.pack(pady=20)

        # Create a button to start waiting for a connection
        self.start_button = tk.Button(root, text="Connect", command=self.start_waiting)
        self.start_button.pack()

        self.adb_status_label = tk.Label(root, text="")
        self.adb_status_label.pack(pady=20)

        self.setup_message = tk.Label(root, text="")
        self.setup_message.pack(pady=20)

        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL,
                               length=100, mode='determinate')
        # self.progress.pack(pady=10)

        # Create a socket server thread

    #        self.server_thread = None

    def start_waiting(self):
        # Disable the start button to prevent multiple connections
        self.start_button.configure(state="disabled")

        # Start the socket server thread
        self.server_thread = threading.Thread(target=self.wait_for_connection)
        self.server_thread.daemon = True
        self.server_thread.start()

    def wait_for_connection(self):
        self.status_label.config(
            text="Waiting for a connection...\n\nPlease remember to unlock your phone and\naccept all connections.\n\nRestart your phone and follow the online guide for help if you have any problems.")

        self.setup_message.config(text="NOTE: If your phone has not been set up yet, go to the phone app\nand type '*#*#62468#*#*', and press the top button. Read the online guide!")

        self.root.after(500, self.update_adb_status)

        #        time.sleep(.5)

        adb.wait_for(timeout=10000)  # give the poor kids enough time to find their phone charger!
        self.device_id = adb.device_list()[0].serial
        self.status_label.config(text=f"Connection established")
        self.show_connected_notification()

        self.device = adb.device(serial=self.device_id)

        if utils.in_setup_mode(self.device) and messagebox.askyesno("Device Setup","The device is not set up! Would you like to set it up now? (If you click \"no\", you cannot continue.)"):

            self.progress.pack(pady=10)

            self.progress['value'] = 10
            self.root.update_idletasks()

            utils.download_apk('setedit')

            self.progress['value'] = 40
            self.root.update_idletasks()

            utils.adb(f'install-multiple {utils.platform_setedit_folder}')

            self.progress['value'] = 80
            self.root.update_idletasks()

            self.device.shell('adb shell pm grant io.github.muntashirakon.setedit android.permission.WRITE_SECURE_SETTINGS')
            self.device.shell('am switch-user 0')  # normal user
            self.device.shell('pm remove-user 10')  # keep this for now. weird errors keep showing up

            messagebox.showinfo("Device Setup", "Please follow these steps:\n\n1. go to to the 'Setedit' app\n\n2. tap the button in the top left, and go to the 'global table'\n\n3. tab 'adb_enabled'\n\n4. type in '1'. CLICK 'OKAY' WHEN YOU ARE DONE.")

            if not utils.in_setup_mode(self.device) and adb.list()[0].state == 'device':
                messagebox.showinfo("Device Setup", "Congrats! You are now ready to start hacking your phone.")

                self.should_continue = True
                utils.setup_device(self.device)

            else:
                messagebox.showinfo("Device Setup", "Oops! You did something wrong. Please exit and try again.")

        else:
            self.should_continue = True
            utils.setup_device(self.device)

        #        self.server_thread = False
        threading.main_thread().join()


class AdbManagerApp:

    def update_adb_status(self):

        try:

            state = adb.list()[0].state

        except IndexError:

            state = 'Disconnected'

        if 'no permission' in state.lower():
            state = 'File transfer not accepted'

        if 'device' in state.lower():
            state = 'Connected'

        if 'unauthorized' in state.lower():
            state = 'USB debugging not accepted'

        self.adb_status_bar.config(text=f'Status: {state}')

        self.root.after(500, self.update_adb_status)

    def open_directory_dialog(self):
        # Open a directory dialog and get the selected directory path

        initial_dir = os.path.expanduser("~/Downloads")

        directory_path = filedialog.askopenfilename(
            filetypes=[("APK Files", "*.apk")],
            initialdir=initial_dir,
            title="Select an APK File",
            #            showhidden=False  # Hide files starting with "."
        )

        # directory_path = ['"' + item + '"' for item in directory_path]
        # directory_path = " ".join(directory_path)

        # Display the selected directory path (you can do something else with it)
        # if directory_path:
        #     self.result_label.config(text=f"Selected Directory: {directory_path}")
        # else:
        #     self.result_label.config(text="No directory selected")

        # self.device.install(directory_path)
        # self.device.adb_output(f'install-multiple {directory_path}')

        try:
            path = adb_path()

            self.result_label.config(text="Installing, please wait...")
            print(f'Executing {directory_path}')
            os.system(f'{path} install-multiple {directory_path}')

            self.result_label.config(text="APK installed!")

        except RuntimeError:
            messagebox.showerror("ADB error", "Error: ADB is not installed or packaged!! Message @kasherpete on discord immediately. This is a highly unusual error.")

    def center_window(self):
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the center position
        center_x = (screen_width - 1000) // 2
        center_y = (screen_height - 600) // 2

        # Set the window's initial geometry to center it on the screen
        self.root.geometry(f"{1000}x{600}+{center_x}+{center_y}")

    # def on_resize(self, event):
    #     # Get the new window size
    #     new_width = event.width
    #     # new_height = event.height
    #
    #     # Update the label's position to stay in the top right corner
    #     self.status_label.place(x=new_width, y=0)

    def create_setup_tab(self, tab):
        # Create custom content for the Setup tab
        label = ttk.Label(tab, text="This is the Setup tab.")
        label.pack(padx=20, pady=20)

        # Add more widgets and elements specific to the Setup tab here

    def create_tab_advanced(self, tab):

        sub_tab_control = ttk.Notebook(tab)
        sub_tab_control.pack(fill="both", expand=True)

        subtab_a = ttk.Frame(sub_tab_control)
        subtab_b = ttk.Frame(sub_tab_control)
        subtab_c = ttk.Frame(sub_tab_control)
        subtab_d = ttk.Frame(sub_tab_control)
        subtab_e = ttk.Frame(sub_tab_control)
        sub_tab_control.add(subtab_a, text="ADB Control")
        sub_tab_control.add(subtab_b, text="Shell")
        sub_tab_control.add(subtab_c, text="Sys Info")
        sub_tab_control.add(subtab_d, text="Sys Control")
        sub_tab_control.add(subtab_e, text="Debug")


        self.adb_text_widget = tk.Text(subtab_a, wrap=tk.WORD, height=5, width=30)
        self.adb_text_widget.pack(pady=10)

        update_button = tk.Button(subtab_a, text="Send to device", command=self.send_adb_command_widget)
        update_button.pack()

        self.adb_output_widget = tk.Text(subtab_a, wrap=tk.WORD, state="disabled", height=10, width=40)
        self.adb_output_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.shell_text_widget = tk.Text(subtab_b, wrap=tk.WORD, height=5, width=30)
        self.shell_text_widget.pack(pady=10)

        update_button = tk.Button(subtab_b, text="Send to device", command=self.send_shell_command_widget)
        update_button.pack()

        self.shell_output_widget = tk.Text(subtab_b, wrap=tk.WORD, state="disabled", height=10, width=40)
        self.shell_output_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def create_tab_other(self, tab):

        sub_tab_control = ttk.Notebook(tab)
        sub_tab_control.pack(fill="both", expand=True)

        subtab_a = ttk.Frame(sub_tab_control)
        subtab_c = ttk.Frame(sub_tab_control)
        subtab_d = ttk.Frame(sub_tab_control)
        subtab_b = ttk.Frame(sub_tab_control)

        sub_tab_control.add(subtab_a, text="Record")
        sub_tab_control.add(subtab_c, text="Message")
        sub_tab_control.add(subtab_d, text="Connect Keyboard")
        sub_tab_control.add(subtab_b, text="Credits")

    def create_tab_status(self, tab):

        button = tk.Button(tab, text="Power Off", command=self.device.shell('reboot -p'))
        button.pack()

    def create_tab_install(self, tab):
        # Create custom content for the Install apps tab
        open_button = tk.Button(tab, text="Open Directory", command=self.open_directory_dialog)
        open_button.pack(pady=20)

        self.result_label = tk.Label(tab, text="")
        self.result_label.pack()

        # Add more widgets and elements specific to the install apps tab here

    # def create_advanced_tab(self, tab):
    #     # Create custom content for the Advanced tab
    #     label = ttk.Label(tab, text="This is the Advanced tab.")
    #     label.pack(padx=20, pady=20)

        # Add more widgets and elements specific to the Advanced tab here

    def send_adb_command_widget(self):
        text = self.adb_text_widget.get(1.0, tk.END)

        # Update the Label widget with the read-only text
        output = utils.adb(text)
        self.adb_output_widget.configure(state="normal")  # Enable editing temporarily
        self.adb_output_widget.delete("1.0", "end")
        self.adb_output_widget.insert("1.0", output)  # Insert text
        self.adb_output_widget.configure(state="disabled")  # Disable editing again

    def send_shell_command_widget(self):
        text = self.shell_text_widget.get(1.0, tk.END)

        # Update the Label widget with the read-only text
        output = self.device.shell(text)

        self.shell_output_widget.configure(state="normal")  # Enable editing temporarily
        self.shell_output_widget.delete("1.0", "end")
        self.shell_output_widget.insert("1.0", output)  # Insert text
        self.shell_output_widget.configure(state="disabled")  # Disable editing again

    def create_tab_updates(self, tab):

        label = tk.Label(tab, text="Software updates. ")
        label.pack(pady=10)

    def __init__(self, root, device_id):
        self.root = root
        root.minsize(400, 300)
        root.geometry("1000x600")
        self.center_window()
        self.device_id = device_id
        self.root.title("Eth0s Group's Gabb Phone Z2 Hacker")
        # self.root.bind("<Configure>", self.on_resize)

        self.device = adb.device(serial=self.device_id)

        self.root.after(500, self.update_adb_status)

        bottom_nav_bar = tk.Frame(root, height=30, bg="gray")
        bottom_nav_bar.pack(side="bottom", fill="x")

        top_nav_bar = tk.Frame(root, height=30, bg="gray")
        top_nav_bar.pack(side="top", fill="x")

        name_label = tk.Label(bottom_nav_bar, text="The Eth0s Group", fg="white", bg="gray")
        name_label.pack(side="left", padx=10, pady=5)

        # Create a label to display text on the right (right-aligned)
        right_label = tk.Label(bottom_nav_bar, text="Created by Keagan Peterson (Kasherpete)", fg="white", bg="gray")
        right_label.pack(side="right", padx=10, pady=5)

        self.adb_status_bar = tk.Label(top_nav_bar, text="", fg="white", bg="gray")
        self.adb_status_bar.pack(side="right", padx=10, pady=5)

        device_id_bar = tk.Label(top_nav_bar, text=device_id, fg="white", bg="gray")
        device_id_bar.pack(side="left", padx=10, pady=5)

        # Create a ttk Notebook (tabs container)
        main_tab_control = ttk.Notebook(root)
        main_tab_control.pack(fill="both", expand=True)

        # Create and add tabs
        #        self.create_tab(tab_control, "Setup")
        tab1 = ttk.Frame(main_tab_control)
        main_tab_control.add(tab1, text="Status")
        self.create_tab_status(tab1)

        tab2 = ttk.Frame(main_tab_control)
        main_tab_control.add(tab2, text="Install Apps")
        self.create_tab_install(tab2)

        tab1 = ttk.Frame(main_tab_control)
        main_tab_control.add(tab1, text="Updates")
        self.create_tab_updates(tab1)

        tab3 = ttk.Frame(main_tab_control)
        main_tab_control.add(tab3, text="Other")
        self.create_tab_other(tab3)

        tab3 = ttk.Frame(main_tab_control)
        main_tab_control.add(tab3, text="Advanced")
        self.create_tab_advanced(tab3)

        # self.status_label = tk.Label(root, text="Top Right Text", bg="red", fg="white")

        # Place the label in the top right corner (adjust coordinates as needed)
        # self.status_label.place(x=400, y=0)

        tab1 = ttk.Frame(main_tab_control)
        main_tab_control.add(tab1, text="Help")

        print(utils.in_setup_mode(self.device))

        #        self.create_tab(tab_control, "Install apps")
        #        self.create_tab(tab_control, "Advanced")

        # Pack the tab control to make it visible

        main_tab_control.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectionWaiterApp(root)
    root.mainloop()

    device_id = app.device_id

    if app.should_continue:

        # device_id = '320525532827'

        root = tk.Tk()
        app = AdbManagerApp(root, device_id)
        root.mainloop()
