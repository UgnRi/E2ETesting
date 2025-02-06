from ..utils.logger import setup_logger
from .ssh_client import SSHClient
import subprocess
import asyncio
import json
import paho.mqtt.client as mqtt
from threading import Event

logger = setup_logger()

class WirelessValidator:
   def __init__(self, device_config):
       self.ssh_client = SSHClient(device_config)
       self.message_received = Event()
       self.last_message = None

   def on_message(self, client, userdata, message):
       """Callback when MQTT message is received"""
       try:
           self.last_message = json.loads(message.payload.decode())
           self.message_received.set()
       except json.JSONDecodeError as e:
           logger.error(f"Failed to parse MQTT message: {str(e)}")
       except Exception as e:
           logger.error(f"Error in MQTT callback: {str(e)}")

   async def validate_mqtt_message(self, expected_name, expected_topic, mqtt_server, timeout=60):
        """
        Validate MQTT message by using mosquitto_sub command
        Wait up to 60 seconds for a message, return False if no message received
        """
        try:
            # Construct the full command as a string
            command = f"mosquitto_sub -h {mqtt_server} -p 1883 -t {expected_topic} -C 1 -W {timeout}"
            
            logger.info(f"Running command: {command}")
            
            # Create a future to track the subprocess
            process_future = asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for the process with a timeout
            try:
                # Await the process with a timeout
                process = await asyncio.wait_for(process_future, timeout=timeout)
                
                # Wait for the process to complete
                stdout, stderr = await process.communicate()
                
                # Decode outputs
                stdout_str = stdout.decode('utf-8').strip()
                stderr_str = stderr.decode('utf-8').strip()
                
                # Log outputs
                if stdout_str:
                    logger.info(f"Received message: {stdout_str}")
                    return True
                
                if stderr_str:
                    logger.error(f"MQTT Subscription Errors: {stderr_str}")
                
                logger.error("No message received within timeout period")
                return False
            
            except asyncio.TimeoutError:
                logger.error(f"MQTT message retrieval timed out after {timeout} seconds")
                return False
        
        except Exception as e:
            logger.error(f"MQTT validation failed: {str(e)}")
            return False

   async def validate_ap_config(self, config):
       try:
           await self.ssh_client.connect()

           # Check MQTT broker configuration
           mqtt_enabled = await self.ssh_client.execute_command(
               "uci show mosquitto.mqtt.enabled"
           )
           mqtt_port = await self.ssh_client.execute_command(
               "uci show mosquitto.mqtt.local_port"
           )
           mqtt_anonymous = await self.ssh_client.execute_command(
               "uci show mosquitto.mqtt.anonymous_access"
           )

           # Check MQTT broker process
           mqtt_process = await self.ssh_client.execute_command(
               "ps | grep mosquitto | grep -v grep"
           )

           # Check Data to Server configuration
           dts_instance = await self.ssh_client.execute_command(
               f"uci show data_sender.1.name='{config['instanceName']}'"
           )
           dts_enabled = await self.ssh_client.execute_command(
               "uci show data_sender.1.enabled"
           )
           dts_period = await self.ssh_client.execute_command(
               f"uci show data_sender.1.period"
           )

           # Check MQTT output configuration
           mqtt_server = await self.ssh_client.execute_command(
               f"uci show data_sender.2.mqtt_host"
           )
           mqtt_topic = await self.ssh_client.execute_command(
               f"uci show data_sender.2.mqtt_topic"
           )
           mqtt_client_id = await self.ssh_client.execute_command(
               f"uci show data_sender.2.mqtt_client_id"
           )
           mqtt_qos = await self.ssh_client.execute_command(
               "uci show data_sender.2.mqtt_qos"
           )

           # Check logread for any errors
           log_errors = await self.ssh_client.execute_command(
               "logread | grep -i 'mqtt\\|data_sender' | grep -i 'error\\|fail' | tail -n 20"
           )

           # Add MQTT message validation
           mqtt_message_valid = await self.validate_mqtt_message(
               expected_name=config['instanceName'],
               expected_topic=config['mqttTopic'],
               mqtt_server=config['mqttServer']
           )

           # Detailed logging of raw results
           logger.info(f"MQTT Broker Enabled Check: {mqtt_enabled}")
           logger.info(f"MQTT Port Check: {mqtt_port}")
           logger.info(f"MQTT Anonymous Access Check: {mqtt_anonymous}")
           logger.info(f"MQTT Process Check: {mqtt_process}")
           logger.info(f"Data to Server Instance Check: {dts_instance}")
           logger.info(f"Data to Server Enabled Check: {dts_enabled}")
           logger.info(f"Data to Server Period Check: {dts_period}")
           logger.info(f"MQTT Server Check: {mqtt_server}")
           logger.info(f"MQTT Topic Check: {mqtt_topic}")
           logger.info(f"MQTT Client ID Check: {mqtt_client_id}")
           logger.info(f"MQTT QoS Check: {mqtt_qos}")
           logger.info(f"Log Errors: {log_errors}")

           # Determine success based on expected values
           success = all([
               "'1'" in mqtt_enabled,  # MQTT broker enabled
               f"'{config['port']}'" in mqtt_port,  # Port matches config
               "'1'" in mqtt_anonymous,  # Anonymous access enabled
               mqtt_process and "mosquitto" in mqtt_process,  # Process running
               "'1'" in dts_enabled,  # DTS enabled
               dts_period and config['period'] in dts_period,  # Period matches
               mqtt_server and config['mqttServer'] in mqtt_server,  # Server matches
               mqtt_topic and config['mqttTopic'] in mqtt_topic,  # Topic matches
               mqtt_client_id and config['clientID'] in mqtt_client_id,  # Client ID matches
               "'1'" in mqtt_qos,  # QoS set to 1
               log_errors,  # No errors in logs
               mqtt_message_valid  # Message validation
           ])

           return {
               'success': success,
               'details': {
                   'mqtt_broker_enabled': "'1'" in mqtt_enabled,
                   'mqtt_port_correct': f"'{config['port']}'" in mqtt_port,
                   'mqtt_anonymous_enabled': "'1'" in mqtt_anonymous,
                   'mqtt_process_running': bool(mqtt_process and "mosquitto" in mqtt_process),
                   'dts_enabled': "'1'" in dts_enabled,
                   'period_correct': bool(dts_period and config['period'] in dts_period),
                   'mqtt_server_correct': bool(mqtt_server and config['mqttServer'] in mqtt_server),
                   'mqtt_topic_correct': bool(mqtt_topic and config['mqttTopic'] in mqtt_topic),
                   'mqtt_client_id_correct': bool(mqtt_client_id and config['clientID'] in mqtt_client_id),
                   'mqtt_qos_correct': "'1'" in mqtt_qos,
                   'no_errors_in_logs': not bool(log_errors),
                   'mqtt_message_received': mqtt_message_valid,
                   'raw_results': {
                       'mqtt_enabled': mqtt_enabled,
                       'mqtt_port': mqtt_port,
                       'mqtt_anonymous': mqtt_anonymous,
                       'mqtt_process': mqtt_process,
                       'dts_instance': dts_instance,
                       'dts_enabled': dts_enabled,
                       'dts_period': dts_period,
                       'mqtt_server': mqtt_server,
                       'mqtt_topic': mqtt_topic,
                       'mqtt_client_id': mqtt_client_id,
                       'mqtt_qos': mqtt_qos,
                       'log_errors': log_errors,
                       'mqtt_message': mqtt_message_valid
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
           try:
               await self.ssh_client.close()
           except:
               pass