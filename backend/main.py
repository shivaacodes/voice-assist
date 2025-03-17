from fastapi import FastAPI, Path

app = FastAPI()

inventory = {
    1: {
        "name": "Milk",
        "cost": 45,
        "brand": "Milma"
    }

}


@app.get("/get-item/{item_id}")
def get_item(item_id: int = Path(None, description="The ID of the item you would like to view")):
    return inventory[item_id]
