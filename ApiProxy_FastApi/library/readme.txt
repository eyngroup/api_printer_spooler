INSTALL

python3 -m venv .venv

source venv/bin/activate
D:\ApiProxy\venv\Scripts\activate.bat
venv/scripts/activate.bat

pip install fastapi uvicorn

pip install fastapi
pip install "uvicorn[standard]"
pip install "D:\ApiProxy\library\pyserial-3.5.tar.gz


from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


uvicorn spooler:app --reload

# Test your FastAPI endpoints

GET http://127.0.0.1:8000/
Accept: application/json

###

GET http://127.0.0.1:8000/hello/User
Accept: application/json

###
