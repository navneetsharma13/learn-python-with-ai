import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [model, setModel] = useState('gpt');
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    setLoading(true);
    try {
      const res = await axios.post('/chat', {
        model,
        message,
        context: []
      });
      setResponse(res.data.response);
    } catch (err) {
      setResponse('Error: ' + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>AgenticAI-PPL Chat</h1>
      <div style={{ marginBottom: 16 }}>
        <label>Model: </label>
        <select value={model} onChange={e => setModel(e.target.value)}>
          <option value="gpt">GPT</option>
          <option value="claude">Claude</option>
          <option value="gemini">Gemini</option>
        </select>
      </div>
      <textarea
        rows={4}
        style={{ width: '100%', marginBottom: 8 }}
        placeholder="Type your message..."
        value={message}
        onChange={e => setMessage(e.target.value)}
      />
      <br />
      <button onClick={sendMessage} disabled={loading || !message}>
        {loading ? 'Sending...' : 'Send'}
      </button>
      <div style={{ marginTop: 24, background: '#f6f6f6', padding: 16, borderRadius: 8 }}>
        <strong>Response:</strong>
        <div>{response}</div>
      </div>
    </div>
  );
}

export default App;
