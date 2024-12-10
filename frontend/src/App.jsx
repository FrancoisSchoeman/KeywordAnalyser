import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [urls, setUrls] = useState('');
  const [keywords, setKeywords] = useState('');
  const [message, setMessage] = useState('');
  const [csvLink, setCsvLink] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('Processing...');
    setCsvLink('');

    try {
      const response = await axios.post('http://127.0.0.1:5000/generate-seo', {
        urls: urls.split(','),
        keywords: keywords.split(','),
      });
      setMessage(response.data.message);
      setCsvLink(response.data.csv);
    } catch (error) {
      setMessage(
        'Error: ' +
          (error.response?.data?.error || 'An unknown error occurred.')
      );
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>SEO Analysis Tool</h1>
        <p>Optimize your pages for maximum visibility with ease.</p>
      </header>
      <div className="container">
        <div className="form-card">
          <h2>Enter Details</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="urls">Enter URLs (comma-separated):</label>
              <input
                type="text"
                id="urls"
                placeholder="https://example.com, https://example2.com"
                value={urls}
                onChange={(e) => setUrls(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="keywords">
                Enter Keywords (comma-separated):
              </label>
              <input
                type="text"
                id="keywords"
                placeholder="keyword1, keyword2, keyword3"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-submit">
              Analyze
            </button>
          </form>
        </div>
        <div className="results-card">
          {message && <p className="message">{message}</p>}
          {csvLink && (
            <a
              href={`http://127.0.0.1:5000/${csvLink}`}
              className="btn-download"
              download
            >
              Download CSV
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
