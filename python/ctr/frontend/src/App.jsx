import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { useApi } from './hooks/useApi';

import Sidebar from './components/Sidebar';
import RawDataset from './pages/RawDataset';
import FormsList from './pages/FormsList';

export default function App() {
  const { triggerJob } = useApi();
  const [toast, setToast] = useState(null);

  const handleTriggerJob = async (jobName) => {
    const result = await triggerJob(jobName);
    if (result) {
      showToast(`${jobName.toUpperCase()} Pipeline completed successfully!`, 'success');
      setTimeout(() => window.location.reload(), 1500);
    } else {
      showToast('Pipeline failed to execute', 'error');
    }
  };

  const showToast = (msg, type) => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 5000);
  };

  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="app-container">
          <Sidebar onTriggerJob={handleTriggerJob} />

          <Routes>
            <Route path="/view/:datasetId" element={<RawDataset />} />
            <Route path="/forms" element={<FormsList />} />
            <Route path="*" element={<Navigate to="/view/raw_transactions" replace />} />
          </Routes>

          {toast && (
            <div className="notification-area">
              <div className={`toast ${toast.type}`}>
                <i className={toast.type === 'success' ? 'ri-checkbox-circle-line' : 'ri-error-warning-line'}></i>
                <span>{toast.msg}</span>
              </div>
            </div>
          )}
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}
