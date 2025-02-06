# src/ui/pages/wireless_page.py
from .base_page import BasePage
from src.utils.logger import setup_logger

logger = setup_logger()

class BrokerPage(BasePage):
    def __init__(self, page, device_config):
        super().__init__(page)
        self.device_config = device_config

    async def navigate(self):
        """Navigate to Network → Wireless → SSIDs section"""
        try:
            url = f'https://{self.device_config["device"]["ip"]}/services/mqttt/broker'
            logger.info(f"Navigating to {url}")
            await self.page.goto(url)
            
            await self.page.wait_for_selector('[test-id="button-add"]')
            logger.info("Wireless page loaded")

        except Exception as e:
            logger.error(f"Failed to navigate to wireless page: {str(e)}")
            await self.page.screenshot(path='wireless_navigation_error.png')
            raise

    async def add_mqtt_broker(self, port):
        """Configure new wireless access point"""
        try:
            # Enable MQTT Broker
            # Check and Enable MQTT Broker if needed
            enable_switch = self.page.locator('[id="mosquitto.mqtt.mqtt.mqtt_enabled"]')
            await enable_switch.wait_for(state='visible', timeout=30000)
            switch_container = self.page.locator('div[aria-checked]').filter(has=enable_switch)
            is_enabled = await switch_container.get_attribute('aria-checked') == 'true'

            if not is_enabled:
                logger.info("MQTT Broker not enabled, enabling it now")
                await enable_switch.click(force=True)
            else:
                logger.info("MQTT Broker already enabled")
            #enable_switch = self.page.locator('[id="mosquitto.mqtt.mqtt.mqtt_enabled"]')
            #await enable_switch.click(force=True)

            # Input Port
            await self.page.click('[test-id="input-local_port_0"]')
            await self.page.keyboard.press('ControlOrMeta+A')
            await self.page.keyboard.press('Backspace')
            await self.page.keyboard.type(port)

            # Navigate to Misc.
            await self.page.click('[test-id="tab-miscellaneous"]')

            # Check and Enable Allow Anonymous if needed
            enable_anonymous = self.page.locator('[id="mosquitto.mqtt.mqtt.mqtt_anonymous_access"]')
            await enable_anonymous.wait_for(state='visible', timeout=30000)

            # Check parent div for the switch state
            anonymous_container = self.page.locator('div[test-id="switch-anonymous_access"]')
            is_anonymous_enabled = await anonymous_container.get_attribute('aria-checked') == 'true'

            if not is_anonymous_enabled:
                logger.info("Anonymous access not enabled, enabling it now")
                await enable_anonymous.click(force=True)
            else:
                logger.info("Anonymous access already enabled")

            # Save and Apply
            save_button = self.page.locator('[test-id="button-saveandapply"]')
            await save_button.click(force=True)
            
            
            await self.wait_for_spinner()

        except Exception as e:
            logger.error(f"Failed to configure MQTT Broker: {str(e)}")