import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import React, { Component } from 'react';
import axios from 'axios';
import {Button} from "react-bootstrap";
import { ColorRing } from 'react-loader-spinner';


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
            input: false,
            loading: false
        };
    }

    handleSubmit = async () => {
        try {
            const { code, rank } = this.state;
            this.setState({
                loading: true
            });
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
            alert('Something went wrong, please try again!');
            this.setState({
                loading: false
            })
        }
        this.setState({
            loading: false
        })
    };

    renderInputForm() {
        const { code, rank } = this.state;

        return (
            <div>
                <div className={'selector'}>
                    <h1>Code Guard</h1>
                    <p>Enter your code to be analysed:</p>
                    <textarea
                        className={'field'}
                        rows={30}
                        cols={80}
                        value={code}
                        onChange={(e) => this.setState({ code: e.target.value })}
                    />
                    <p></p>
                    the rank of the AST path:
                    <textarea
                        rows={1}
                        cols={2}
                        value={rank}
                        onChange={(e) => this.setState({ rank: e.target.value })}
                    />
                    <br />
                    <br />
                    <Button variant="contained" className={'button'} onClick={() => {
                        this.handleSubmit()
                    }}>
                        <div>
                            Analyse!
                        </div>
                    </Button>
                    <br />
                    <br />
                    <ColorRing
                        visible={this.state.loading}
                        height="80"
                        width="80"
                        ariaLabel="blocks-loading"
                        wrapperStyle={{}}
                        wrapperClass="blocks-wrapper"
                        colors={['#e15b64', '#f47e60', '#f8b26a', '#abbd81', '#849b87']}
                    />
                </div>
            </div>


        );
    }

    renderOutput() {
        const { attn, path, negative, positive, pdfUrl } = this.state;
        var style, hint;
        console.log(negative, positive)
        if(Number(negative) < Number(positive)) {
            style = {
                color: 'red'
            };
            hint = 'Oops, you are DANGEROUS';
        } else {
            style = {
                color: 'green'
            };
            hint = 'Congratulations! You are SAFE';
        }
        return (
            <div>
                <h1 style={style}>{hint}</h1>
                <p>Attention Weight: {attn}</p>
                <p>probability of safe: {negative}, unsafe: {positive}</p>
                {pdfUrl && <embed src={pdfUrl} type="application/pdf" width="100%" height="550px" />}
                <Button variant="contained" className={'button'} onClick={() => {
                    this.setState({
                        input: false
                    });
                }}>
                    <div>
                        Go Back
                    </div>
                </Button>

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
