# -*- coding: utf-8 -*-
import sys
import os

# Add parent directory to path to import detector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector import SIM7600SMS

# Configuration
DESTINATION_NUMBERS = ["+639514343942"]  # Change to your phone number


def main() -> None:
	print("Testing SMS Functionality")
	
	modem = None
	try:
		modem = SIM7600SMS()
		print("SMS modem initialized successfully")
		
		# Send test SMS
		test_message = "Test SMS from Raspberry Pi - YOLOv5 Detection System"
		print(f"Sending test SMS to {DESTINATION_NUMBERS}")
		modem.send_sms(DESTINATION_NUMBERS, test_message)
		print("Test SMS sent successfully!")
		
	except Exception as e:
		print(f"SMS error: {e}")
		print("Make sure SIM7600 is connected and SIM card is inserted")
	finally:
		try:
			if modem is not None:
				modem.close()
				print("SMS connection closed")
		except Exception:
			pass


if __name__ == "__main__":
	main()
