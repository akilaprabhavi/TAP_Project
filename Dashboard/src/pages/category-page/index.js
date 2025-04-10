import React, { useEffect, useState } from 'react';
import './category-page.css';

const AttackVectors = () => {
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
  const [initialLoading, setInitialLoading] = useState(true);

  const fetchThreatData = async (attackVector) => {
    setLoadingStates((prevState) => ({
      ...prevState,
      [attackVector]: true,
    }));
    setError(null);

    try {
      const response = await fetch(
        `https://ulaq2p5pomaufimwt3pfxr3tpa0szfux.lambda-url.us-east-1.on.aws/update?attackVector=${encodeURIComponent(
          attackVector
        )}`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      const data = await response.json();

      setThreatData((prevData) =>
        prevData.map((threat) =>
          threat.attackVector === attackVector
            ? { ...threat, ...data }
            : threat
        )
      );
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(`Error fetching data: ${err.message}`);
    } finally {
      setLoadingStates((prevState) => ({
        ...prevState,
        [attackVector]: false,
      }));
    }
  };

  // Fetch all data on component mount
  useEffect(() => {
    const fetchAllThreatData = async () => {
      for (const threat of threatData) {
        await fetchThreatData(threat.attackVector);
      }
      setInitialLoading(false);
    };

    fetchAllThreatData();
  }, []); // Empty dependency array = runs once on mount

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
          {initialLoading ? (
            <p>Loading threat data...</p>
          ) : (
            <table className="table table-striped">
              <thead>
                <tr>
                  {/* <th>Change State</th> */}
                  <th>Attack Vector</th>
                  <th>TTPs</th>
                  <th>IoCs</th>
                  <th>CVEs</th>
                  <th>Attack Timelines</th>
                  <th>Incident Reports</th>
                  <th>Threat Feeds</th>
                </tr>
              </thead>
              <tbody>
                {threatData.map((threat, index) => (
                  <tr key={index}>
                    {/* <td>
                      <button
                        className="btn btn-primary"
                        disabled
                      >
                        Update
                      </button>
                    </td> */}
                    <td>{threat.attackVector}</td>
                    <td>{threat.ttps || '-'}</td>
                    <td>{threat.iocs || '-'}</td>
                    <td>{threat.cve || '-'}</td>
                    <td>{threat.attackTimeline || '-'}</td>
                    <td>{threat.incidentReport || '-'}</td>
                    <td>{threat.threatFeed || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default AttackVectors;
