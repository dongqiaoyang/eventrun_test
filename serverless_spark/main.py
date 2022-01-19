
# [START cloudrun_pubsub_server_setup]
# [START run_pubsub_server_setup]
import base64
import os
import ast
from flask import Flask, request


import warnings

### Main app
app = Flask(__name__)
    
@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    parameter = "World"
    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        parameter = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()

    try:
        print("start ge")
        ge=ge_run(parameter)
        print("ge finished")
    except:
        print('something went wrong')
    
    return "", 204
    
def ge_run(parameter):
    print(parameter)
    import os
    os.system('ls -l')
    os.system('gcloud config list')
    
if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)
