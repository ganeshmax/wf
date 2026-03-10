import React from 'react';
import ThemeSwitcher from './ThemeSwitcher';

export default function Header({ title, subtitle, stats }) {
    return (
        <header className="main-header">
            <div className="header-title">
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
            <div className="header-actions">
                {stats && (
                    <>
                        {stats.type === 'simple' ? (
                            <div className="stat-card">
                                <span className="stat-label">Total Records</span>
                                <span className="stat-value">{stats.totalRecords.toLocaleString()}</span>
                            </div>
                        ) : (
                            <div className="header-stats" id="ctr-stats-panel" style={{ display: 'flex', marginLeft: '12px', gap: '16px' }}>
                                <div className="stat-card" title="Total number of unique Form 112s created">
                                    <span className="stat-label">Forms Generated</span>
                                    <span className="stat-value" style={{ color: 'var(--accent-success)' }}>{stats.forms.toLocaleString()}</span>
                                </div>
                                <div className="stat-card" title="Total count of unique Customers and Non-Customers analyzed by the pipeline">
                                    <span className="stat-label">Total Entities Evaluated</span>
                                    <span className="stat-value">{stats.processed.toLocaleString()}</span>
                                </div>
                                <div className="stat-card" title="Count of distinct entities that triggered a threshold or were secondarily associated in a Form 112">
                                    <span className="stat-label" style={{ color: 'var(--accent-warning)' }}>Reportable Entities</span>
                                    <span className="stat-value">{stats.reportable.toLocaleString()}</span>
                                </div>
                            </div>
                        )}
                    </>
                )}
                <ThemeSwitcher />
            </div>
        </header>
    );
}
