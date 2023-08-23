// WORKING
import React from 'react';
import { useTable, useSortBy } from 'react-table';
import './SortableTable.css';




const SortableTable = ({ data, selectedSymbol, LTPdata }) => {
  const [changedCells, setChangedCells] = React.useState([]);


  // Function to render cells with placeholder text for empty values
  const renderCell = (cell) => {
    if (cell.value === undefined || cell.value === null || cell.value === '') {
      return <span className="empty-cell"> - </span>;
    }

    const classNames = [];
    
    let formattedValue = cell.value;

    if (typeof cell.value === 'number') {
      formattedValue = cell.value.toFixed(2); 
      
    }

    if (cell.column.id === 'calls.change' || cell.column.id === 'puts.change') {
      const chngValue = parseFloat(cell.value);
      classNames.push(chngValue < 0 ? 'chng-negative' : 'chng-positive');
      if (changedCells.includes(cell)) {
        classNames.push('value-change');
        setTimeout(() => {
          setChangedCells((prevChangedCells) =>
            prevChangedCells.filter((c) => c !== cell)
          );
        }, 1000);
      }
    }

    
    
  
    return <span className={classNames.join(' ')}>{formattedValue}</span>;
  };


  const columns = React.useMemo(
    () => [
      {
        Header: 'CALLS',
        columns: [
          { Header: 'OI', accessor: 'calls.oi' },
          { Header: 'CHNG IN OI', accessor: 'calls.change in oi' },
          { Header: 'VOLUME', accessor: 'calls.Volume' },
          { Header: 'IV', accessor: 'calls.iv' },
          { Header: 'LTP', accessor: 'calls.ltp' },
          { Header: 'CHNG', accessor: 'calls.change' },
          { Header: 'BID', accessor: 'calls.bid' },
          { Header: 'QTY BID', accessor: 'calls.bid quantity' },
          { Header: 'ASK', accessor: 'calls.ask' },
          { Header: 'ASK QTY', accessor: 'calls.ask quantity' },
          { Header: 'STRIKE', accessor: 'strike' },
        ],
      },
      {
        Header: 'PUTS',
        columns: [
          { Header: 'BID QTY', accessor: 'puts.bid quantity' },
          { Header: 'BID', accessor: 'puts.bid' },
          { Header: 'ASK', accessor: 'puts.ask' },
          { Header: 'ASK QTY', accessor: 'puts.ask quantity' },
          { Header: 'CHNG', accessor: 'puts.change' },
          { Header: 'LTP', accessor: 'puts.ltp' },
          { Header: 'IV', accessor: 'puts.iv' },
          { Header: 'VOLUME', accessor: 'puts.Volume' },
          { Header: 'CHNG IN OI', accessor: 'puts.change in oi' },
          { Header: 'OI', accessor: 'puts.oi' },        
        ],
      },
    ],
    []
  );
  

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = useTable({ columns, data }, useSortBy);

  return (
    <div>
      <table {...getTableProps()} className="table">
      <thead>
        {headerGroups.map((headerGroup) => (
          <tr {...headerGroup.getHeaderGroupProps()}>
            {headerGroup.headers.map((column) => (
              <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                {column.render('Header')}
                <span>
                  {column.isSorted ? (column.isSortedDesc ? ' 🔽' : ' 🔼') : ''}
                </span>
              </th>
            ))}
          </tr>
        ))}
      </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map((row) => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map((cell) => (
                  <td
                  {...cell.getCellProps()}
                  className={`cell ${cell.column.id === 'strike' || cell.column.id === 'calls.ltp' || cell.column.id === 'puts.ltp'? 'blue-column' : ''}`}
                >
                  {renderCell(cell)}
                </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default SortableTable;
