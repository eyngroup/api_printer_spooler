from fastapi import FastAPI, Body, Request
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import (CORSMiddleware)

from hka import TfhkaPyGD
import json
import config

# Crea una instancia de FastAPI
app = FastAPI()
fiscal = TfhkaPyGD.Tfhka()

PORT = "COM3"

origins = [
    "http://127.0.0.1",
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_json(json_data):
    try:
        params = json_data["params"]
        cmd = params["cmd"]
        return True
    except KeyError:
        return False

def validate_list_cmd(cmd):
    return all(isinstance(item, str) for item in cmd)



@app.get("/")
async def root():
    return {"message":"Proxy API Running"}


@app.post("/api/invoice")
async def invoice(request: Request):


    data = await request.json()
    print(data)
    cmd_values = data["cmd"]

    print(cmd_values)

    fiscal.OpenFpctrl(PORT)
    fiscal.SendCmd("PJ2100")                                  # Comando para establecer el Flag 21 en 00 0000000100  2010000000100 
    fiscal.SendCmd("PJ5001")                                  # Comando para establecer el Flag 50 en 01

    for value in cmd_values:
        print(value)
        fiscal.SendCmd(value)
    fiscal.CloseFpctrl()
    return json.dumps({"invoice_number": "invoice_n"})

    if validate_json(data):
        cmd_values = data["params"]["cmd"]
        if validate_list_cmd(cmd_values):
            fiscal.OpenFpctrl(PORT)
            for value in cmd_values:
                # print(value)
                fiscal.SendCmd(value)
            fiscal.CloseFpctrl()
            return json.dumps({"invoice_number": "invoice_n"})
        else:
            print("The list of commands does not meet the requirements.")
    else:
        print("The JSON does not comply with the required structure.")


    return json.dumps({"Error": "Printer Not Connected"}), 404


# # Define el método POST para la ruta /api/invoice
# @app.post("/api/invoice")
# def create_invoice(invoice: Invoice = Body(...)):
#     print("recibir solicitud")




#     # Retorna la factura creada
#     return invoice

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("spooler:app", host=config.IP, port=config.PORT, reload=True)