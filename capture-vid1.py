import os
import cv2
import uuid
from datetime import datetime
import threading

from utils import record_video

def main():
    # Define camera indices
    camera_index = 1  # Index of the first camera

    # Create threads for each camera
    thread1 = threading.Thread(target=record_video, args=(camera_index, "video1",))
    

    # Start the threads
    thread1.start()


    # Wait for both threads to finish
    thread1.join()

if __name__ == "__main__":
    main()
