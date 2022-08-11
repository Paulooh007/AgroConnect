from google.cloud import storage
import tensorflow as tf
from PIL import Image
import numpy as np

model = None
interpreter = None
input_index = None
output_index = None

class_names = ["Early Blight", "Late Blight", "Healthy"]
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

BUCKET_NAME = "agroconnect_tfmodules" # Here you need to put the name of your GCP bucket


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")


def predict(request):
    global model
    if model is None:
        download_blob(
            BUCKET_NAME,
            "models/model.h5",
            "/tmp/model.h5",
        )
        model = tf.keras.models.load_model("/tmp/model.h5")

    image = request.files["file"]

    image = np.array(
        Image.open(image).convert("RGB").resize((256, 256)) # image resizing
    )

    # image = image/255 # normalize the image in 0 to 1 range

    img_array = tf.expand_dims(image, 0)
    predictions = model.predict(img_array)

    print("Predictions:",predictions)

    predicted_class = class_names[np.argmax(predictions[0])]
    confidence = round(100 * (np.max(predictions[0])), 2)
    treatment = TREATMENT[np.argmax(predictions[0])]

    return {"class": predicted_class, "confidence": confidence, "treatment": treatment}

