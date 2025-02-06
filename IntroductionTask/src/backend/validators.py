from ..utils.logger import setup_logger
from .ssh_client import SSHClient
logger = setup_logger()

class WirelessValidator:
    def __init__(self, device_config):
        # Create SSHClient with the full configuration
        self.ssh_client = SSHClient(device_config)

    async def validate_ap_config(self, config):
        try:
            # Ensure connection is established
            await self.ssh_client.connect()

            # Validate SSID configuration
            ssid_result = await self.ssh_client.execute_command(
                f"uci show wireless | grep \"ssid='{config['ssid']}'\" "
            )
            
            # Validate LAN interface existence
            lan_result = await self.ssh_client.execute_command(
                f"uci show network | grep {config['lan_interface']['name']}"
            )
            
            # Validate IP address configuration
            ip_result = await self.ssh_client.execute_command(
                f"uci show network | grep \"ipaddr='{config['lan_interface']['ip_address']}'\" "
            )
            
            # Validate Subnet Mask
            subnet_result = await self.ssh_client.execute_command(
                f"uci show network | grep \"netmask='{config['lan_interface']['subnet_mask']}'\" "
            )
            
            # Validate DHCP configuration
            # Check DHCP interface configuration
            dhcp_interface_result = await self.ssh_client.execute_command(
                f"uci show dhcp | grep ifLan1"
            )
        
            # More robust process check
            process_result = await self.ssh_client.execute_command(
                "ps | grep -E 'hostapd|wpa_supplicant'"
            )
            
            # Detailed logging of raw results
            logger.info(f"SSID Check Result: {ssid_result}")
            logger.info(f"LAN Interface Check Result: {lan_result}")
            logger.info(f"IP Address Check Result: {ip_result}")
            logger.info(f"Subnet Mask Check Result: {subnet_result}")
            logger.info(f"DHCP Interface Check Result: {dhcp_interface_result}")
            logger.info(f"Process Check Result: {process_result}")

            # Determine success
            success = all([
                ssid_result,              # SSID configured
                lan_result,               # LAN interface exists
                ip_result,                # IP address matches
                subnet_result,            # Subnet mask matches
                dhcp_interface_result,    # DHCP interface configured
                process_result            # Wireless processes running
            ])
            
            return {
                'success': success,
                'details': {
                    'ssid_config': bool(ssid_result),
                    'lan_interface': bool(lan_result),
                    'ip_address': bool(ip_result),
                    'subnet_mask': bool(subnet_result),
                    'dhcp_interface': bool(dhcp_interface_result),
                    'process_running': bool(process_result),
                    'raw_results': {
                        'ssid': ssid_result,
                        'lan': lan_result,
                        'ip': ip_result,
                        'subnet': subnet_result,
                        'dhcp_interface': dhcp_interface_result,
                        'process': process_result
                    }
                }
            }
        
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {
                'success': False,
                'details': str(e)
            }
        finally:
            # Ensure SSH connection is closed
            try:
                await self.ssh_client.close()
            except:
                pass