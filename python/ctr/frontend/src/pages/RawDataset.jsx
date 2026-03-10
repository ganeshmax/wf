import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Header from '../components/Header';
import DataTable from '../components/DataTable';
import Pagination from '../components/Pagination';
import { useApi } from '../hooks/useApi';

const viewConfig = {
    'raw_customers': { title: 'Raw Customers', subtitle: 'Source data from CRM systems.' },
    'raw_non_customers': { title: 'Raw Non-Customers', subtitle: 'Shadow profiles for non-customer conductors.' },
    'raw_locations': { title: 'Raw Locations', subtitle: 'Branch and ATM location data.' },
    'raw_transactions': { title: 'Raw Transactions', subtitle: 'All incoming bank transactions.' },
    'canonical_customers': { title: 'Canonical Customers', subtitle: 'Cleaned customer profiles.' },
    'canonical_non_customers': { title: 'Canonical Non-Customers', subtitle: 'Cleaned non-customer shadow profiles.' },
    'canonical_transactions': { title: 'Canonical Transactions', subtitle: 'Cleaned, typed, partitioned data in Parquet.' },
    'aggregated_ben_in': { title: 'Beneficiary Daily Cash-In', subtitle: 'Cash deposits summed per beneficiary per day.' },
    'aggregated_ben_out': { title: 'Beneficiary Daily Cash-Out', subtitle: 'Cash withdrawals summed per beneficiary per day.' },
    'aggregated_cond_in': { title: 'Conductor Daily Cash-In', subtitle: 'Cash deposits summed per conductor per day.' },
    'aggregated_cond_out': { title: 'Conductor Daily Cash-Out', subtitle: 'Cash withdrawals summed per conductor per day.' },
    'ctr': { title: 'Flat Reportable Entities', subtitle: 'Raw flattened entities that will be grouped into CTRs.' }
};

const ITEMS_PER_PAGE = 50;

export default function RawDataset() {
    const { datasetId } = useParams();
    const { fetchDataset, fetchStats, fetchAccountsBatch, loading, error } = useApi();
    const [data, setData] = useState([]);
    const [totalRows, setTotalRows] = useState(0);
    const [ctrStats, setCtrStats] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [expandedRows, setExpandedRows] = useState({});
    const [expandedData, setExpandedData] = useState({});

    const id = datasetId || 'raw_transactions';
    const config = viewConfig[id] || { title: 'Dataset', subtitle: 'Viewing dataset' };

    useEffect(() => {
        // We fetch a larger pool and paginate client-side for this demo, 
        // or we could pass offset to backend. For demo purposes we will fetch up to 1000 and slice.
        const loadData = async () => {
            const result = await fetchDataset(id, 1000);
            if (result) {
                setData(result.data || []);
                setTotalRows(result.total_rows || 0);
            }

            if (id === 'ctr') {
                const stats = await fetchStats();
                if (stats && stats.data) setCtrStats(stats.data);
            } else {
                setCtrStats(null);
            }
            setCurrentPage(1); // Reset page on dataset change
            setExpandedRows({});
            setExpandedData({});
        };
        loadData();
    }, [id, fetchDataset, fetchStats]);

    const totalPages = Math.ceil(data.length / ITEMS_PER_PAGE);
    const paginatedData = data.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);

    const handleExpandRow = async (rowIndex, row) => {
        if (id !== 'canonical_customers') return;

        const isCurrentlyExpanded = expandedRows[rowIndex];

        setExpandedRows(prev => ({
            ...prev,
            [rowIndex]: !isCurrentlyExpanded
        }));

        if (!isCurrentlyExpanded && !expandedData[rowIndex]) {
            const customerId = row.customer_id;
            if (customerId) {
                const response = await fetchAccountsBatch([customerId]);
                if (response && response.data) {
                    setExpandedData(prev => ({
                        ...prev,
                        [rowIndex]: response.data
                    }));
                } else {
                    setExpandedData(prev => ({
                        ...prev,
                        [rowIndex]: []
                    }));
                }
            }
        }
    };

    const renderExpandedRow = (rowIndex, row) => {
        const accounts = expandedData[rowIndex];
        if (!accounts) {
            return <div style={{ padding: '20px', textAlign: 'center' }}><div className="spinner" style={{ width: 20, height: 20, borderWidth: 2, display: 'inline-block' }}></div></div>;
        }
        if (accounts.length === 0) {
            return <div style={{ padding: '20px', color: 'var(--text-muted)', textAlign: 'center' }}>No accounts found for this profile.</div>;
        }

        return (
            <div style={{ padding: '0', background: 'var(--bg-primary)' }}>
                <div className="sub-table-container">
                    <DataTable data={accounts} isSubTable={true} />
                </div>
            </div>
        );
    };

    return (
        <div className="main-content">
            <Header
                title={config.title}
                subtitle={config.subtitle}
                stats={
                    id === 'ctr' && ctrStats
                        ? { type: 'complex', forms: ctrStats.total_forms, processed: ctrStats.total_processed, reportable: ctrStats.total_with_ctrs }
                        : { type: 'simple', totalRecords: totalRows || data.length }
                }
            />

            <div className="content-body">
                {error && <div className="toast error" style={{ position: 'absolute', top: 20, right: 20, zIndex: 100 }}>{error}</div>}

                <div className="table-container">
                    {loading && (
                        <div className="table-overlay active">
                            <div className="spinner"></div>
                            <p>Loading...</p>
                        </div>
                    )}

                    <DataTable
                        data={paginatedData}
                        expandable={id === 'canonical_customers'}
                        expandedRows={expandedRows}
                        onExpandRow={handleExpandRow}
                        renderExpandedRow={renderExpandedRow}
                    />
                </div>

                <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={setCurrentPage}
                />
            </div>
        </div>
    );
}
