
## Take-home submission from Alexandru Bangau (Cloudgeometry) to sedric.ai

The project was implementing using serverless services (aws lambda), and achieves scalability through the asynchronous operation of the pipeline.

The source is strctured in two parts: iac containing cdk code to deploy all required infrastructure and code, and src where the application logic lies.

## Deployment
Just change into the cdk directory, and deploy it.
The application only has one stack that deploys all the necessary resources. After the cdk deployment everything should work just fine.

## Architecture
The application consists of three main lambda functions as follows.

### transcripts_api
This functions has the following jobs:
- Handles requests to post a new audio file and sentences and returns a request id.
- Handles requests to get the status and results of the analysis request.
- Launches the analysis process by posting a message to an sqs queue

### process_audio
This lambda will be triggered by the sqs queue mentioned above and perform the following:
- Download the audio file into s3
- Launch a transcription request to aws transcribe

### analyse_transcript
The final function gets triggered when an object matching the format we define in our transcribe request is created on s3.
The steps of this function are:
- Load the transcript
- Perform the analysis of sentences
- Save the result

All functions use `aws_lambda_powertools` layer and a common application layer (found under `src/layers/common`).
All lambdas store/read metadata about the request which is stored in a dynamodb table.
All functions also use only python `standard`, `boto3` or `aws_lambda_powertools` libraries.
