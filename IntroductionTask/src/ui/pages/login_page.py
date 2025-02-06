# src/ui/pages/login_page.py
from .base_page import BasePage
from ...utils.logger import setup_logger
from playwright.async_api import TimeoutError as PlaywrightTimeout

logger = setup_logger()

class LoginPage(BasePage):
    def __init__(self, page, device_config):
        super().__init__(page)
        self.device_config = device_config

    
    async def login(self, username, password):
        """Login to the device web interface."""
        try:
            logger.info("Attempting to navigate to router...")
            
            # Navigate to HTTPS login page
            url = f'https://{self.device_config["device"]["ip"]}/login'
            logger.info(f"Navigating to {url}")
            await self.page.goto(url, 
                               wait_until='networkidle',
                               timeout=10000)

            
            # Fill credentials using test-id
            await self.page.fill('[test-id="input-username"]', username)
            logger.info("Filled username")
            
            await self.page.fill('[test-id="input-password"]', password)
            logger.info("Filled password")
            
            # Click the login button
            await self.page.click('[test-id="button-login"]')
            logger.info("Clicked login button")
            
            # Wait for successful login by checking for status/overview page
            url = f'https://{self.device_config["device"]["ip"]}/status/overview'
            await self.page.wait_for_url(url, timeout=10000)
            logger.info("Login successful - reached overview page")
            await self.wait_for_spinner()
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            try:
                await self.page.screenshot(path='login_error.png')
                logger.info("Saved error screenshot to login_error.png")
                content = await self.page.content()
                with open('page_content.html', 'w') as f:
                    f.write(content)
                logger.info("Saved page content to page_content.html")
            except Exception as se:
                logger.error(f"Failed to save debug info: {str(se)}")
            raise