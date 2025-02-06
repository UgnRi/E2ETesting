# src/ui/pages/wireless_page.py
from .base_page import BasePage
from ...utils.logger import setup_logger

logger = setup_logger()

class WirelessPage(BasePage):
    def __init__(self, page, device_config):
        super().__init__(page)
        self.device_config = device_config

    async def navigate(self):
        """Navigate to Network → Wireless → SSIDs section"""
        try:
            url = f'https://{self.device_config["device"]["ip"]}/network/wireless/ssids'
            logger.info(f"Navigating to {url}")
            await self.page.goto(url)
            
            await self.page.wait_for_selector('[test-id="button-add"]')
            logger.info("Wireless page loaded")

        except Exception as e:
            logger.error(f"Failed to navigate to wireless page: {str(e)}")
            await self.page.screenshot(path='wireless_navigation_error.png')
            raise

    async def add_wireless_ap(self, ssid, password, lan_interface_name):
        """Configure new wireless access point"""
        try:
            # Click add button
            await self.page.click('[test-id="button-add"]')
            logger.info("Clicked add wireless button")
            await self.wait_for_spinner()

            # Wait for modal to load
            await self.page.wait_for_selector('[test-id="input-ssid"]')
            logger.info("Modal loaded")

            # Press Enable
            #enable_checkbox = self.page.locator('div[test-id="modal-container"] div[test-id="switch-enabled"] input[type="checkbox"]')
            #await enable_checkbox.wait_for(state="visible")
            #await enable_checkbox.click(force=True)
            #logger.info("Pressed enabled switch")

            # Fill SSID settings in modal
            await self.page.fill('[test-id="input-ssid"]', ssid)
            await self.page.fill('[test-id="input-key"]', password)
            logger.info("Filled SSID and password")

            # Select the network (LAN interface)
            await self.page.click('[test-id="input-network"]')
            await self.page.click('[test-id="button-network"]')
            await self.page.keyboard.type(lan_interface_name)
            logger.info(f"Selected network interface: {lan_interface_name}") 

            # Save the wireless configuration
            await self.page.click('[test-id="button-network"]')
            save_button = self.page.locator('div[test-id="modal-container"] button[test-id="button-saveandapply"]')
            await save_button.click()
            logger.info("Clicked Save & Apply button inside modal")
            
            await self.page.wait_for_timeout(5000)
            logger.info("Waiting for changes to apply")
            
            await self.wait_for_spinner()

        except Exception as e:
            logger.error(f"Failed to configure wireless AP: {str(e)}")
            await self.page.screenshot(path='wireless_config_error.png')
            html = await self.page.content()
            with open('wireless_error_content.html', 'w') as f:
                f.write(html)
            raise