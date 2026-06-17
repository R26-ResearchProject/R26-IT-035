import api from "./api"

export async function getFullExplanation(
  diseaseId,
  confidence,
  prakriti,
  userContext = null
) {
  const requestBody = {
    prakriti_result: {
      dominant_prakriti: Object.entries(prakriti)
        .sort((a, b) => b[1] - a[1])[0][0],
      prakriti_scores: prakriti,
      confidence: 0.85
    },
    skin_result: {
      predicted_condition: diseaseId,
      confidence: confidence,
      referral_required: false
    },
    user_context: userContext || {
      age_group: "adult",
      pregnancy_status: false,
      known_allergies: []
    }
  }

  const response = await api.post(
    "/api/explanation/full",
    requestBody
  )
  return response.data
}

export async function getAllDiseases() {
  const response = await api.get("/api/diseases")
  return response.data
}
