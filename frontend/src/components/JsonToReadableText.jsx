import React from 'react';
import './JsonToReadableText.css';

const JsonToReadableText = ({ data }) => {
  const renderEntry = (entry) => {
    const lines = [];

    // Support multiple keys that may represent same concept
    const headerKeys = ['institution', 'company', 'organization', 'university'];
    const roleKeys = ['degree', 'title', 'role', 'module'];

    const headerLineParts = [];
    headerKeys.forEach((key) => {
      if (entry[key]) headerLineParts.push(entry[key]);
    });
    if (entry.location) headerLineParts.push(entry.location);

    // For your data, add dates if present in header line parts or alone
    if (entry.dates && !headerLineParts.includes(entry.dates)) {
      lines.push(`Dates: ${entry.dates}`);
    }

    if (headerLineParts.length > 0) lines.unshift(headerLineParts.join(', '));

    roleKeys.forEach((key) => {
      if (entry[key]) lines.push(entry[key]);
    });

    // Safely handle details field
    if (Array.isArray(entry.details)) {
      lines.push('Details:');
      entry.details.forEach((d) => lines.push(` - ${d}`));
    } else if (typeof entry.details === 'string') {
      lines.push(`Details: ${entry.details}`);
    }

    // Safely handle description field
    if (Array.isArray(entry.description)) {
      lines.push('Description:');
      entry.description.forEach((desc) => lines.push(` - ${desc}`));
    } else if (typeof entry.description === 'string') {
      lines.push(`Description: ${entry.description}`);
    }

    return (
      <div className="entry" key={headerLineParts.join('-')}>
        {lines.map((line, index) =>
          line.startsWith(' - ') ? (
            <li key={index} className="entry-list-item">{line.slice(3)}</li>
          ) : (
            <p key={index} className="entry-paragraph">{line}</p>
          )
        )}
      </div>
    );
  };

  return (
    <div className="json-container">
      {data.map((section, idx) => (
        <section className="section" key={idx}>
          <h2 className="section-header">{section.header}</h2>
          {Array.isArray(section.content) ? (
            section.content.every(item => typeof item === 'string') ? (
              // Handle comma-separated strings in skills/hobbies arrays
              <ul className="simple-list">
                {section.content.map((item, i) => {
                  // Split by commas if string contains commas
                  if (item.includes(',')) {
                    return item.split(',').map((part, idx2) => (
                      <li key={`${i}-${idx2}`}>{part.trim()}</li>
                    ));
                  }
                  return <li key={i}>{item}</li>;
                })}
              </ul>
            ) : (
              section.content.map((entry, i) => (
                <div className="entry-container" key={i}>
                  {renderEntry(entry)}
                </div>
              ))
            )
          ) : (
            <p>{section.content}</p>
          )}
        </section>
      ))}
    </div>
  );
};

export default JsonToReadableText;
