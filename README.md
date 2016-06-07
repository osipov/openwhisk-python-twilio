# Serverless computing on IBM Cloud

This text messaging app shows how to use IBM Cloud serverless computing infrastructure built on OpenWhisk. The app is implemented in Python with Flask, packaged as a Docker image, and executed by OpenWhisk in a Docker container. 

When a JSON document describing the text message is created in a Cloudant (PouchDB based) database, OpenWhisk instantiates a Docker container with the Python code that connects to Twilio's text messaging service and sends an SMS.

### Before you start

[OpenWhisk](https://github.com/openwhisk/openwhisk) serverless computing environment is hosted on IBM Bluemix. To sign up for a 30 day trial of Bluemix register here: https://console.ng.bluemix.net/registration/

This app uses [Twilio](https://www.twilio.com) for text messaging capabilities. To sign up for a Twilio account visit: https://www.twilio.com/try-twilio Make sure that once you have a Twilio account, you also obtain the account SID, authentication token, and register a phone number with an SMS capability.

OpenWhisk uses [Docker Hub](https://hub.docker.com) to execute Docker based actions. You will need a Docker Hub account; to sign up for one use: https://hub.docker.com

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

The OpenWhisk action is implemented as a Python Flask application which is packaged as a Docker image and published to Docker Hub. You can clone the code for the action from github by running the following from your command line

```git clone https://github.com/osipov/openwhisk-python-twilio.git```

This will create an ```openwhisk-python-twilio``` folder in your current working directory.

All of the code for the OpenWhisk action is in the ```py/service.py``` file. There are two functions, called _init_ and _run_ that correspond to Flask app routes /init and /run. The init function is called on an HTTP POST request and returns an HTTP 200 status code as expected by the OpenWhisk platform. The run function verifies that an incoming HTTP POST request is a JSON document containing Twilio configuration parameters and the content of the text message. After configuring a Twilio client and sending the text message, the function returns back an HTTP 200 status code and a JSON document with a success status message.

###Build and package the action implementation in a Docker image

If you don't have Docker installed, it is available per the instructions provided in the link below. Note that if you are using Windows or OSX, you will want to install Docker Toolbox from:

https://docs.docker.com/engine/installation/

Make sure that your [Docker Hub](https://hub.docker.com) account is working correctly by trying to login using

```docker login -u $DOCKER_USER ```

You will be prompted to enter your Docker Hub password.

Run the following commands to build the Docker image with the OpenWhisk action implementation and to push the image to Docker Hub. 

```
cd openwhisk-python-twilio
docker build -t $DOCKER_USER/openwhisk .
docker push $DOCKER_USER/openwhisk
```

Use your browser to login to https://hub.docker.com after the docker push command is done. You should be able to see the **openwhisk** image in the list of your Docker Hub images.

###Create a stateless, Docker-based OpenWhisk action

To get started with OpenWhisk, download and install a command line interface using the instructions from the following link:

https://new-console.ng.bluemix.net/openwhisk/cli

The following commands need to be executed to configure your OpenWhisk action instance:

```
wsk action create --docker textAction $DOCKER_USER/openwhisk
wsk action update textAction --param account_sid "$TWILIO_SID" --param auth_token "$TWILIO_TOKEN"
```

The first command sets up a Docker-based OpenWhisk action called textAction that is implemented using the ```$DOCKER_USER/openwhisk``` image from Docker Hub. The second command configures the textAction with the Twilio account SID and authentication token so that they don't need to be passed to the action execution environment on every action invocation.

###Test the serverless computing action

Open a dedicated console window and execute 

```
wsk activation poll
```

to monitor the result of running the OpenWhisk action.

In a separate console, execute the following command, replacing the **to** value to specify the phone number and the **msg** value to specify the text message contents:

```
wsk action invoke --blocking --result -p from "$TWILIO_NUMBER" -p to "867-5309" -p msg "Jenny I got your number" textAction
```

Upon successful action execution your **to** phone number should receive the text message and you should be able to see an output similar to the following:

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

## OPTIONAL Use Cloudant to log text messages

Before sending a text message, many applications need to log the text message contents. Cloudant, a PouchDB based JSON document database available from IBM Bluemix is well suited for storing records of the text messages. Since OpenWhisk integrates with Cloudant, it is possible to setup OpenWhisk to automatically trigger a Docker-based action to send a text message once the text message contents are stored in Cloudant. 

### Before you start

Make sure that you have completed the steps in the previous section and have a working textAction in OpenWhisk that sends text messages using Twilio.

Next, download a Cloud Foundry command line interface for your operating system using the following link

https://github.com/cloudfoundry/cli/releases

and then install it.

### Create a Cloudant deployment in IBM Bluemix

In your console, type in 

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
curl https://$USER:$PASSWORD@$HOST/sms -X PUT
```

On successful creation of a database you should get back a JSON response that looks like this:

```
{"ok":true}
```

###Integrate Cloudant with OpenWhisk rules and triggers 

Configure OpenWhisk to use the same Bluemix organization and space as your Cloudant instance by executing the following from your command line

```
wsk property set --namespace $ORG\_$SPACE
```

If your $ORG and $SPACE environment variables are not set, refer back to the section on creating the Cloudant database.

Next update the list of packages by executing

```
wsk package refresh
```

One of the bindings listed in the output should be named ```Bluemix_cloudant-deployment_cloudant-key``` 

Run following commands to configure OpenWhisk to start the action in case if a new document is placed in the Cloudant **sms** database. 

```
wsk trigger create textTrigger --feed /$ORG\_$SPACE/Bluemix_cloudant-deployment_cloudant-key/changes --param includeDoc true --param dbname sms
wsk rule create --enable textRule textTrigger textAction
```

The first command creates a trigger that listens to changes to the Cloudant database. The second command is a rule that indicates that whenever the trigger is activated with a document in Cloudant, then the text messaging action (textAction created in the previous section) needs to be invoked.

###Test the OpenWhisk trigger by logging the text message to the Cloudant database

Open a separate console window and execute the following command to monitor the OpenWhisk log 

```
wsk activation poll
```

In another console, create a document in Cloudant using the following curl command, replacing the **to** value to specify the phone number and the **msg** value to specify the text message contents:

```
curl https://$USER:$PASSWORD@$HOST/sms -X POST -H "Content-Type: application/json" -d '{"from": "$TWILIO_NUMBER", "to": "867-5309", "msg":"Jenny I got your number"}'
```

On success,  you should see in the console running the ```wsk activation poll``` a response similar to following 

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
