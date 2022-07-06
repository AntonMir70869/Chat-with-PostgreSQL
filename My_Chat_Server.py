import socket
from threading import Thread
import psycopg2
from psycopg2 import Error


class Server:
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5002
    separator_token = "<SEP>"

    def __init__(self):
        self.serv = socket.socket()
        self.serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv.bind((Server.SERVER_HOST, Server.SERVER_PORT))
        self.serv.listen(5)
        print(f"[*] Listening as {Server.SERVER_HOST}:{Server.SERVER_PORT}")

    def _accept(self):
        return self.serv.accept()


class DBcommand:
    def __init__(self, conn):
        self.conn = conn
        self.tab_name = "chat_log"
        self.create_tab()

    def create_tab(self):
        with self.conn:
            with self.conn.cursor() as cur:
                try:
                    tab_set = "(massage_id serial PRIMARY KEY, massage varchar)"
                    cur.execute(f"DROP TABLE IF EXISTS {self.tab_name}", )
                    cur.execute(f"CREATE TABLE {self.tab_name} {tab_set}", )

                except (Exception, Error):
                    print("Error while working with PostgreSQL", Error)

                finally:
                    print(f"Table {self.tab_name}  has been created successfully")

    def create_log(self, massage):
        with self.conn:
            with self.conn.cursor() as cur:
                try:
                    massage = list(massage)
                    massage.insert(len(massage), "'")
                    massage.insert(0, "'")
                    massage = "".join(massage)
                    cur.execute(f"INSERT INTO {self.tab_name} (massage) VALUES ({massage})")
                except (Exception, Error):
                     print("Error while working with PostgreSQL", Error)
                finally:
                    print(f"In the table {self.tab_name} new values has been inserted successfully")

    def read_tab(self):
        with self.conn:
            with self.conn.cursor() as cur:
                try:
                    cur.execute(f"SELECT * FROM {self.tab_name}", )

                except (Exception, Error):
                    print("Error while working with PostgreSQL", Error)

                finally:
                    print("The table content:")
                    full_fetch = cur.fetchall()
                    for record in full_fetch:
                        print(record)
                    return full_fetch

    def read_last_log(self):
        with self.conn:
            with self.conn.cursor() as cur:
                try:
                    cur.execute(f"SELECT * FROM {self.tab_name}", )

                except (Exception, Error):
                    print("Error while working with PostgreSQL", Error)

                finally:
                    print("The table content:")
                    full_fetch = cur.fetchall()
                    print(full_fetch[-1])
                    return full_fetch[-1]


client_sockets = set()

serv = Server()

conn = psycopg2.connect(dbname="test_db", password="axbsl286", user="postgres")

db_com = DBcommand(conn)


def listen_for_client(cs, db_com):
    while True:
        try:
            msg = cs.recv(1024).decode()
            msg = msg.replace(serv.separator_token, ":")
            db_com.create_log(msg)
            msg = db_com.read_last_log()[1]

            for client_socket in client_sockets:
                client_socket.send(msg.encode())
        except Exception as e:

            print(f"[!] Error: {e}")
            client_sockets.remove(cs)


while True:
    client_socket, client_address = serv._accept()
    print(f"[+] {client_address} connected.")

    client_sockets.add(client_socket)

    t1 = Thread(target=listen_for_client, args=(client_socket, db_com))

    t1.daemon = True

    t1.start()

for cs in client_sockets:
    cs.close()

serv.close()
