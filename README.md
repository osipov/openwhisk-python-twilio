# Serverless computing on IBM Cloud

This text messaging app shows how to use IBM Cloud serverless computing infrastructure built on OpenWhisk. The app is implemented in Python, packaged as a Docker image, and executed by OpenWhisk in a Docker container. 

When a JSON document describing the text message is created in a Cloudant (PouchDB based) database, OpenWhisk instantiates a Docker container with the Python code that connects to Twilio's text messaging service and sends an SMS.

### Before you start

[OpenWhisk](https://github.com/openwhisk/openwhisk) serverless computing environment is hosted on IBM Bluemix. To sign up for a 30 day trial of Bluemix register here: https://console.ng.bluemix.net/registration/

This app uses [Twilio](https://www.twilio.com) for text messaging capabilities. To sign up for a Twilio account visit: https://www.twilio.com/try-twilio Make sure that once you have a Twilio account, you also obtain the account SID, authentication token, and register a phone number with an SMS capability.

OpenWhisk uses [Docker Hub](https://hub.docker.com) to execute Docker based actions. You will need a Docker Hub account and you can sign up for one here: https://hub.docker.com

**NOTE:** To make it easier to use the instructions, export your various account settings as environment variables:

* your Docker Hub username as DOCKER_USER
* your Twilio Account SID as TWILIO_SID
* your Twilio Auth Token as TWILIO_TOKEN
* your Twilio SMS capable phone number as TWILIO_NUMBER

```
export DOCKER_USER=''
export TWILIO_SID=''
export TWILIO_TOKEN=''
export TWILIO_NUMBER=''
```

### Clone the OpenWhisk action implementation

The OpenWhisk action is implemented as a Python Flask application that is packaged as a Docker image and published to Docker Hub. You can clone the code for the action from github by running the following from your command line

```git clone https://github.com/osipov/openwhisk-python-twilio.git```

This will create an ```openwhisk-python-twilio``` folder in your current working directory.

All of the code for the OpenWhisk action is in the ```py/service.py``` file. There are two functions, called _init_ and _run_ that correspond to Flask app routes /init and /run. The init function is called on an HTTP POST request and returns an HTTP 200 status code as expected by the OpenWhisk platform. The run function verifies that an incoming HTTP POST request is a JSON document containing Twilio configuration parameters and the content of the text message. After configuring a Twilio client and sending the text message, the function returns back an HTTP 200 status code and a JSON document with a success status message.

###Build and package the action implementation in a Docker image

If you don't have Docker installed, it is available per the instructions provided in the link below. Note that if you are using Windows or OSX, you will want to install Docker Toolbox.

https://docs.docker.com/engine/installation/

Make sure that your [Docker Hub](https://hub.docker.com) account is working correctly by trying to login using

```docker login -u $DOCKER_USER ```

You will be prompted to enter your Docker Hub password.

Change to ```openwhisk-python-twilio``` as your working directory and execute the following commands to build the Docker image with the OpenWhisk action implementation and to push the image to Docker Hub. 

```
docker build -t $DOCKER_USER/openwhisk .
docker push $DOCKER_USER/openwhisk
```

Use your browser to login to https://hub.docker.com after the docker push command is done. You should be able to see the **openwhisk** image in the list of your Docker Hub images.

###Create a stateless, Docker-based OpenWhisk action

To get started with OpenWhisk, download and install a command line interface using the instructions from the following link

https://new-console.ng.bluemix.net/openwhisk/cli

The following commands need to be executed to configure your OpenWhisk action instance:

```
wsk action create --docker textAction $DOCKER_USER/openwhisk
wsk action update textAction --param account_sid "$TWILIO_SID" --param auth_token "$TWILIO_TOKEN"
```

The first command sets up a Docker-based OpenWhisk action called textAction that is implemented using the ```$DOCKER_USER/openwhisk``` image from Docker Hub. The second command configures the textAction with the Twilio account SID and authentication token, so that they don't need to be passed to the action on every action invocation.

###Test the serverless computing action

Replace the to phone number (to parameter) and the text message contents (msg parameter) with the ones you prefer and execute the command to confirm that the text message is sent as expected.

```
wsk action invoke --blocking --result -p from "$TWILIO_NUMBER" -p to "555-867-5309" -p msg "Jenny I got your number" textAction
```

Upon successful action execution you should be able to see an output similar to the following:

```
{
    "status": [
        {
            "success": "true"
        },
        {
            "message_sid": "SM5ecc4ee8c73b4ec29e79c0f1ede5a4c8"
        }
    ]
}
```

## [OPTIONAL] Use Cloudant to log text messages

by creating a document in the Cloudant database

Open a separate console window and execute the following command to monitor the result of running the OpenWhisk action 

```
wsk activation poll
```

In another console, create a document in Cloudant using the following curl command




###Create a Cloudant / JSON document database in IBM Bluemix

Download a CF command line interface for your operating system using the following link

https://github.com/cloudfoundry/cli/releases

and then install it.

From your command line type in 

    cf login -a api.ng.bluemix.net

to authenticate with IBM Bluemix and then enter your Bluemix email, password, as well as the deployment organization and space as prompted.

To export your selection of the deployment organization and space as environment variables for the future configuration of the OpenWhisk action:

```
export ORG=`cf target | grep 'Org:' | awk '{print $2}'`
export SPACE=`cf target | grep 'Space:' | awk '{print $2}'`
```

To create a new Cloudant database, run the following commands from your console

```
cf create-service cloudantNoSQLDB Shared cloudant-deployment

cf create-service-key cloudant-deployment cloudant-key

cf service-key cloudant-deployment cloudant-key
```

The first command creates a new Cloudant deployment in your IBM Bluemix account, the second assigns a set of credentials for your account to the Cloudant deployment. The third command should output a JSON document similar to the following. 
```
{
 "host": "d5695abd-d00e-40ef-1da6-1dc1e1111f63-bluemix.cloudant.com",
 "password": "5555ee55555a555555c8d559e248efce2aa9187612443cb8e0f4a2a07e1f4",
 "port": 443,
 "url": "https://"d5695abd-d00e-40ef-1da6-1dc1e1111f63-bluemix:5555ee55555a555555c8d559e248efce2aa9187612443cb8e0f4a2a07e1f4@d5695abd-d00e-40ef-1da6-1dc1e1111f63-bluemix.cloudant.com",
 "username": "d5695abd-d00e-40ef-1da6-1dc1e1111f63-bluemix"
}
```

You will need to put these Cloudant credentials in environment variables to create a database and populate the database with documents. Insert the values from the returned JSON document in the corresponding environment variables in the code snippet below.

```
export USER=''
export PASSWORD=''
export HOST=''
```

After the environment variables are correctly configured you should be able to create a new Cloudant database by executing the following curl command

```
curl https://$USER:$PASSWORD@$HOST/address_db -X PUT
```

On successful creation of a database you should get back a JSON response that looks like this:

```
{"ok":true}
```


