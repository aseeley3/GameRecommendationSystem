
/**
 * Theme Management Module
 * Handles dark/light mode switching and persistence
 */

/**
 * Initialize theme on page load
 */
function initializeTheme() {
    const savedTheme = localStorage.getItem('color-theme');

    if (savedTheme === 'dark') {
        // Apply dark mode
        document.documentElement.classList.add('dark');
        updateThemeIcons(true);
    } else {
        // Default to light mode
        document.documentElement.classList.remove('dark');
        updateThemeIcons(false);

        // Set light mode in localStorage if not already set
        if (!savedTheme) {
            localStorage.setItem('color-theme', 'light');
        }
    }
}

/**
 * Toggle between dark and light themes
 */
function toggleTheme() {
    const html = document.documentElement;
    const isDarkMode = html.classList.contains('dark');

    if (isDarkMode) {
        // Switch to light mode
        html.classList.remove('dark');
        localStorage.setItem('color-theme', 'light');
        updateThemeIcons(false);
    } else {
        // Switch to dark mode
        html.classList.add('dark');
        localStorage.setItem('color-theme', 'dark');
        updateThemeIcons(true);
    }
}

/**
 * Update theme toggle button icons
 * @param {boolean} isDarkMode - Whether dark mode is active
 */
function updateThemeIcons(isDarkMode) {
    const darkIcon = document.getElementById('theme-toggle-dark-icon');
    const lightIcon = document.getElementById('theme-toggle-light-icon');

    if (darkIcon && lightIcon) {
        if (isDarkMode) {
            darkIcon.classList.add('hidden');
            lightIcon.classList.remove('hidden');
        } else {
            darkIcon.classList.remove('hidden');
            lightIcon.classList.add('hidden');
        }
    }
}

/**
 * Initialize theme toggle button event listener
 */
function initializeThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            toggleTheme();
        });
    }
}

// Export functions for use in other modules
window.ThemeManager = {
    initializeTheme,
    toggleTheme,
    initializeThemeToggle,
    updateThemeIcons
};

// Make toggleTheme available globally for backward compatibility
window.toggleTheme = toggleTheme;
