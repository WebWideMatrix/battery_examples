## Example of bldg batteries


### Simple clock battery example

* This is a simple implementation of a bldg battery, with a simple clock protocol

* To install: 
```
cd sample-battery
pip install fastapi
pip install uvicorn[standard]
pip install python-dotenv
```

* To configure: create a `.env` file, such as:
```
BLDG_SERVER_URL="https://api.w2m.site"
BLDG_ADDRESS="g-b(17,24)-l0-b(12,2)"
BLDG_TYPE="clock-battery"
BLDG_VENDOR="w2m"
BLDG_VERSION="0.0.1"
```

* To run: 
```
cd sample-battery
uvicorn main:app --reload
```
