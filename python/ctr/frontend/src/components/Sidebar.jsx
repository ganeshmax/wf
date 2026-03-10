import React from 'react';
import { NavLink } from 'react-router-dom';

export default function Sidebar({ onTriggerJob }) {
    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <h2><i className="ri-bank-line"></i> CTR System</h2>
            </div>

            <nav className="sidebar-nav">
                <div className="nav-section">
                    <h3>Data Engineering</h3>
                    <button className="nav-btn pipeline-btn" onClick={() => onTriggerJob('ingestion')}>
                        <i className="ri-database-2-line"></i> Run Ingestion
                    </button>
                    <button className="nav-btn pipeline-btn" onClick={() => onTriggerJob('aggregation')}>
                        <i className="ri-bar-chart-2-line"></i> Run Aggregations
                    </button>
                    <button className="nav-btn pipeline-btn" onClick={() => onTriggerJob('ctr')}>
                        <i className="ri-file-search-line"></i> Generate CTRs
                    </button>
                    <button className="nav-btn pipeline-btn" onClick={() => alert("Please run MIL/SAR pipelines via CLI for now.")}>
                        <i className="ri-radar-line"></i> Run SAR Engine
                    </button>
                </div>

                <div className="nav-section">
                    <h3>Reference Data</h3>
                    <NavLink to="/view/canonical_customers" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-user-line"></i> Customers</NavLink>
                    <NavLink to="/view/canonical_non_customers" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-user-unfollow-line"></i> Non-Customers</NavLink>
                    <NavLink to="/view/canonical_accounts" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-bank-card-line"></i> All Accounts</NavLink>
                </div>

                <div className="nav-section">
                    <h3>Transactions</h3>
                    <NavLink to="/view/raw_transactions" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-exchange-dollar-line"></i> Raw Transactions</NavLink>
                    <NavLink to="/view/canonical_transactions" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-database-2-line"></i> Canonical Tx</NavLink>
                    <NavLink to="/view/aggregated_ben_in" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-login-box-line"></i> Beneficiary Cash-In</NavLink>
                    <NavLink to="/view/aggregated_ben_out" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-logout-box-line"></i> Beneficiary Cash-Out</NavLink>
                    <NavLink to="/view/aggregated_cond_in" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-login-circle-line"></i> Conductor Cash-In</NavLink>
                    <NavLink to="/view/aggregated_cond_out" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-logout-circle-line"></i> Conductor Cash-Out</NavLink>
                </div>

                <div className="nav-section">
                    <h3>Compliance Hub</h3>
                    <NavLink to="/forms" className={({ isActive }) => `nav-btn highlight ${isActive ? 'active' : ''}`}><i className="ri-file-shield-2-fill"></i> Form 112 (Maker Queue)</NavLink>
                    <NavLink to="/view/canonical_sars" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-alarm-warning-line" style={{ color: 'var(--accent-warning)' }}></i> Structuring Alerts (SAR)</NavLink>
                    <NavLink to="/view/canonical_mils" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-money-dollar-circle-line"></i> Monetary Log (MIL)</NavLink>
                    <NavLink to="/view/canonical_exemptions" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}><i className="ri-shield-check-line" style={{ color: 'var(--accent-green)' }}></i> DOEP Exemptions</NavLink>
                </div>
            </nav>
        </aside>
    );
}
