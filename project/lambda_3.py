import json
import boto3
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer


# s3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input

    key =  event['s3_key']
    bucket = event['s3_bucket']

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }



# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2024-08-21-17-39-37-379'

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image-data'])

    # Instantiate a Predictor
    predictor = sagemaker.predictor.Predictor(
            endpoint_name=ENDPOINT,
            sagemaker_session=sagemaker.Session())

    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")

    # Make a prediction:
    inferences = predictor.predict(image)

    # We return the data back to the Step Function
    event['body']["inferences"] = inferences.decode('utf-8')
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }



THRESHOLD = .93

def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['body']['inferences']

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = inferences > THRESHOLD

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        event['body']['inferences'] = inferences
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
