import React, { useEffect, useState } from 'react';
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import './DailyUpdates-page.css';

const DailyUpdates = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('https://ulaq2p5pomaufimwt3pfxr3tpa0szfux.lambda-url.us-east-1.on.aws/get-prompts-results')
      .then(response => response.json())
      .then(result => {        
        if (result.error) {
          throw new Error(result.error);
        }
        setData(result);
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  }, []);

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
          <h1 className="main-heading">Your daily updates</h1>
        </div>
      </div>

      <div className="row mt-5">
        <div className="col-sm-12">
          <h2 className="table-title">Cyber Threat Intelligence</h2>
          {loading ? (
            <p>Loading data...</p>
          ) : error ? (
            <p className="error">Error: {error}</p>
          ) : (
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Prompt</th>
                  <th>Result</th>
                  <th>Last updated Time</th>                
                </tr>
              </thead>
              <tbody>
                {data.length === 0 ? (
                  <tr><td colSpan="3">No data available</td></tr>
                ) : (
                  data.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.prompt}</td>
                      <td>
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{item.result}</ReactMarkdown>
                      </td>
                      <td>{item.last_updated ? new Date(item.last_updated).toLocaleString('en-US', { timeZone: 'Australia/Sydney' }) : 'N/A'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default DailyUpdates;
