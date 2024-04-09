import os
import cv2
import uuid
from datetime import datetime
import threading

def record_video(camera_index, output_directory="video0"):
    # Get MAC address
    mac_address = hex(uuid.getnode())[2:]

    # Check if output directory exists, create if not
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Capture video from camera
    cap = cv2.VideoCapture(camera_index)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_is_open = False

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            if frame.mean() > 50:
                if not out_is_open:
                    output_filename = os.path.join(output_directory, f"{mac_address}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4")
                    out = cv2.VideoWriter(output_filename, fourcc, 20.0, (width, height))
                    out_is_open = True
                out.write(frame)
            elif frame.mean() < 50 and out_is_open:
                out.release()
                out_is_open = False

            cv2.imshow(output_directory, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()