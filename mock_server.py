from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define API request models
class Merchant(BaseModel):
    merchant_id: str
    name: str
    address: str

class MerchantSettings(BaseModel):
    recurring_billing_enabled: bool
    auto_settlement_enabled: bool

@app.post("/api/merchant/create")
async def create_merchant(merchant: Merchant):
    return {"message": f"Merchant {merchant.name} created with ID {merchant.merchant_id}"}

@app.get("/api/merchant/{merchant_id}")
async def get_merchant_info(merchant_id: str):
    return {"message": f"Merchant {merchant_id} details fetched successfully"}

@app.put("/api/merchant/{merchant_id}/update-details")
async def update_merchant_details(merchant_id: str, merchant: Merchant):
    return {"message": f"Merchant {merchant_id} updated with name {merchant.name} and address {merchant.address}"}

@app.put("/api/merchant/update-settings")
async def update_merchant_settings(merchant_id: str, settings: MerchantSettings):
    return {"message": f"Merchant {merchant_id} settings updated"}
