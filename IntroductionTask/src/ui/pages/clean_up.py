from .base_page import BasePage
from ...utils.logger import setup_logger
logger = setup_logger()

class CleanUp(BasePage):
    def __init__(self, page):
        super().__init__(page)

    async def delete_wifi_interface(self, index=0):
        """
        Delete a specific WiFi interface by index
        
        :param index: Index of the interface to delete (default is 0, first interface)
        """
        try:
            await self.page.wait_for_timeout(5000)

            delete_buttons = self.page.locator('[test-id="button-delete"]')
            
            # Verify the index is valid
            total_buttons = await delete_buttons.count()
            if index >= total_buttons:
                return False
            
            # Select the specific delete button
            specific_delete_button = delete_buttons.nth(index)
            
            # Wait for the button to be visible and clickable
            await specific_delete_button.wait_for(state='visible')
            
            # Click the delete button
            await specific_delete_button.click()
            
            # Wait for and click confirmation dialog if it exists
            try:
                confirm_button = self.page.locator('[test-id="button-ok"]')
                await confirm_button.click()
                await self.page.wait_for_timeout(5000)
            except:
                pass
            
            return True
        
        except Exception as e:
            await self.page.screenshot(path='delete_interface_error.png')
            return False