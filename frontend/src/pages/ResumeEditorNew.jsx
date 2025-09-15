import { useEffect, useState } from "react";
import Sidenav from "../components/sidenav";
import "./ResumeEditor.css";
import api from '../axios.js';
import { useAuth } from "../AuthContext"; // adjust path if needed


function ResumeViewer() {
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useAuth();              // expects { token, ...userData }
  const { token, uid } = user; // Extract the token and uid from user object

  useEffect(() => {
    const fetchResume = async () => {
      try {
        console.log(uid)
        const response = await api.get("/resume-editor", {
        params: { uid }});
        console.log(response.data)
        setResume(response.data); // store the JSON resume
        console.log("Resume fetched:", response.data);
      } catch (err) {
        console.error("Failed to fetch resume:", err);
        setError("Failed to fetch resume. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchResume();
  }, []);

  if (loading) return <p>Loading resume...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <Sidenav/>
      <h2>Resume Data</h2>
      <pre>{JSON.stringify(resume, null, 2)}</pre>
    </div>
  );
}

export default ResumeViewer;
