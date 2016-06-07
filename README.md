# Serverless computing on IBM Cloud

This text messaging app shows how to use IBM Cloud serverless computing infrastructure built on OpenWhisk. The app is implemented in Python, packaged as a Docker image, and executed by OpenWhisk in a Docker container. 

When a JSON document describing the text message is created in Cloudant (a PouchDB based) database, OpenWhisk instantiates a Docker container with the Python code that connects to Twilio's text messaging service and sends an SMS.

### Getting Started

**NOTE:** you need to create a [Twilio](https://twilio.com) account before trying this app. Make sure that after signing up for the account, you obtain the account SID, authentication token, and register a phone number with an SMS capability.

If you need an IBM Bluemix account, you can sign up for a 30 day trial here: https://console.ng.bluemix.net/registration/

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


