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
  const [showAllCourses, setShowAllCourses] = useState(false);
  const [showAllMentors, setShowAllMentors] = useState(false);
  const visibleCourses = showAllCourses ? courses : courses.slice(0, 3);
  const visibleMentors = showAllMentors ? mentors : mentors.slice(0, 3);

  // Helper to convert score -> percent (assume 0–20 scale; tweak if different)
  const toPct = (v) => {
    const MAX = 20;
    const n = Number(v) || 0;
    return Math.max(0, Math.min(100, Math.round((n / MAX) * 100)));
  };

   // 🔗 NEW: receive payload from Chatbot and update Stats state
  const handleChatServerPayload = (payload) => {
    if (!payload) return;
    const { skillScore: s, careerPath: cp, courses: cs, mentors: ms } = payload;

    if (s && typeof s === "object") {
      // merge scores (keeps existing keys unless overwritten by backend)
      setSkillScore((prev) => ({ ...prev, ...s }));
    }
    if (Array.isArray(cp)) setCareerPath(cp);
    if (Array.isArray(cs)) setCourses(cs);
    if (Array.isArray(ms)) setMentors(ms);
  };

  useEffect(() => {
    if (!user?.token) return;
    let alive = true;

    (async () => {
      try {
        setLoading(true);
        setErr(null);
        const res = await api.get("/stats", {
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
    <SidebarNav>
      <div style={{ width: "100%", padding: "2rem", boxSizing: "border-box" }}>
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
<div className="stats-main">
  {/* Left: Recommendations */}
  <div className="panel panel--list">
    <h3>Recommendations</h3>

    <div>
      <strong>Courses</strong>
      {loading && <p>Loading…</p>}
      {err && <p style={{ color: "red" }}>{err}</p>}
      <ul>
        {visibleCourses.map((course) => (
          <li key={course.id ?? course.name}>
            {course.name ?? String(course)}
          </li>
        ))}
      </ul>

      {courses.length > 3 && (
        <button
          type="button"
          className="view-toggle"
          onClick={() => setShowAllCourses((v) => !v)}
          aria-expanded={showAllCourses}
        >
          {showAllCourses ? "View less" : `View more (${courses.length - 3} more)`}
        </button>
      )}
    </div>

    <div style={{ marginTop: 16 }}>
      <strong>Mentors</strong>
      <ul>
        {visibleMentors.map((m) => (
          <li key={m.id ?? m.name}>{m.name ?? String(m)}</li>
        ))}
      </ul>

      {mentors.length > 3 && (
        <button
          type="button"
          className="view-toggle"
          onClick={() => setShowAllMentors((v) => !v)}
          aria-expanded={showAllMentors}
        >
          {showAllMentors ? "View less" : `View more (${mentors.length - 3} more)`}
        </button>
      )}
    </div>
  </div>

  {/* Middle: Chatbot (centered) */}
  <div className="panel panel--chatbot">
    <h4>AURA CAREER COACH</h4>
    <Chatbot onServerPayload={handleChatServerPayload} />
  </div>

  {/* Right: Career Path */}
  <div className="panel panel--career">
    <h4>Career Path</h4>
    <ul>
      {careerPath.map((step, i) => (
        <li key={`cp-${i}`}>{step}</li>
      ))}
    </ul>
  </div>
</div>
    </div>
  </SidebarNav>
  );
}
