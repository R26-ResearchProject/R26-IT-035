import os
import joblib
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    balanced_accuracy_score
)
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    QuantileTransformer
)


# =========================================================
# CONFIG
# =========================================================

np.random.seed(42)

MAX_SAMPLES = 8000
RANDOM_STATE = 42


# =========================================================
# LOAD ORIGINAL 17 FEATURES
# =========================================================

X = np.load(
    "data/processed/X.npy"
)

print(
    "Loaded features:",
    X.shape
)


# =========================================================
# OPTIONAL SUBSAMPLING
# =========================================================

if X.shape[0] > MAX_SAMPLES:

    indices = np.random.choice(
        X.shape[0],
        MAX_SAMPLES,
        replace=False
    )

    X = X[indices]


print(
    "Using dataset:",
    X.shape
)


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def add_extra_features(X):

    extra_features = []

    for row in X:

        (
            face_ratio,
            jaw_ratio,
            forehead_ratio,
            eye_ratio,
            eye_spacing_ratio,
            nose_ratio,
            mouth_ratio,
            jaw_angle_left,
            jaw_angle_right,
            laplacian_var,
            edge_density,
            mean_L,
            mean_A,
            mean_B,
            redness,
            color_std,
            symmetry
        ) = row

        # Facial roundness
        roundness = (
            1 /
            (face_ratio + 1e-6)
        )

        # Difference between left and right jaw angles
        jaw_balance = abs(
            jaw_angle_left
            - jaw_angle_right
        )

        # Approximate smoothness
        smoothness = (
            1 /
            (edge_density + 1e-6)
        )

        extra_features.append([
            roundness,
            jaw_balance,
            smoothness
        ])

    extra_features = np.array(
        extra_features,
        dtype=np.float32
    )

    return np.hstack(
        (
            X,
            extra_features
        )
    )


X = add_extra_features(X)


print(
    "After feature engineering:",
    X.shape
)


# =========================================================
# TRAIN / TEST SPLIT
# =========================================================

X_train_raw, X_test_raw = train_test_split(
    X,
    test_size=3000,
    random_state=RANDOM_STATE
)


print(
    "\nTraining samples:",
    X_train_raw.shape[0]
)

print(
    "Testing samples:",
    X_test_raw.shape[0]
)


# =========================================================
# NORMALIZATION FOR PSEUDO-LABEL GENERATION
# =========================================================

label_feature_scaler = MinMaxScaler()


X_train_label = (
    label_feature_scaler.fit_transform(
        X_train_raw
    )
)


X_test_label = (
    label_feature_scaler.transform(
        X_test_raw
    )
)


X_train_label = np.clip(
    X_train_label,
    0,
    1
)

X_test_label = np.clip(
    X_test_label,
    0,
    1
)


# =========================================================
# RAW DOSHA TENDENCY GENERATION
# =========================================================

def calculate_raw_tendencies(X_normalized):

    tendencies = []

    for row in X_normalized:

        (
            face_ratio,
            jaw_ratio,
            forehead_ratio,
            eye_ratio,
            eye_spacing_ratio,
            nose_ratio,
            mouth_ratio,
            jaw_angle_left,
            jaw_angle_right,
            laplacian_var,
            edge_density,
            mean_L,
            mean_A,
            mean_B,
            redness,
            color_std,
            symmetry,
            roundness,
            jaw_balance,
            smoothness
        ) = row


        # VATA TENDENCY

        vata = (
            face_ratio * 0.18
            + edge_density * 0.16
            + symmetry * 0.14
            + color_std * 0.14
            + jaw_balance * 0.12
            + eye_spacing_ratio * 0.10
            + (1 - smoothness) * 0.08
            + eye_ratio * 0.08
        )


        # PITTA TENDENCY

        pitta = (
            redness * 0.20
            + mean_A * 0.15
            + jaw_angle_left * 0.10
            + jaw_angle_right * 0.10
            + nose_ratio * 0.15
            + mouth_ratio * 0.10
            + laplacian_var * 0.10
            + color_std * 0.10
        )


        # KAPHA TENDENCY

        kapha = (
            roundness * 0.18
            + smoothness * 0.16
            + mean_L * 0.12
            + forehead_ratio * 0.14
            + jaw_ratio * 0.12
            + mouth_ratio * 0.10
            + (1 - edge_density) * 0.10
            + eye_ratio * 0.08
        )


        tendencies.append([
            vata,
            pitta,
            kapha
        ])


    return np.array(
        tendencies,
        dtype=np.float64
    )


raw_train_tendencies = calculate_raw_tendencies(
    X_train_label
)

raw_test_tendencies = calculate_raw_tendencies(
    X_test_label
)


# =========================================================
# DATASET-LEVEL TENDENCY CALIBRATION
# =========================================================

tendency_calibrator = QuantileTransformer(
    n_quantiles=min(
        500,
        len(raw_train_tendencies)
    ),
    output_distribution="uniform",
    random_state=RANDOM_STATE
)


calibrated_train = (
    tendency_calibrator.fit_transform(
        raw_train_tendencies
    )
)


calibrated_test = (
    tendency_calibrator.transform(
        raw_test_tendencies
    )
)


# =========================================================
# CONVERT CALIBRATED TENDENCIES TO PRAKRITI SCORES
# =========================================================

def normalize_dosha_scores(tendencies):

    results = []

    for scores in tendencies:

        scores = np.nan_to_num(
            scores,
            nan=0.0,
            posinf=0.0,
            neginf=0.0
        )

        scores = np.maximum(
            scores,
            0
        )

        total = np.sum(
            scores
        )

        if total <= 1e-6:

            normalized = np.array([
                0.33,
                0.33,
                0.34
            ])

        else:

            normalized = (
                scores /
                total
            )

        results.append(
            normalized
        )

    return np.array(
        results,
        dtype=np.float32
    )


Y_train = normalize_dosha_scores(
    calibrated_train
)

Y_test = normalize_dosha_scores(
    calibrated_test
)


# =========================================================
# CHECK LABEL DISTRIBUTION
# =========================================================

def print_label_distribution(
    Y,
    title
):

    dominant = np.argmax(
        Y,
        axis=1
    )

    vata_count = np.sum(
        dominant == 0
    )

    pitta_count = np.sum(
        dominant == 1
    )

    kapha_count = np.sum(
        dominant == 2
    )

    total = len(
        dominant
    )

    print(
        "\n-------------------------"
    )

    print(
        title
    )

    print(
        "-------------------------"
    )

    print(
        "Vata:",
        vata_count,
        f"({vata_count / total * 100:.2f}%)"
    )

    print(
        "Pitta:",
        pitta_count,
        f"({pitta_count / total * 100:.2f}%)"
    )

    print(
        "Kapha:",
        kapha_count,
        f"({kapha_count / total * 100:.2f}%)"
    )


print_label_distribution(
    Y_train,
    "Training Pseudo Label Distribution"
)


print_label_distribution(
    Y_test,
    "Testing Pseudo Label Distribution"
)


# =========================================================
# SCALE FEATURES FOR RANDOM FOREST PIPELINE
# =========================================================

scaler = StandardScaler()


X_train = scaler.fit_transform(
    X_train_raw
)


X_test = scaler.transform(
    X_test_raw
)


# =========================================================
# RANDOM FOREST
# =========================================================

model = RandomForestRegressor(
    n_estimators=350,
    max_depth=12,
    min_samples_split=6,
    min_samples_leaf=3,
    max_features=0.85,
    random_state=RANDOM_STATE,
    n_jobs=-1
)


print(
    "\nTraining model...\n"
)


model.fit(
    X_train,
    Y_train
)


# =========================================================
# MODEL PREDICTION
# =========================================================

Y_pred = model.predict(
    X_test
)


# =========================================================
# MAE
# =========================================================

overall_mae = mean_absolute_error(
    Y_test,
    Y_pred
)


vata_mae = mean_absolute_error(
    Y_test[:, 0],
    Y_pred[:, 0]
)


pitta_mae = mean_absolute_error(
    Y_test[:, 1],
    Y_pred[:, 1]
)


kapha_mae = mean_absolute_error(
    Y_test[:, 2],
    Y_pred[:, 2]
)


# =========================================================
# DOMINANT PRAKRITI
# =========================================================

true_classes = np.argmax(
    Y_test,
    axis=1
)


predicted_classes = np.argmax(
    Y_pred,
    axis=1
)


# =========================================================
# NORMAL ACCURACY
# =========================================================

correct_predictions = np.sum(
    true_classes
    == predicted_classes
)


total_predictions = len(
    true_classes
)


dominant_accuracy = (
    correct_predictions
    / total_predictions
)


# =========================================================
# BALANCED ACCURACY
# =========================================================

balanced_accuracy = balanced_accuracy_score(
    true_classes,
    predicted_classes
)


# =========================================================
# DISPLAY RESULTS
# =========================================================

print(
    "\n========================="
)

print(
    "MODEL EVALUATION"
)

print(
    "========================="
)


print(
    "Overall MAE:",
    round(
        overall_mae,
        4
    )
)


print(
    "Vata MAE:",
    round(
        vata_mae,
        4
    )
)


print(
    "Pitta MAE:",
    round(
        pitta_mae,
        4
    )
)


print(
    "Kapha MAE:",
    round(
        kapha_mae,
        4
    )
)


#print(
#  "\nCorrect Dominant Predictions:",
#    correct_predictions
#)


print(
    "\nTotal Test Samples:",
    total_predictions
)


print(
    "Dominant Prakriti Accuracy:",
    round(
        dominant_accuracy * 100,
        2
    ),
    "%"
)


print(
    "Balanced Accuracy:",
    round(
        balanced_accuracy * 100,
        2
    ),
    "%"
)


# =========================================================
# SAVE MODEL
# =========================================================

os.makedirs(
    "model",
    exist_ok=True
)


joblib.dump(
    model,
    "model/prakriti_model.pkl"
)


joblib.dump(
    scaler,
    "model/scaler.pkl"
)


print(
    "\nModel saved successfully!"
)