from picamera2 import Picamera2
from ultralytics import YOLO
import os
import cv2

# alle variabelen aanmaken die nodig zijn voor het script
model = YOLO("yolov8n.pt")
home = os.environ['HOME']
yolo_dir = home + "/YOLO"
os.makedirs(yolo_dir, exist_ok=True) # ~/YOLO moet bestaan, anders maakt hij deze eest aan
image = yolo_dir + "/image.jpg"
result = yolo_dir + "/result.jpg"


# camera aanmaken en een foto maken
if os.path.exists(image):
    os.remove(image)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

def get_animal():
    picam2.capture_file(image)
    picam2.stop()
    print("Image captured and saved to " + image)


    # model laden en de foto analyseren
    results = model(image, imgsz=640, verbose=False)[0]


    # resultaten uitlezen
    if len(results.boxes) == 0:
        class_name = "no object"
        print("No objects detected.")
    else:
        for box in results.boxes:
            confidence = box.conf[0].item()     #Confidence score of the detection
            class_id = int(box.cls[0].item())   #Class ID of the detection
            class_name = model.names[class_id]  #Name of the detected class
            print(f"Detected {class_name} with confidence {confidence*100:.0f}%")


    # result opslaan
    if os.path.exists(result):
        os.remove(result)
        print("Old result file removed.")

    annotated = results.plot()
    cv2.imwrite(result, annotated)
    print(f"{len(results.boxes)} objects detected, saved as {result}")


    # Verwijderen file na gebruik
    if os.path.exists(image):
        os.remove(image)
        print("Image file removed after processing.")
    return(class_name)