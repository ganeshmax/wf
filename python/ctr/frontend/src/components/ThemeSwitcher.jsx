import React from 'react';
import { useTheme } from '../context/ThemeContext';

export default function ThemeSwitcher() {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
        >
            <i className={theme === 'light' ? 'ri-moon-line' : 'ri-sun-line'}></i>
        </button>
    );
}
