import React from 'react';
import './dashboard.css';
import ChatInterface from '../../components/Layout/ChatInterface';

const dashboard = () => { 
  return (
    <div id="dashboard" className="dashboard">
      <div className="row">
        <div className="col-sm-12">
          <h1 className="main-heading">Dashboard</h1>
        </div>
        <div className="chat-section">
        <h2>Cyber Threat Chat Assistant</h2>
          <ChatInterface />
        </div>
      </div>
      
      {/* Cyber Threat Data Table */}
      {/* <div className="row mt-5">
        <div className="col-sm-12">
          <h2 className="table-title">Cyber Threat Intelligence</h2>
          <table className="table table-striped">
            <thead>
              <tr>
                <th>#</th>
                <th>Attack Type</th>
                <th>TTPs (Techniques, Tactics, and Procedures)</th>
                <th>Indicators of Compromise (IoCs)</th>
                <th>Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {threatData.map((threat) => (
                <tr key={threat.id}>
                  <td>{threat.id}</td>
                  <td>{threat.attackType}</td>
                  <td>{threat.ttps}</td>
                  <td>{threat.iocs}</td>
                  <td className={`risk-${threat.riskLevel.toLowerCase()}`}>{threat.riskLevel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div> */}
      


    </div>
    
   
  );
};

export default dashboard;
