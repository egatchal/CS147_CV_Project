import threading

import cv2
from deepface import DeepFace
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0

threads = []
face_match = False

reference_img = cv2.imread("reference.jpg")

def check_face(frame):
    global face_match
    try:
        if DeepFace.verify(frame, reference_img.copy())['verified']:
            if not face_match:
                face_match = True
        else:
            if not face_match:
                face_match = False
    except ValueError:
        if not face_match:
            face_match = False


while True:
    ret, frame = cap.read() # TODO: image received from camera 
    threads = []
    if ret:
        # TODO: create for loop that over users friends
        if counter % 30 == 0:
            try:
                thread = threading.Thread(target=check_face, args=(frame.copy(), )).start()
                threads.append(thread)
            except ValueError:
                pass
            counter += 1

        if face_match: # if match
            cv2.putText(frame, "MATCH!", (20,450), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2, (0,255,0)) # filler code
        else: # if match
            cv2.putText(frame, "NO MATCH!", (20,450), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2, (0,0,255)) 

        cv2.imshow("vidoe", frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

cv2.destroyAllWindows()
