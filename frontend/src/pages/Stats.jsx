import React, { useEffect, useState } from "react";
import Chatbot from "../components/Chatbot";
import SidebarNav from "../components/sidenav";
import api from "../axios";               // your axios instance
import { useAuth } from "../AuthContext"; // provides { user, ... }  :contentReference[oaicite:0]{index=0}
import "./stats.css";

export default function Stats() {
  const { user } = useAuth(); // expects user.token for auth  :contentReference[oaicite:1]{index=1}

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  const [courses, setCourses] = useState([]);
  const [mentors, setMentors] = useState([]);
  const [careerPath, setCareerPath] = useState([]);
  const [skillScore, setSkillScore] = useState({});

  // Helper to convert score -> percent (assume 0–20 scale; tweak if different)
  const toPct = (v) => {
    const MAX = 20;
    const n = Number(v) || 0;
    return Math.max(0, Math.min(100, Math.round((n / MAX) * 100)));
  };

  useEffect(() => {
    if (!user?.token) return;
    let alive = true;

    (async () => {
      try {
        setLoading(true);
        setErr(null);
        const res = await api.get("/stats", {
          headers: { Authorization: `Bearer ${user.token}` },
          // params: { uid: user.uid }, // only if you still use ?uid=...
        });
        if (!alive) return;
        const { courses = [], mentors = [], careerPath = [], skillScore = {} } = res.data || {};
        setCourses(courses);
        setMentors(mentors);
        setCareerPath(careerPath);
        setSkillScore(skillScore);
      } catch (e) {
        if (alive) setErr("Failed to load stats");
        console.error(e);
      } finally {
        if (alive) setLoading(false);
      }
    })();

    return () => { alive = false; };
  }, [user?.token]);

  return (
    <div style={{ width: "100%", padding: "2rem", boxSizing: "border-box" }}>
      <SidebarNav />

      {/* 🔝 Top skills bar */}
      <div className="stats-topbar">
        {Object.keys(skillScore).length === 0 && !loading && (
          <span className="muted">No skill scores yet</span>
        )}
        {Object.entries(skillScore).map(([name, value]) => (
          <div className="skill-chip" key={name} title={`${name}: ${value}`}>
            <div className="skill-chip__row">
              <span className="skill-name">{name}</span>
              <span className="skill-value">{Number(value) || 0}</span>
            </div>
            <div className="skill-bar">
              <div className="skill-fill" style={{ width: `${toPct(value)}%` }} />
            </div>
          </div>
        ))}
      </div>

      {/* Main section */}
      <div
        style={{
          background: "#fff",
          padding: "2rem",
          borderRadius: "8px",
          display: "flex",
          gap: "2rem",
          marginTop: "1rem",
        }}
      >
        {/* Left: Recommendations */}
        <div style={{ flex: 2 }}>
          <h3>Recommendations</h3>

          <div>
            <strong>Courses</strong>
            {loading && <p>Loading…</p>}
            {err && <p style={{ color: "red" }}>{err}</p>}
            <ul>
              {courses.map((course) => (
                <li key={course.id ?? course.name}>
                  {course.name ?? String(course)}
                </li>
              ))}
              <li><a href="#">View all</a></li>
            </ul>
          </div>

          <div style={{ marginTop: 16 }}>
            <strong>Mentors</strong>
            <ul>
              {mentors.map((m) => (
                <li key={m.id ?? m.name}>{m.name ?? String(m)}</li>
              ))}
              <li><a href="#">View all</a></li>
            </ul>
          </div>
        </div>

        {/* Middle: Chatbot */}
        <div
          style={{
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
            overflowY: "auto",
          }}
        >
          <h4>CHATBOT</h4>
          <Chatbot />
        </div>

        {/* Right: Career Path */}
        <div
          style={{
            background: "#f7f7f7",
            borderRadius: "8px",
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minWidth: "300px",
            padding: "1rem",
          }}
        >
          <h4>Career Path</h4>
          <ul>
            {careerPath.map((step, i) => (
              <li key={`cp-${i}`}>{step}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
