import os
from datetime import datetime

import keyboard
from loguru import logger

from Browser import Browser

if __name__ == '__main__':
    browser = Browser().browser

    filedir = f'{os.getcwd()}/_screenshots'
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    browser.screenshot_dir = filedir


    def screenshot() -> None:
        """
        Take a screenshot of the current page
        """
        logger.debug('screenshot function called')
        filename = f'{filedir}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
        result = browser.save_screenshot(filename)
        if result:
            logger.success('screenshot saved successfully')
        else:
            logger.error('screenshot not saved')


    def quit_() -> None:
        """
        Quit the browser
        """
        logger.debug('shutdown function called')
        browser.quit()


    def load() -> None:
        """
        Load local default Vue server
        """
        logger.debug('load function called')
        # browser.execute_script("""
        #     alert('Please enter the website URL');
        # """)
        browser.get("http://localhost:4200")


    keyboard.add_hotkey('ctrl+shift+alt+l', load)
    keyboard.add_hotkey('ctrl+shift+alt+w', screenshot)
    keyboard.add_hotkey('ctrl+shift+alt+q', quit_)
    keyboard.wait('ctrl+shift+alt+q')
    keyboard.unhook_all()
