import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';

export default function Form112Card({ form, onFormUpdated }) {
    const [expandedRows, setExpandedRows] = useState({});
    const [hydratedTransactions, setHydratedTransactions] = useState({});
    const [loadingRows, setLoadingRows] = useState({});
    const [editedEntities, setEditedEntities] = useState({});
    const [showXmlModal, setShowXmlModal] = useState(false);
    const [xmlContent, setXmlContent] = useState(null);
    const { fetchTransactionsBatch, updateCtrForm, generateXML } = useApi();

    const toggleRow = async (idx, entity) => {
        const isCurrentlyExpanded = !!expandedRows[idx];
        setExpandedRows(prev => ({ ...prev, [idx]: !isCurrentlyExpanded }));

        if (!isCurrentlyExpanded && entity.transaction_ids && entity.transaction_ids.length > 0 && !hydratedTransactions[idx]) {
            setLoadingRows(prev => ({ ...prev, [idx]: true }));
            const res = await fetchTransactionsBatch(entity.transaction_ids);
            if (res && res.data) {
                setHydratedTransactions(prev => ({ ...prev, [idx]: res.data }));
            }
            setLoadingRows(prev => ({ ...prev, [idx]: false }));
        }
    };

    const handleEdit = (idx, field, value) => {
        setEditedEntities(prev => ({
            ...prev,
            [idx]: { ...(prev[idx] || {}), [field]: value, customer_id: form.entities[idx].customer_id }
        }));
    };

    const submitAction = async (newStatus) => {
        const payload = {
            entities: Object.values(editedEntities),
            status: newStatus
        };
        const updated = await updateCtrForm(form.report_id, payload);
        if (updated && onFormUpdated) {
            onFormUpdated(updated);
        }
        return updated;
    };

    const handleGenerateXML = async () => {
        if (form.status !== 'APPROVED') {
            const updated = await submitAction('APPROVED');
            if (!updated) return;
        }
        const xml = await generateXML(form.report_id);
        if (xml) {
            setXmlContent(xml);
            setShowXmlModal(true);
        }
    };

    const amountFormatted = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(form.report_amount);
    const colorDirection = form.direction === 'Cash-In' ? 'var(--accent-green)' : 'var(--accent-warning)';

    let statusBadge = null;
    if (form.status === 'ACTION_REQUIRED') {
        statusBadge = <span style={{ background: '#fce8e8', color: '#c53030', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, marginLeft: '10px', border: '1px solid #fbd5d5' }}><i className="ri-error-warning-fill"></i> ACTION REQUIRED</span>;
    } else if (form.status === 'APPROVED') {
        statusBadge = <span style={{ background: '#def7ec', color: '#03543f', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, marginLeft: '10px', border: '1px solid #bcdefa' }}><i className="ri-checkbox-circle-fill"></i> APPROVED</span>;
    } else {
        statusBadge = <span style={{ background: '#fef4e4', color: '#8a4b08', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, marginLeft: '10px', border: '1px solid #fde8c3' }}><i className="ri-time-line"></i> PENDING REVIEW</span>;
    }

    return (
        <div style={{ background: 'var(--bg-panel)', border: form.status === 'ACTION_REQUIRED' ? '2px solid var(--accent-warning)' : '1px solid var(--border-color)', borderRadius: '8px', marginBottom: '1.5rem', padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1rem' }}>
                <div>
                    <h3 style={{ margin: 0, color: 'var(--text-main)', display: 'flex', alignItems: 'center' }}>
                        Form 112: <span style={{ fontFamily: 'monospace', fontSize: '0.9em', color: 'var(--text-muted)', marginLeft: '8px' }}>{form.report_id}</span>
                        {statusBadge}
                    </h3>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                        Date: {form.date} • Entities Involved: {form.entity_count}
                    </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 600, fontSize: '1.1rem', color: colorDirection }}>{form.direction}</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>{amountFormatted}</div>
                </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {form.entities.map((entity, idx) => {
                    const isPrimary = entity.ctr_role.includes('Primary');
                    const badgeBg = isPrimary ? (entity.ctr_role.includes('Beneficiary') ? 'var(--badge-blue-bg)' : 'var(--badge-purple-bg)') : 'var(--bg-primary)';
                    const badgeText = isPrimary ? (entity.ctr_role.includes('Beneficiary') ? 'var(--badge-blue-text)' : 'var(--badge-purple-text)') : 'var(--text-muted)';

                    const isExpanded = !!expandedRows[idx];

                    return (
                        <div key={idx} style={{ border: '1px dashed var(--border-color)', borderRadius: '6px', overflow: 'hidden' }}>
                            <div
                                onClick={() => toggleRow(idx, entity)}
                                style={{ display: 'flex', alignItems: 'center', padding: '0.75rem', cursor: 'pointer', background: isExpanded ? 'var(--bg-hover)' : 'transparent', transition: 'background 0.2s' }}
                            >
                                <div style={{ marginRight: '8px', color: 'var(--text-muted)' }}>
                                    <i className={isExpanded ? "ri-arrow-down-s-line" : "ri-arrow-right-s-line"}></i>
                                </div>
                                <div style={{ flexShrink: 0, background: badgeBg, color: badgeText, padding: '0.25rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, width: '140px', textAlign: 'center', marginRight: '1.25rem' }}>
                                    {entity.ctr_role}
                                </div>
                                <div style={{ flexGrow: 1 }}>
                                    <div style={{ fontWeight: 500, color: 'var(--text-main)' }}>
                                        {entity.first_name} {entity.last_name}{' '}
                                        <span style={{ fontSize: '0.8em', color: 'var(--text-muted)', fontWeight: 'normal' }}>
                                            [{entity.entity_type}]
                                            (TIN: {entity.tin ? entity.tin : (
                                                <input
                                                    type="text"
                                                    placeholder="Missing TIN..."
                                                    value={editedEntities[idx]?.tin || ''}
                                                    onChange={e => handleEdit(idx, 'tin', e.target.value)}
                                                    style={{ border: '1px solid var(--accent-warning)', borderRadius: '4px', padding: '2px 6px', background: 'var(--bg-primary)', color: 'var(--text-main)', fontSize: '0.9em', marginLeft: '4px' }}
                                                />
                                            )})
                                        </span>
                                    </div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                                        {entity.address}, {entity.city}, {entity.state} {entity.zip}
                                    </div>
                                </div>
                                <div style={{ flexShrink: 0, fontWeight: 600, color: 'var(--text-main)' }}>
                                    {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(entity.entity_amount)}
                                </div>
                            </div>

                            {isExpanded && entity.transaction_ids && entity.transaction_ids.length > 0 && (
                                <div style={{ padding: '0.75rem 1rem 1rem 3rem', background: 'var(--bg-primary)', borderTop: '1px solid var(--border-color)' }}>
                                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                        Underlying Transactions ({entity.transaction_ids.length})
                                    </div>
                                    {loadingRows[idx] ? (
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '0.5rem 0' }}>Loading transactions...</div>
                                    ) : hydratedTransactions[idx] ? (
                                        <table style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse', marginTop: '0.5rem' }}>
                                            <thead>
                                                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                                                    <th style={{ paddingBottom: '0.5rem' }}>ID</th>
                                                    <th style={{ paddingBottom: '0.5rem' }}>Date</th>
                                                    <th style={{ paddingBottom: '0.5rem' }}>Type</th>
                                                    <th style={{ paddingBottom: '0.5rem' }}>Account</th>
                                                    <th style={{ paddingBottom: '0.5rem' }}>Location</th>
                                                    <th style={{ paddingBottom: '0.5rem', textAlign: 'right' }}>Amount</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {hydratedTransactions[idx].map(tx => (
                                                    <tr key={tx.transaction_id} style={{ borderBottom: '1px dotted var(--border-color)' }}>
                                                        <td style={{ padding: '0.5rem 0', fontFamily: 'monospace', color: 'var(--text-muted)', fontSize: '0.7rem' }}>{tx.transaction_id.split('-')[0]}</td>
                                                        <td style={{ padding: '0.5rem 0' }}>{tx.timestamp}</td>
                                                        <td style={{ padding: '0.5rem 0' }}>{tx.transaction_type}</td>
                                                        <td style={{ padding: '0.5rem 0', fontFamily: 'monospace', color: 'var(--accent-purple)' }}>{tx.account_id}</td>
                                                        <td style={{ padding: '0.5rem 0' }}>{tx.location_id}</td>
                                                        <td style={{ padding: '0.5rem 0', textAlign: 'right', fontWeight: 600, color: 'var(--text-main)' }}>
                                                            {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(tx.amount)}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    ) : (
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-danger)' }}>Failed to load transactions.</div>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Maker / Checker Action Bar */}
            <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                {form.status === 'ACTION_REQUIRED' && (
                    <button onClick={() => submitAction('PENDING_REVIEW')} style={{ background: 'var(--accent-purple)', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 600 }}>
                        <i className="ri-save-line"></i> Save PII & Submit to Checker
                    </button>
                )}
                {form.status === 'PENDING_REVIEW' && (
                    <button onClick={handleGenerateXML} style={{ background: 'var(--accent-green)', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 600 }}>
                        <i className="ri-check-double-line"></i> Approve & Generate XML
                    </button>
                )}
                {form.status === 'APPROVED' && (
                    <button onClick={handleGenerateXML} style={{ background: 'var(--accent-blue)', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 600 }}>
                        <i className="ri-file-code-line"></i> View EFiling XML
                    </button>
                )}
            </div>

            {/* XML Modal */}
            {showXmlModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center' }} onClick={(e) => { if (e.target === e.currentTarget) setShowXmlModal(false); }}>
                    <div style={{ background: 'var(--bg-panel)', width: '80%', maxWidth: '900px', maxHeight: '85vh', borderRadius: '12px', display: 'flex', flexDirection: 'column', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)' }}>
                        <div style={{ padding: '20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}><i className="ri-file-code-line" style={{ color: 'var(--accent-blue)' }}></i> FinCEN BSA E-Filing XML</h3>
                            <button onClick={() => setShowXmlModal(false)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '1.5rem', color: 'var(--text-muted)' }}><i className="ri-close-line"></i></button>
                        </div>
                        <div style={{ padding: '20px', overflow: 'auto', flex: 1 }}>
                            <pre style={{ margin: 0, background: '#1e1e1e', color: '#d4d4d4', padding: '16px', borderRadius: '6px', fontSize: '0.85rem', fontFamily: 'monospace', whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
                                {xmlContent}
                            </pre>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
