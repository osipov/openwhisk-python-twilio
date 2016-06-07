from flask import Flask, request, jsonify
from twilio.rest import TwilioRestClient

app = Flask(__name__)

@app.route('/init', methods = ['POST'])
def init():
    try:
        json = request.get_json()

        response = [
            {'success': 'true'}
        ]
        return jsonify(status=response), 200

    except Exception as e:
        err = "Error: " + str(e)

        response = [
            {'success': 'false'},
            {'msg': err}
        ]

        return jsonify(status=response), 500

@app.route('/run', methods = ['POST'])
def run():
    try:
        json = request.get_json()

        assert json
        assert "value" in json, "Missing value key in the input JSON"
        assert "account_sid" in json["value"], "Missing Twilio account SID"
        assert "auth_token" in json["value"], "Missing Twilio Authentication Token"

        account_sid = json["value"]["account_sid"]
        auth_token  = json["value"]["auth_token"]

        client = TwilioRestClient(account_sid, auth_token)

        assert "from" in json["value"], "Missing from phone number"
        assert "to" in json["value"], "Missing to phone number"

        assert "msg" in json["value"], "Missing the body of the message"

        fromNumber = json["value"]["from"]
        toNumber = json["value"]["to"]
        msg = json["value"]["msg"]

        message = client.messages.create(body=msg,
            to=toNumber,
            from_=fromNumber)

        assert message.sid, "Unable to retrieve Twilio SMS message SID"

        response = [
            {'success': 'true'},
            {'message_sid': message.sid}
        ]

        return jsonify(status=response), 200

    except Exception as e:
        err = "Error: " + str(e)
        response = [
            {'success': 'false'},
            {'msg': err}
        ]

        return jsonify(status=response), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
