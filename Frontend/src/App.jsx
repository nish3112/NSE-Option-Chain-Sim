import SortableTable from './sortableTable';
import './App.css';
import React, { useState, useEffect } from 'react';
import TickerTape from '../src/TickerTape.jsx';


function App() {
  const [selectedSymbol, setSelectedSymbol] = useState('MAINIDX');
  const [LTPdata, setLTPData] = useState({});
  const [Optiondata, setOptionData] = useState({});

  const handleSymbolChange = (event) => {
    setSelectedSymbol(event.target.value);
  };

  const currentTime = new Date().toLocaleString();
  useEffect(() => {
    const sse_ltp_values = new EventSource('https://nse-option-chain-sim-nish.onrender.com/api/current_ltp_values');
    const sse_option_values = new EventSource('https://nse-option-chain-sim-nish.onrender.com/api/current_option_values')

    // FOR LTP VALUES
    sse_ltp_values.onmessage = (event) => {
      try {
        const jsonData_ltp = JSON.parse(event.data);
        setLTPData(jsonData_ltp.data);
      } catch (error) {
        console.error('Error parsing JSON LTP data:', error);
      }
    };

    sse_ltp_values.onerror = (error) => {
      console.error('Error with LTP EventSource:', error);
      sse_ltp_values.close();
    };

    // FOR CURRENT OPTION VALUES

    sse_option_values.onmessage = (event) => {
      try {
        const jsonData_option = JSON.parse(event.data);
        console.log(jsonData_option);
        setOptionData(jsonData_option.data);
      } catch (error) {
        console.error('Error parsing OPTION JSON data:', error);
      }
    };

    sse_option_values.onerror = (error) => {
      console.error('Error with OPTION EventSource:', error);
      sse_option_values.close();
    };

    return () => {
      sse_ltp_values.close();
      sse_option_values.close();
    };

  }, []);

  // Filter data based on the strike price range (-5000 to +7500 of LTP)
  const optionDataArray = Object.keys(Optiondata[selectedSymbol] || {}).map((strikePrice) => {
    const ltp = LTPdata[selectedSymbol]?.LTP || 0;
    const strike = parseFloat(strikePrice);
    const nearestStrike = Math.round((ltp - 1000) / 2000) * 2000 + 1000;

    if (strike >= nearestStrike - 1500 && strike <= nearestStrike + 7500) {
      return {
        strike: strikePrice,
        calls: Optiondata[selectedSymbol][strikePrice].calls || {},
        puts: Optiondata[selectedSymbol][strikePrice].puts || {},
      };
    }
    return null;
  }).filter(Boolean); 
  

  return (
    <div>
      <div className="filter-container">
        <TickerTape description={"If you are unable to view the table below, kindly allow for a brief delay of 3-4 minutes. This may be due to the backend infrastructure transitioning from a state of dormancy. Please avoid unnecessary refreshes"}/>
        <label htmlFor="symbol-select" className ="symbol-select" >View Options Contracts for:</label><br></br>
        <select id="symbol-select" className ="symbol-select-dropdown" value={selectedSymbol} onChange={handleSymbolChange}>
          <option value="">SELECT</option>
          <option value="MAINIDX">MAINIDX</option>
          <option value="FINANCIALS">FINANCIALS</option>
          <option value="ALLBANKS">ALLBANKS</option>
          <option value="MIDCAPS">MIDCAPS</option>
        </select>

      </div>
      <div className='LTP'>
        Underlying Index: {selectedSymbol || "MAINIDX"} {LTPdata[selectedSymbol]?.LTP && LTPdata[selectedSymbol]?.LTP.toFixed(2)} As on {currentTime} IST
      </div>
      <div>
      <SortableTable data={optionDataArray} selectedSymbol={selectedSymbol} LTPdata={LTPdata} />
      </div>
    </div>
  );
}


export default App;

