import React, {
  useEffect,
  useRef,
  useState
} from "react";

export default function WebcamCapture({ setImage }) {

  // =====================================================
  // REFS
  // =====================================================

  const videoRef = useRef(null);

  // Used to capture the clean image
  const captureCanvasRef = useRef(null);

  // Used only to display the face mesh preview
  const meshCanvasRef = useRef(null);

  // Keep MediaPipe instance between renders
  const faceMeshRef = useRef(null);

  // Keep animation frame ID
  const animationRef = useRef(null);

  // Prevent multiple automatic captures
  const captureStartedRef = useRef(false);

  // Keep latest detected landmarks
  const landmarksRef = useRef(null);


  // =====================================================
  // STATE
  // =====================================================

  const [isCameraOn, setIsCameraOn] = useState(false);

  const [stream, setStream] = useState(null);

  const [faceDetected, setFaceDetected] = useState(false);

  const [scanning, setScanning] = useState(false);

  const [preview, setPreview] = useState(null);

  const [meshReady, setMeshReady] = useState(false);

  const [error, setError] = useState("");


  // =====================================================
  // START CAMERA
  // =====================================================

  const startCamera = async () => {

    try {

      setError("");
      setPreview(null);
      setMeshReady(false);
      setFaceDetected(false);

      captureStartedRef.current = false;
      landmarksRef.current = null;

      const mediaStream =
        await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: "user"
          },
          audio: false
        });

      setStream(mediaStream);
      setIsCameraOn(true);

    } catch (err) {

      console.error(
        "Camera error:",
        err
      );

      setError(
        "Unable to access camera."
      );
    }
  };


  // =====================================================
  // ATTACH CAMERA STREAM
  // =====================================================

  useEffect(() => {

    if (
      !isCameraOn ||
      !stream ||
      !videoRef.current
    ) {
      return;
    }

    const video = videoRef.current;

    video.srcObject = stream;

    const startVideo = async () => {

      try {

        await video.play();

        initializeFaceMesh();

      } catch (err) {

        console.error(
          "Video play error:",
          err
        );
      }
    };

    if (video.readyState >= 2) {

      startVideo();

    } else {

      video.onloadedmetadata =
        startVideo;
    }

  }, [isCameraOn, stream]);


  // =====================================================
  // INITIALIZE MEDIAPIPE FACE MESH
  // =====================================================

  const initializeFaceMesh = () => {

    if (!window.FaceMesh) {

      console.error(
        "FaceMesh not loaded"
      );

      setError(
        "FaceMesh is not loaded. Please refresh the page."
      );

      return;
    }


    // Close previous instance if available

    if (faceMeshRef.current) {

      try {

        faceMeshRef.current.close();

      } catch (err) {

        console.log(err);
      }
    }


    const faceMesh =
      new window.FaceMesh({

        locateFile: (file) =>

          `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`

      });


    faceMesh.setOptions({

      maxNumFaces: 1,

      refineLandmarks: false,

      minDetectionConfidence: 0.5,

      minTrackingConfidence: 0.5

    });


    // ===================================================
    // FACE MESH RESULTS
    // ===================================================

    faceMesh.onResults(
      (results) => {

        if (
          results.multiFaceLandmarks &&
          results.multiFaceLandmarks.length > 0
        ) {

          const landmarks =
            results.multiFaceLandmarks[0];

          landmarksRef.current =
            landmarks;

          setFaceDetected(true);


          // Start automatic capture only once

          if (
            !captureStartedRef.current
          ) {

            captureStartedRef.current =
              true;

            setScanning(true);

            setTimeout(() => {

              captureImage();

            }, 2500);
          }

        } else {

          setFaceDetected(false);

          landmarksRef.current =
            null;
        }
      }
    );


    faceMeshRef.current =
      faceMesh;


    detectLoop();
  };


  // =====================================================
  // FACE DETECTION LOOP
  // =====================================================

  const detectLoop = async () => {

    if (
      !videoRef.current ||
      !faceMeshRef.current
    ) {
      return;
    }


    const video =
      videoRef.current;


    if (
      video.readyState >= 2 &&
      video.videoWidth > 0
    ) {

      try {

        await faceMeshRef.current.send({
          image: video
        });

      } catch (err) {

        console.error(
          "FaceMesh detection error:",
          err
        );
      }
    }


    animationRef.current =
      requestAnimationFrame(
        detectLoop
      );
  };


  // =====================================================
  // DRAW FACE MESH
  // =====================================================
  //
  // This uses the SAME method as ImageUpload.jsx.
  //
  // Original image is drawn first.
  // Green landmarks are then drawn over it.
  //
  // =====================================================

  const drawFaceMesh = (
    image,
    landmarks
  ) => {

    const canvas =
      meshCanvasRef.current;


    if (
      !canvas ||
      !image ||
      !landmarks
    ) {
      return;
    }


    canvas.width =
      image.naturalWidth;

    canvas.height =
      image.naturalHeight;


    const ctx =
      canvas.getContext("2d");


    // Clear canvas

    ctx.clearRect(
      0,
      0,
      canvas.width,
      canvas.height
    );


    // Draw captured image

    ctx.drawImage(
      image,
      0,
      0,
      canvas.width,
      canvas.height
    );


    // ===================================================
    // DRAW GREEN LANDMARK POINTS
    // ===================================================

    ctx.fillStyle =
      "#00ff66";


    landmarks.forEach(
      (point) => {

        const x =
          point.x *
          canvas.width;

        const y =
          point.y *
          canvas.height;


        ctx.beginPath();

        ctx.arc(
          x,
          y,
          1.5,
          0,
          2 * Math.PI
        );

        ctx.fill();
      }
    );


    // ===================================================
    // DRAW MESH CONNECTIONS
    // ===================================================

    if (
      window.FACEMESH_TESSELATION
    ) {

      ctx.strokeStyle =
        "rgba(0, 255, 102, 0.45)";

      ctx.lineWidth =
        0.7;


      window.FACEMESH_TESSELATION.forEach(
        ([start, end]) => {

          const p1 =
            landmarks[start];

          const p2 =
            landmarks[end];


          if (
            !p1 ||
            !p2
          ) {
            return;
          }


          ctx.beginPath();


          ctx.moveTo(

            p1.x *
            canvas.width,

            p1.y *
            canvas.height

          );


          ctx.lineTo(

            p2.x *
            canvas.width,

            p2.y *
            canvas.height

          );


          ctx.stroke();
        }
      );
    }


    setMeshReady(true);
  };


  // =====================================================
  // CAPTURE IMAGE
  // =====================================================

  const captureImage = () => {

    const video =
      videoRef.current;

    const canvas =
      captureCanvasRef.current;


    if (
      !video ||
      !canvas ||
      video.videoWidth === 0
    ) {

      console.log(
        "Video not ready."
      );

      captureStartedRef.current =
        false;

      setScanning(false);

      return;
    }


    // Save landmarks BEFORE stopping camera

    const capturedLandmarks =
      landmarksRef.current;


    if (!capturedLandmarks) {

      console.log(
        "No landmarks available."
      );

      captureStartedRef.current =
        false;

      setScanning(false);

      return;
    }


    // ===================================================
    // CREATE CLEAN CAPTURE
    // ===================================================

    canvas.width =
      video.videoWidth;

    canvas.height =
      video.videoHeight;


    const ctx =
      canvas.getContext("2d");


    ctx.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );


    // ===================================================
    // CREATE IMAGE FILE
    // ===================================================

    canvas.toBlob(

      (blob) => {

        if (!blob) {

          setScanning(false);

          return;
        }


        // ------------------------------------------------
        // ORIGINAL CLEAN FILE
        // ------------------------------------------------
        //
        // This is what goes to backend.
        // Mesh is NOT included.
        //
        // ------------------------------------------------

        const file =
          new File(
            [blob],
            "capture.jpg",
            {
              type: "image/jpeg"
            }
          );


        setImage(file);


        // ------------------------------------------------
        // PREVIEW URL
        // ------------------------------------------------

        const imageUrl =
          URL.createObjectURL(blob);


        setPreview(
          imageUrl
        );


        // ------------------------------------------------
        // LOAD CAPTURED IMAGE
        // ------------------------------------------------
        //
        // After image loads, draw the saved landmarks
        // onto the separate mesh canvas.
        //
        // ------------------------------------------------

        const capturedImage =
          new Image();


        capturedImage.onload =
          () => {

            drawFaceMesh(
              capturedImage,
              capturedLandmarks
            );

          };


        capturedImage.onerror =
          () => {

            setError(
              "Unable to create face mesh preview."
            );

          };


        capturedImage.src =
          imageUrl;


        // Stop camera AFTER capture

        stopCamera();

        setScanning(false);

      },

      "image/jpeg",

      0.95
    );
  };


  // =====================================================
  // STOP CAMERA
  // =====================================================

  const stopCamera = () => {

    // Stop animation loop

    if (
      animationRef.current
    ) {

      cancelAnimationFrame(
        animationRef.current
      );

      animationRef.current =
        null;
    }


    // Stop webcam

    if (stream) {

      stream
        .getTracks()
        .forEach(
          (track) =>
            track.stop()
        );
    }


    setStream(null);

    setIsCameraOn(false);
  };


  // =====================================================
  // CLEANUP
  // =====================================================

  useEffect(() => {

    return () => {

      if (
        animationRef.current
      ) {

        cancelAnimationFrame(
          animationRef.current
        );
      }


      if (
        faceMeshRef.current
      ) {

        try {

          faceMeshRef.current.close();

        } catch (err) {

          console.log(err);
        }
      }


      if (stream) {

        stream
          .getTracks()
          .forEach(
            (track) =>
              track.stop()
          );
      }
    };

  }, [stream]);


  // =====================================================
  // UI
  // =====================================================

  return (

    <div className="text-center mt-4">


      {/* ERROR */}

      {error && (

        <p className="mb-3 text-red-500 text-sm">

          {error}

        </p>

      )}


      {/* START CAMERA */}

      {!isCameraOn && (

        <button

          type="button"

          onClick={
            startCamera
          }

          className="bg-green-600 hover:bg-green-700 transition text-white px-5 py-3 rounded-xl shadow-md"

        >

          Start Camera

        </button>

      )}


      {/* =================================================
          CAPTURED FACE MESH PREVIEW
      ================================================= */}

      {preview && (

        <div className="mt-6">


          {meshReady && (

            <p className="text-green-600 text-sm font-medium mb-3">

              Face detected ✓ Facial landmarks identified

            </p>

          )}


          <p className="text-sm text-gray-500 mb-2">

            Face Mesh Preview

          </p>


          {/* IMPORTANT:
              We display the CANVAS,
              not the normal image.
          */}

          <canvas

            ref={
              meshCanvasRef
            }

            className="mx-auto w-64 h-64 object-cover rounded-xl shadow-md border"

          />

        </div>

      )}


      {/* =================================================
          CAMERA POPUP
      ================================================= */}

      {isCameraOn && (

        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">


          <div className="bg-white rounded-2xl p-6 shadow-2xl text-center relative">


            <h2 className="text-2xl font-bold mb-4">

              AI Face Scan

            </h2>


            <div className="relative inline-block">


              {/* VIDEO */}

              <video

                ref={
                  videoRef
                }

                autoPlay

                playsInline

                muted

                className="rounded-2xl w-[400px] h-[400px] object-cover"

              />


              {/* FACE BORDER */}

              <div

                className={`absolute inset-0 border-4 rounded-2xl pointer-events-none transition-all duration-300 ${
                  faceDetected
                    ? "border-green-500"
                    : "border-red-500"
                }`}

              />


              {/* SCANNING */}

              {scanning && (

                <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center rounded-2xl pointer-events-none">

                  <div className="text-white text-lg font-semibold animate-pulse">

                    Scanning...

                  </div>

                </div>

              )}

            </div>


            {/* STATUS */}

            <div className="mt-4">

              {faceDetected ? (

                <p className="text-green-600 font-medium">

                  Face detected ✓

                </p>

              ) : (

                <p className="text-red-500 font-medium">

                  Align your face properly

                </p>

              )}

            </div>


            {/* CLOSE */}

            <button

              type="button"

              onClick={
                stopCamera
              }

              className="mt-5 bg-red-500 hover:bg-red-600 transition text-white px-5 py-2 rounded-xl"

            >

              Close

            </button>


          </div>

        </div>

      )}


      {/* =================================================
          HIDDEN CLEAN CAPTURE CANVAS
      ================================================= */}

      <canvas

        ref={
          captureCanvasRef
        }

        style={{
          display: "none"
        }}

      />


    </div>
  );
}