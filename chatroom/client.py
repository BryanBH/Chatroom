import logging
import sys

from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QWidget, QMessageBox, QHBoxLayout, \
    QApplication
from PyQt5.QtCore import Qt
from socket import AF_INET, socket, SOCK_STREAM, inet_aton
from threading import Thread

from qconsole import QConsole

ip, port, username = '0.0.0.0', 33000, 'anon'
client_socket = None
window = None
BUFSIZ = 2048

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.ip = QLineEdit()
        self.port = QLineEdit()
        self.username = QLineEdit()
        self.login_button = QPushButton('Connect')
        self.login_button.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('IP:'))
        layout.addWidget(self.ip)
        layout.addStretch()
        layout.addWidget(QLabel('Port:'))
        layout.addWidget(self.port)
        layout.addStretch()
        layout.addWidget(self.login_button)

        self.resize(300, 100)
        self.setLayout(layout)
        self.setWindowTitle('Connect')

    def login(self):
        if self.ip.text() != '' \
                and self.port.text() != '':
            if check_ip(self.ip.text()):
                global ip, port, username
                ip = self.ip.text()
                port = int(self.port.text())
                username = self.username.text()

                try:
                    address = (ip, port)
                    global client_socket
                    client_socket = socket(AF_INET, SOCK_STREAM)
                    client_socket.connect(address)
                    self.accept()
                except ConnectionError as e:
                    QMessageBox.warning(self, 'Error', str(e))

            else:
                logging.warning('Invalid IP')
                QMessageBox.warning(self, 'Error', 'Invalid IP')
        else:
            logging.warning('No username and/or password entered')
            QMessageBox.warning(self, 'Error', 'No username and/or password entered')


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.message_window = QConsole()

        self.message_input = QLineEdit()
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send)
        self.message_input.returnPressed.connect(self.send)

        self.send_hbox = QHBoxLayout()
        self.send_hbox.addWidget(self.message_input)
        self.send_hbox.addWidget(self.send_button)

        self.full = QVBoxLayout()
        self.full.addWidget(self.message_window, Qt.AlignLeft)
        self.full.addLayout(self.send_hbox)

        self.setLayout(self.full)
        self.setWindowTitle('WIT Chatroom')

    def send(self):
        message = self.message_input.text()
        self.message_input.clear()
        send_msg(message, username)


def check_ip(string):
    try:
        inet_aton(string)
        return True
    except socket.error:
        return False


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            rcv = client_socket.recv(BUFSIZ).decode("utf8")
            logging.debug(rcv)
            message, username = rcv.split(';')
            window.message_window.print_user_message(message, username)

        except OSError:  # Possibly client has left the chat.
            break


def send_msg(message, username, event=None):  # event is passed by binders.
    """Handles sending of messages."""
    if message == "-quit-":
        client_socket.close()
        sys.exit()
    else:
        client_socket.send(bytes(message, "utf8"))


def main():
    global window
    app = QApplication(sys.argv)
    login = Login()
    window = Window()

    if login.exec_() == QDialog.Accepted:
        receive_thread = Thread(target=receive)
        receive_thread.start()

        window.resize(800, 600)
        window.show()
        sys.exit(app.exec_())

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()