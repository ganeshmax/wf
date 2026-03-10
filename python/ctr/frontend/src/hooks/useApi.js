import { useState, useCallback } from 'react';

// Central API hook strictly interacting with the FastAPI backend
export function useApi() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchDataset = useCallback(async (dataset, limit = 50) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`/api/data/${dataset}?limit=${limit}`);
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.detail || 'Data fetch failed');
            return data; // { data: [...], total_rows: X }
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const triggerJob = useCallback(async (jobName) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch('/api/jobs/trigger', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_name: jobName })
            });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.detail || 'Job failed');
            return data;
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchTransactionsBatch = useCallback(async (transaction_ids) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch('/api/data/transactions/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ transaction_ids })
            });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.detail || 'Failed to fetch transactions');
            return data;
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchAccountsBatch = useCallback(async (customer_ids) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch('/api/data/accounts/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ customer_ids })
            });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.detail || 'Failed to fetch accounts');
            return data;
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const updateCtrForm = useCallback(async (reportId, payload) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`/api/data/ctr_forms/${reportId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.detail || 'Failed to update form');
            return data;
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchStats = useCallback(async () => {
        try {
            const resp = await fetch('/api/data/ctr_stats');
            if (!resp.ok) return null;
            return await resp.json();
        } catch (err) {
            return null;
        }
    }, []);

    const generateXML = useCallback(async (reportId) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`/api/data/ctr_forms/${reportId}/xml`);
            const data = await resp.text();
            if (!resp.ok) throw new Error('Failed to generate XML');
            return data;
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    return { loading, error, fetchDataset, triggerJob, fetchStats, fetchTransactionsBatch, fetchAccountsBatch, updateCtrForm, generateXML };
}
