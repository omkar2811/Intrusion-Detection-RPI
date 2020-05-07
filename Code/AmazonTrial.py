import boto3
import pprint

#sdk for accesing aws.
s3 = boto3.resource('s3')#s3 is a cloud storage system.

#connect to rekognition api
client = boto3.client('rekognition')


for bucket in s3.buckets.all():
    print(bucket.name)
    for image in bucket.objects.all():
        print(image.key)#key of image
        
        #function compare faces is used to compare.
        response = client.compare_faces(
            SimilarityThreshold=90,#90% similar at least.
            SourceImage={
                'S3Object': {
                    'Bucket': 'samplebucket',
                    'Name': 'frame.jpg',
                },
            },
            TargetImage={
                'S3Object': {
                    'Bucket': 'samplebucket',
                    'Name': image.key,#compare with every image
                },
            },
        )

        pprint.pprint(response)
        print(len(response['FaceMatches']))
        if(len(response['FaceMatches']) > 0)
        {
                
        }
        print("#"*100)

# print(response)
