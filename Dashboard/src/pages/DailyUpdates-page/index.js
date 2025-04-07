import React, { useEffect, useState } from 'react';
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import './DailyUpdates-page.css';


const DailyUpdates = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [input, setInput] = useState("");

  //Fetching prompts and results from aws lambda
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

  const handleAddMessage = async () => {
    if (!input.trim()) return;

    try {
      // AWS-hosted Flask endpoint here for saving to S3
      const response = await fetch("https://ulaq2p5pomaufimwt3pfxr3tpa0szfux.lambda-url.us-east-1.on.aws/save-to-s3", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input }),
      });

      const data = await response.json();
      if (response.ok) {
        alert(`Message saved to S3! File. ${data.file_name}`);

        setData(prevData => [
        ...prevData,
        { prompt: input, result: "Processing...", last_updated: new Date().toISOString() }
      ]);

      setInput("");  // Clear input field
      } else {
        alert("Error saving message: " + data.error);
      }
    } catch (error) {
      console.error("Error saving message:", error);
      alert("Error saving message.");
    }
  };

  return (
    <div id="dashboard" className="dashboard">      
      <div className="row">
        <div className="col-sm-12">
          <h1 className="main-heading">Your daily updates</h1>
        </div>
      </div>

      <div className="row mt-5">
        <div className="col-sm-12">
          <h2 className="table-title">Cyber Threat Intelligence</h2>
            <div className="chat-container">
              <div className="input-area">
                <input
                  type="text"
                  placeholder="Add prompts to daily execution list.."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}                 
                />                
                <button onClick={handleAddMessage}>Add</button>
              </div>
              {/* <div></div>
              <div className="time-selector">
                <label> Set the time to execute the prompts   : </label>
                <input 
                  type="time" 
                  value={selectedTime} 
                  onChange={(e) => setSelectedTime(e.target.value)} 
                />
                <button onClick={handleSaveTime}>Save Time</button>
              </div> */}
            </div>            
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
                      <td>{item.last_updated ? new Date(item.last_updated).toLocaleString('en-AU') : 'N/A'}</td>
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
