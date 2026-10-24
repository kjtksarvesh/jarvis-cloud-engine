import pyautogui
import os

def check_security_permission(command_name):
    """
    கமாண்ட் வரும்போதெல்லாம் ஸ்கிரீனில் பெர்மிஷன் கேட்கும் செக்யூரிட்டி சிஸ்டம்.
    """
    # உங்கள் லேப்டாப் ஸ்கிரீனில் தோன்றும் பாப்-அப் அலர்ட்
    response = pyautogui.confirm(
        text=f"JARVIS Security Alert:\n\nயாரோ கிளவுட் வழியாக '{command_name}' கமாண்டை இயக்க முயல்கிறார்கள்.\nஅனுமதிக்கலாமா?", 
        title="JARVIS System Access Request", 
        buttons=['Allow Access', 'Deny']
    )
    
    # நீங்கள் என்ன பட்டனை கிளிக் செய்கிறீர்கள் என்பதைப் பொறுத்து அனுமதி
    if response == 'Allow Access':
        print(f"JARVIS: Permission Granted for {command_name}")
        return True
    else:
        print(f"JARVIS: Access Denied for {command_name}")
        return False

# இதை உங்கள் கமாண்ட் லாஜிக்குடன் இணைக்கும் முறை (உதாரணம்):
def process_cloud_command(cmd_type, app_name):
    if cmd_type == "app_open":
        # ஆப்பை ஓபன் செய்யும் முன் பெர்மிஷன் கேட்கும்
        if check_security_permission(f"Open App - {app_name}"):
            print(f"Opening {app_name}...")
            os.system(f"start {app_name}") # விண்டோஸில் ஆப் ஓபன் செய்ய
        else:
            print("Access block trigger sent to UI.")
            # UI-க்கு "Access Denied by Boss" என்று மெசேஜ் அனுப்பலாம்
