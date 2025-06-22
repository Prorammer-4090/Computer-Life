import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)    # is this correct 




def eye_dist(img):
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:
        face = faces[0]
        pointLeft = face[145]
        pointRight = face[374]
        cv2.circle(img,pointLeft,5, (255,0,255), cv2.FILLED)
        cv2.circle(img, pointRight, 5, (255, 0, 255), cv2.FILLED)
        w, _ = detector.findDistance(pointLeft, pointRight)

        W = 6.3 
        f = 820
        d = W*f/w
        d = int(d)
        return d
    





# while True:
#     sucess, img  = cap.read()
#     img, faces = detector.findFaceMesh(img, draw=False)

#     if faces:
#         face = faces[0]
#         pointLeft = face[145]
#         pointRight = face[374]
#         cv2.circle(img,pointLeft,5, (255,0,255), cv2.FILLED)
#         cv2.circle(img, pointRight, 5, (255, 0, 255), cv2.FILLED)
#         w, _ = detector.findDistance(pointLeft, pointRight)

#         #Finding the focal length
#         W = 6.3 #avg distance between eyes
#         # d = 50
#         # f = w*d/W
#         # print(f)

#         #Finding distance
#         f = 820
#         d = W*f/w
#         d = int(d)
#         cvzone.putTextRect(img, f'Depth: {d}cm', (face[10][0], face[10][1]), scale = 2)

#     cv2.imshow("Image", img)
#     cv2.waitKey(1)