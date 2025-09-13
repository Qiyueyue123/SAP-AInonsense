import React from "react";
import Chatbot from '../components/Chatbot';

export default function Stats({
  strengths = [],
  weaknesses = [],
  courses = [],
  mentors = [],
  careerPath = [],
  chatbot = null
}) {
  return (
    <div style={{
        width: "100%",
        padding: "2rem",
        boxSizing: "border-box"
    }}>
      {/* Top section: Stats/Feedback/Strengths & Weaknesses */}
      <div style={{
        background: "#f7f7f7",
        padding: "2rem",
        borderRadius: "8px",
        marginBottom: "2rem",
        width: "100%"
      }}>
        <h2>STATS</h2>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div>
            {/* Placeholder for numbers/graphs */}
            <p>/* ...stats graphs... */</p>
          </div>
          <div>
            <h4>Feedback</h4>
            <ul>
              <li>Strengths:
                <ul>
                  {strengths.map((item, i) => (
                    <li key={"str-" + i} style={{ color: "green" }}>{item}</li>
                  ))}
                </ul>
              </li>
              <li>Weaknesses:
                <ul>
                  {weaknesses.map((item, i) => (
                    <li key={"weak-" + i} style={{ color: "red" }}>{item}</li>
                  ))}
                </ul>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Recommendations section */}
      <div style={{
        background: "#fff",
        padding: "2rem",
        borderRadius: "8px",
        display: "flex",
        gap: "2rem"
      }}>
        {/* Left: Course and Mentor recommendations */}
        <div style={{ flex: 2 }}>
          <h3>Recommendations</h3>
          <div>
            <strong>Courses</strong>
            <ul>
              {courses.map(course => (
                <li key={course.id}>{course.name} <button>Apply</button></li>
              ))}
              <li><a href="#">View all</a></li>
            </ul>
          </div>
          <div style={{ marginTop: 16 }}>
            <strong>Mentors</strong>
            <ul>
              {mentors.map(mentor => (
                <li key={mentor.id}>{mentor.name} <button>Apply</button></li>
              ))}
              <li><a href="#">View all</a></li>
            </ul>
          </div>
        </div>

        {/* Center: Chatbot */}
        <div style={{
          background: "#f7f7f7",
          borderRadius: "6px",
          flex: 1.5,
          minHeight: "500px",
          minWidth: "500px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "flex-start",
          padding: "1rem",
          overflowY: "auto"
        }}>
          <h4>CHATBOT</h4>
          <Chatbot />
        </div>

        {/* Right: Career Path */}
        <div style={{
          background: "#f7f7f7",
          borderRadius: "8px",
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minWidth: "300px"
        }}>
          <h4>Career Path</h4>
          <ul>
            {careerPath.map((step, i) => (
              <li key={"cp-" + i}>{step}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
