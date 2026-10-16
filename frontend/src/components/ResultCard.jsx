import React from "react";

export default function ResultCard({ result }) {

  if (!result) return null;


  // =====================================================
  // FINAL PRAKRITI SCORES
  // =====================================================

  const scores = result.prakriti_scores || {
    vata: 0,
    pitta: 0,
    kapha: 0,
  };


  // =====================================================
  // MODULE ANALYSIS
  // =====================================================

  const modules =
    result.module_analysis || {};


  // =====================================================
  // FORMAT PERCENTAGE
  // =====================================================

  const formatPercentage = (value) => {

    const number =
      Number(value) || 0;

    return `${(
      number * 100
    ).toFixed(2)}%`;
  };


  // =====================================================
  // PROGRESS BAR WIDTH
  // =====================================================

  const getScoreWidth = (value) => {

    const percentage =
      (Number(value) || 0) * 100;

    return `${Math.min(
      Math.max(
        percentage,
        0
      ),
      100
    )}%`;
  };


  // =====================================================
  // MODULE ORDER
  // =====================================================
  // Questionnaire removed from frontend display.
  // It is still used in backend final calculation.
  // =====================================================

  const moduleOrder = [
    "geometry",
    "texture",
    "colour",
    "symmetry",
  ];


  // =====================================================
  // UI
  // =====================================================

  return (

    <div className="mt-6 space-y-6">


      {/* =================================================
          MAIN PRAKRITI RESULT
      ================================================= */}

      <div className="rounded-2xl bg-white p-6 shadow-xl">

        <h2 className="mb-6 text-center text-2xl font-bold text-gray-800">

          Prakriti Analysis Result

        </h2>


        <div className="grid gap-4 sm:grid-cols-3">


          {/* DOMINANT PRAKRITI */}

          <div className="rounded-xl bg-blue-50 p-4 text-center">

            <p className="mb-1 text-sm font-medium text-gray-500">

              Dominant Prakriti

            </p>

            <p className="text-xl font-bold text-blue-600">

              {result.dominant_prakriti}

            </p>

          </div>


          {/* SECONDARY PRAKRITI */}

          <div className="rounded-xl bg-purple-50 p-4 text-center">

            <p className="mb-1 text-sm font-medium text-gray-500">

              Secondary Prakriti

            </p>

            <p className="text-xl font-bold text-purple-600">

              {result.secondary_prakriti}

            </p>

          </div>


          {/* OVERALL CONFIDENCE */}

          <div className="rounded-xl bg-green-50 p-4 text-center">

            <p className="mb-1 text-sm font-medium text-gray-500">

              Overall Confidence

            </p>

            <p className="text-xl font-bold text-green-600">

              {formatPercentage(
                result.confidence
              )}

            </p>

          </div>

        </div>

      </div>


      {/* =================================================
          FINAL DOSHA DISTRIBUTION
      ================================================= */}

      <div className="rounded-2xl bg-white p-6 shadow-xl">

        <h3 className="mb-5 text-xl font-bold text-gray-800">

          Dosha Score Distribution

        </h3>


        <div className="space-y-5">


          {/* VATA */}

          <div>

            <div className="mb-2 flex justify-between">

              <span className="font-semibold text-gray-700">

                Vata

              </span>

              <span className="font-semibold text-blue-600">

                {formatPercentage(
                  scores.vata
                )}

              </span>

            </div>


            <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">

              <div
                className="h-full rounded-full bg-blue-500 transition-all duration-500"
                style={{
                  width: getScoreWidth(
                    scores.vata
                  ),
                }}
              />

            </div>

          </div>


          {/* PITTA */}

          <div>

            <div className="mb-2 flex justify-between">

              <span className="font-semibold text-gray-700">

                Pitta

              </span>

              <span className="font-semibold text-orange-600">

                {formatPercentage(
                  scores.pitta
                )}

              </span>

            </div>


            <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">

              <div
                className="h-full rounded-full bg-orange-500 transition-all duration-500"
                style={{
                  width: getScoreWidth(
                    scores.pitta
                  ),
                }}
              />

            </div>

          </div>


          {/* KAPHA */}

          <div>

            <div className="mb-2 flex justify-between">

              <span className="font-semibold text-gray-700">

                Kapha

              </span>

              <span className="font-semibold text-green-600">

                {formatPercentage(
                  scores.kapha
                )}

              </span>

            </div>


            <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">

              <div
                className="h-full rounded-full bg-green-500 transition-all duration-500"
                style={{
                  width: getScoreWidth(
                    scores.kapha
                  ),
                }}
              />

            </div>

          </div>

        </div>

      </div>


      {/* =================================================
          MODULE-WISE ANALYSIS
      ================================================= */}

      {Object.keys(modules).length > 0 && (

        <div className="rounded-2xl bg-white p-6 shadow-xl">

          <h3 className="mb-2 text-xl font-bold text-gray-800">

            Module-wise Analysis

          </h3>


          <p className="mb-6 text-sm text-gray-500">

            Each facial module calculates separate Vata,
            Pitta and Kapha tendency scores.

          </p>


          <div className="grid gap-5 md:grid-cols-2">


            {moduleOrder.map(
              (moduleKey) => {

                const module =
                  modules[moduleKey];


                if (!module)
                  return null;


                const moduleScores =
                  module.scores || {
                    vata: 0,
                    pitta: 0,
                    kapha: 0,
                  };


                return (

                  <div
                    key={moduleKey}
                    className="rounded-xl border border-gray-200 bg-gray-50 p-5"
                  >


                    {/* =====================================
                        MODULE HEADER
                    ===================================== */}

                    <div className="mb-5 flex items-start justify-between gap-3">


                      <div>

                        <h4 className="text-lg font-bold text-gray-800">

                          {module.module ||
                            moduleKey}

                        </h4>


                        <p className="mt-1 text-sm text-gray-500">

                          Dominant Dosha

                        </p>

                      </div>


                      <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-700">

                        {module.dominant_dosha}

                      </span>

                    </div>


                    {/* =====================================
                        MODULE CONFIDENCE
                    ===================================== */}

                    <div className="mb-5">

                      <div className="mb-2 flex justify-between text-sm">

                        <span className="font-semibold text-gray-700">

                          Module Confidence

                        </span>

                        <span className="font-bold text-gray-800">

                          {formatPercentage(
                            module.confidence
                          )}

                        </span>

                      </div>


                      <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">

                        <div
                          className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                          style={{
                            width:
                              getScoreWidth(
                                module.confidence
                              ),
                          }}
                        />

                      </div>

                    </div>


                    {/* =====================================
                        VATA MODULE SCORE
                    ===================================== */}

                    <div className="mb-4">

                      <div className="mb-2 flex justify-between text-sm">

                        <span className="font-medium text-gray-700">

                          Vata

                        </span>

                        <span className="font-semibold text-blue-600">

                          {formatPercentage(
                            moduleScores.vata
                          )}

                        </span>

                      </div>


                      <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-200">

                        <div
                          className="h-full rounded-full bg-blue-500 transition-all duration-500"
                          style={{
                            width:
                              getScoreWidth(
                                moduleScores.vata
                              ),
                          }}
                        />

                      </div>

                    </div>


                    {/* =====================================
                        PITTA MODULE SCORE
                    ===================================== */}

                    <div className="mb-4">

                      <div className="mb-2 flex justify-between text-sm">

                        <span className="font-medium text-gray-700">

                          Pitta

                        </span>

                        <span className="font-semibold text-orange-600">

                          {formatPercentage(
                            moduleScores.pitta
                          )}

                        </span>

                      </div>


                      <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-200">

                        <div
                          className="h-full rounded-full bg-orange-500 transition-all duration-500"
                          style={{
                            width:
                              getScoreWidth(
                                moduleScores.pitta
                              ),
                          }}
                        />

                      </div>

                    </div>


                    {/* =====================================
                        KAPHA MODULE SCORE
                    ===================================== */}

                    <div>

                      <div className="mb-2 flex justify-between text-sm">

                        <span className="font-medium text-gray-700">

                          Kapha

                        </span>

                        <span className="font-semibold text-green-600">

                          {formatPercentage(
                            moduleScores.kapha
                          )}

                        </span>

                      </div>


                      <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-200">

                        <div
                          className="h-full rounded-full bg-green-500 transition-all duration-500"
                          style={{
                            width:
                              getScoreWidth(
                                moduleScores.kapha
                              ),
                          }}
                        />

                      </div>

                    </div>

                  </div>

                );
              }
            )}

          </div>

        </div>

      )}

    </div>
  );
}