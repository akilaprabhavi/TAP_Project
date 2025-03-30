import React, { useState } from 'react';
import './category-page.css';

const AttackVectors = () => {

  /*Sample data for cyber threat intelligence*/
  const threatData = [

    { attackvector: 'Phishing'},
    { attackvector: 'Ransomware'},
    { attackvector: 'malware',},
    { attackvector: 'denial-of-service (DoS)'},
    { attackvector: 'supply chain attacks'},
    { attackvector: 'zero-day exploits'},
    { attackvector: 'SQL injection'},
  ];

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Function to fetch data from backend API
  const fetchThreatData = async (attackVector) => {
    setLoading(true);
    setError(null); // Reset any previous errors

    try {
      // Send GET request with the attackvector as a query parameter
      const response = await fetch(`https://ulaq2p5pomaufimwt3pfxr3tpa0szfux.lambda-url.us-east-1.on.aws/update?attackvector=${encodeURIComponent(AttackVectors)}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Data for attackvector:', data);  // You can handle this data as needed
        alert(`Data fetched for attackvector: ${attackVector}`);
      } else {
        setError('Error fetching data');
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Error fetching data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="dashboard" className="dashboard">
      <div className='browse db'>
        <div className='row'>
          <div className='col-9'>
            <div className="db-header">
              <p className="custom-header db m-0">Global Trade Explorer</p>
              <p className="fst-normal db m-0">Visualize flows of trade around the world</p>
            </div>
          </div>
          <div className='col-3'>
            <button className='custom-button db'>Browse</button>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-sm-12">
          <h1 className="main-heading">Attack Vector Monitoring</h1>
        </div>
      </div>
      {/* <div className="row mt-4 data-filter p-0 m-0">
      <div className="col-sm-3 data-filtersub">
        <p className="px-3 m-0"><b>Data Filters</b></p>
      </div>
      <div className="col-sm-3 data-filtersub">
        <p className="px-3 m-0"><b>Data Filters</b></p>
      </div>
      <div className="col-sm-3 data-filtersub">
        <p className="px-3 m-0"><b>Data Filters</b></p>
      </div>
      <div className="col-sm-3 data-filtersub">
        <p className="px-3 m-0"><b>Data Filters</b></p>
      </div>
    </div> */}


      {/* Cyber Threat Data Table */}
      <div className="row mt-5">
        <div className="col-sm-12">
          <h2 className="table-title">Cyber Threat Intelligence</h2>
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Attack Vactor</th>
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
                  <td>{threat.attackvector}</td>
                  <td>{threat.ttps}</td>
                  <td>{threat.iocs}</td>
                  <td>{threat.cves}</td>
                  <td>{threat.attacktimelines}</td>
                  <td>{threat.IncReports}</td>
                  <td>{threat.feed}</td>
                  <td><button className="btn btn-primary">Update</button></td>
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
