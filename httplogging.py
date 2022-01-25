import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class HttpHandler(logging.Handler):
    def __init__(self, url: str, silent: bool= True, level_specific: bool= False):

        self.url    = url
        self.silent = silent

        # Set default auth
        self.auth = False

        # Set default telegram_chat_id
        self.setTelegramChatId()
        
        # If set to True, this handler ignores lower-level records
        # For example, if level_specific=True and the level is set to 
        # logging.CRITICAL, this handle will ignore logging.ERROR records
        self.level_specific = level_specific

        # Create and set up server session
        self.session = requests.Session()
        self._setup_session()

        super().__init__()
        

    def _setup_session(self):
        '''Sets up the session with the server'''

        self.session.headers.update({
            'Content-Type': 'application/json',
        })

        self.session.mount('https://', HTTPAdapter(
            max_retries=Retry(
                total=5,
                backoff_factor=0.05,
                status_forcelist=[403, 500]
            ),
            pool_connections=100,
            pool_maxsize=100
        ))

    def setCredentials(self, username: str, password: str):
        self.auth     = True
        self.username = username
        self.password = password

    def setTelegramChatId(self, chat_id="0"):
        self.telegram_chat_id = chat_id

    def setLevel(self, level):
        super().setLevel(level)
        self.fixed_level = level
        

    def emit(self, record):
        '''Sends the record in a POST request to the specified url'''

        # Ignore lower-level records if self.level_specific
        if self.level_specific:
            if record.levelno != self.fixed_level:
                return

        logEntry = self.format(record)

        if self.auth:
            username = self.username + "@" + self.telegram_chat_id
            password = self.password

            response = r = self.session.post(self.url, 
                                        data=logEntry, 
                                        auth=(username, password))
        else:
            response = r = self.session.post(self.url, data=logEntry)

        if not self.silent:
            print(f"Response: {r.status_code} - {r._content.decode('utf-8')}")
            