import face_recognition
import os
import cv2
import pickle
import time
import csv
import collections

KNOWN_FACES_DIR = 'known_faces'
#UNKNOWN_FACES_DIR = 'unknown_faces'
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'hog'  # default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model
video = cv2.VideoCapture(0)

# Returns (R, G, B) from name
def name_to_color(name):
    # Take 3 first letters, tolower()
    # lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8
    color = [(ord(c.lower())-97)*8 for c in name[:3]]
    return color


print('Loading known faces...')
known_faces = []
known_names = []

# We oranize known faces as subfolders of KNOWN_FACES_DIR
# Each subfolder's name becomes our label (name)
for name in os.listdir(KNOWN_FACES_DIR):

    # Next we load every file of faces of known person
    for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):

        # Load an image
      #  image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}/{filename}')

        # Get 128-dimension face encoding
        # Always returns a list of found faces, for this purpose we take first face only (assuming one face per image as you can't be twice on one image)

       # encoding = face_recognition.face_encodings(image)[0]
        encoding = pickle.load(open(f"{name}/{filename}","rb"))
        # Append encodings and name
        known_faces.append(encoding)
        known_names.append(int(name))
if len(known_names)>0:
    next_id = max(known_names) + 1
else:
    next_id = 0

print('Opening camera...')
# Now let's loop over a folder of faces we want to label
while True:

    # Load image
    #print(f'Filename {filename}', end='')

    #image = face_recognition.load_image_file(f'{UNKNOWN_FACES_DIR}/{filename}')
    ret,image = video.read()
    cv2.imshow("frame", image)
    # This time we first grab face locations - we'll need them to draw boxes

        #if image == "None":
    locations = face_recognition.face_locations(image, model=MODEL)

# Now since we know loctions, we can pass them to face_encodings as second argument
# Without that it will search for faces once again slowing down whole process
    encodings = face_recognition.face_encodings(image, locations)

# We passed our image through face_locations and face_encodings, so we can modify it
# First we need to convert it from RGB to BGR as we are going to work with cv2
#image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

# But this time we assume that there might be more faces in an image - we can find faces of dirrerent people
    print(f', found {len(encodings)} face(s)')
    for face_encoding, face_location in zip(encodings, locations):

    # We use compare_faces (but might use face_distance as well)
    # Returns array of True/False values in order of passed known_faces
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)

    # Since order is being preserved, we check if any face was found then grab index
    # then label (name) of first matching known face withing a tolerance
        match = None
        if True in results:  # If at least one is true, get a name of first of found labels
            match = known_names[results.index(True)]
            print(f'Match found: {match}')
        else:
            match = str(next_id)
            next_id += 1
            known_names.append(match)
            known_faces.append(face_encoding)
            os.mkdir(f"{KNOWN_FACES_DIR}/{match}")
            pickle.dump(face_encoding,open(f"{KNOWN_FACES_DIR}/{match}/{match}-{int(time.time())}.pkl","wb"))
            fieldnames = ["student_ID"]
            with open('thefile.csv', 'a') as file:
                writer = csv.DictWriter(file,fieldnames=fieldnames)
                writer.writerow({
                    "student_ID":next_id})

        # Each location contains positions in order: top, right, bottom, left
        top_left = (face_location[3], face_location[0])
        bottom_right = (face_location[1], face_location[2])

    # Get color by name using our fancy function
        color = name_to_color(match)

    # Paint frame
        cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

    # Now we need smaller, filled grame below for a name
    # This time we use bottom in both corners - to start from bottom and move 50 pixels down
        top_left = (face_location[3], face_location[2])
        bottom_right = (face_location[1], face_location[2] + 22)

    # Paint frame
        cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)

    # Wite a name
        cv2.putText(image, match, (face_location[3] + 10, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), FONT_THICKNESS)

# Show image
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
#cv2.destroyWindow(filename)
