import React from 'react';

const formatCurrency = (val) => {
    if (typeof val === 'number') {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
    }
    return val;
};

export default function DataTable({ data, expandable, expandedRows, onExpandRow, renderExpandedRow, isSubTable }) {
    if (!data || data.length === 0) {
        return (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                <i className="ri-inbox-line" style={{ fontSize: '2rem', display: 'block', marginBottom: '10px' }}></i>
                No data available. Please run the required pipelines.
            </div>
        );
    }

    const cols = Object.keys(data[0]);

    return (
        <table id={isSubTable ? "" : "data-table"} className={isSubTable ? "sub-table" : ""}>
            <thead>
                <tr>
                    {expandable && <th style={{ width: '40px' }}></th>}
                    {cols.map(col => <th key={col}>{col.replace(/_/g, ' ')}</th>)}
                </tr>
            </thead>
            <tbody>
                {data.map((row, i) => (
                    <React.Fragment key={i}>
                        <tr style={expandable ? { cursor: 'pointer' } : {}} onClick={() => expandable && onExpandRow && onExpandRow(i, row)}>
                            {expandable && (
                                <td style={{ color: 'var(--text-muted)', textAlign: 'center' }}>
                                    <i className={expandedRows && expandedRows[i] ? "ri-arrow-down-s-line" : "ri-arrow-right-s-line"}></i>
                                </td>
                            )}
                            {cols.map(col => {
                                let val = row[col];
                                let isAmount = col.includes('amount') || col.includes('total');

                                if (isAmount) {
                                    return <td key={col} className="col-amount">{formatCurrency(val)}</td>;
                                } else if (typeof val === 'boolean') {
                                    return (
                                        <td key={col}>
                                            {val ? <><i className="ri-check-line col-amount"></i> True</> : <><i className="ri-close-line" style={{ color: 'var(--text-muted)' }}></i> False</>}
                                        </td>
                                    );
                                } else if (!val && typeof val !== 'number') {
                                    return <td key={col}><span style={{ color: 'var(--text-muted)' }}>NULL</span></td>;
                                } else {
                                    return <td key={col}>{val}</td>;
                                }
                            })}
                        </tr>
                        {expandable && expandedRows && expandedRows[i] && renderExpandedRow && (
                            <tr style={{ background: 'var(--bg-hover)' }}>
                                <td colSpan={cols.length + 1} style={{ padding: '0' }}>
                                    {renderExpandedRow(i, row)}
                                </td>
                            </tr>
                        )}
                    </React.Fragment>
                ))}
            </tbody>
        </table>
    );
}
