from ppadb.client import Client as AdbClient
import xml.etree.ElementTree as ET
import time
from datetime import datetime
import random

class AndroidAutomate():
    def __init__(self, package_name, device: None | str = None, debug_mode=True, last_user_interaction_username=str) -> None:
        self.package_name = package_name
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.debug_mode = debug_mode
        self.last_user_interaction_username = last_user_interaction_username 
    
    def DEBUG(self, message: str) -> str | None:
        if self.debug_mode:
            print(f"🛠️  [{datetime.now().strftime("%H:%M:%S")}] DEBUG >> {message}")

    def device_init(self, open: bool = False) -> object:
        devices = self.client.devices()
        for device in devices:
            if device.is_installed(self.package_name):
                self.DEBUG(f"{self.package_name} package found")
                if open:
                    device.shell(f"monkey -p {self.package_name} 1")
                    self.DEBUG(f"{self.package_name} package opened")
                return device

        raise RuntimeError(f"No device or package {self.package_name} installed was found.")
    
    def open_profile(self, device, username: str) -> None:
        self.DEBUG(F"Opening profile - {username}")
        device.shell(f"am start -a android.intent.action.VIEW -d \"https://www.instagram.com/{username}\"")

    def open_followers(self, device, root_xml) -> None:
        self.DEBUG("Going to followers")
        following_nodes = root_xml.findall(".//node[@text='followers']")
        for node in following_nodes:
            self.click(device, node.attrib.get("bounds"))
    
    def scroll_down(self, device) -> None:
        self.DEBUG("Scrolling down")
        device.shell(f"input swipe 500 800 300 300")

    def device_xml_content(self, device) -> ET.Element:
        device.shell("uiautomator dump /sdcard/view.xml")
        xml = device.shell("cat /sdcard/view.xml")
        root = ET.fromstring(xml)
        return root

    def get_all_followers(self, root_xml) -> list:
        self.DEBUG("Scrapping all followers")
        following_nodes = root_xml.findall(".//node[@text='Follow']")
        return following_nodes

    def click(self, device, bounds):
        bounds = bounds.replace('[', '').replace(']', ',').split(',')
        x1, y1, x2, y2 = map(int, bounds[:4])
        x = (x1 + x2) // 2
        y = (y1 + y2) // 2
        device.shell(f"input tap {x} {y}")

    @property
    def load_usernames(self) -> list[str]:
        with open("usernames.txt", 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    def in_blacklist(self, username) -> bool:
        with open("new_account_dialog_bypass.txt", "r") as f:
            usernames = f.read().split("\n")
            return username in usernames
        return False

    def add_to_blacklist(self, username) -> None:
        self.DEBUG("Adding to blacklist")
        if not self.in_blacklist(username):
            self.DEBUG("Added to blacklist")
            with open("new_account_dialog_bypass.txt", "w") as f:
                f.write(username + "\n")

    def bypass_follow_new_account_dialog(self, device, root_xml): # PASS "Review this account before following"
        cancel_button = root_xml.findall(".//node[@content-desc='Cancel']")
        if cancel_button:
            for node in cancel_button:
                self.add_to_blacklist(self.last_user_interaction_username)
                self.click(device, node.attrib.get("bounds"))
    
    def follow_list(self, device, following_nodes, time_interval) -> None:
        for node in following_nodes:
            if node.attrib.get("resource-id") == "com.instagram.android:id/follow_list_row_large_follow_button":
                    self.last_user_interaction_username = node.attrib.get("content-desc").split("Follow ")[-1]
                    if not self.in_blacklist(self.last_user_interaction_username):
                        self.DEBUG("Following: " + self.last_user_interaction_username)
                        self.click(device, node.attrib.get("bounds"))
                        time.sleep(time_interval)
        
    def fetch_more_followers(self, device, root_xml) -> None:
        self.DEBUG("Fetching more followers")
        see_more_button = root_xml.findall(".//node[@text='See More']")
        for node in see_more_button:
            self.click(device, node.attrib.get("bounds"))
    
def main():
    android = AndroidAutomate("com.instagram.android", debug_mode=True)
    device = android.device_init(open=True) 
    time.sleep(2)

    random_user = random.choice(android.load_usernames)
    android.open_profile(device, username=random_user)
    time.sleep(1)
    
    android.open_followers(device, android.device_xml_content(device))
    time.sleep(1)
    
    # loop
    while True:
        xml = android.device_xml_content(device)
        followers = android.get_all_followers(xml)
        android.follow_list(device, followers, random.randint(120, 240)) # follow one person each 2 min ~ 4 min
        android.scroll_down(device)
        xml = android.device_xml_content(device)
        android.bypass_follow_new_account_dialog(device, xml)
        android.fetch_more_followers(device, xml)

if __name__ == "__main__":
    main()