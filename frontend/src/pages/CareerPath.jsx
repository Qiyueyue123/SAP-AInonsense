import { useState } from "react";
import SidebarNav from "../components/sidenav";
import "./careerPath.css"; // Import the custom CSS file for the career path page

export default function CareerPath() {
  // State for the job titles
  const [jobTitles, setJobTitles] = useState({
    current: "Software Developer",
    intermediate1: "Senior Software Developer",
    intermediate2: "Lead Developer",
    intermediate3: "Engineering Manager",
    final: "CTO (Chief Technology Officer)",
  });

  // State for editing
  const [editing, setEditing] = useState(false); // Toggle edit mode

  const handleJobChange = (e, jobPosition) => {
    setJobTitles((prevTitles) => ({
      ...prevTitles,
      [jobPosition]: e.target.value,
    }));
  };

  const handleSave = () => {
    // Logic to save all changes (for now, we are simply saving in the state)
    setEditing(false); // Exit edit mode
  };

  return (
    <div className="career-path-container">
      <SidebarNav />
      <div className="career-path-content">
        <h2>Your Career Path</h2>
        <p>Here’s how you can progress through your career:</p>

        {/* Career Path Chain */}
        <div className="career-path-chain">
          {/* Current Job */}
          <div className="career-path-item current-job">
            <h3>Current Position</h3>
            <div className="job-title">
              {editing ? (
                <input
                  type="text"
                  value={jobTitles.current}
                  onChange={(e) => handleJobChange(e, "current")}
                />
              ) : (
                <p>{jobTitles.current}</p>
              )}
            </div>
          </div>

          {/* Intermediate Jobs */}
          <div className="career-path-item intermediate-job">
            <h3>Intermediate Position 1</h3>
            <div className="job-title">
              {editing ? (
                <input
                  type="text"
                  value={jobTitles.intermediate1}
                  onChange={(e) => handleJobChange(e, "intermediate1")}
                />
              ) : (
                <p>{jobTitles.intermediate1}</p>
              )}
            </div>
          </div>

          <div className="career-path-item intermediate-job">
            <h3>Intermediate Position 2</h3>
            <div className="job-title">
              {editing ? (
                <input
                  type="text"
                  value={jobTitles.intermediate2}
                  onChange={(e) => handleJobChange(e, "intermediate2")}
                />
              ) : (
                <p>{jobTitles.intermediate2}</p>
              )}
            </div>
          </div>

          <div className="career-path-item intermediate-job">
            <h3>Intermediate Position 3</h3>
            <div className="job-title">
              {editing ? (
                <input
                  type="text"
                  value={jobTitles.intermediate3}
                  onChange={(e) => handleJobChange(e, "intermediate3")}
                />
              ) : (
                <p>{jobTitles.intermediate3}</p>
              )}
            </div>
          </div>

          {/* Final Job */}
          <div className="career-path-item final-job">
            <h3>Final Goal Position</h3>
            <div className="job-title">
              {editing ? (
                <input
                  type="text"
                  value={jobTitles.final}
                  onChange={(e) => handleJobChange(e, "final")}
                />
              ) : (
                <p>{jobTitles.final}</p>
              )}
            </div>
          </div>
        </div>

        {/* Edit Button */}
        {!editing && (
          <button className="edit-button" onClick={() => setEditing(true)}>
            Edit Job Titles
          </button>
        )}

        {/* Save Changes Button */}
        {editing && (
          <div className="save-cancel-container">
            <button className="save-button" onClick={handleSave}>
              Save Changes
            </button>
            <button
              className="cancel-button"
              onClick={() => setEditing(false)}
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
