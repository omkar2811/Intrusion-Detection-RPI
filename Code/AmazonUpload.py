import boto3

s3 = boto3.client('s3')

filename = 'frame.jpg'
bucket_name = 'samplebucket'

# Uploads the given file using a managed uploader, which will split up large
# files automatically and upload parts in parallel.
s3.upload_file('path-to-image/frame.jpg', bucket_name, filename)
