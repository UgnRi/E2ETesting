from playwright.async_api import Page
from utils.logger import setup_logger

logger = setup_logger()

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        
    async def wait_for_spinner(self):
        try:
            await self.page.wait_for_selector('[data-testid="loading-spinner"]', 
                                            state='visible', 
                                            timeout=5000)
            await self.page.wait_for_selector('[data-testid="loading-spinner"]', 
                                            state='hidden', 
                                            timeout=30000)
        except Exception as e:
            logger.warning(f"No spinner detected or timeout: {str(e)}")
