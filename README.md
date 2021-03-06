## Examples of bldg batteries


### Simple clock battery example

* This is a simple implementation of a bldg battery, with a simple clock protocol

* To install: 
```
cd sample-battery
pip install fastapi
pip install uvicorn[standard]
pip install python-dotenv
```

* To configure: create a `.env` file in the sample-battery folder, e.g.:
```
BLDG_SERVER_URL="https://api.w2m.site"
BLDG_ADDRESS="g-b(17,24)-l0-b(12,2)"
BATTERY_TYPE="clock-battery"
BATTERY_VENDOR="w2m"
BATTERY_VERSION="0.0.1"
CALLBACK_URL="http://localhost:3000/v1/on_message"
```

* To run: 
```
cd sample-battery
uvicorn main:app --reload
```
