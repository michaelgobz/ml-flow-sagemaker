import json
import boto3
import sagemaker
import ast
import base64
from sagemaker.serializers import IdentitySerializer


THRESHOLD = .93

class ThresholdException(Exception):
    def __init__( self, message):
        self.mssg = message
        
        
    def __rep__(self):
        print(f'{self.mssg}')

def lambda_handler(event, context):


    # Grab the inferences from the event
    inferences = ast.literal_eval(event['body']['inferences'])

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = inferences[0] > THRESHOLD or  inferences[1] > THRESHOLD

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold == 1:
        event['body']['inferences'] = inferences
    else:
        raise ThresholdException("THRESHOLD_CONFIDENCE_NOT_MET of 93%, Retain the Classifier")
       
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
