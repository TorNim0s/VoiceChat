import tkinter as tk
import socket
import threading
import pyaudio


class Client:
    def __init__(self, ip, port, canvas, login_screen):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.target_ip = ip
        self.target_port = int(port)

        self.canvas = canvas

        self.login_screen = login_screen

        try:
            self.s.connect((self.target_ip, self.target_port))
            output = tk.Label(self.login_screen)
            output.config(font=('David', 10), fg="firebrick2", bg="gray86", text="Connected")
            self.canvas.create_window(200, 200, window=output)


        except:
            print("Couldn't connect to server")
            output = tk.Label(self.login_screen)
            output.config(font=('David', 10), fg="firebrick2", bg="gray86", text="Couldn't connect to server")
            self.canvas.create_window(200, 200, window=output)

            return

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

        self.send_data_to_server()

    def receive_server_data(self):
        while True:
            try:
                data = self.s.recv(1024)
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


def main():
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

        client = Client(ip, port, canvas1, login_screen)

    button1 = tk.Button(text='Connect to server', command=make_connection)
    canvas1.create_window(200, 230, window=button1)

    login_screen.mainloop()


if __name__ == "__main__":
    main()