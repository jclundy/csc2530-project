from common import *
from threading import Thread
from threading import Event
from queue import Queue


if __name__ == '__main__':
    print("running multithreaded supervisor")

    camera_event = Event()
    serial_event = Event()

    camera_queue = Queue()
    serial_queue = Queue()

    user_input_thread = Thread(target=run_user_input, args=(serial_queue, camera_queue,))
    serial_thread = Thread(target=run_serial, args=(serial_queue, serial_event, ))
    camera_thread = Thread(target=run_camera, args=(camera_queue, camera_event, ))

    user_input_thread.start()
    serial_thread.start()
    camera_thread.start()