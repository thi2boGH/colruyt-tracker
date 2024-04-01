import random

class UserAgentGenerator:
    """
    This class is responsible for generating random user-agent strings.
    """

    def __init__(self):
 
        self.random = random
        self.mac_os_versions = [f'10_{i}_{j}' for i in range(14, 16) for j in range(0, 10)]
        self.chrome_versions = [f'{i}.0.0.0' for i in range(118, 123)]
        self.opera_versions = [f'{i}.0.0.0' for i in range(104, 109)]
        self.safari_versions = ['605.1.15', '606.1.14', '607.1.40']
        self.windows_versions = ['10.0', '6.1', '6.2', '6.3']
        self.windows_chrome_versions = [f'{i}.0.0.0' for i in range(121, 131)]

    def generate(self):
        platform = self.random.choice(['macOS', 'Windows'])

        if platform == 'macOS':
            return self._generate_macos_user_agent()
        else:
            return self._generate_windows_user_agent()

    def _generate_macos_user_agent(self):
        mac_os_version = self.random.choice(self.mac_os_versions)
        browser_choice = self.random.choice(['Opera', 'Safari'])

        if browser_choice == 'Opera':
            chrome_version = self.random.choice(self.chrome_versions)
            opera_version = self.random.choice(self.opera_versions)
            return f'Mozilla/5.0 (Macintosh; Intel Mac OS X {mac_os_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36 OPR/{opera_version}'
        else:  # Safari
            safari_version = self.random.choice(self.safari_versions)
            return f'Mozilla/5.0 (Macintosh; Intel Mac OS X {mac_os_version}) AppleWebKit/{safari_version} (KHTML, like Gecko) Version/{self.random.choice(["17.0", "17.1", "17.2"])} Safari/{safari_version}'

    def _generate_windows_user_agent(self):
        windows_version = self.random.choice(self.windows_versions)
        chrome_version = self.random.choice(self.windows_chrome_versions)
        return f'Mozilla/5.0 (Windows NT {windows_version}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'