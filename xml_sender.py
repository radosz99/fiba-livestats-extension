import time
import sys

import paramiko
from paramiko.ssh_exception import AuthenticationException


class Server():
    def __init__(self, ip, username, path_to_xml, password):
        self.ip = ip
        self.username = username
        self.path_to_xml = path_to_xml
        self.password = password

    def init_ssh_session(self):
        self.ssh = paramiko.SSHClient() 
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname=self.ip, username=self.username, password=self.password)
            print("Udało się zalogować za pomocą hasła")
        except AuthenticationException:
            print("Hasło z 'config.json' jest nieprawidłowe!")
            return 
        self.sftp = self.ssh.open_sftp()

    def put_xml_on_server(self, local_xml_path, server_xml_path):
        self.sftp.put(local_xml_path, server_xml_path)

    def close_ssh_session(self):
        self.sftp.close()
        self.ssh.close()

def get_server_info():
    return Server("12.345.67.89", "test_user", "/home/stats/game.xml", "123456")


def send_xml(local_xml_path, server_xml_path):
    server = get_server_info()
    while(True):
        try:
            server.put_xml_on_server(local_xml_path, server_xml_path)
            print("Umieszczono plik .xml na serwerze")
            time.sleep(0.2)
        except Exception:
            server = get_server_info()
            server.init_ssh_session()


if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print("Podaj lokalną ścieżkę do XML oraz ścieżkę gdzie umieścić XML na serwerze")
        sys.exit(1)
    else:
        send_xml(sys.argv[1], sys.argv[2])