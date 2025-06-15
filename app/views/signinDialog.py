import keyring
from PyQt6.QtCore import Qt, pyqtSignal
from qframelesswindow import FramelessWindow
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import (
    Theme,
    InfoBar,
    LineEdit,
    setTheme,
    CheckBox,
    BodyLabel,
    TitleLabel,
    PushButton,
    CaptionLabel,
    InfoBarPosition,
)


class SignInDialog(FramelessWindow):
    """Sign-in dialog using qfluentwidgets for modern UI"""

    signinRequested = pyqtSignal(str, str, bool)  # username, password, remember
    signupRequested = pyqtSignal()

    KEYRING_SERVICE = "NanokoClient"
    KEYRING_USERNAME_KEY = "username"
    KEYRING_PASSWORD_KEY = "password"
    KEYRING_REMEMBER_KEY = "remember"

    def __init__(self, parent=None):
        super().__init__(parent)
        setTheme(Theme.LIGHT)
        self.setupUi()
        self._loadSavedCredentials()

    def setupUi(self):
        """Set up the user interface using qfluentwidgets"""
        self.setWindowTitle("Nanoko")
        self.resize(400, 380)
        self.setMinimumSize(400, 380)
        self.setStyleSheet("background-color: #f5f5f5;")

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(40, 40, 40, 40)
        mainLayout.setSpacing(20)

        # Title
        titleLabel = TitleLabel("Sign in")
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        subtitleLabel = BodyLabel("Enter your username or email to sign in")
        subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitleLabel.setWordWrap(True)

        mainLayout.addWidget(titleLabel)
        mainLayout.addWidget(subtitleLabel)
        mainLayout.addSpacing(10)

        # Form container
        formWidget = QWidget()
        formLayout = QVBoxLayout(formWidget)
        formLayout.setSpacing(15)

        # Username
        usernameLabel = BodyLabel("Username")
        self.usernameInput = LineEdit()
        self.usernameInput.setPlaceholderText("Username or email")
        self.usernameInput.setClearButtonEnabled(True)

        formLayout.addWidget(usernameLabel)
        formLayout.addWidget(self.usernameInput)

        # Password
        passwordLabel = BodyLabel("Password")
        self.passwordInput = LineEdit()
        self.passwordInput.setPlaceholderText("Password")
        self.passwordInput.setEchoMode(LineEdit.EchoMode.Password)
        self.passwordInput.setClearButtonEnabled(True)

        formLayout.addWidget(passwordLabel)
        formLayout.addWidget(self.passwordInput)

        # Remember password checkbox
        self.rememberCheckbox = CheckBox("Remember password")

        formLayout.addWidget(self.rememberCheckbox)
        formLayout.addSpacing(15)

        # Sign in button
        self.signinButton = PushButton("Sign in")
        self.signinButton.clicked.connect(self.handleSignin)

        formLayout.addWidget(self.signinButton)

        mainLayout.addWidget(formWidget)
        mainLayout.addSpacing(20)

        # Sign up link
        signupLayout = QHBoxLayout()
        signupLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        signupText = CaptionLabel("Don't have an account?")

        signupLink = PushButton("Sign up")
        signupLink.clicked.connect(self.handleSignup)
        signupLink.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0078d4;
                text-decoration: underline;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #106ebe;
            }
        """)

        signupLayout.addWidget(signupText)
        signupLayout.addWidget(signupLink)

        mainLayout.addLayout(signupLayout)

        self.setLayout(mainLayout)

        self.usernameInput.setFocus()

        self.usernameInput.returnPressed.connect(self.handleSignin)
        self.passwordInput.returnPressed.connect(self.handleSignin)

    def _loadSavedCredentials(self):
        """Load saved credentials if they exist"""
        try:
            rememberEnabled = keyring.get_password(
                self.KEYRING_SERVICE, self.KEYRING_REMEMBER_KEY
            )
            if rememberEnabled == "true":
                username = keyring.get_password(
                    self.KEYRING_SERVICE, self.KEYRING_USERNAME_KEY
                )
                password = keyring.get_password(
                    self.KEYRING_SERVICE, self.KEYRING_PASSWORD_KEY
                )

                if username and password:
                    self.usernameInput.setText(username)
                    self.passwordInput.setText(password)
                    self.rememberCheckbox.setChecked(True)
        except Exception:
            pass

    def _saveCredentials(self, username, password):
        """Save credentials to keyring

        Args:
            username (str): The username to save
            password (str): The password to save
        """
        try:
            keyring.set_password(
                self.KEYRING_SERVICE, self.KEYRING_USERNAME_KEY, username
            )
            keyring.set_password(
                self.KEYRING_SERVICE, self.KEYRING_PASSWORD_KEY, password
            )
            keyring.set_password(
                self.KEYRING_SERVICE, self.KEYRING_REMEMBER_KEY, "true"
            )
        except Exception:
            InfoBar.warning(
                title="Warning",
                content="Could not save credentials",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=3000,
            )

    def _clearSavedCredentials(self):
        """Clear saved credentials from keyring"""
        try:
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME_KEY)
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_PASSWORD_KEY)
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_REMEMBER_KEY)
        except Exception:
            pass

    def showError(self, message):
        """Show error message using InfoBar"""
        InfoBar.error(
            title="Error",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def showInfo(self, message):
        """Show info message using InfoBar"""
        InfoBar.info(
            title="Info",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )

    def handleSignin(self):
        """Handle sign-in button click"""
        username = self.usernameInput.text().strip()
        password = self.passwordInput.text()
        remember = self.rememberCheckbox.isChecked()

        if not username or not password:
            self.showError("Please enter your username or email and password")
            self.usernameInput.setFocus()
            return

        if not remember:
            self._clearSavedCredentials()
        else:
            self._saveCredentials(username, password)

        self.signinRequested.emit(username, password, remember)

    def handleSignup(self):
        """Handle sign-up link click"""
        self.signupRequested.emit()
