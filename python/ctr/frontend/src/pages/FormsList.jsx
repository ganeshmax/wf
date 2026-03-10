import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import Form112Card from '../components/Form112Card';
import Pagination from '../components/Pagination';
import { useApi } from '../hooks/useApi';

const ITEMS_PER_PAGE = 50;

export default function FormsList() {
    const { fetchDataset, fetchStats, loading, error } = useApi();
    const [forms, setForms] = useState([]);
    const [totalRows, setTotalRows] = useState(0);
    const [ctrStats, setCtrStats] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);

    const handleFormUpdated = (updatedForm) => {
        setForms(prevForms => prevForms.map(f => f.report_id === updatedForm.report_id ? updatedForm : f));
    };

    useEffect(() => {
        const loadForms = async () => {
            // Fetch up to limit for demo (typically backend paginates)
            const result = await fetchDataset('ctr_forms', 1000);
            if (result) {
                setForms(result.data || []);
                setTotalRows(result.total_rows || 0);
            }

            const stats = await fetchStats();
            if (stats && stats.data) setCtrStats(stats.data);
        };
        loadForms();
    }, [fetchDataset, fetchStats]);

    const totalPages = Math.ceil(forms.length / ITEMS_PER_PAGE);
    const paginatedForms = forms.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);

    return (
        <div className="main-content">
            <Header
                title="Target Form 112s (Grouped CTRs)"
                subtitle="Fully assembled CTR Reports grouped by transaction triggering event."
                stats={
                    ctrStats
                        ? { type: 'complex', forms: ctrStats.total_forms, processed: ctrStats.total_processed, reportable: ctrStats.total_with_ctrs }
                        : { type: 'simple', totalRecords: totalRows || forms.length }
                }
            />

            <div className="content-body" style={{ overflowY: 'auto' }}>
                {error && <div className="toast error" style={{ position: 'absolute', top: 20, right: 20, zIndex: 100 }}>{error}</div>}

                <div style={{ flex: 1 }}>
                    {loading && (
                        <div className="table-overlay active" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0 }}>
                            <div className="spinner"></div>
                            <p>Loading Forms...</p>
                        </div>
                    )}

                    {!loading && forms.length === 0 && !error && (
                        <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            No Report Forms generated yet. Run the Pipeline.
                        </div>
                    )}

                    {paginatedForms.map(form => (
                        <Form112Card key={form.report_id} form={form} onFormUpdated={handleFormUpdated} />
                    ))}
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
