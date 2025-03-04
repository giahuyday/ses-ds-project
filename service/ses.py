import os
import threading
import socket
from datetime import datetime

class Process(threading.Thread):
    def __init__(self, pid, ip, port, processes, log_file, num_messages):
        super().__init__()
        self.pid = pid
        self.ip = ip
        self.port = port
        self.processes = processes
        self.lock = threading.Lock()
        self.buffer = []
        self.log_file = log_file
        self.num_messages = num_messages

        # Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def process_logger(self, message):
        with open(f'{self.log_file}', 'a') as f:
            f.write(f"{datetime.now()} - {message}\n")

    def send_message(self, message, target_process):
        self.sock.sendto(message.encode(), (target_process.ip, target_process.port))
        self.process_logger(f"Process {self.pid} delivering: {message}")

    def send_messages(self):
        for i in range(self.num_messages):
            message = f"message {i + 1} from Process {self.pid}"

            for target in self.processes:
                if target.pid != self.pid:
                    self.process_logger(f"Process {self.pid} buffering: {message}")
                    self.buffer.append((message, target))

            threads = []
            for msg, target in self.buffer:
                t = threading.Thread(target=self.send_message, args=(msg, target))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            self.buffer.clear()

    def receive_messages(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            self.receive_message(message, addr)

    def receive_message(self, message, addr):
        with self.lock:
            timestamp = datetime.now()
            print(f"Process {self.pid} received: {message} at {timestamp} by {addr}")
            self.process_logger(f"Process {self.pid} received: {message}")

    def run(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.send_messages()