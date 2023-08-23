# NSE-Option-Chain-Simulator

A web application that displays real-time (random) options contracts. The application provides an interactive user interface to view underlying index prices, and options contracts.

<h2>Introduction</h2> 
The NSE-Option-Chain-Simulator is a web application built using React and Flask. It fetches real-time stock market data and options contracts from an API (built using flask) using Server-Sent Events (SSE) and displays them in an organized manner. Users can select an underlying index, view option prices.
<br>

## :exclamation: Note : 
If the API endpoints or the table do not load immediately, kindly wait a moment as the backend may be waking up from sleep.
<br>

<h2>Features</h2> 
<li>Real-time stock market data updates using SSE. (Automatically updates every 15 seconds)</li>
<li>User-friendly interface to select underlying indices.</li>
<li>Display of underlying index prices and options contracts.</li>
<li>Interactive and sortable table for options contracts.</li>
<br>

<h2>Demo</h2> 
You can view a live demo of the project <a href = "https://nishith-nse-option-chain-sim.vercel.app/"> here </a> <br><br><br>

The api endpoints are built using flask and deployed on <a href="https://render.com/">render</a> <br>
Links to the api endpoints are as follows <br>

<li>Current Option Data <a href="https://nse-option-chain-sim-nish.onrender.com/api/current_option_values"> here </a></li>
<li>Current LTP Data <a href="https://nse-option-chain-sim-nish.onrender.com/api/current_ltp_values"> here </a></li>
<br>
<br>

<h3>Structure of json is as follows:</h3><br>

Current LTP data : <br>

```json
{
  "data": {
    "MAINIDX": {
      "underlying": "MAINIDX",
      "LTP": 18691.25
    },
    "FINANCIALS": {
      "underlying": "FINANCIALS",
      "LTP": 19798.75
    },
    "MIDCAPS": {
      "underlying": "MIDCAPS",
      "LTP": 7864.05
    },
    "ALLBANKS": {
      "underlying": "ALLBANKS",
      "LTP": 44401.0
    }
  }
}
```

Current Option Data

```json
{
  "data": {
    "MAINIDX": {
        "calls": {
            "10000": {
            "oi": 0,
            "change in oi": -3100,
            "Volume": 0,
            "iv": "-",
            "ltp": 1.1,
            "change": 1.1,
            "bid quantity": 0,
            "bid": 0,
            "ask": 1.8,
            "ask quantity": 1000
          },
            "11000": {
            "oi": 0,
            "change in oi": 0,
            "Volume": 0,
            "iv": "-",
            "ltp": 2,
            "change": -16,
            "bid quantity": 1800,
            "bid": 0.5,
            "ask": 0,
            "ask quantity": 0
          }
        },
      "puts": {
        "11000": {
          "oi": 0,
          "change in oi": 0,
          "Volume": 0,
          "iv": "-",
          "ltp": 2,
          "change": -16,
          "bid quantity": 1800,
          "bid": 0.5,
          "ask": 0,
          "ask quantity": 0
        }
      }
    },
    "FINANCIALS": {
      "same as above"
    },
    "ALLBANKS": {
      "same as above"
    },
    "MIDCAPS":{
      "same as above"
    }
  }
}



```



<br>


<h2>Technologies Used</h2>

<li>React + Vite</li>
<li>Server-Sent Events (SSE)</li>
<li>REST API</li>
<li>Python</li>
<li>Flask (Backend)</li>
<li>Docker</li>
<li>CSS (Styling)</li>
<li>Quant libraries (to calculate implied volatility, etc) </li>
<br>
<br>

<h2>The work flow is as follows:</h2>

![Project Working](https://github.com/nish3112/NSE-Option-Chain-Sim/blob/main/Frontend/src/assets/overlayImage.png)

<h2>License</h2><br>
This project is licensed under the <a href="https://github.com/nish3112/NSE-Option-Chain-Sim/blob/main/LICENSE">MIT License.</a>

