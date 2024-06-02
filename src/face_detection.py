import threading
import cv2
from deepface import DeepFace

face_match = False
reference_img = cv2.imread("reference.jpg")

def check_face(frame):
    global face_match
    result = False
    faces = []
    # TODO: create for loop that loops over user's friends (insert sql retrieval)
    for face in faces:
        try:
            if DeepFace.verify(frame, face): # user friend image
                result = True
                break
        except ValueError:
            continue
    face_match = result


while True:
    ret, frame = cap.read() # TODO: image received from camera 
    if ret:
        if counter % 30 == 0:
            try:
                threading.Thread(target=check_face, args=(frame.copy(), )).start()
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