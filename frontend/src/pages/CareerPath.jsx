import React from "react";
import SidebarNav from "../components/sidenav";
import "./careerPath.css";
import api from "../axios";   

class CareerPath extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      editing: false,
      jobTitles:["Junior Developer","Software Developer","Senior Developer","Engineering Manager","CTO"]
      
    };
  }
  
  async componentDidMount() {
  var self = this;
  try {
    var response = await api.get("http://localhost:5000/career-path");
    var careerPath = response.data.careerPath;
    self.setState({ jobTitles: careerPath });
  } catch (error) {
    console.error("Error fetching career path:", error);
  }
}

  toggleEdit() {
    this.setState({ editing: true });
  }

  cancelEdit() {
    this.setState({ editing: false });
  }

  handleInputChange(event, index) {
    var updatedTitles = [...this.state.jobTitles];
    updatedTitles[index] = event.target.value;

    this.setState({
      jobTitles: updatedTitles
    });
  }

  handleSave() {
    // ============================
    // ✅ INSERT BACKEND CALL HERE
    // Example: Send updated jobTitles to backend (POST)
    // ============================

    /*
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:5000/setCareerPath/USER_ID", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(this.state.jobTitles));
    */

    this.setState({ editing: false });
  }
  //We shouldnt need this ah

  renderJobField(label, index, className) {
    var editing = this.state.editing;
    var jobTitle = this.state.jobTitles[index];

    return (
      <div className={className}>
        <h3>{label}</h3>
        <div className="job-title">
          {editing ? (
            <input
              type="text"
              value={jobTitle}
              onChange={(event) => this.handleInputChange(event, index)}
            />
          ) : (
            <p>{jobTitle}</p>
          )}
        </div>
      </div>
    );
  }

  render() {
    return (
    <div className="career-path-container">
      <SidebarNav />
      <div className="career-path-content">
        <h2>Your Career Path</h2>
        <p>Here’s how you can progress through your career:</p>

        <div className="career-path-chain">
          {this.state.jobTitles.map((job, index) => {
            const label = `Position ${index + 1}`;

            let className = "career-path-item intermediate-job";
            if (index === 0) className = "career-path-item current-job";
            else if (index === this.state.jobTitles.length - 1) className = "career-path-item final-job";

            return (
              <div key={index} className={className}>
                <h3>{label}</h3>
                <div className="job-title">
                  {this.state.editing ? (
                    <input
                      type="text"
                      value={job}
                      onChange={(event) => this.handleInputChange(event, index)}
                    />
                  ) : (
                    <p>{job}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {!this.state.editing && (
          <button className="edit-button" onClick={this.toggleEdit.bind(this)}>
            Edit Job Titles
          </button>
        )}

        {this.state.editing && (
          <div className="save-cancel-container">
            <button className="save-button" onClick={this.handleSave.bind(this)}>
              Save Changes
            </button>
            <button className="cancel-button" onClick={this.cancelEdit.bind(this)}>
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
  }
}

export default CareerPath;
