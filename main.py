from service.ses import Process
from constant.config import config

def main():
    num_messages = config["num_messages"]
    log_file_prefix = "process_log_"

    processes = []
    for pid, (ip, port) in config["processes"].items():
        log_file = f"./logger/{log_file_prefix}{pid}.log"
        processes.append(Process(int(pid), ip, port, processes, log_file, num_messages))

    for p in processes:
        p.start()

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()