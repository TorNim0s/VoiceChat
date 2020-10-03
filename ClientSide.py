import tkinter as tk
import socket
import threading
import pyaudio

class Client:
    def __init__(self, ip, port, canvas, login_screen, name):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.target_ip = ip
            self.target_port = int(port)
            self.name = name

            self.canvas = canvas

            self.users = []

            self.login_screen = login_screen

            self.s.connect((self.target_ip, self.target_port))

        except:
            print("Couldn't connect to server")
            output = tk.Label(self.login_screen)
            output.config(font=('David', 10), fg="firebrick2", bg="gray86", text="Couldn't connect to server")
            self.canvas.create_window(200, 200, window=output)

            return

        self.s.send(self.name.encode())

        # Receive data from server
        data_users = self.s.recv(1024).decode()
        self.users = data_users.split("|")
        self.users.remove("accounts")

        print(self.users)

        chunk_size = 1024  # 512
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        # initialise microphone recording
        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)
        self.login_screen.destroy()
        print("Connected to Server")

        # start threads
        receive_thread = threading.Thread(target=self.receive_server_data).start()

        send_thread = threading.Thread(target=self.send_data_to_server).start()

        update_app_thread = threading.Thread(target=self.update_app_screen).start()

        self.app = App_screen(self, self.name, self.users)

    def update_app_screen(self):
        while True:
            try:
                data = self.s.recv(1024).decode()
                print(data)
                if ("accounts" in data):
                    print("test2")
                    self.users = data.split("|")
                    self.users.remove("accounts")
                    self.app.destroy
                    self.app = App_screen(self, self.name, self.users)
            except:
                pass

    def receive_server_data(self):
        while True:
            try:
                data = self.s.recv(1024)
                if ("accounts" not in data.decode()):
                    self.playing_stream.write(data)
            except:
                pass

    def send_data_to_server(self):
        while True:
            try:
                data = self.recording_stream.read(1024)
                self.s.sendall(data)
            except:
                pass

    def terminate_session(self):

        self.s.close()

def login_screen():
    login_screen = tk.Tk()

    canvas1 = tk.Canvas(login_screen, width=400, height=500)
    canvas1.config(bg="gray86")
    canvas1.pack()

    Title = tk.Label(login_screen, text='Login panel')
    Title.config(font=('helvetica 35 bold'), fg="dark turquoise", bg="gray86")

    canvas1.create_window(175, 40, window=Title)

    name_label = tk.Label(login_screen, text='Name:')
    name_label.config(font=('helvetica', 10), bg="gray86")
    canvas1.create_window(100, 100, window=name_label)

    name_input = tk.Entry(login_screen)
    canvas1.create_window(200, 100, window=name_input)

    ip_label = tk.Label(login_screen, text='IP:')
    ip_label.config(font=('helvetica', 10), bg="gray86")
    canvas1.create_window(100, 140, window=ip_label)

    ip_input = tk.Entry(login_screen)
    canvas1.create_window(200, 140, window=ip_input)

    port_label = tk.Label(login_screen, text='Port:')
    port_label.config(font=('helvetica', 10), bg="gray86")
    canvas1.create_window(100, 180, window=port_label)

    port_input = tk.Entry(login_screen)
    canvas1.create_window(200, 180, window=port_input)

    def make_connection():
        ip = ip_input.get()
        port = port_input.get()
        name = name_input.get()

        client = Client(ip, port, canvas1, login_screen, name)

    button1 = tk.Button(text='Connect to server', command=make_connection)
    canvas1.create_window(100, 450, window=button1)

    login_screen.mainloop()

def App_screen(client, name, users):
    app_screen = tk.Tk()

    app_canvas = tk.Canvas(app_screen, width=400, height=500)
    app_canvas.config(bg="gray86")
    app_canvas.pack()

    Title = tk.Label(app_screen, text='EL-Talk')
    Title.config(font=('helvetica 35 bold'), fg="dark turquoise", bg="gray86")
    app_canvas.create_window(100, 40, window=Title)

    name_label = tk.Label(app_screen, text='List of users')
    name_label.config(font=('helvetica bold', 20), bg="gold")
    app_canvas.create_window(100, 100, window=name_label)

    i = 140

    for user in users:
        if user == name:
            ip_label = tk.Label(app_screen, text=user)
            ip_label.config(font=('helvetica', 10), bg="steel blue")
            app_canvas.create_window(100, i, window=ip_label)
            i += 25
            continue

        ip_label = tk.Label(app_screen, text=user)
        ip_label.config(font=('helvetica', 10), bg="light goldenrod")
        app_canvas.create_window(100, i, window=ip_label)
        i += 25

    #ip_label = tk.Label(app_screen, text=name)
    #ip_label.config(font=('helvetica', 10), bg="light goldenrod")
    #app_canvas.create_window(100, 140, window=ip_label)

    def close_app():
        client.terminate_session() # stop session with the server
        app_screen.destroy() # stop app_scren
        login_screen() # go back to login screen

    close_app_button = tk.Button(text='Exit', command=close_app)
    app_canvas.create_window(100, 450, window=close_app_button)

    app_screen.mainloop()

    return app_screen

def main():
    login_screen()

if __name__ == "__main__":
    main()