from .base_page import BasePage
from src.utils.logger import setup_logger

logger = setup_logger()

class DTSPage(BasePage):
    def __init__(self, page, device_config):
        super().__init__(page)
        self.device_config = device_config

        
    async def navigate(self):
        """Navigate to Services → Data to Server """
        try:
            url = f'https://{self.device_config["device"]["ip"]}/services/data_sender'
            logger.info(f"Navigating to {url}")
            await self.page.goto(url)
            # Wait for multiple possible indicators of page load
            await self.page.wait_for_selector('[test-id="button-add"]', timeout=30000)
            logger.info("Successfully navigated to Data to Server page")
        except Exception as e:
            logger.error(f"Failed to navigate to Data to Server page: {str(e)}")
            await self.page.screenshot(path='wireless_navigation_error.png')
            raise

    async def add_new_instance(self, instanceName, period, mqttServer, mqttTopic, clientID):
        """Create new DTS instance"""
        try:
            logger.info(f"Starting to add new DTS instance with name: {instanceName}")
            
            # Set name
            logger.info("Setting instance name")
            await self.page.click('[test-id="input-name"]')
            await self.page.keyboard.type(instanceName)
            
            # Press add
            logger.info("Clicking add button")
            try:
                # Get all add buttons
                add_buttons = self.page.locator("[test-id='button-add']")
                # Get count of buttons
                count = await add_buttons.count()
                if count > 0:
                    # Click the last button (index is count-1)
                    await add_buttons.nth(count - 1).click()
                    logger.info(f"Successfully clicked last add button (index {count-1})")
                else:
                    raise Exception("No add buttons found")
            except Exception as e:
                logger.error(f"Failed to click add button: {str(e)}")
                raise

            # Next
            logger.info("Clicking next button")
            try:
                save_button = self.page.locator('div[test-id="modal-container"] button[test-id="button-next"]')
                await save_button.click()
                logger.info("Successfully clicked next button")
            except Exception as e:
                logger.error(f"Failed to click next button: {str(e)}")
                raise

            # Set Period
            logger.info(f"Setting period: {period}")
            try:
                period_input = self.page.locator('[test-id="input-period"]')
                await self.page.wait_for_timeout(1000)
                
                # Select all existing text and delete it
                await period_input.click()
                await self.page.keyboard.press('Control+A')
                await self.page.keyboard.press('Backspace')
                
                # Now type the new period
                await period_input.type(period)
                logger.info("Successfully set period")
            except Exception as e:
                logger.error(f"Failed to set period: {str(e)}")
                raise

            # Next
            logger.info("Clicking next button after period")
            try:
                save_button = self.page.locator('div[test-id="modal-container"] button[test-id="button-next"]')
                await save_button.click()
                logger.info("Successfully clicked next button after period")
            except Exception as e:
                logger.error(f"Failed to click next button after period: {str(e)}")
                raise

            # Set MQTT
            logger.info("Setting MQTT plugin")
            try:
                # Click the dropdown to open it
                dropdown_button = self.page.locator('#section-server-configuration [test-id="input-plugin"]')
                await dropdown_button.wait_for(state='visible', timeout=30000)
                await dropdown_button.click()
                logger.info("Clicked plugin dropdown")
                
                # Wait for dropdown list to be visible and stable
                await self.page.wait_for_timeout(1000)  # Give UI time to fully render dropdown
                
                # Click MQTT option directly with improved locator
                mqtt_option = self.page.get_by_role("option", name="MQTT", exact=True)
                await mqtt_option.wait_for(state='visible', timeout=30000)
                await mqtt_option.click()
                
                # Verify the selection took effect
                await self.page.wait_for_timeout(1000)
                logger.info("Successfully set MQTT plugin")

            except Exception as e:
                logger.error(f"Failed to set MQTT plugin: {str(e)}")
                await self.page.screenshot(path='mqtt_select_error.png')
                
                # Debug info
                try:
                    logger.debug("Checking visible elements:")
                    visible_options = await self.page.locator('li[test-id^="selectoption-"]').all()
                    for option in visible_options:
                        text = await option.text_content()
                        logger.debug(f"Found option: {text}")
                except Exception as debug_e:
                    logger.debug(f"Debug check failed: {debug_e}")
                raise

            # Set Server Address
            logger.info(f"Setting MQTT server address: {mqttServer}")
            try:
                address_input = self.page.locator('input[test-id="input-mqtt_host"]')
                await address_input.type(mqttServer)
                logger.info("Successfully set server address")
            except Exception as e:
                logger.error(f"Failed to set server address: {str(e)}")
                raise

            # Set Topic
            logger.info(f"Setting MQTT topic: {mqttTopic}")
            try:
                topic_input = self.page.locator('input[test-id="input-mqtt_topic"]')
                await topic_input.type(mqttTopic)
                logger.info("Successfully set MQTT topic")
            except Exception as e:
                logger.error(f"Failed to set MQTT topic: {str(e)}")
                raise

            # Set Client ID
            logger.info(f"Setting Client ID: {clientID}")
            try:
                ID_input = self.page.locator('input[test-id="input-mqtt_client_id"]')
                await ID_input.type(clientID)
                logger.info("Successfully set Client ID")
            except Exception as e:
                logger.error(f"Failed to set Client ID: {str(e)}")
                raise

            # Set QoS
            try:
                # Click the dropdown to open it
                dropdown_button = self.page.locator('#section-server-configuration [test-id="input-mqtt_qos"]')
                await dropdown_button.wait_for(state='visible', timeout=30000)
                await dropdown_button.click()
                logger.info("Clicked QoS dropdown")
                
                # Wait for dropdown list to be visible and stable
                await self.page.wait_for_timeout(1000)  # Give UI time to fully render dropdown
                
                # Click MQTT option directly with improved locator
                mqtt_option = self.page.get_by_role("option", name="1", exact=True)
                await mqtt_option.wait_for(state='visible', timeout=30000)
                await mqtt_option.click()
                
                # Verify the selection took effect
                await self.page.wait_for_timeout(1000)  # Wait for UI to update
                logger.info("Successfully set QoS")

            except Exception as e:
                logger.error(f"Failed to set QoS: {str(e)}")
                await self.page.screenshot(path='mqtt_select_error.png')
                
                # Debug info
                try:
                    logger.debug("Checking visible elements:")
                    visible_options = await self.page.locator('li[test-id^="selectoption-"]').all()
                    for option in visible_options:
                        text = await option.text_content()
                        logger.debug(f"Found option: {text}")
                except Exception as debug_e:
                    logger.debug(f"Debug check failed: {debug_e}")
                raise

            # Save
            logger.info("Saving configuration")
            try:
                save_button = self.page.locator('div[test-id="modal-container"] button[test-id="button-next"]')
                await save_button.click()
                logger.info("Successfully clicked save button")
            except Exception as e:
                logger.error(f"Failed to click save button: {str(e)}")
                raise

            # Wait for changes to apply
            logger.info("Waiting for changes to apply")
            await self.page.wait_for_timeout(5000)
            await self.wait_for_spinner()
            logger.info("Successfully completed adding new DTS instance")

        except Exception as e:
            logger.error(f"Failed to add new DTS instance: {str(e)}")
            await self.page.screenshot(path='lan_config_error.png')
            html = await self.page.content()
            with open('lan_error_content.html', 'w') as f:
                f.write(html)
            raise