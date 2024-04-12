import time
import tkinter as tk
import zipfile
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk, font
import pyperclip
import adbutils
import requests
from adbutils import errors
import os
import utils
import threading
from tkinterhtml import HtmlFrame
import json
from PIL import Image, ImageTk


print(utils.platform)

# create a folder for this. Please find another method for this code
for i in utils.create_folders:
    if not os.path.exists(i):
        os.mkdir(i)


# set up client

adb = adbutils.AdbClient()
for info in adb.list():
    print(info.serial, info.state)


class ConnectionWaiterApp:

    def check(self):

        if self.finished:
            self.root.destroy()

        else:
            self.root.after(200, self.check)

    def update_adb_status(self):

        try:

            state = adb.list()[0].state

        except IndexError:

            state = 'Disconnected'

        if 'no permission' in state:
            state = 'Please unplug and replug your phone in, and accept the info message.'

        if 'unauthorized' in state:
            state = 'Please disconnect your phone and try again.'

        self.adb_status_label.config(text=f'Status:\n\n{state}')

        self.root.after(200, self.update_adb_status)

    def show_connected_notification(self):
        messagebox.showinfo("Phone Connected", "Your Gabb Z2 has been connected!")

    def center_window(self):
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the center position
        center_x = (screen_width - 1000) // 2
        center_y = (screen_height - 600) // 2

        # Set the window's initial geometry to center it on the screen
        self.root.geometry(f"{1000}x{600}+{center_x}+{center_y}")

    def __init__(self, root: tk.Tk):
        self.root = root

        # Set the initial size of the window
        root.minsize(400, 300)
        root.geometry("1000x600")
        self.center_window()
        self.finished = False
        self.root.after(500, self.check)

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
        self.status_label = tk.Label(root, text="Please follow the steps on the guide at gabbhackguide.netlify.app,\n connect your phone, and press the button below.")
        self.status_label.pack(pady=20)

        # Create a button to start waiting for a connection
        self.start_button = tk.Button(root, text="Connect", command=self.start_waiting)
        self.start_button.pack()

        self.adb_status_label = tk.Label(root, text="", font=font.Font(size=16, weight="bold"))
        self.adb_status_label.pack(pady=20)

        self.setup_message = tk.Label(root, text="")
        self.setup_message.pack(pady=20)

        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=100, mode='determinate')
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
        self.status_label.config(text="Waiting for a connection...\n\nPlease remember to unlock your phone and\naccept all connections.\n\nRestart your phone and follow the online guide for help if you have any problems.")

        self.setup_message.config(text="NOTE: If your phone has not been set up yet, go to the phone app\nand type '*#*#62468#*#*', and press the top button. Read the online guide!")

        self.root.after(500, self.update_adb_status)

        #        time.sleep(.5)

        adb.wait_for(timeout=10000)  # give the poor kids enough time to find their phone charger!
        self.device_id = adb.device_list()[0].serial
        self.status_label.config(text=f"Connection established")

        self.device = adb.device(serial=self.device_id)

        if utils.in_setup_mode(self.device) and messagebox.askyesno("Device Setup","The device is not set up! Would you like to set it up now? (If you click \"no\", you cannot continue.)"):

            self.device.shell('settings put global adb_enabled 1')
            self.device.shell('pm remove-user 10')  # maintenance mode user
            self.device.shell('am switch-user 0')  # normal user

            messagebox.showinfo('Device Setup Wizard', 'Your device has been set up! You are now ready to start hacking your phone.')
            time.sleep(2)
            messagebox.showinfo('Device Setup Wizard',  'Please unplug your phone and launch this program again.')

            self.should_continue = False

        else:
            self.should_continue = True
            utils.setup_device(self.device)

        #        self.server_thread = False
        self.show_connected_notification()
        self.finished = True


class AppStore:

    def create_info_dialog(self, root, photo, entry):

        def on_resize(event):
            # This function will be called every time the window is resized
            info_label.config(wraplength=popup.winfo_width() - 122)

        # root.withdraw()

        popup = tk.Toplevel(root)
        popup.title(f"{entry['name']} Info")
        popup.geometry("500x350")
        popup.bind("<Configure>", on_resize)

        title_frame = tk.Frame(popup, bg="#aaa")
        title_frame.pack(fill='x')

        main_frame = tk.Frame(popup)
        main_frame.pack()

        description_frame = tk.Frame(main_frame)
        description_frame.grid(row=0, column=0, sticky='nw')

        button_frame = tk.Frame(main_frame, bg='#aaa')
        button_frame.grid(row=0, column=1, sticky='n')

        if photo is not None:

            image_label = ttk.Label(title_frame, image=photo)
            image_label.image = photo
            image_label.grid(row=0, column=0, padx=5, pady=5)

        else:

            image_label = ttk.Label(title_frame, text="ERROR")
            image_label.grid(row=0, column=0, padx=5, pady=5)

        if not utils.is_installed(self.device, entry['code_name']):

            install_button = tk.Button(button_frame, text="Install", bg="#0000ff", fg="#fff", activebackground="#bbb",
                               activeforeground="#000", cursor="hand2", highlightthickness=2,
                               highlightbackground="#aaa")
            install_button.grid(row=0, column=0, padx=5, pady=2)

            install_button.bind("<Enter>", self.on_install_button_enter)
            install_button.bind("<Leave>", self.on_install_button_leave)

            install_button.config(
                command=lambda x=entry['apk_name'], button=install_button, name=entry['code_name']: self.install_button(x, button, name))

        else:
            install_button = tk.Button(button_frame, text="Installed", state='disabled', bg='#777')
            install_button.grid(row=0, column=0, padx=5, pady=2)

        button = tk.Button(button_frame, text='Copy APK\nlink', command=lambda url=entry['url']: pyperclip.copy(url))
        button.grid(row=1, column=0, padx=5, pady=5, sticky='n')

        name_label = tk.Label(title_frame, text=entry["name"], font=font.Font(size=16, weight="bold"), bg='#aaa')
        name_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        info_label = tk.Label(description_frame, text=entry['description'], wraplength=300, anchor='w', justify='left')
        info_label.grid(row=1, column=1, sticky='nw', padx=10, pady=10)

        try:
            version = entry['version'][:22]
        except:
            version = '0'

        version = utils.insert_newlines(version, 11)

        if len(version) >= 22:
            version += '...'

        version_label = tk.Label(button_frame, text=f'v{version}', bg='#aaa')
        version_label.grid(row=2, column=0, padx=5, pady=5, sticky='n')

    def on_install_button_enter(self, event):
        event.widget.config(highlightbackground="#0000ff")

    def on_install_button_leave(self, event):
        event.widget.config(highlightbackground="#aaa")

    def install_button(self, app: str, button: tk.Button, code_name: str):

        def target(app, button, code_name):
            button.config(text='Downloading...', state='disabled', bg='#777')
            path = utils.download_apk(app)

            if path is None:
                messagebox.showerror('Connection Error', f'There was an error downloading {app}. You may be disconnected from the internet.')
                return

            button.config(text='Installing...', state='disabled', bg='#777')
            utils.install(self.device, path, code_name)

            button.config(text="Installed", state='disabled', bg='#777')

        thread = threading.Thread(target=target, args=(app, button, code_name))
        thread.daemon = True
        thread.start()

    def __init__(self, root: tk.Toplevel, device: adbutils.AdbDevice):

        data = json.loads(open('AppStoreApkList.json', 'r', encoding='utf-8').read())
        self.device = device

        # Create the main window
        self.root = root
        root.title("Gabb Phone Z2 App Store")

        # Create a function to generate boxes

        for row, entry in enumerate(data):

            # Create a frame for each box
            box_frame = tk.Frame(root, bg="#aaa")
            box_frame.grid(row=row // 3, column=row % 3, padx=10, pady=10)

            # Load images
            try:

                image = Image.open(entry["image_path"])  # TODO: fix Windows path
                image = image.resize((50, 50))  # Adjust images size as needed
                photo = ImageTk.PhotoImage(image)

                # Display images on the left
                image_label = ttk.Label(box_frame, image=photo)
                image_label.image = photo
                image_label.grid(row=0, column=0, padx=5, pady=5)

            except FileNotFoundError:
                image_label = ttk.Label(box_frame, text="ERROR")
                image_label.grid(row=0, column=0, padx=5, pady=5)

                photo = None

            text_frame = tk.Frame(box_frame, bg="#aaa")
            text_frame.grid(row=0, column=1, padx=0, pady=0, sticky="w")

            name = entry['name']

            if entry['important']:
                name = '★ ' + name

            desc = utils.insert_newlines(entry['description'].replace('\n', ''), 30)[:59]
            if len(desc) >= 59:
                desc += '...'
            # try:
            #     version = entry['version']
            # except:
            #     version = '0'
            #
            # if len(version) > 8:
            #     version = version[:8] + '-'

            package_name = entry['code_name']

            # Display text on the right as multiline label
            text_label = ttk.Label(text_frame, background="#aaa", text=name, font=font.Font(size=12, weight="bold"))
            text_label.grid(row=0, column=0, sticky="w")

            text_label = ttk.Label(text_frame, background="#aaa", text=desc, foreground="#333")
            text_label.grid(row=1, column=0, sticky="w")

            button_frame = tk.Frame(box_frame, bg="#aaa")
            button_frame.grid(row=0, column=2)

            if not utils.is_installed(self.device, package_name):

                button = tk.Button(button_frame, text="Install", bg="#0000ff", fg="#fff", activebackground="#bbb",
                                   activeforeground="#000", cursor="hand2", highlightthickness=2,
                                   highlightbackground="#aaa")
                button.grid(row=0, column=0, padx=5, pady=2)

                button.bind("<Enter>", self.on_install_button_enter)
                button.bind("<Leave>", self.on_install_button_leave)

                button.config(command=lambda x=entry['apk_name'], button=button, name=entry['code_name']: self.install_button(x, button, name))

            else:
                button = tk.Button(button_frame, text="Installed", state='disabled', bg='#777')
                button.grid(row=0, column=0, padx=5, pady=2)

            info_button = tk.Button(button_frame, text="Info", cursor="hand2", bg="#aaa",
                                    highlightbackground="#aaa",
                                    command=lambda r=root, p=photo, e=entry: self.create_info_dialog(r, p, e))
            info_button.grid(row=1, column=0, padx=5, pady=2, ipadx=7)

            # version_label = ttk.Label(button_frame, text=f' v{version}', background='#aaa', foreground="#333")
            # version_label.grid(row=1, column=0, padx=5, sticky='w')

            # Bind the hover functions to the button


class AdbManagerApp:

    def open_app_store(self):

        popup = tk.Toplevel(self.root)

        AppStore(popup, self.device)

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

        initial_dir = utils.platform_downloads_folder

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

            self.result_label.config(text="Installing, please wait...")
            print(f'Executing {directory_path}')
            utils.install(self.device, directory_path)

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
        subtab_b = ttk.Frame(sub_tab_control)
        subtab_e = ttk.Frame(sub_tab_control)

        sub_tab_control.add(subtab_a, text="Record")
        self.create_tab_record(subtab_a)
        sub_tab_control.add(subtab_c, text="Message")
        self.create_tab_message(subtab_c)
        sub_tab_control.add(subtab_e, text="Control Device")
        self.create_tab_scrcpy(subtab_e)
        sub_tab_control.add(subtab_b, text="Credits")

    def create_tab_scrcpy(self, tab):

        # ---UNIVERSAL---

        def find_scrcpy_path():
            if self.device._record_client:
                return self.device._record_client
            r1 = adbutils._device._ScrcpyScreenRecord(self.device)
            if r1.check_env():
                self.device._record_client = r1
                return r1
            r2 = adbutils._device._AdbScreenRecord(self.device)
            if r2.check_env():
                self.device._record_client = r2
                return r2
            return None

        set_up = False

        try:

            scrcpy_path = find_scrcpy_path()._scrcpy_path

            if scrcpy_path is not None:

                button = ttk.Button(tab, text='Connect Device', command=lambda: os.system(f'{scrcpy_path} --window-title="Eth0s Group Device Control Program" -V error -t'))
                button.pack(pady=10)

            set_up = True

        except:
            pass

        if set_up:
            pass

        # ---WINDOWS---

        elif utils.platform == 'windows':

            def execute():

                os.system(f'{utils.platform_scrcpy_extract}\\scrcpy-win64-v2.1.1\\scrcpy')

            def download():

                progress = ttk.Progressbar(tab, orient=tk.HORIZONTAL, length=100, mode='determinate')
                progress.pack(pady=10)

                progress['value'] = 10
                root.update_idletasks()

                if not utils.check_scrcpy_install():
                    print('installing')
                    with open(utils.platform_scrcpy_zip, 'wb') as f:
                        f.write(requests.get('https://github.com/Genymobile/scrcpy/releases/download/v2.1.1/scrcpy-win64-v2.1.1.zip').content)

                progress['value'] = 50
                root.update_idletasks()

                try:
                    # Open the ZIP file for reading
                    with zipfile.ZipFile(utils.platform_scrcpy_zip, "r") as zip_ref:
                        # Extract all the contents to the specified directory
                        zip_ref.extractall(utils.platform_scrcpy_extract)
                    # print(f"Successfully extracted files to {extract_path}")
                except:
                    messagebox.showerror('Error Extracting File', 'There was an error extracting Scrcpy.')

                button.config(text='Connect Device', command=execute)

                progress['value'] = 100
                root.update_idletasks()

                progress.destroy()
                messagebox.showinfo('Scrcpy Installed', 'Scrcpy has been installed. You may now connect to your phone.')

            if utils.check_scrcpy_install():

                button = ttk.Button(tab, text='Connect Device', command=execute)
                button.pack(pady=10)

            else:

                button = ttk.Button(tab, text='Install Scrcpy', command=download)
                button.pack(pady=10)

        # ---LINUX---
        elif utils.platform == 'linux':
            label = ttk.Label(tab, text='Use "sudo apt install scrcpy" to use this first.')
            label.pack(pady=10)

        elif utils.platform == 'darwin':

            def target():

                button.config(text='Downloading Homebrew...', state='disabled')
                os.system('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

                button.config(text='Installing Scrcpy...')
                os.system('brew install scrcpy')

                button.config(text='Done', state='disabled')
                messagebox.showinfo('MacOS Scrcpy Installation', 'The app will now close. Please reopen the app to update.')

            def download():

                thread = threading.Thread(target=target)
                thread.daemon = True
                thread.start()

            button = ttk.Button(tab, text='Install Scrcpy', command=download)
            button.pack(pady=10)

        else:
            label = ttk.Label(tab, text='Could not recognize Operating System. Please install the scrcpy binary.')
            label.pack(pady=10)

    def create_tab_message(self, tab):

        def on_focus_in(entry):
            if entry.cget('state') == 'disabled':
                entry.configure(state='normal')
                entry.delete(1.0, 'end')

        def on_focus_out(entry, placeholder):

            if entry.get(index1=1.0).replace('\n', '') == "":
                entry.insert(1.0, placeholder)
                entry.configure(state='disabled')

        def send_message(number, message):
            self.device.shell(f'service call isms 7 i32 0 s16 "com.android.mms.service" s16 "{number}" s16 "null" s16 "{message}" s16 "null" s16 "null"')

        def read_text_boxes():

            def target():
                number = entry_x.get("1.0", "end-1c")  # Get content of text box 1
                message = entry_y.get("1.0", "end-1c")  # Get content of text box 2

                # result_label.config(text=f"Text Box 1: {text_box1_content}\nText Box 2: {text_box2_content}")
                if (number is not None) and (number != '') and (number != 'Phone number') and (message is not None) and (message != '') and (message != 'Phone number'):
                    send_message(number, message)

                    result_label.config(text=f"Message to '{number}' sent!")
                else:
                    result_label.config(text="Oops! Please include a phone number to send to and a message to send to them.")

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()

        # Create text boxes with different sizes
        entry_x = tk.Text(tab, height=1, width=13)
        entry_x.pack(pady=10)
        entry_x.insert(1.0, "Phone number")
        entry_x.configure(state='disabled')

        entry_y = tk.Text(tab, height=8, width=35)
        entry_y.pack(pady=10)
        entry_y.insert(1.0, "Message")
        entry_y.configure(state='disabled')

        # text_box1 = tk.Text(tab, height=1, width=13)
        # text_box1.pack(pady=10, padx=10)
        #
        # text_box1.bind("<Button-1>", click)
        # text_box1.bind("<Leave>", leave)
        #
        # text_box2 = tk.Text(tab, height=8, width=35)
        # text_box2.pack(pady=10, padx=10)

        entry_x.bind('<Button-1>', lambda x: on_focus_in(entry_x))
        entry_x.bind('<FocusOut>', lambda x: on_focus_out(entry_x, 'Phone number'))

        entry_y.bind('<Button-1>', lambda x: on_focus_in(entry_y))
        entry_y.bind('<FocusOut>', lambda x: on_focus_out(entry_y, 'Message'))

        # Create a button to read the content of the text boxes
        read_button = tk.Button(tab, text="Send SMS Message", command=read_text_boxes)
        read_button.pack(pady=10)

        # Create a label to display the result
        result_label = tk.Label(tab, text="")
        result_label.pack()

    def create_tab_record(self, tab):

        # def worker_thread():
        #     self.device.shell('screenrecord /sdcard/record.mp4')

        def stop_recording():
            # self.device.shell('\x03')
            start_button.config(text="Saving...", state="disabled")
            self.root.update_idletasks()
            self.device.stop_recording()

            start_button.config(text="Start Recording", command=start_recording, state="active")

            file = filedialog.asksaveasfile(title='Save file', filetypes=[('Video', 'mp4')], initialfile='record.mp4', initialdir=utils.platform_desktop_folder)

            if file is not None:
                os.rename(utils.platform_temporary_video_folder, file.name)

        def start_recording():
            # thread = threading.Thread(target=worker_thread)
            # thread.daemon = True
            # thread.start()
            self.device.start_recording(utils.platform_temporary_video_folder)

            start_button.config(text="Stop Recording")
            start_button.config(command=stop_recording)

        def screenshot():

            button.config(text="Processing...", state="disabled")
            self.root.update_idletasks()

            image = self.device.screenshot()

            button.config(text="Screenshot", state="active")

            file_path = filedialog.asksaveasfile(title='Save file', filetypes=[('Picture', 'png')], initialfile='record.png', initialdir=utils.platform_desktop_folder)

            if file_path is not None:
                image.save(fp=file_path.name)

        label = ttk.Label(tab, text="")
        label.pack(pady=10)

        label = ttk.Label(tab, text="Record Screen")
        label.pack()

        start_button = tk.Button(tab, text="Start Recording", command=start_recording)
        start_button.pack(pady=20)

        label = ttk.Label(tab, text="")
        label.pack(pady=10)

        label = ttk.Label(tab, text="Screenshot")
        label.pack()

        button = tk.Button(tab, text="Screenshot", command=screenshot)
        button.pack(pady=20)

    def create_tab_status(self, tab):

        # button = tk.Button(tab, text="Power Off", command=self.device.shell('reboot -p'))
        # button.pack()

        def power_off():

            def target():
                button1.config(text="Shutting Down...", state="disabled")
                self.device.shell('reboot -p')
                button1.config(text="Turn Off Device Device", state="active")

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()

        def reboot():

            def target():
                button2.config(text="Rebooting...", state="disabled")
                self.device.shell('reboot')
                button2.config(text="Reboot Device", state="active")

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()

        def toggle_screen():
            thread = threading.Thread(target=self.device.shell, args=('input keyevent KEYCODE_POWER',))
            thread.daemon = True
            thread.start()

        frame = tk.Frame(tab, pady=20)
        frame.pack()

        # Create two buttons and pack them side by side
        button1 = tk.Button(frame, text="Turn Off Device", command=power_off)
        button1.pack(side="left", padx=10)

        button2 = tk.Button(frame, text="Reboot Device", command=reboot)
        button2.pack(side="left", padx=10)

        button3 = tk.Button(frame, text="Toggle Screen", command=toggle_screen)
        button3.pack(side="left", padx=10)

        frame = ttk.Frame(tab)
        frame.pack(pady=10)

        label = ttk.Label(frame, text="Battery Percent")
        label.grid(row=0, column=0, padx=10, sticky="e")

        # Create a separator (a horizontal line)
        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=0, column=1, sticky="ew")

        # Create the second label
        self.status_battery_percent = ttk.Label(frame, text="")
        self.status_battery_percent.grid(row=0, column=2, padx=10, sticky="w")

        label = ttk.Label(frame, text="Battery is charging")
        label.grid(row=1, column=0, padx=10, sticky="e")

        # Create a separator (a horizontal line)
        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=1, column=1, sticky="ew")

        # Create the second label
        self.status_battery_charging = ttk.Label(frame, text="")
        self.status_battery_charging.grid(row=1, column=2, padx=10, sticky="w")

        label = ttk.Label(frame, text="Screen on")
        label.grid(row=2, column=0, padx=10, sticky="e")

        # Create a separator (a horizontal line)
        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=2, column=1, sticky="ew")

        # Create the second label
        self.status_screen_on = ttk.Label(frame, text="")
        self.status_screen_on.grid(row=2, column=2, padx=10, sticky="w")

        label = ttk.Label(frame, text="Screen locked")
        label.grid(row=3, column=0, padx=10, sticky="e")

        # Create a separator (a horizontal line)
        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=3, column=1, sticky="ew")

        # Create the second label
        self.status_screen_locked = ttk.Label(frame, text="")
        self.status_screen_locked.grid(row=3, column=2, padx=10, sticky="w")

        label = ttk.Label(frame, text="Time since boot")
        label.grid(row=4, column=0, padx=10, sticky="e")

        # Create a separator (a horizontal line)
        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=4, column=1, sticky="ew")
        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=4, column=1, padx=10, sticky="ew")

        # Create the second label
        self.status_time_boot = ttk.Label(frame, text="")
        self.status_time_boot.grid(row=4, column=2, padx=10, sticky="w")

    def update_status_tab(self):

        # multithreading is used here to increase speed by 33%

        def worker_thread():

            battery_status = utils.get_device_dumpsys(self.device, 'battery')
            screen_status = utils.get_device_dumpsys(self.device, 'poweron')
            # cpu_status = utils.get_device_dumpsys(self.device, 'cpuinfo')
            uptime_status = utils.get_device_dumpsys(self.device, 'uptime')

            self.status_battery_percent.config(text=battery_status['percent'])
            self.status_battery_charging.config(text=str(battery_status['is_charging']))
            self.status_screen_on.config(text=str(screen_status['screen_on']))
            self.status_screen_locked.config(text=str(screen_status['screen_locked']))
            self.status_time_boot.config(text=uptime_status)

        thread = threading.Thread(target=worker_thread)
        thread.daemon = True
        thread.start()

        # recommended amount. it takes 0.25-0.4 seconds to do the calculation
        # so I would not recommend any amount below 200 here.
        self.root.after(1000, self.update_status_tab)

    def create_tab_install(self, tab):
        # Create custom content for the install apps tab

        # def target():
        #     print(1)
        #     self.open_app_store()
        #     print(2)

        def execute():

            # thread = threading.Thread(target=target)
            # thread.daemon = True
            open_button.config(text='Opening App Store...', state='disabled', bg='#777', cursor="hand1")
            self.root.update_idletasks()
            self.open_app_store()
            open_button.config(text="Open App Store", bg="#0000ff", fg="#fff", activebackground="#bbb", activeforeground="#000", cursor="hand2", state="active")
            # thread.start()
            # thread.join()

        open_button = tk.Button(tab, text="Open App Store", bg="#0000ff", fg="#fff", activebackground="#bbb", activeforeground="#000", cursor="hand2")
        open_button.pack(pady=20)

        open_button.config(command=execute)

        self.result_label = tk.Label(tab, text="")
        self.result_label.pack()

        self.result_label = tk.Label(tab, text="Installed apps:")
        self.result_label.pack()

        adb_output_widget = tk.Text(tab, wrap='none', height=5, width=30)
        adb_output_widget.insert(tk.END, "\n".join(utils.get_installed_apps(self.device, third_party=True, enabled_only=True)))
        adb_output_widget.config(state='disabled')
        adb_output_widget.pack(padx=10, pady=10)

        button = tk.Button(tab, text="Install APK", command=self.open_directory_dialog)
        button.pack(pady=10)

        button = tk.Button(tab, text="Uninstall App", command=self.uninstall_app_dialog)
        button.pack(pady=10)

        button = tk.Button(tab, text="Enable Apps", command=self.enable_app_dialog)
        button.pack(pady=7)

    def uninstall_app_dialog(self):

        window = tk.Toplevel(self.root)  # Create a new Toplevel window
        window.title("Uninstallation Wizard")  # Set the title for the second window
        window.geometry("800x500")

        def get_selected_items():

            selected_items = [listbox.get(index) for index in listbox.curselection()]  # Get the items from indices

            if messagebox.askyesno("Uninstallation Confirmation", "Are you sure you want to uninstall these apps? (You can always enable them again later by slecting 'enable apps'.)"):

                for app in selected_items:
                    self.device.shell(f'pm disable-user --user 0 {app}')
                    window.destroy()

        yscrollbar = tk.Scrollbar(window)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        label = tk.Label(window, text="Select apps to uninstall: ", padx=10, pady=10)
        label.pack()

        listbox = tk.Listbox(window, selectmode="multiple", yscrollcommand=yscrollbar.set, selectbackground="red")

        packages = utils.get_installed_apps(self.device, third_party=True, enabled_only=True)

        for item in packages:
            listbox.insert(tk.END, item)
            listbox.itemconfig(tk.END, bg="gray")

        listbox.pack(padx=10, pady=10, expand=tk.YES, fill="both")

        yscrollbar.config(command=listbox.yview)

        # Create a button to capture selected items
        capture_button = tk.Button(window, text="Uninstall", command=get_selected_items)
        capture_button.pack(pady=10)

        window.mainloop()

    def enable_app_dialog(self):

        window = tk.Toplevel(self.root)  # Create a new Toplevel window
        window.title("ReInstallation Wizard")  # Set the title for the second window
        window.geometry("800x500")

        def get_selected_items():

            selected_items = [listbox.get(index) for index in listbox.curselection()]  # Get the items from indices

            if messagebox.showinfo("ReInstallation Success", "The apps have been enabled successfully."):

                for app in selected_items:
                    self.device.shell(f'pm enable --user 0 {app}')
                    window.destroy()

        yscrollbar = tk.Scrollbar(window)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        label = tk.Label(window, text="Select apps to enable: ", padx=10, pady=10)
        label.pack()

        listbox = tk.Listbox(window, selectmode="multiple", yscrollcommand=yscrollbar.set, selectbackground="green")

        packages = utils.get_installed_apps(self.device, disabled_only=True)

        for item in packages:
            listbox.insert(tk.END, item)
            listbox.itemconfig(tk.END, bg="gray")

        listbox.pack(padx=10, pady=10, expand=tk.YES, fill="both")

        yscrollbar.config(command=listbox.yview)

        # Create a button to capture selected items
        capture_button = tk.Button(window, text="Renable", command=get_selected_items)
        capture_button.pack(pady=10)

        window.mainloop()

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



        def update():

            # global gabb_updates_disabled
            # global system_updates_disabled
            # print(self.gabb_updates_disabled, self.system_updates_disabled)

            self.gabb_updates_disabled = utils.gabb_updates_disabled(self.device)
            self.system_updates_disabled = utils.system_updates_disabled(self.device)

            if self.system_updates_disabled and not self.updates_is_unlocked:
                capture_button.config(text='System Updates Disabled', state='disabled')
            elif self.system_updates_disabled and self.updates_is_unlocked:
                capture_button.config(text='Enable System Updates', state='normal')
            else:
                capture_button.config(text='Disable System Updates (HIGHLY RECOMMENDED)', state='normal')

            if self.gabb_updates_disabled and not self.updates_is_unlocked:
                capture_button2.config(text='Gabb Updates Disabled', state='disabled')
            elif self.gabb_updates_disabled and self.updates_is_unlocked:
                capture_button2.config(text='Enable PackageUpdater Updates', state='normal')
            else:
                capture_button2.config(text='Disable Gabb Updates (HIGHLY RECOMMENDED)', state='normal')

            if self.updates_is_unlocked:
                button.config(text='Lock')
            else:
                button.config(text='Unlock')

        def unlock():
            if not self.updates_is_unlocked:
                if messagebox.askyesnocancel('Update Confirmation', 'Are you sure you want to unlock updates?'):

                    self.updates_is_unlocked = True
                    update()
            else:
                self.updates_is_unlocked = False
                update()

        def gabb_updates():
            utils.toggle_gabb_updates(self.device, self.gabb_updates_disabled)
            update()

        def system_updates():
            utils.toggle_system_updates(self.device, self.system_updates_disabled)
            update()

        label = tk.Label(tab, text="System Software Updates", padx=10, pady=10)
        label.pack()

        capture_button = tk.Button(tab, command=system_updates)
        capture_button.pack(pady=20)


        label = tk.Label(tab, text="PackageUpdater Gabb Updates", padx=10, pady=10)
        label.pack()

        capture_button2 = tk.Button(tab, command=gabb_updates)
        capture_button2.pack(pady=20)

        button = tk.Button(tab, text='Unlock', command=unlock)
        button.pack(pady=20)

        update()

    def check_disconnect(self):
        """Return True if connected"""
        try:
            response = self.device.info
        except errors.AdbError:
            return False
        return True

    def check_disconnect_loop(self):
        if not self.check_disconnect() and self.device_is_connected:
            self.device_is_connected = False
            messagebox.showwarning('Device Disconnected', 'Your device was disconnected.')
            self.root.destroy()  # remove this line of code to stop the app from closing

        self.root.after(200, self.check_disconnect_loop)

    def create_tab_help(self, tab):

        sub_tab_control = ttk.Notebook(tab)
        sub_tab_control.pack(fill="both", expand=True)

        subtab_a = ttk.Frame(sub_tab_control)
        subtab_b = ttk.Frame(sub_tab_control)
        sub_tab_control.add(subtab_a, text="GUI Help")
        sub_tab_control.add(subtab_b, text="General Help (old)")

        if utils.get_python_version()[1] >= '10':

            try:
                string = requests.get('https://gabbhackguide.netlify.app')

                if string.status_code == 200:
                    string = utils.remove_html_tag(string.text, 'head')
                else:
                    print(string.status_code)
                    raise
            except:
                with open('data/html1.html', 'r', encoding='utf-8') as f:
                    string = f.read()

            frame = HtmlFrame(subtab_b, horizontal_scrollbar="auto")
            frame.set_content(string)
            frame.pack()

            try:
                string = requests.get('https://gabbhackguide.netlify.app/gui')

                if string.status_code == 200:
                    string = utils.remove_html_tag(string.text, 'head')
                else:
                    print(string.status_code)
                    raise
            except:
                with open('data/html1.html', 'r', encoding='utf-8') as f:
                    string = f.read()

            frame = HtmlFrame(subtab_a, horizontal_scrollbar="auto")
            frame.set_content(string)
            frame.pack()


    def __init__(self, root: tk.Tk, device_id):
        self.root = root
        root.minsize(400, 300)
        root.geometry("1000x600")
        self.center_window()
        self.device_id = device_id
        self.root.title("Eth0s Group's Gabb Phone Z2 Hacker")
        # self.root.bind("<Configure>", self.on_resize)

        self.device = adb.device(serial=self.device_id)
        self.gabb_updates_disabled = utils.gabb_updates_disabled(self.device)
        self.system_updates_disabled = utils.system_updates_disabled(self.device)
        self.updates_is_unlocked = False
        self.device_is_connected = self.check_disconnect()

        utils.setup_device(self.device)

        self.root.after(500, self.update_adb_status)
        self.root.after(200, self.check_disconnect_loop())

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
        self.create_tab_help(tab1)  # this takes a longgg time to do. not sure whether to delete or not

        # print(utils.in_setup_mode(self.device))

        #        self.create_tab(tab_control, "Install apps")
        #        self.create_tab(tab_control, "Advanced")

        # Pack the tab control to make it visible

        main_tab_control.pack(fill="both", expand=True)
        self.root.after(1000, self.update_status_tab)


if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectionWaiterApp(root)
    root.mainloop()

    device_id = app.device_id
    should_continue = app.should_continue

    # should_continue = True
    # device_id = '320525532827'

    if should_continue:

        root = tk.Tk()
        app = AdbManagerApp(root, device_id)
        root.mainloop()

