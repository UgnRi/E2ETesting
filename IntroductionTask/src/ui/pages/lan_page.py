from .base_page import BasePage
from ...utils.logger import setup_logger
logger = setup_logger()

class LanPage(BasePage):
    def __init__(self, page, device_config):
        super().__init__(page)
        self.device_config = device_config

    async def navigate(self):
        """Navigate to Network → Wireless → SSIDs section"""
        try:
            url = f'https://{self.device_config["device"]["ip"]}/network/wireless/ssids'
            logger.info(f"Navigating to {url}")
            await self.page.goto(url)

            
            # Wait for multiple possible indicators of page load
            await self.page.wait_for_selector('[test-id="button-add"]', timeout=30000)

            # Enable 
            enable_switch = self.page.locator('[id="wireless.wifi-iface.1.1_enabled"]')
            await enable_switch.click(force=True)


            # Save
            await self.page.click('[test-id="button-saveandapply"]')


        except Exception as e:

            await self.page.screenshot(path='wireless_navigation_error.png')
            raise

    async def add_lan_interface(self, lan_config):
        """Create new LAN interface"""
        try:

            
            # Set name
            await self.page.fill('[test-id="input-name"]', lan_config['name'])

            
            # Set IP address
            await self.page.fill('[test-id="input-ipaddr"]', lan_config['ip_address'])

            
            # Click DHCPv4 Switch
            dhcp_checkbox = self.page.locator('div[test-id="modal-container"] div[test-id="switch-enable_dhcpv4"] input[type="checkbox"]')
            await dhcp_checkbox.click(force=True)

            
            # Click Save & Apply
            save_button = self.page.locator('div[test-id="modal-container"] button[test-id="button-saveandapply"]')
            await save_button.click()

            
            # Wait for changes to apply
            await self.page.wait_for_timeout(5000)
            await self.wait_for_spinner()
            
        except Exception as e:
            await self.page.screenshot(path='lan_config_error.png')
            html = await self.page.content()
            with open('lan_error_content.html', 'w') as f:
                f.write(html)
            raise