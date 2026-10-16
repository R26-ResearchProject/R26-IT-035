import React, { useState } from "react";

const questions = [
  { id: 1, text: "Do you have dry skin?", dosha: "vata", weight: 2 },
  { id: 2, text: "Do you feel cold easily?", dosha: "vata", weight: 2 },
  { id: 6, text: "Do you feel hot easily?", dosha: "pitta", weight: 2 },
  { id: 7, text: "Do you sweat a lot?", dosha: "pitta", weight: 2 },
  { id: 11, text: "Do you gain weight easily?", dosha: "kapha", weight: 2 },
];

export default function Questionnaire({ setAnswers }) {
  const [scores, setScores] = useState({
    vata: 0,
    pitta: 0,
    kapha: 0,
  });

  const [index, setIndex] = useState(0);

  const handleAnswer = (q, answer) => {
    let updated = { ...scores };

    if (answer === "yes") {
      updated[q.dosha] += q.weight;
    }

    setScores(updated);
    setAnswers(updated);

    // Move next question
    setIndex((prev) => prev + 1);
  };

  const current = questions[index];

  if (!current) {
    return <p className="text-green-600 mt-4">Questions completed ✔</p>;
  }

  return (
    <div className="mt-6 bg-white shadow-lg p-6 rounded-xl text-center">
      <h2 className="text-xl font-semibold mb-4">
        {current.text}
      </h2>

      <div className="flex justify-center gap-4">
        <button
          className="bg-green-500 text-white px-6 py-2 rounded-lg"
          onClick={() => handleAnswer(current, "yes")}
        >
          Yes
        </button>

        <button
          className="bg-gray-400 text-white px-6 py-2 rounded-lg"
          onClick={() => handleAnswer(current, "no")}
        >
          No
        </button>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Question {index + 1} / {questions.length}
      </div>
    </div>
  );
}