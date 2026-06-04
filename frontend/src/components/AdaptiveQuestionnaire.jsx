import React, { useState, useEffect } from "react";

export default function AdaptiveQuestionnaire({ setAnswers }) {

  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [scores, setScores] = useState({ vata: 0, pitta: 0, kapha: 0 });
  const [askedIds, setAskedIds] = useState([]);

  // NEW STATES (IMPORTANT)
  const [starterQuestions, setStarterQuestions] = useState([]);
  const [starterIndex, setStarterIndex] = useState(0);
  const [isStarterPhase, setIsStarterPhase] = useState(true);

  const [done, setDone] = useState(false);

  // -------------------------
  // START QUESTIONNAIRE
  // -------------------------
  useEffect(() => {
    fetch("http://127.0.0.1:8000/questionnaire/start")
      .then(res => res.json())
      .then(data => {
        setScores(data.scores);
        setAskedIds(data.asked_ids);

        // store all starter questions
        setStarterQuestions(data.questions);

        // start with first one
        setCurrentQuestion(data.questions[0]);
      });
  }, []);

  // -------------------------
  // HANDLE ANSWER
  // -------------------------
  const handleAnswer = async (answer) => {

    // 🔹 STARTER PHASE (first 3 questions)
    if (isStarterPhase) {

      let updatedScores = { ...scores };

      if (answer === "yes") {
        updatedScores[currentQuestion.dosha] += currentQuestion.weight;
      }

      setScores(updatedScores);
      setAnswers(updatedScores);

      const nextIndex = starterIndex + 1;

      if (nextIndex < starterQuestions.length) {
        setStarterIndex(nextIndex);
        setCurrentQuestion(starterQuestions[nextIndex]);
      } else {
        // switch to adaptive phase
        setIsStarterPhase(false);

        // call backend after starter phase
        fetchNextAdaptive(updatedScores, askedIds, currentQuestion, answer);
      }

      return;
    }

    // 🔹 ADAPTIVE PHASE
    fetchNextAdaptive(scores, askedIds, currentQuestion, answer);
  };

  // -------------------------
  // BACKEND ADAPTIVE CALL
  // -------------------------
  const fetchNextAdaptive = async (scores, askedIds, lastQuestion, answer) => {

    const payload = {
      scores,
      asked_ids: askedIds,
      last_question: lastQuestion,
      answer
    };

    const res = await fetch("http://127.0.0.1:8000/questionnaire/next", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    setScores(data.scores);
    setAnswers(data.scores);

    if (data.done) {
      setDone(true);
      return;
    }

    setCurrentQuestion(data.next_question);
    setAskedIds(data.asked_ids);
  };

  // -------------------------
  // UI STATES
  // -------------------------
  if (done) {
    return (
      <div className="text-green-600 text-center mt-4">
        Questionnaire completed ✔
      </div>
    );
  }

  if (!currentQuestion) {
    return <p className="text-center mt-4">Loading...</p>;
  }

  // -------------------------
  // UI
  // -------------------------
  return (
    <div className="bg-white shadow-lg p-6 rounded-xl mt-6 text-center">

      <h2 className="text-xl font-semibold mb-4">
        {currentQuestion.text}
      </h2>

      <div className="flex justify-center gap-4">
        <button
          className="bg-green-500 text-white px-6 py-2 rounded-lg"
          onClick={() => handleAnswer("yes")}
        >
          Yes
        </button>

        <button
          className="bg-gray-400 text-white px-6 py-2 rounded-lg"
          onClick={() => handleAnswer("no")}
        >
          No
        </button>
      </div>

     

    </div>
  );
}