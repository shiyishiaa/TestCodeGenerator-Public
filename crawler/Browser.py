from pathlib import Path

from loguru import logger
from selenium.webdriver import Edge, EdgeOptions


class Browser:
    __instance = None
    __browser: Edge | None = None
    __options: EdgeOptions | None

    def __init__(self):
        self.__screenshot_dir = Path(__file__).parent / 'vue2-manage'
        if not self.__screenshot_dir.exists():
            self.__screenshot_dir.mkdir(parents=True, exist_ok=True)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Browser, cls).__new__(cls)
        return cls.__instance

    @property
    def browser(self) -> Edge:
        """
        See https://developer.chrome.com/docs/chromedriver/capabilities for more custom capabilities.
        """
        if not self.__browser:
            _options = EdgeOptions()
            # Incognito mode
            _options.add_argument('--inprivate')
            # Set agent
            _options.add_argument(
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/58.0.3029.110 Safari/537.3')
            # Set screen to 1600 * 800
            _options.add_argument('--window-size=1600,800')
            _options.add_argument("--force-dark-mode=false")  # Deprecated but sometimes works
            _options.add_argument("--enable-features=WebUIDarkMode")
            _options.add_argument("--disable-features=PrefersColorSchemeDark")  # Forces light mode
            _options.add_argument("--blink-settings=preferredColorScheme=1")  # 1=Light, 2=Dark
            # Open devtools automatically
            _options.add_argument('--auto-open-devtools-for-tabs')
            _options.add_experimental_option('prefs', {
                # Set devtools position
                'devtools.preferences.currentDockState': '"bottom"',
                # Set devtools shortcuts
                # 1. Ctrl + Alt + Shift + A: Capture node screenshot
                # 2. Ctrl + Alt + Shift + D: Capture area screenshot
                # 3. Ctrl + Alt + Shift + S: Capture full height screenshot
                'devtools.preferences.user-shortcuts': '[{"descriptors":[{"key":1857,'
                                                       '"name":"Ctrl + Alt + Shift + A"}],'
                                                       '"action":"emulation.capture-node-screenshot",'
                                                       '"type":"UserShortcut","keybindSets":{}},{"descriptors":[{'
                                                       '"key":1860,"name":"Ctrl + Alt + Shift + D"}],'
                                                       '"action":"elements.capture-area-screenshot",'
                                                       '"type":"UserShortcut","keybindSets":{}},{"descriptors":[{'
                                                       '"key":1875,"name":"Ctrl + Alt + Shift + S"}],'
                                                       '"action":"emulation.capture-full-height-screenshot",'
                                                       '"type":"UserShortcut","keybindSets":{}}]',
                # Set download directory
                'download.default_directory': str(self.__screenshot_dir),
            })
            self.__options = _options
            self.__browser = Edge(options=self.__options)
        return self.__browser

    @property
    def screenshot_dir(self) -> Path:
        logger.info(f'Screenshot directory: {self.__screenshot_dir}')
        return self.__screenshot_dir

    @screenshot_dir.setter
    def screenshot_dir(self, value: Path):
        self.__screenshot_dir = value
        logger.info(f'Screenshot directory set to {self.__screenshot_dir}')
