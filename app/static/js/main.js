/**
 * Main JavaScript file for the Game Recommendation System
 * This file orchestrates the initialization of all application modules
 */

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Game Recommendation System initialized');

    // Initialize all modules
    initializeApplication();
});

/**
 * Initialize all application modules
 */
function initializeApplication() {
    // Initialize theme first (before other features)
    if (window.ThemeManager) {
        ThemeManager.initializeTheme();
        ThemeManager.initializeThemeToggle();
    }

    // Initialize utilities
    if (window.Utils) {
        Utils.initializeSmoothScrolling();
        Utils.initializeFormLoadingStates();
    }

    // Initialize page-specific features
    initializePageSpecificFeatures();
}

/**
 * Initialize features specific to the current page
 */
function initializePageSpecificFeatures() {
    // Check what page we're on and initialize accordingly
    const currentPath = window.location.pathname;

    if (currentPath === '/') {
        initializeHomePage();
    } else if (currentPath.includes('/select_platform')) {
        initializePlatformSelectionPage();
    }
}

/**
 * Initialize home page specific features
 */
function initializeHomePage() {
    console.log('Initializing home page features');
    // Add any home page specific initialization here
}

/**
 * Initialize platform selection page specific features
 */
function initializePlatformSelectionPage() {
    console.log('Initializing platform selection page features');
    // Platform selection logic is already in the template
    // This is where we could move it for better organization
}

// Export main application object for global access
window.GameRecommendationSystem = {
    initializeApplication,
    initializePageSpecificFeatures
};