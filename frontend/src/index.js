import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [code, setCode] = useState('');
    const [pdfUrl, setPdfUrl] = useState('');
    const [rank, setRank] = useState('')
    const [attn, setAttn] = useState('')
    const [path, setPath] = useState('')
    const [positive, setPositive] = useState('')
    const [negative, setNegative] = useState('')

    const handleSubmit = async () => {
        try {
            console.log(rank)
            console.log(code)

            // 发送 HTTP 请求并接收 PDF 数据
            const response1 = await axios.post('http://localhost:9999/getASTGraph/' + rank, code, { responseType: 'blob' });
            // 创建一个 URL 对象
            const pdfUrl = URL.createObjectURL(response1.data);

            // 更新 PDF URL
            setPdfUrl(pdfUrl);

            const response2 = await axios.post('http://localhost:9999/getAttnAndPath/' + rank, code, { responseType: 'application/json' });
            // 创建一个 URL 对象
            const data = JSON.parse(response2.data)
            setAttn(data[0])
            setPath(data[1])
            setNegative(data[2])
            setPositive(data[3])

        } catch (error) {
            console.log('Error:', error);
        }
    };

    return (
        <div>
            <div>
                <p>code to be parsed:</p>
                <textarea rows={8} cols={80} value={code} onChange={(e) => setCode(e.target.value)} />
                <p>the rank of the AST path:</p>
                <textarea rows={1} cols={2} value={rank} onChange={(e) => setRank(e.target.value)} />
                <br/>
                <button onClick={handleSubmit}>submit</button>
                <p>Attention Weight: {attn}</p>
                <p>Path: {path}</p>
                <p>probability of negative: {negative}, positive: {positive}</p>
            </div>
            {pdfUrl && <embed src={pdfUrl} type="application/pdf" width="100%" height="500px" />}
        </div>
    );
}

export default App;

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
