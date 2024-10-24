from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from datetime import date
from enum import Enum
import pandas as pd
from typing import List
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import json
import uuid

app = FastAPI()

S3_BUCKET_NAME = 'user-06-smm-ueia-so'
S3_REGION = 'us-east-1'  # Región de tu bucket
s3_client = boto3.client('s3', region_name=S3_REGION)

engine = create_engine('postgresql+psycopg2://myuser:mypassword@localhost:3007/avocado')#cambiar usuario y contraseña
conexion = engine.connect()

class product_type(Enum):
    ORGANIC = 'organic'
    CONVENTIONAL = 'conventional'

class Item(BaseModel):
    id: int
    Date: date
    AveragePrice: float
    Total_Volume: float
    plu_4046: float #aguacate pequeño
    plu_4225: float #aguacate grande
    plu_4770: float #aguacate grande
    Type: product_type
    year: int
    region: str

def custom_json_serializer(obj):
    if isinstance(obj, date):
        return obj.isoformat()  # Convertir date a string en formato ISO 8601
    elif isinstance(obj, Enum):
        return obj.value  # Devolver el valor del Enum
    raise TypeError(f"Type {type(obj)} not serializable")

def upload_to_s3(json_data: str, bucket_name: str, file_name: str):
    try:
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json_data,
            ContentType='application/json'
        )
        return response
    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="Credenciales de AWS no encontradas.")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error al subir a S3: {e}")

@app.get("/")
def read_root():
    return {"message":"welcome to the api"}

@app.get("/avocado/{region}")
def read_item(region: str, limit: int = Query(100, le=100), offset: int = 0):
    """
    GET method to query avocado data filtered by region,
    with pagination.
    
    Parameters:
    - region: The region to filter by.
    - limit: Maximum number of records per page (max 100).
    - offset: Number of records to skip (for pagination).
    """
    try:
        # Build the SQL query with limit and offset for pagination
        query = f"""
        SELECT * 
        FROM avocado_price 
        WHERE region = '{region}' 
        LIMIT {limit} 
        OFFSET {offset}
        """
        
        # Execute the query and load the data into a DataFrame
        df = pd.read_sql(query, engine)

        # Check if there are results
        if df.empty:
            raise HTTPException(status_code=404, detail="No results found for the provided region")

        # Convert DataFrame to a list of dictionaries
        result = df.to_dict(orient="records")

        # Return the data in JSON format
        return {
            "region": region,
            "data": result,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while performing the query: {str(e)}")

import traceback

@app.post("/items/")
async def create_items(items: List[Item]):
    try:
        if not items or not all(isinstance(item, Item) for item in items):
            raise HTTPException(status_code=422, detail="Invalid or incomplete data for inserting records.")
        
        # Convertimos los items a JSON, usando la función personalizada para serializar
        items_data = json.dumps([item.dict() for item in items], default=custom_json_serializer)
        
        # Nombre único para el archivo
        file_name = f"{uuid.uuid4()}.json"
        
        # Subir el JSON a S3
        upload_to_s3(items_data, S3_BUCKET_NAME, file_name)
        
        # Consulta la base de datos
        query = """
            SELECT * 
            FROM avocado_price
        """
        
        fake_db = pd.read_sql(query, engine)
        
        final_count = len(fake_db)
        
        return {
            "message": f"{len(items)} records were inserted and uploaded to S3.",
            "total_records": final_count,
            "s3_file_name": file_name
        }
    
    except HTTPException as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

