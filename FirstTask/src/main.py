import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from ui.pages.data_to_server_page import DTSPage
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger
from src.utils.result_writer import ResultWriter
from src.ui.pages.login_page import LoginPage
from ui.pages.broker_page import BrokerPage
from src.backend.validators import WirelessValidator
from src.ui.pages.clean_up import CleanUp

logger = setup_logger()

async def run_test_scenario(page, device_config, scenario_config):
    try:
        
        # Initialize pages
        login_page = LoginPage(page)
        data_to_server_page = DTSPage(page)
        broker_page = BrokerPage(page)
        clean_up = CleanUp(page)
        
        # Login to device
        await login_page.login(
            device_config['device']['credentials']['username'],
            device_config['device']['credentials']['password']
        )
        

        await broker_page.navigate()
        await broker_page.add_mqtt_broker(
            scenario_config['config']['port'],
        )
        
        await data_to_server_page.navigate()
        await data_to_server_page.add_new_instance(
            scenario_config['config']['instanceName'],
            scenario_config['config']['period'],
            scenario_config['config']['mqttServer'],
            scenario_config['config']['mqttTopic'],
            scenario_config['config']['clientID'],
        )
        
        # Create validator with the device configuration
        validator = WirelessValidator(device_config)
        
        # Validate configuration
        validation_result = await validator.validate_ap_config(
            scenario_config['config']
        )

        # Clean Up
        await clean_up.delete_wifi_interface()
        
        return {
            'scenario': scenario_config['scenario_name'],
            'status': 'PASS' if validation_result['success'] else 'FAIL',
            'details': validation_result.get('details', '')
        }
    except Exception as e:
        return {
            'scenario': scenario_config['scenario_name'],
            'status': 'FAIL',
            'details': str(e)
        }

async def main():
    # Load configurations
    device_config = load_config('config/device_config.json')
    
    # Generate result file name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f"{device_config['device']['name']}_{timestamp}_" \
                  f"{device_config['device']['modem']}_{device_config['device']['firmware']}.csv"
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=False,
            slow_mo=100,
            args=['--ignore-certificate-errors']
        )
        context = await browser.new_context(
            ignore_https_errors=True,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            for scenario_name in device_config['test_scenarios']:
                scenario_config = load_config(f'config/test_scenarios/{scenario_name}.json')
                result = await run_test_scenario(page, device_config, scenario_config)
                results.append(result)
        
        except Exception as e:
            await asyncio.sleep(10)  # Keep browser open for 10 seconds on error
            raise
        
        finally:
            await browser.close()
    
    # Write results
    result_writer = ResultWriter(result_file)
    result_writer.write_results(results)

if __name__ == "__main__":
    asyncio.run(main())