import cv2
import sys
import time
import boto3, pprint
import email, smtplib, ssl

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)

def send_email_notification():
    subject = "Door Visitor notification"
    body = "There is a visitor at your door"
    sender_email = #Enter Sender Email-id
    receiver_email = #Enter Reciever Email-id
    password = ""

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "/home/pi/SMART_DOOR_LOCK/frame0.jpg"

    # Open JPG file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        "attachment; filename=" + filename,
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


def compare_faces_using_amazon_rekognition():
    s3 = boto3.resource('s3')
    client = boto3.client('rekognition')
    for bucket in s3.buckets.all():
        print(bucket.name)
        for image in bucket.objects.all():
            print(image.key)
            if(image.key == "frame.jpg"):
                print("NOT GOING")
                continue;

            response = client.compare_faces(
                SimilarityThreshold=90,
                SourceImage={
                    'S3Object': {
                        'Bucket': 'samplebucket',
                        'Name': 'frame.jpg',
                    },
                },
                TargetImage={
                    'S3Object': {
                        'Bucket': 'samplebucket',
                        'Name': image.key,
                    },
                },
            )

            pprint.pprint(response)
            print(len(response['FaceMatches']))
            if(len(response['FaceMatches']) > 0):
                send_email_notification();
                GPIO.output(16, GPIO.HIGH) # Turn on
                sleep(1) # Sleep for 1 second
                GPIO.output(16, GPIO.LOW) # Turn off
                sleep(1) # Sleep for 1 second
            else:
                print("-"*100)    
            print("#"*100)


def upload_on_amazon_s3():
    s3 = boto3.client('s3')
    filename = 'frame.jpg'
    bucket_name = 'samplebucket'

    # Uploads the given file using a managed uploader, which will split up large
    # files automatically and upload parts in parallel.
    s3.upload_file('/home/pi/SMART_DOOR_LOCK/frame0.jpg', bucket_name, filename)


def capture_image():
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # Draw a rectangle around the faces
        count =0;
        for (x, y, w, h) in faces:
            #cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            print("Count = " + str(count) + "\n");
            video_capture.set(cv2.CAP_PROP_POS_MSEC,5000)
            cv2.imwrite("/home/pi/SMART_DOOR_LOCK/frame%d.jpg"%count, frame)
            upload_on_amazon_s3();
            compare_faces_using_amazon_rekognition();
            count = count +1

        # Display the resulting frame
    #    cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


capture_image();
