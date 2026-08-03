import numpy as np


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clamp_01(value):
    """
    Keep a value inside the 0-1 range.
    """

    return float(
        np.clip(
            value,
            0.0,
            1.0
        )
    )


def normalize_module_scores(vata, pitta, kapha):
    """
    Normalize Vata, Pitta and Kapha scores
    so their total becomes 1.
    """

    scores = np.array(
        [
            vata,
            pitta,
            kapha
        ],
        dtype=np.float64
    )

    # Replace invalid values such as NaN or infinity
    scores = np.nan_to_num(
        scores,
        nan=0.0,
        posinf=0.0,
        neginf=0.0
    )

    # Prevent negative values
    scores = np.maximum(
        scores,
        0
    )

    # Add Vata + Pitta + Kapha
    total = float(
        np.sum(scores)
    )

    # If all three scores are zero,
    # use a safe approximately equal distribution
    if total <= 1e-6:

        scores = np.array(
            [
                0.33,
                0.33,
                0.34
            ]
        )

    else:

        # Convert the scores into proportions
        #
        # Example:
        #
        # Raw scores:
        # Vata  = 2
        # Pitta = 3
        # Kapha = 5
        #
        # Total = 10
        #
        # Normalized:
        # Vata  = 2 / 10 = 0.20
        # Pitta = 3 / 10 = 0.30
        # Kapha = 5 / 10 = 0.50

        scores = (
            scores /
            total
        )

    return {

        "vata": round(
            float(scores[0]),
            4
        ),

        "pitta": round(
            float(scores[1]),
            4
        ),

        "kapha": round(
            float(scores[2]),
            4
        )
    }


def get_module_result(
    module_name,
    scores,
    explanation
):
    """
    Create a standard response for one module.
    """

    # Sort Vata, Pitta and Kapha
    # from highest score to lowest score
    sorted_scores = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Example:
    #
    # Vata  = 0.25
    # Pitta = 0.40
    # Kapha = 0.35
    #
    # Highest = Pitta
    #
    # Therefore:
    # Dominant Dosha = Pitta

    dominant_dosha = (
        sorted_scores[0][0]
    )

    # The highest normalized dosha score
    # becomes the confidence of this module
    #
    # Example:
    #
    # Pitta = 0.40
    #
    # Module Confidence = 0.40 = 40%

    confidence = (
        sorted_scores[0][1]
    )

    return {

        "module":
            module_name,

        "dominant_dosha":
            dominant_dosha.capitalize(),

        "confidence":
            round(
                float(confidence),
                4
            ),

        "scores":
            scores,

        "explanation":
            explanation
    }


# =========================================================
# FEATURE NORMALIZATION HELPERS
# =========================================================

def normalize_ratio(value):
    """
    Convert facial ratio values into
    a bounded 0-1 range.
    """

    # Example:
    #
    # face_ratio = 1.4
    #
    # 1.4 / 2.0 = 0.70

    return clamp_01(
        value / 2.0
    )


def normalize_angle(value):
    """
    Facial angles are approximately
    between 0 and 180 degrees.

    Convert them into 0-1.
    """

    # Example:
    #
    # jaw angle = 90 degrees
    #
    # 90 / 180 = 0.50

    return clamp_01(
        value / 180.0
    )


def normalize_lab(value):
    """
    OpenCV LAB values are approximately
    between 0 and 255.

    Convert into 0-1.
    """

    # Example:
    #
    # mean_L = 153
    #
    # 153 / 255 = 0.60

    return clamp_01(
        value / 255.0
    )


def normalize_redness(value):
    """
    Convert redness value into
    a bounded 0-1 value.
    """

    return clamp_01(
        (value + 255.0)
        / 510.0
    )


def normalize_variation(value):
    """
    Convert texture or colour variation
    into a bounded 0-1 value.
    """

    value = max(
        float(value),
        0.0
    )

    return clamp_01(
        value /
        (
            value
            + 100.0
            + 1e-6
        )
    )


def normalize_positive(value):
    """
    Convert any positive value
    into the 0-1 range.
    """

    value = max(
        float(value),
        0.0
    )

    return (
        value /
        (
            1.0
            + value
        )
    )


# =========================================================
# FACIAL MODULE ANALYSIS
# =========================================================

def create_module_analysis(features):
    """
    Separate the 20 facial features into
    four facial analysis modules:

    1. Geometry
    2. Texture
    3. Colour
    4. Symmetry

    Each module independently calculates:

    - Vata score
    - Pitta score
    - Kapha score
    - Dominant Dosha
    - Module Confidence

    The four modules are later combined using
    confidence-aware fusion to produce one
    facial Prakriti score distribution.
    """

    # Stop if feature extraction failed
    if features is None:
        return None

    # This implementation expects exactly
    # the same 20 features produced by
    # feature_extraction.py
    if len(features) != 20:

        raise ValueError(
            f"Expected 20 facial features, "
            f"but received {len(features)}"
        )


    # =====================================================
    # UNPACK 20 FACIAL FEATURES
    # =====================================================

    (
        # -------------------------------------------------
        # Geometry-related features
        # -------------------------------------------------

        face_ratio,
        jaw_ratio,
        forehead_ratio,

        eye_ratio,
        eye_spacing_ratio,
        nose_ratio,

        mouth_ratio,

        jaw_angle_left,
        jaw_angle_right,


        # -------------------------------------------------
        # Texture-related features
        # -------------------------------------------------

        laplacian_var,
        edge_density,


        # -------------------------------------------------
        # Colour-related features
        # -------------------------------------------------

        mean_L,
        mean_A,
        mean_B,

        redness,
        color_std,


        # -------------------------------------------------
        # Symmetry-related feature
        # -------------------------------------------------

        symmetry,


        # -------------------------------------------------
        # Engineered features
        # -------------------------------------------------

        roundness,
        jaw_balance,
        smoothness

    ) = features


    # =====================================================
    # NORMALIZE FEATURES
    # =====================================================
    #
    # Different facial features have different numeric
    # ranges.
    #
    # Example:
    #
    # jaw angle   -> can be around 0-180
    # LAB colour  -> around 0-255
    # face ratio  -> small decimal
    #
    # Therefore they are converted into similar
    # approximately 0-1 ranges before module calculations.
    # =====================================================

    n_face_ratio = normalize_ratio(
        face_ratio
    )

    n_jaw_ratio = normalize_ratio(
        jaw_ratio
    )

    n_forehead_ratio = normalize_ratio(
        forehead_ratio
    )

    n_eye_ratio = normalize_ratio(
        eye_ratio
    )

    n_eye_spacing = normalize_ratio(
        eye_spacing_ratio
    )

    n_nose_ratio = normalize_ratio(
        nose_ratio
    )

    n_mouth_ratio = normalize_ratio(
        mouth_ratio
    )

    n_jaw_left = normalize_angle(
        jaw_angle_left
    )

    n_jaw_right = normalize_angle(
        jaw_angle_right
    )

    n_laplacian = normalize_variation(
        laplacian_var
    )

    n_edge_density = clamp_01(
        edge_density
    )

    n_mean_L = normalize_lab(
        mean_L
    )

    n_mean_A = normalize_lab(
        mean_A
    )

    n_mean_B = normalize_lab(
        mean_B
    )

    n_redness = normalize_redness(
        redness
    )

    n_color_std = normalize_variation(
        color_std
    )

    n_symmetry_difference = normalize_positive(
        symmetry
    )

    n_roundness = normalize_positive(
        roundness
    )

    n_jaw_balance = normalize_angle(
        jaw_balance
    )

    n_smoothness = normalize_positive(
        smoothness
    )


    # Keep these normalized values available
    # even though they are not directly used
    # in the current module formulas.
    _ = (
        n_eye_ratio,
        n_mean_B
    )


    # =====================================================
    # 1. GEOMETRY MODULE
    # =====================================================
    #
    # Geometry analyses:
    #
    # - face shape
    # - jaw structure
    # - forehead proportion
    # - eye spacing
    # - nose ratio
    # - mouth ratio
    # - facial roundness
    # - jaw balance
    #
    # It calculates three separate tendencies:
    #
    # Geometry Vata
    # Geometry Pitta
    # Geometry Kapha
    # =====================================================

    geometry_vata = (

        n_face_ratio * 0.30

        + n_jaw_balance * 0.20

        + n_eye_spacing * 0.15

        + (
            1
            - n_roundness
        ) * 0.20

        + n_nose_ratio * 0.15
    )


    geometry_pitta = (

        n_jaw_left * 0.20

        + n_jaw_right * 0.20

        + n_nose_ratio * 0.20

        + n_mouth_ratio * 0.15

        + n_face_ratio * 0.15

        + n_forehead_ratio * 0.10
    )


    geometry_kapha = (

        n_roundness * 0.30

        + n_forehead_ratio * 0.20

        + n_jaw_ratio * 0.20

        + n_mouth_ratio * 0.15

        + (
            1
            - n_jaw_balance
        ) * 0.15
    )


    # Convert the three raw geometry tendencies
    # into a distribution that totals approximately 1.
    #
    # Example:
    #
    # Vata  = 0.25
    # Pitta = 0.40
    # Kapha = 0.35
    #
    # Highest = Pitta
    #
    # Geometry Dominant = Pitta
    # Geometry Confidence = 40%

    geometry_scores = (
        normalize_module_scores(
            geometry_vata,
            geometry_pitta,
            geometry_kapha
        )
    )


    geometry_dominant = max(
        geometry_scores,
        key=geometry_scores.get
    ).capitalize()


    geometry_explanation = (

        f"The geometry module analysed facial shape, "
        f"jaw structure, forehead proportion, nose ratio, "
        f"mouth ratio and facial roundness. "
        f"The strongest geometry tendency was "
        f"{geometry_dominant}."
    )


    geometry_module = (
        get_module_result(
            "Geometry",
            geometry_scores,
            geometry_explanation
        )
    )


    # =====================================================
    # 2. TEXTURE MODULE
    # =====================================================
    #
    # Texture analyses:
    #
    # - edge density
    # - Laplacian surface variation
    # - smoothness
    # - colour variation
    #
    # It independently calculates:
    #
    # Texture Vata
    # Texture Pitta
    # Texture Kapha
    # =====================================================

    texture_vata = (

        n_edge_density * 0.40

        + n_laplacian * 0.35

        + (
            1
            - n_smoothness
        ) * 0.25
    )


    texture_pitta = (

        n_laplacian * 0.40

        + n_edge_density * 0.30

        + n_color_std * 0.30
    )


    texture_kapha = (

        n_smoothness * 0.50

        + (
            1
            - n_edge_density
        ) * 0.30

        + (
            1
            - n_laplacian
        ) * 0.20
    )


    texture_scores = (
        normalize_module_scores(
            texture_vata,
            texture_pitta,
            texture_kapha
        )
    )


    texture_dominant = max(
        texture_scores,
        key=texture_scores.get
    ).capitalize()


    texture_explanation = (

        f"The texture module analysed skin surface variation, "
        f"edge density and smoothness. "
        f"The strongest texture tendency was "
        f"{texture_dominant}."
    )


    texture_module = (
        get_module_result(
            "Texture",
            texture_scores,
            texture_explanation
        )
    )


    # =====================================================
    # 3. COLOUR MODULE
    # =====================================================
    #
    # Colour analyses:
    #
    # - facial brightness
    # - redness
    # - LAB colour information
    # - colour variation
    #
    # It independently calculates:
    #
    # Colour Vata
    # Colour Pitta
    # Colour Kapha
    # =====================================================

    colour_vata = (

        (
            1
            - n_mean_L
        ) * 0.30

        + n_color_std * 0.40

        + (
            1
            - n_redness
        ) * 0.30
    )


    colour_pitta = (

        n_redness * 0.45

        + n_mean_A * 0.35

        + n_color_std * 0.20
    )


    colour_kapha = (

        n_mean_L * 0.45

        + (
            1
            - n_color_std
        ) * 0.30

        + (
            1
            - n_redness
        ) * 0.25
    )


    colour_scores = (
        normalize_module_scores(
            colour_vata,
            colour_pitta,
            colour_kapha
        )
    )


    colour_dominant = max(
        colour_scores,
        key=colour_scores.get
    ).capitalize()


    colour_explanation = (

        f"The colour module analysed facial brightness, "
        f"redness and colour variation. "
        f"The strongest colour tendency was "
        f"{colour_dominant}."
    )


    colour_module = (
        get_module_result(
            "Colour",
            colour_scores,
            colour_explanation
        )
    )


    # =====================================================
    # 4. SYMMETRY MODULE
    # =====================================================
    #
    # Symmetry analyses:
    #
    # - left-right facial difference
    # - jaw balance
    #
    # It independently calculates:
    #
    # Symmetry Vata
    # Symmetry Pitta
    # Symmetry Kapha
    # =====================================================

    symmetry_level = (
        1.0
        - n_symmetry_difference
    )


    symmetry_vata = (

        n_symmetry_difference * 0.55

        + n_jaw_balance * 0.45
    )


    symmetry_pitta = (

        0.50

        + (
            1
            - abs(
                n_symmetry_difference
                - 0.50
            )
        ) * 0.20
    )


    symmetry_kapha = (

        symmetry_level * 0.60

        + (
            1
            - n_jaw_balance
        ) * 0.40
    )


    symmetry_scores = (
        normalize_module_scores(
            symmetry_vata,
            symmetry_pitta,
            symmetry_kapha
        )
    )


    symmetry_dominant = max(
        symmetry_scores,
        key=symmetry_scores.get
    ).capitalize()


    symmetry_explanation = (

        f"The symmetry module analysed left-right facial "
        f"balance and jaw balance. "
        f"The strongest symmetry tendency was "
        f"{symmetry_dominant}."
    )


    symmetry_module = (
        get_module_result(
            "Symmetry",
            symmetry_scores,
            symmetry_explanation
        )
    )


    # =====================================================
    # RETURN FOUR FACIAL MODULES
    # =====================================================
    #
    # At this stage we have:
    #
    # Geometry:
    # Vata / Pitta / Kapha / Confidence
    #
    # Texture:
    # Vata / Pitta / Kapha / Confidence
    #
    # Colour:
    # Vata / Pitta / Kapha / Confidence
    #
    # Symmetry:
    # Vata / Pitta / Kapha / Confidence
    #
    # These four results are then sent to
    # combine_facial_modules().
    # =====================================================

    return {

        "geometry":
            geometry_module,

        "texture":
            texture_module,

        "colour":
            colour_module,

        "symmetry":
            symmetry_module
    }


# =========================================================
# CONFIDENCE-AWARE FACIAL MODULE FUSION
# =========================================================

def combine_facial_modules(module_analysis):
    """
    Combine Geometry, Texture, Colour and Symmetry
    using each module's confidence as a weight.

    Higher-confidence modules contribute more strongly
    to the combined facial result.
    """

    facial_module_names = [

        "geometry",
        "texture",
        "colour",
        "symmetry"
    ]


    # Store the weighted contributions
    # for each Dosha.
    weighted_scores = {

        "vata": 0.0,

        "pitta": 0.0,

        "kapha": 0.0
    }


    # Store the total of all module confidences.
    total_confidence = 0.0


    # =====================================================
    # FULL WORKED EXAMPLE
    # =====================================================
    #
    # Assume the four modules generated:
    #
    # -----------------------------------------------------
    # GEOMETRY
    # -----------------------------------------------------
    #
    # Vata       = 0.25
    # Pitta      = 0.40
    # Kapha      = 0.35
    # Confidence = 0.40
    #
    #
    # -----------------------------------------------------
    # TEXTURE
    # -----------------------------------------------------
    #
    # Vata       = 0.20
    # Pitta      = 0.30
    # Kapha      = 0.50
    # Confidence = 0.50
    #
    #
    # -----------------------------------------------------
    # COLOUR
    # -----------------------------------------------------
    #
    # Vata       = 0.30
    # Pitta      = 0.35
    # Kapha      = 0.35
    # Confidence = 0.35
    #
    #
    # -----------------------------------------------------
    # SYMMETRY
    # -----------------------------------------------------
    #
    # Vata       = 0.05
    # Pitta      = 0.35
    # Kapha      = 0.60
    # Confidence = 0.60
    #
    #
    # WHY MULTIPLY SCORE × CONFIDENCE?
    #
    # Dosha score tells us:
    #
    # "What tendency does this module detect?"
    #
    # Confidence tells us:
    #
    # "How much influence should this module have?"
    #
    # Therefore:
    #
    # Weighted Contribution
    # =
    # Dosha Score × Module Confidence
    #
    # A higher-confidence module has more influence.
    # =====================================================


    # =====================================================
    # PROCESS EACH FACIAL MODULE
    # =====================================================

    for module_name in facial_module_names:

        # Get Geometry, Texture,
        # Colour or Symmetry
        module = module_analysis.get(
            module_name
        )


        # Skip the module if it is missing
        if not module:
            continue


        # Get the confidence of this module
        #
        # Example for Geometry:
        #
        # Confidence = 0.40

        confidence = float(
            module.get(
                "confidence",
                0.0
            )
        )


        # Get this module's three Dosha scores
        #
        # Example Geometry:
        #
        # Vata  = 0.25
        # Pitta = 0.40
        # Kapha = 0.35

        scores = module.get(
            "scores",
            {}
        )


        # =================================================
        # VATA WEIGHTED CONTRIBUTION
        # =================================================
        #
        # Formula:
        #
        # Module Vata Score × Module Confidence
        #
        #
        # Example Geometry:
        #
        # Geometry Vata = 0.25
        # Geometry Confidence = 0.40
        #
        # 0.25 × 0.40
        # =
        # 0.10
        #
        # Geometry therefore contributes
        # 0.10 weighted evidence toward Vata.
        #
        #
        # Other example contributions:
        #
        # Texture:
        #
        # 0.20 × 0.50
        # =
        # 0.10
        #
        #
        # Colour:
        #
        # 0.30 × 0.35
        # =
        # 0.105
        #
        #
        # Symmetry:
        #
        # 0.05 × 0.60
        # =
        # 0.03
        #
        #
        # Total weighted Vata later becomes:
        #
        # 0.10
        # + 0.10
        # + 0.105
        # + 0.03
        #
        # =
        # 0.335
        # =================================================

        weighted_scores["vata"] += (

            float(
                scores.get(
                    "vata",
                    0.0
                )
            )

            * confidence
        )


        # =================================================
        # PITTA WEIGHTED CONTRIBUTION
        # =================================================
        #
        # Formula:
        #
        # Module Pitta Score × Module Confidence
        #
        #
        # Example:
        #
        # Geometry:
        #
        # 0.40 × 0.40 = 0.16
        #
        #
        # Texture:
        #
        # 0.30 × 0.50 = 0.15
        #
        #
        # Colour:
        #
        # 0.35 × 0.35 = 0.1225
        #
        #
        # Symmetry:
        #
        # 0.35 × 0.60 = 0.21
        #
        #
        # Total weighted Pitta:
        #
        # 0.16
        # + 0.15
        # + 0.1225
        # + 0.21
        #
        # =
        # 0.6425
        # =================================================

        weighted_scores["pitta"] += (

            float(
                scores.get(
                    "pitta",
                    0.0
                )
            )

            * confidence
        )


        # =================================================
        # KAPHA WEIGHTED CONTRIBUTION
        # =================================================
        #
        # Formula:
        #
        # Module Kapha Score × Module Confidence
        #
        #
        # Example:
        #
        # Geometry:
        #
        # 0.35 × 0.40 = 0.14
        #
        #
        # Texture:
        #
        # 0.50 × 0.50 = 0.25
        #
        #
        # Colour:
        #
        # 0.35 × 0.35 = 0.1225
        #
        #
        # Symmetry:
        #
        # 0.60 × 0.60 = 0.36
        #
        #
        # Total weighted Kapha:
        #
        # 0.14
        # + 0.25
        # + 0.1225
        # + 0.36
        #
        # =
        # 0.8725
        # =================================================

        weighted_scores["kapha"] += (

            float(
                scores.get(
                    "kapha",
                    0.0
                )
            )

            * confidence
        )


        # =================================================
        # ADD MODULE CONFIDENCE
        # =================================================
        #
        # Example:
        #
        # Geometry   = 0.40
        # Texture    = 0.50
        # Colour     = 0.35
        # Symmetry   = 0.60
        #
        # Total confidence:
        #
        # 0.40
        # + 0.50
        # + 0.35
        # + 0.60
        #
        # =
        # 1.85
        # =================================================

        total_confidence += confidence


    # =====================================================
    # SAFETY CHECK
    # =====================================================
    #
    # If every module somehow had zero confidence,
    # division by zero would occur.
    #
    # Therefore an approximately equal fallback
    # distribution is returned.
    # =====================================================

    if total_confidence <= 1e-6:

        return {

            "vata": 0.33,

            "pitta": 0.33,

            "kapha": 0.34
        }


    # =====================================================
    # CONFIDENCE-WEIGHTED AVERAGE
    # =====================================================
    #
    # Now divide each accumulated weighted Dosha
    # value by the total module confidence.
    #
    #
    # -----------------------------------------------------
    # VATA EXAMPLE
    # -----------------------------------------------------
    #
    # Total weighted Vata
    # =
    # 0.335
    #
    # Total confidence
    # =
    # 1.85
    #
    # Facial Vata
    # =
    # 0.335 / 1.85
    #
    # =
    # 0.181
    #
    # =
    # 18.1%
    #
    #
    # -----------------------------------------------------
    # PITTA EXAMPLE
    # -----------------------------------------------------
    #
    # Total weighted Pitta
    # =
    # 0.6425
    #
    # 0.6425 / 1.85
    #
    # =
    # 0.347
    #
    # =
    # 34.7%
    #
    #
    # -----------------------------------------------------
    # KAPHA EXAMPLE
    # -----------------------------------------------------
    #
    # Total weighted Kapha
    # =
    # 0.8725
    #
    # 0.8725 / 1.85
    #
    # =
    # 0.472
    #
    # =
    # 47.2%
    #
    #
    # So the facial result is approximately:
    #
    # Vata  = 18.1%
    # Pitta = 34.7%
    # Kapha = 47.2%
    #
    # Highest = Kapha
    #
    # Therefore:
    #
    # Facial Dominant Dosha = Kapha
    # =====================================================

    facial_scores = {

        "vata":
            weighted_scores["vata"]
            / total_confidence,

        "pitta":
            weighted_scores["pitta"]
            / total_confidence,

        "kapha":
            weighted_scores["kapha"]
            / total_confidence
    }


    # =====================================================
    # FINAL NORMALIZATION
    # =====================================================
    #
    # The three values should already be close to a
    # probability-like distribution.
    #
    # We normalize again so:
    #
    # Vata + Pitta + Kapha = 1
    #
    # This keeps the final facial result consistent.
    # =====================================================

    total = (

        facial_scores["vata"]

        + facial_scores["pitta"]

        + facial_scores["kapha"]
    )


    if total <= 1e-6:

        return {

            "vata": 0.33,

            "pitta": 0.33,

            "kapha": 0.34
        }


    final_facial_scores = {

        "vata": (
            facial_scores["vata"]
            / total
        ),

        "pitta": (
            facial_scores["pitta"]
            / total
        ),

        "kapha": (
            facial_scores["kapha"]
            / total
        )
    }


    # =====================================================
    # RETURN FINAL FACIAL DISTRIBUTION
    # =====================================================
    #
    # Example:
    #
    # {
    #     "vata":  0.181,
    #     "pitta": 0.347,
    #     "kapha": 0.472
    # }
    #
    # Meaning:
    #
    # Vata  = 18.1%
    # Pitta = 34.7%
    # Kapha = 47.2%
    #
    # Facial Dominant = Kapha
    # =====================================================

    return {

        "vata": round(
            float(
                final_facial_scores["vata"]
            ),
            4
        ),

        "pitta": round(
            float(
                final_facial_scores["pitta"]
            ),
            4
        ),

        "kapha": round(
            float(
                final_facial_scores["kapha"]
            ),
            4
        )
    }


# =========================================================
# QUESTIONNAIRE MODULE
# =========================================================

def create_questionnaire_analysis(
    q_scores
):
    """
    Create a separate explainable
    questionnaire module.
    """

    # Normalize questionnaire Vata,
    # Pitta and Kapha values.
    questionnaire_scores = (
        normalize_module_scores(

            q_scores.get(
                "vata",
                0
            ),

            q_scores.get(
                "pitta",
                0
            ),

            q_scores.get(
                "kapha",
                0
            )
        )
    )


    # Highest questionnaire score
    # becomes questionnaire dominant Dosha.
    dominant = max(
        questionnaire_scores,
        key=questionnaire_scores.get
    ).capitalize()


    explanation = (

        f"The questionnaire responses indicate "
        f"stronger {dominant} characteristics based on "
        f"physiological, behavioural and lifestyle factors."
    )


    return get_module_result(

        "Questionnaire",

        questionnaire_scores,

        explanation
    )


# =========================================================
# FINAL AI EXPLANATION
# =========================================================

def create_ai_explanation(
    dominant,
    secondary,
    confidence,
    module_analysis
):
    """
    Generate a final human-readable explanation.

    This section does not calculate the final prediction.
    It only creates readable explanation text.
    """

    supporting_modules = []


    # Check which modules have the same
    # dominant Dosha as the final system result.
    for module in (
        module_analysis.values()
    ):

        if (
            module[
                "dominant_dosha"
            ].lower()

            ==

            dominant.lower()
        ):

            supporting_modules.append(
                module[
                    "module"
                ]
            )


    # =====================================================
    # SUPPORTING MODULES FOUND
    # =====================================================

    if supporting_modules:

        module_text = ", ".join(
            supporting_modules
        )


        return (

            f"The system identified {dominant} as the "
            f"dominant Prakriti and {secondary} as the "
            f"secondary Prakriti with "
            f"{round(confidence * 100)}% confidence. "

            f"The {module_text} module analysis supported "
            f"the {dominant} tendency. "

            f"The facial result was obtained using "
            f"confidence-aware fusion of the Geometry, "
            f"Texture, Colour and Symmetry modules. "

            f"The final Prakriti result was produced by "
            f"combining the facial analysis with the "
            f"questionnaire analysis."
        )


    # =====================================================
    # NO DIRECT MODULE SUPPORT
    # =====================================================

    return (

        f"The system identified {dominant} as the "
        f"dominant Prakriti and {secondary} as the "
        f"secondary Prakriti with "
        f"{round(confidence * 100)}% confidence. "

        f"The facial result was obtained using "
        f"confidence-aware fusion of the Geometry, "
        f"Texture, Colour and Symmetry modules. "

        f"The final Prakriti result was produced by "
        f"combining facial analysis with questionnaire "
        f"analysis."
    )