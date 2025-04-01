import React, { useState } from 'react';
import './category-page.css';

const AttackVectors = () => {
  // State to store threat data
  const [threatData, setThreatData] = useState([
    { attackVector: 'Phishing Email' },
    { attackVector: 'Ransomware' },
    { attackVector: 'Malware' },
    { attackVector: 'denial-of-service (DoS)' },
    { attackVector: 'Supply Chain Attack' },
    { attackVector: 'Zero-day Exploits' },
    { attackVector: 'SQL Injection' },
  ]);

  const [loadingStates, setLoadingStates] = useState({});
  const [error, setError] = useState(null);

  // Function to fetch data and update the table
  const fetchThreatData = async (attackVector) => {
  setLoadingStates((prevState) => ({
    ...prevState,
    [attackVector]: true, // Set loading for this specific attack vector
  }));
  setError(null);

    try {
      const response = await fetch(`https://ulaq2p5pomaufimwt3pfxr3tpa0szfux.lambda-url.us-east-1.on.aws/update?attackVector=${encodeURIComponent(attackVector)}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      const data = await response.json();
      console.log('Data for attackvector:', data);

      // Update threatData with the new information
      setThreatData((prevData) =>
        prevData.map((threat) =>
          threat.attackVector === attackVector
            ? { ...threat, ...data } // Merge fetched data into existing row
            : threat
        )
      );
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(`Error fetching data: ${err.message}`);
    } finally {
      setLoadingStates((prevState) => ({
        ...prevState,
        [attackVector]: false, // Reset loading for this specific attack vector
      }));
    }
  };

  return (
    <div id="dashboard" className="dashboard">
         <div className="row">
        <div className="col-sm-12">
          <h1 className="main-heading">Attack Vector Monitoring</h1>
          {error && <p className="error-message">{error}</p>}
        </div>
      </div>

      <div className="row mt-5">
        <div className="col-sm-12">
          <h2 className="table-title">Cyber Threat Intelligence</h2>
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Attack Vector</th>
                <th>TTPs (Tactics, Techniques, Procedures)</th>
                <th>Indicators of Compromise (IoCs)</th>
                <th>Common Vulnerabilities and Exposures (CVEs)</th>
                <th>Attack Timelines</th>
                <th>Incident Reports & Case Studies</th>
                <th>Threat Intelligence Feeds</th>
                <th>Change State</th>
              </tr>
            </thead>
            <tbody>
              {threatData.map((threat, index) => (
                <tr key={index}>
                  <td>{threat.attackVector}</td>
                  <td>{threat.ttps }</td>
                  <td>{threat.iocs }</td>
                  <td>{threat.cve }</td>
                  <td>{threat.attackTimeline}</td>
                  <td>{threat.incidentReport}</td>
                  <td>{threat.threatFeed}</td>
                  <td>
                  <button
                      className="btn btn-primary"
                      onClick={() => fetchThreatData(threat.attackVector)}
                      disabled={loadingStates[threat.attackVector]} 
                    >
                      {loadingStates[threat.attackVector] ? 'Updating...' : 'Update'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AttackVectors;
