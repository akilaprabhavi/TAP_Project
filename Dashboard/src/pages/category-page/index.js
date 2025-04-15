import React, { useEffect, useState } from 'react';
import './category-page.css';

const AttackVectors = () => {
  const [threatData, setThreatData] = useState([]);
  const [error, setError] = useState(null);
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    const fetchAllThreatData = async () => {
      try {
        const res = await fetch('https://ulaq2p5pomaufimwt3pfxr3tpa0szfux.lambda-url.us-east-1.on.aws/all-threats');
        if (!res.ok) throw new Error('Failed to fetch threat data');
        const data = await res.json();  
   
        setThreatData(data);
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setInitialLoading(false);
      }
    };
  
    fetchAllThreatData();
  }, []);
  
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
            <p>Loading all threat data...</p>
          ) : (
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
                </tr>
              </thead>
              <tbody>
                {threatData.map((threat, index) => (
                  <tr key={index}>                
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
