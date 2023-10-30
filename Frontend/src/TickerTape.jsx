import React from 'react';
import '../src/TickerTape.css';
import 'font-awesome/css/font-awesome.min.css';

const TickerTape = ({ description }) => {

  const nbsp = '\u00A0';

  return (
    <div className="ticker-tape">
      <marquee behavior="scroll" direction="left">
        <span className="red-text">
        <i className="fa fa-exclamation-triangle"></i>
          {nbsp}{ description }{nbsp}
        <i className="fa fa-exclamation-triangle"></i>
        </span>
      </marquee>
    </div>
  );
};

export default TickerTape;
