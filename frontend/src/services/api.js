export async function analyzePrakriti(image, answers) {

  const formData = new FormData();

  //  REQUIRED 
  formData.append("user_id", "user123");

  // image
  formData.append("image", image);

  // safe answers (avoid undefined → 422 error)
  formData.append("answers", JSON.stringify({
    vata: answers?.vata || 0,
    pitta: answers?.pitta || 0,
    kapha: answers?.kapha || 0
  }));

  try {
    const response = await fetch("http://127.0.0.1:8000/prakriti/analyze", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    // handle backend errors
    if (!response.ok) {
      throw new Error(data.error || "Something went wrong");
    }

    return data;

  } catch (error) {
    console.error("API Error:", error.message);
    return { error: error.message };
  }
}