import random
import scraper.user_agent_generator as uag
# import UserAgentGenerator

class HeaderGenerator:
    """
    This class is responsible for generating HTTP headers for requests.
    """

    def __init__(self):
        self.random = random
        self.user_agent_generator = uag.UserAgentGenerator()
        self.base_header = {
            'host': 'apip.colruyt.be',
            'origin': "https://www.colruyt.be",
            'referer': "https://www.colruyt.be/",
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            "X-Cg-Apikey": "a8ylmv13-b285-4788-9e14-0f79b7ed2411",
        }
        self.accept_languages = [
            'en-GB,en-US;q=0.9,en;q=0.8',
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9",
            "fr-FR,fr;q=0.9",
            "de-DE,de;q=0.9",
            "es-ES,es;q=0.9",
            "it-IT,it;q=0.9",
            "ja-JP,ja;q=0.9",
            "zh-CN,zh;q=0.9"
        ]
        self.accepts = [
            "application/json, text/plain, */*",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "application/json",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "application/xml,application/json,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
        ]

    def generate(self):
        header = self.base_header.copy()
        header['user-agent'] = self.user_agent_generator.generate().strip()
        header['Accept-Language'] = self.random.choice(self.accept_languages).strip()
        header['Accept'] = self.random.choice(self.accepts).strip()
        header['accept-encoding'] = self._generate_accept_encoding().strip()
        return header

    def _generate_accept_encoding(self):
        encodings = ['gzip', 'deflate', 'br', 'identity']
        variations = [
            'gzip, deflate, br',
            'gzip, deflate',
            'br',
            'gzip',
            'deflate, br',
            'deflate',
            'identity',
            '*',  # Indicates that any encoding is acceptable.
        ]
        for _ in range(5):  # Generate 5 random combinations
            self.random.shuffle(encodings)
            variations.append(', '.join(encodings[:self.random.randint(1, len(encodings))]))
        return self.random.choice(variations)
