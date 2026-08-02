import React, { useState } from "react";

import ImageUpload from "../components/ImageUpload";
import WebcamCapture from "../components/WebcamCapture";
import AdaptiveQuestionnaire from "../components/AdaptiveQuestionnaire";
import ResultCard from "../components/ResultCard";

import { analyzePrakriti } from "../services/api";


export default function Home() {

  // -------------------------
  // MAIN STATES
  // -------------------------

  const [step, setStep] = useState(1);

  const [image, setImage] = useState(null);

  // Track where image came from:
  // null | "upload" | "camera"
  const [imageSource, setImageSource] = useState(null);

  // Used to reset child components
  const [selectionKey, setSelectionKey] = useState(0);

  const [answers, setAnswers] = useState({});

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");


  // =====================================================
  // IMAGE SELECTED FROM UPLOAD
  // =====================================================

  const handleUploadedImage = (file) => {

    if (!file) return;

    // Prevent camera image being replaced
    if (
      imageSource &&
      imageSource !== "upload"
    ) {
      return;
    }

    setImage(file);

    setImageSource("upload");

    setError("");
  };


  // =====================================================
  // IMAGE CAPTURED FROM CAMERA
  // =====================================================

  const handleCameraImage = (file) => {

    if (!file) return;

    // Prevent uploaded image being replaced
    if (
      imageSource &&
      imageSource !== "camera"
    ) {
      return;
    }

    setImage(file);

    setImageSource("camera");

    setError("");
  };


  // =====================================================
  // CHANGE IMAGE METHOD
  // =====================================================

  const resetImageSelection = () => {

    setImage(null);

    setImageSource(null);

    setError("");

    // Force ImageUpload and WebcamCapture
    // to reset their internal preview states
    setSelectionKey(
      (previous) => previous + 1
    );
  };


  // =====================================================
  // NEXT FROM IMAGE STEP
  // =====================================================

  const handleImageNext = () => {

    setError("");

    if (!image) {

      setError(
        "Please upload or capture an image before continuing"
      );

      return;
    }

    if (!imageSource) {

      setError(
        "Please select an image method"
      );

      return;
    }

    setStep(3);
  };


  // =====================================================
  // FINAL ANALYSIS
  // =====================================================

  const handleSubmit = async () => {

    setError("");

    if (!image) {

      setError(
        "Please upload or capture an image"
      );

      return;
    }

    if (
      !answers ||
      Object.keys(answers).length === 0
    ) {

      setError(
        "Please complete the questionnaire"
      );

      return;
    }

    try {

      setLoading(true);

      const res =
        await analyzePrakriti(
          image,
          answers
        );

      if (res.error) {

        setError(res.error);

      } else {

        setResult(res.data);

        setStep(4);
      }

    } catch {

      setError(
        "Something went wrong"
      );

    } finally {

      setLoading(false);
    }
  };


  // =====================================================
  // START AGAIN
  // =====================================================

  const handleStartAgain = () => {

    setStep(1);

    setImage(null);

    setImageSource(null);

    setAnswers({});

    setResult(null);

    setError("");

    setSelectionKey(
      (previous) => previous + 1
    );
  };


  // =====================================================
  // UI
  // =====================================================

  return (

    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 flex items-center justify-center p-6">

      <div className="bg-white shadow-2xl rounded-2xl p-8 w-full max-w-2xl">


        {/* =================================================
            STEP 1 - LANDING
        ================================================= */}

        {step === 1 && (

          <div className="text-center">

            <h1 className="text-4xl font-bold mb-4">

              Prakriti Body Type Identification

            </h1>

            <p className="text-gray-600 mb-6">

              Discover your Ayurvedic body constitution
              using AI-based facial analysis

            </p>

            <button

              onClick={() =>
                setStep(2)
              }

              className="bg-blue-600 text-white px-6 py-3 rounded-lg text-lg"
            >

              Get Started

            </button>

          </div>

        )}


        {/* =================================================
            STEP 2 - IMAGE
        ================================================= */}

        {step === 2 && (

          <div>

            <h2 className="text-2xl font-semibold text-center mb-4">

              Upload or Capture Image

            </h2>


            {/* =============================================
                UPLOAD IMAGE
            ============================================= */}

            {imageSource !== "camera" && (

              <ImageUpload

                key={`upload-${selectionKey}`}

                setImage={
                  handleUploadedImage
                }

              />

            )}


            {/* =============================================
                SHOW OR ONLY WHEN NOTHING SELECTED
            ============================================= */}

            {imageSource === null && (

              <div className="text-center mt-4 text-gray-500">

                OR

              </div>

            )}


            {/* =============================================
                WEBCAM
            ============================================= */}

            {imageSource !== "upload" && (

              <WebcamCapture

                key={`camera-${selectionKey}`}

                setImage={
                  handleCameraImage
                }

              />

            )}


            {/* =============================================
                SELECTED METHOD
            ============================================= */}

            {imageSource && (

              <div className="mt-5 text-center">

                <p className="text-green-600 font-medium">

                  {imageSource === "upload"
                    ? "Image selected using Upload ✓"
                    : "Image captured using Camera ✓"}

                </p>


                <button

                  type="button"

                  onClick={
                    resetImageSelection
                  }

                  className="mt-3 text-sm text-red-500 hover:text-red-700 underline"

                >

                  Change image method

                </button>

              </div>

            )}


            {/* ERROR */}

            {error && (

              <p className="text-red-500 mt-4 text-center">

                {error}

              </p>

            )}


            {/* NEXT */}

            <button

              onClick={
                handleImageNext
              }

              disabled={!image}

              className={`
                w-full
                mt-6
                text-white
                py-3
                rounded-lg
                transition

                ${
                  image
                    ? "bg-blue-600 hover:bg-blue-700"
                    : "bg-gray-400 cursor-not-allowed"
                }
              `}

            >

              Next

            </button>

          </div>

        )}


        {/* =================================================
            STEP 3 - QUESTIONNAIRE
        ================================================= */}

        {step === 3 && (

          <div>

            <h2 className="text-2xl font-semibold text-center mb-4">

              Answer Questions

            </h2>


            <AdaptiveQuestionnaire

              setAnswers={
                setAnswers
              }

            />


            {error && (

              <p className="text-red-500 mt-4 text-center">

                {error}

              </p>

            )}


            <button

              onClick={
                handleSubmit
              }

              disabled={
                loading
              }

              className={`
                w-full
                mt-6
                py-3
                rounded-lg
                text-lg
                text-white

                ${
                  loading
                    ? "bg-gray-400"
                    : "bg-blue-600"
                }
              `}

            >

              {loading
                ? "Analyzing..."
                : "Analyze"}

            </button>

          </div>

        )}


        {/* =================================================
            STEP 4 - RESULT
        ================================================= */}

        {step === 4 && (

          <div>

            <ResultCard
              result={
                result
              }
            />


            <button

              onClick={
                handleStartAgain
              }

              className="w-full mt-6 bg-gray-600 text-white py-3 rounded-lg"

            >

              Start Again

            </button>

          </div>

        )}

      </div>

    </div>
  );
}