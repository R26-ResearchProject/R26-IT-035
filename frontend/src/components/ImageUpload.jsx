import React, { useRef, useState } from "react";

export default function ImageUpload({ setImage }) {

  const [preview, setPreview] = useState(null);
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState("");
  const [detecting, setDetecting] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);

  const canvasRef = useRef(null);

  // -------------------------
  // DRAW FACE MESH
  // -------------------------

  const drawFaceMesh = (image, landmarks) => {

    const canvas = canvasRef.current;

    if (!canvas) return;

    canvas.width = image.naturalWidth;
    canvas.height = image.naturalHeight;

    const ctx = canvas.getContext("2d");

    // Draw original image
    ctx.clearRect(
      0,
      0,
      canvas.width,
      canvas.height
    );

    ctx.drawImage(
      image,
      0,
      0,
      canvas.width,
      canvas.height
    );

    // -------------------------
    // DRAW LANDMARK POINTS
    // -------------------------

    ctx.fillStyle = "#00ff66";

    landmarks.forEach((point) => {

      const x = point.x * canvas.width;
      const y = point.y * canvas.height;

      ctx.beginPath();

      ctx.arc(
        x,
        y,
        1.5,
        0,
        2 * Math.PI
      );

      ctx.fill();
    });

    // -------------------------
    // DRAW MESH CONNECTIONS
    // -------------------------

    if (window.FACEMESH_TESSELATION) {

      ctx.strokeStyle = "rgba(0, 255, 102, 0.45)";
      ctx.lineWidth = 0.7;

      window.FACEMESH_TESSELATION.forEach(
        ([start, end]) => {

          const p1 = landmarks[start];
          const p2 = landmarks[end];

          if (!p1 || !p2) return;

          ctx.beginPath();

          ctx.moveTo(
            p1.x * canvas.width,
            p1.y * canvas.height
          );

          ctx.lineTo(
            p2.x * canvas.width,
            p2.y * canvas.height
          );

          ctx.stroke();
        }
      );
    }
  };


  // -------------------------
  // DETECT FACE
  // -------------------------

  const detectFace = async (imageUrl) => {

    if (!window.FaceMesh) {

      setError(
        "FaceMesh is not loaded. Please refresh the page."
      );

      return;
    }

    setDetecting(true);
    setFaceDetected(false);

    const image = new Image();

    image.onload = async () => {

      try {

        const faceMesh = new window.FaceMesh({
          locateFile: (file) =>
            `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
        });

        faceMesh.setOptions({
          maxNumFaces: 1,
          refineLandmarks: false,
          minDetectionConfidence: 0.5
        });

        faceMesh.onResults((results) => {

          setDetecting(false);

          if (
            results.multiFaceLandmarks &&
            results.multiFaceLandmarks.length > 0
          ) {

            const landmarks =
              results.multiFaceLandmarks[0];

            setFaceDetected(true);
            setError("");

            drawFaceMesh(
              image,
              landmarks
            );

          } else {

            setFaceDetected(false);

            setError(
              "No face detected. Please upload a clear front-facing image."
            );
          }

          faceMesh.close();
        });

        await faceMesh.send({
          image: image
        });

      } catch (err) {

        console.error(
          "Face mesh error:",
          err
        );

        setDetecting(false);

        setError(
          "Unable to analyze the face."
        );
      }
    };

    image.onerror = () => {

      setDetecting(false);

      setError(
        "Unable to load the selected image."
      );
    };

    image.src = imageUrl;
  };


  // -------------------------
  // HANDLE FILE
  // -------------------------

  const handleFile = (file) => {

    if (!file) return;

    // -------------------------
    // VALIDATION
    // -------------------------

    if (
      ![
        "image/jpeg",
        "image/png"
      ].includes(file.type)
    ) {

      setError(
        "Only JPG or PNG images are allowed"
      );

      setPreview(null);
      setFaceDetected(false);

      return;
    }

    if (
      file.size >
      5 * 1024 * 1024
    ) {

      setError(
        "File size must be less than 5MB"
      );

      setPreview(null);
      setFaceDetected(false);

      return;
    }


    // -------------------------
    // SUCCESS
    // -------------------------

    setError("");
    setFileName(file.name);

    // IMPORTANT:
    // Original image is still sent
    // to backend.
    setImage(file);

    const url =
      URL.createObjectURL(file);

    setPreview(url);

    // Run face mesh visualization
    detectFace(url);
  };


  // -------------------------
  // DRAG & DROP
  // -------------------------

  const handleDrop = (e) => {

    e.preventDefault();

    handleFile(
      e.dataTransfer.files[0]
    );
  };


  const handleDragOver = (e) => {

    e.preventDefault();
  };


  // -------------------------
  // UI
  // -------------------------

  return (

    <div className="mt-4">

      {/* UPLOAD BOX */}

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-blue-500 transition"
      >

        <p className="text-gray-600">
          Drag & Drop Image Here
        </p>

        <p className="text-sm text-gray-400 mt-1">
          or click to upload
        </p>

        <input
          type="file"
          accept="image/png, image/jpeg"
          className="hidden"
          id="fileInput"
          onChange={(e) =>
            handleFile(
              e.target.files[0]
            )
          }
        />

        <label
          htmlFor="fileInput"
          className="inline-block mt-3 bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer"
        >
          Choose File
        </label>

      </div>


      {/* FILE NAME */}

      {fileName && (

        <p className="mt-2 text-sm text-gray-600">

          Selected: {fileName}

        </p>

      )}


      {/* DETECTING */}

      {detecting && (

        <p className="mt-3 text-blue-600 text-sm font-medium animate-pulse">

          Detecting facial landmarks...

        </p>

      )}


      {/* ERROR */}

      {error && (

        <p className="mt-2 text-red-500 text-sm">

          {error}

        </p>

      )}


      {/* FACE DETECTED */}

      {faceDetected && (

        <p className="mt-3 text-green-600 text-sm font-medium">

          Face detected ✓ Facial landmarks identified

        </p>

      )}


      {/* NORMAL PREVIEW WHILE DETECTING */}

      {preview && detecting && (

        <div className="mt-4 text-center">

          <p className="text-sm text-gray-500 mb-2">

            Preview

          </p>

          <img
            src={preview}
            alt="preview"
            className="mx-auto w-48 h-48 object-cover rounded-xl shadow-md"
          />

        </div>

      )}


      {/* FACE MESH PREVIEW */}

      <div
        className={
          faceDetected
            ? "mt-4 text-center"
            : "hidden"
        }
      >

        <p className="text-sm text-gray-500 mb-2">

          Face Mesh Preview

        </p>

        <canvas
          ref={canvasRef}
          className="mx-auto w-64 h-64 object-cover rounded-xl shadow-md border"
        />

      </div>

    </div>
  );
}