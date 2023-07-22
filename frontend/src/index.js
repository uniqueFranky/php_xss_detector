import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import React, { Component } from 'react';
import axios from 'axios';

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            code: '',
            pdfUrl: '',
            rank: '',
            attn: '',
            path: '',
            positive: '',
            negative: '',
            input: false
        };
    }

    handleSubmit = async () => {
        try {
            const { code, rank } = this.state;

            const response1 = await axios.post(
                'http://localhost:9999/getASTGraph/' + rank,
                code,
                { responseType: 'blob' }
            );
            const pdfUrl = URL.createObjectURL(response1.data);
            this.setState({ pdfUrl });

            const response2 = await axios.post(
                'http://localhost:9999/getAttnAndPath/' + rank,
                code,
                { responseType: 'application/json' }
            );
            const [attn, path, negative, positive] = JSON.parse(response2.data);
            this.setState({
                attn,
                path,
                negative,
                positive,
                input: true
            });
        } catch (error) {
            console.log('Error:', error);
        }
    };

    renderInputForm() {
        const { code, rank } = this.state;

        return (
            <div>
                <div>
                    <p>code to be parsed:</p>
                    <textarea
                        rows={5}
                        cols={80}
                        value={code}
                        onChange={(e) => this.setState({ code: e.target.value })}
                    />
                    <p>the rank of the AST path:</p>
                    <textarea
                        rows={1}
                        cols={2}
                        value={rank}
                        onChange={(e) => this.setState({ rank: e.target.value })}
                    />
                    <br />
                    <button onClick={this.handleSubmit}>submit</button>
                </div>
            </div>
        );
    }

    renderOutput() {
        const { attn, path, negative, positive, pdfUrl } = this.state;

        return (
            <div>
                <p>Attention Weight: {attn}</p>
                <p>Path: {path}</p>
                <p>probability of safe: {negative}, unsafe: {positive}</p>
                {pdfUrl && <embed src={pdfUrl} type="application/pdf" width="100%" height="400px" />}
            </div>
        );
    }

    render() {
        const { input } = this.state;

        return (
            <div>
                {input ? this.renderOutput() : this.renderInputForm()}
            </div>
        );
    }
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
