import pandas as pd
import sqlite3
from fastapi import FastAPI

app = FastAPI()



@app.get('/')
def home():
    return {'message':'Welcome to inventory Management System'}