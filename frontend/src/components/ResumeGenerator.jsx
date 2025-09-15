import React from 'react';
import './ResumeGenerator.css';

const ResumeGenerator = ({ jsonData }) => {
  if (!jsonData || !Array.isArray(jsonData)) {
    return <div className="error">Invalid JSON data provided</div>;
  }

  const renderArrayContent = (items) => {
    if (!Array.isArray(items)) return null;

    return items.map((item, index) => (
      <div key={index} className="content-item">
        {renderObjectContent(item)}
      </div>
    ));
  };

  const renderObjectContent = (obj) => {
    if (typeof obj === 'string') {
      return <div className="text-content">{obj}</div>;
    }
    if (!obj || typeof obj !== 'object') {
      return <div className="text-content">{String(obj)}</div>;
    }
    return (
      <div className="object-content">
        {Object.entries(obj).map(([key, value], index) => (
          <div key={index} className="object-field">
            {renderField(key, value)}
          </div>
        ))}
      </div>
    );
  };

  const renderField = (key, value) => {
    const lowerKey = key.toLowerCase();

    if (Array.isArray(value)) {
      if (value.length === 0) return null;

      if (value.every(item => typeof item === 'string')) {
        return (
          <div className="field-group">
            <span className="field-label">{formatFieldName(key)}:</span>
            <div className="field-content">
              {lowerKey.includes('detail') || lowerKey.includes('responsibilit') || lowerKey.includes('description') ? (
                <ul className="bullet-list">
                  {value.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              ) : (
                <span className="comma-separated">{value.join(', ')}</span>
              )}
            </div>
          </div>
        );
      } else {
        return (
          <div className="field-group">
            <span className="field-label">{formatFieldName(key)}:</span>
            <div className="field-content">
              {renderArrayContent(value)}
            </div>
          </div>
        );
      }
    }

    if (typeof value === 'object' && value !== null) {
      return (
        <div className="field-group">
          <span className="field-label">{formatFieldName(key)}:</span>
          <div className="field-content nested-object">
            {renderObjectContent(value)}
          </div>
        </div>
      );
    }

    if (lowerKey.includes('date')) {
      return (
        <div className="field-group date-field">
          <span className="field-label">{formatFieldName(key)}:</span>
          <span className="field-value date-value">{value}</span>
        </div>
      );
    }

    if (lowerKey.includes('title') || lowerKey.includes('degree') || lowerKey.includes('role') ||
      lowerKey.includes('institution') || lowerKey.includes('company') || lowerKey.includes('organization')) {
      return (
        <div className="field-group title-field">
          <span className="field-label">{formatFieldName(key)}:</span>
          <span className="field-value title-value">{value}</span>
        </div>
      );
    }

    return (
      <div className="field-group">
        <span className="field-label">{formatFieldName(key)}:</span>
        <span className="field-value">{value}</span>
      </div>
    );
  };

  const formatFieldName = (fieldName) => {
    return fieldName
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase())
      .trim();
  };

  const renderSectionContent = (content) => {
    if (Array.isArray(content)) {
      if (content.every(item => typeof item === 'string')) {
        return (
          <ul className="simple-list">
            {content.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        );
      }
      return renderArrayContent(content);
    }
    if (typeof content === 'object' && content !== null) {
      return renderObjectContent(content);
    }
    return <div className="text-content">{String(content)}</div>;
  };

  return (
    <div className="resume-container">
      {jsonData.map((section, index) => (
        <div key={index} className="resume-section">
          <h2 className="section-header">{section.header}</h2>
          <div className="section-content">{renderSectionContent(section.content)}</div>
        </div>
      ))}
    </div>
  );
};

export default ResumeGenerator;
