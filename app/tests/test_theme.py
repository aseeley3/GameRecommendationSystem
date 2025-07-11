import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestTheme:
    def wait_for_theme_initialization(self, selenium):
        """Wait for theme initialization to complete"""
        WebDriverWait(selenium, 10).until(
            lambda d: d.execute_script("return localStorage.getItem('color-theme')") is not None
        )

    def test_initial_theme_detection(self, selenium):
        """Test that the initial theme is correctly detected based on system preference"""
        selenium.get("http://localhost:5000")
        self.wait_for_theme_initialization(selenium)
        
        # Check if dark mode is applied based on system preference
        html = selenium.find_element(By.TAG_NAME, "html")
        is_dark = "dark" in html.get_attribute("class")
        
        # Verify the correct icon is shown
        dark_icon = selenium.find_element(By.ID, "theme-toggle-dark-icon")
        light_icon = selenium.find_element(By.ID, "theme-toggle-light-icon")
        
        dark_classes = dark_icon.get_attribute("class").split()
        light_classes = light_icon.get_attribute("class").split()
        
        if is_dark:
            assert "hidden" not in dark_classes
            assert "hidden" in light_classes
        else:
            assert "hidden" in dark_classes
            assert "hidden" not in light_classes

    def test_theme_toggle(self, selenium):
        """Test that clicking the theme toggle button switches between themes"""
        selenium.get("http://localhost:5000")
        self.wait_for_theme_initialization(selenium)
        
        # Get initial theme
        html = selenium.find_element(By.TAG_NAME, "html")
        initial_theme = "dark" in html.get_attribute("class")
        
        # Click the theme toggle button
        toggle_button = selenium.find_element(By.ID, "theme-toggle")
        toggle_button.click()
        
        # Wait for theme change
        WebDriverWait(selenium, 10).until(
            lambda d: ("dark" in d.find_element(By.TAG_NAME, "html").get_attribute("class")) != initial_theme
        )
        
        # Verify theme has changed
        new_theme = "dark" in html.get_attribute("class")
        assert new_theme != initial_theme
        
        # Verify correct icon is shown
        dark_icon = selenium.find_element(By.ID, "theme-toggle-dark-icon")
        light_icon = selenium.find_element(By.ID, "theme-toggle-light-icon")
        
        dark_classes = dark_icon.get_attribute("class").split()
        light_classes = light_icon.get_attribute("class").split()
        
        if new_theme:
            assert "hidden" not in dark_classes
            assert "hidden" in light_classes
        else:
            assert "hidden" in dark_classes
            assert "hidden" not in light_classes

    def test_theme_persistence(self, selenium):
        """Test that theme preference persists after page reload"""
        selenium.get("http://localhost:5000")
        self.wait_for_theme_initialization(selenium)
        
        # Click the theme toggle button to change theme
        toggle_button = selenium.find_element(By.ID, "theme-toggle")
        toggle_button.click()
        
        # Wait for theme change
        WebDriverWait(selenium, 10).until(
            lambda d: d.find_element(By.ID, "theme-toggle-dark-icon").is_displayed() or 
                     d.find_element(By.ID, "theme-toggle-light-icon").is_displayed()
        )
        
        # Get the theme after toggle
        html = selenium.find_element(By.TAG_NAME, "html")
        theme_after_toggle = "dark" in html.get_attribute("class")
        
        # Reload the page
        selenium.refresh()
        self.wait_for_theme_initialization(selenium)
        
        # Wait for page to load
        WebDriverWait(selenium, 10).until(
            lambda d: d.find_element(By.ID, "theme-toggle").is_displayed()
        )
        
        # Verify theme persists
        html = selenium.find_element(By.TAG_NAME, "html")
        theme_after_reload = "dark" in html.get_attribute("class")
        assert theme_after_reload == theme_after_toggle

    def test_local_storage(self, selenium):
        """Test that theme preference is saved in localStorage"""
        selenium.get("http://localhost:5000")
        self.wait_for_theme_initialization(selenium)
        
        # Click the theme toggle button
        toggle_button = selenium.find_element(By.ID, "theme-toggle")
        toggle_button.click()
        
        # Wait for theme change
        WebDriverWait(selenium, 10).until(
            lambda d: d.find_element(By.ID, "theme-toggle-dark-icon").is_displayed() or 
                     d.find_element(By.ID, "theme-toggle-light-icon").is_displayed()
        )
        
        # Get the theme after toggle
        html = selenium.find_element(By.TAG_NAME, "html")
        is_dark = "dark" in html.get_attribute("class")
        
        # Check localStorage
        theme_in_storage = selenium.execute_script("return localStorage.getItem('color-theme')")
        expected_theme = "dark" if is_dark else "light"
        assert theme_in_storage == expected_theme 