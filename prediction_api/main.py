from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = tf.keras.models.load_model("../saved_models/v1/model.h5")

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]
TREATMENT = [[
            "Prune or stake plants to improve air circulation and reduce fungal problems.",
            "Make sure to disinfect your pruning shears (one part bleach to 4 parts water) after each cut.",
            "Keep the soil under plants clean and free of garden debris",
            "Add a layer of organic compost to prevent the spores from splashing back up onto vegetation.",
            "Drip irrigation and soaker hoses can be used to help keep the foliage dry.",
            "Burn or bag infected plant parts. Do NOT compost."
        ],
        ["Plant resistant cultivars when available",
        "Remove volunteers from the garden prior to planting and space plants far enough apart to allow for plenty of air circulation.",
        "Water in the early morning hours, or use soaker hoses, to give plants time to dry out during the day — avoid overhead irrigation.",
        "Destroy all potato debris after harvest"
        ],
        []
]

@app.get("/ping")
async def ping():
    return "Hello, I am alive"

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)).convert("RGB").resize((256,256)))
    return image

@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):
    image = read_file_as_image(await file.read())

    # image = image/255.0

    img_batch = np.expand_dims(image, 0)
    
    predictions = MODEL.predict(img_batch)

    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    treatment = TREATMENT[np.argmax(predictions[0])]
    confidence = np.max(predictions[0])
    return {
        'class': predicted_class,
        'confidence': float(confidence),
        "treatment": treatment
    }

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)

# {
#         'class': "Early Blight",
#         'confidence': 0.67,
#         'treatment': [
#             "Prune or stake plants to improve air circulation and reduce fungal problems.",
#             "Make sure to disinfect your pruning shears (one part bleach to 4 parts water) after each cut.",
#             "Keep the soil under plants clean and free of garden debris",
#             "Add a layer of organic compost to prevent the spores from splashing back up onto vegetation.",
#             "Drip irrigation and soaker hoses can be used to help keep the foliage dry.",
#             "Burn or bag infected plant parts. Do NOT compost."

#         ]
# }