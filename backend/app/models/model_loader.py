import joblib

model = joblib.load("model/prakriti_model.pkl")
scaler = joblib.load("model/scaler.pkl")

def get_model():
    return model

def get_scaler():
    return scaler