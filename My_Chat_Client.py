import socket
from threading import Thread
from datetime import datetime
from tkinter import *


class Client(socket.socket):
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5002
    separator_token = "<SEP>"

    def __init__(self):
        super(Client, self).__init__()
        super(Client, self).connect((Client.SERVER_HOST.encode(),
                                     Client.SERVER_PORT))

        print(f"[*] Connecting to {Client.SERVER_HOST}:{Client.SERVER_PORT}...")
        print("[+] Connected.")


class Strings(Thread):
    def __init__(self, sock):
        super(Strings, self).__init__(target=listen_for_messages)
        self.sock = sock
        self.daemon = True


def listen_for_messages():
    cli.setblocking(False)
    while True:
        try:
            message = cli.recv(1024).decode()
            log.insert(END, message + '\n')
            print("\n" + message)
        except:
            continue


tk = Tk()

text = StringVar()
name = StringVar()
name.set('HabrUser')
text.set('')
tk.title('MegaChat')
tk.geometry('400x300')

log = Text(tk)
nick = Entry(tk, textvariable=name)
msg = Entry(tk, textvariable=text)
msg.pack(side='bottom', fill='x', expand=True)
nick.pack(side='bottom', fill='x', expand=True)
log.pack(side='top', fill='both', expand=True)

cli = Client()

t = Strings(cli)

t.start()


def sendproc(event):
    while True:
        to_send = msg.get()

        if to_send.lower() == 'q':
            break
        elif to_send.lower() == '':
            break

        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        to_send = f"[{date_now}] {name.get()}{cli.separator_token} {to_send}"

        cli.send(to_send.encode())
        text.set('')


msg.bind('<Return>', sendproc)
tk.mainloop()
cli.close()
