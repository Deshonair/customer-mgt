from fastapi import FastAPI, Depends, Request, Form
from starlette.responses import RedirectResponse, JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import schema
from database import SessionLocal, engine
import model 
from model import Customer

                                                              
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")  
templates = Jinja2Templates(directory="templates")

model.Base.metadata.create_all(bind=engine)

def get_database_session():
    try:
        db = SessionLocal()
        yield db

    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/customer", response_class=HTMLResponse)
async def get_customers(request: Request, db: Session = Depends(get_database_session)):
    customers = db.query(Customer).all()
    return templates.TemplateResponse("index.html", {"request": request, "data": customers})


@app.get("/customer/{name}", response_class=HTMLResponse)
async def get_customer(request: Request, name: schema.Customer.name, db: Session = Depends(get_database_session)):
    cusotmer = db.query(Customer).filter(Customer.id==name).first()
    return templates.TemplateResponse("overview.html", {"request": request, "customer": customer})


@app.post("/customer")
async def create_customer(db: Session = Depends(get_database_session), name: schema.Customer.name = Form(...), account_number: schema.Customer.account_number = Form(...), request_type: schema.Customer.request_type = Form(...), request_desc: schema.Customer.request_desc = Form(...)):
    customer = Customer(name=name, account_number=account_number,request_type=request_type,request_desc=request_desc)
    db.add(customer)
    db.commit()
    response = RedirectResponse('/', status_code=303)
    return response


@app.patch("/customer/{id}")
async def update_customer(request: Request, id:int, db:Session = Depends(get_database_session)):
    requestBody = await request.json()
    customer = db.query(Customer).get(id)
    customer.name = requestBody['name']
    customer.account_number = requestBody['account_number']
    customer.request_type = requestBody['request_type']
    customer.request_desc = requestBody['request_desc']

    db.commit()
    db.refresh(customer)

    new_customer = jsonable_encoder(customer)
    return JSONResponse(status_code=200, content = {
        "status_code" : 200,
        "message" : "success",
        "customer": new_customer
    })





