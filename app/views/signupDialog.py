import re
from PyQt6.QtCore import Qt, pyqtSignal
from qframelesswindow import FramelessWindow
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QWidget
from qfluentwidgets import (
    Theme,
    InfoBar,
    LineEdit,
    ComboBox,
    setTheme,
    BodyLabel,
    TitleLabel,
    FluentIcon,
    PushButton,
    TeachingTip,
    CaptionLabel,
    InfoBarPosition,
    TransparentToolButton,
    TeachingTipTailPosition,
)


class SignUpDialog(FramelessWindow):
    """Sign-up dialog using qfluentwidgets for modern UI"""

    signupRequested = pyqtSignal(
        str, str, str, str, str, str
    )  # username, firstName, lastName, email, role, password
    signinRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        setTheme(Theme.LIGHT)
        self.setupUi()

    def setupUi(self):
        """Set up the user interface using qfluentwidgets"""
        self.setWindowTitle("Nanoko")
        self.resize(420, 400)
        self.setMinimumSize(420, 400)
        self.setStyleSheet("background-color: #f5f5f5;")

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(40, 40, 40, 40)
        mainLayout.setSpacing(20)

        # Title
        titleLabel = TitleLabel("Create an account")
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        subtitleLabel = BodyLabel("Enter your information to sign up")
        subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitleLabel.setWordWrap(True)

        mainLayout.addWidget(titleLabel)
        mainLayout.addWidget(subtitleLabel)
        mainLayout.addSpacing(10)

        formLayout = QFormLayout()
        formLayout.setSpacing(15)
        formLayout.setHorizontalSpacing(15)
        formLayout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        # Username
        usernameLabel = BodyLabel("Username:")
        self.usernameInput = LineEdit()
        self.usernameInput.setPlaceholderText("Username")
        self.usernameInput.setClearButtonEnabled(True)
        self.usernameInput.setMinimumWidth(200)

        formLayout.addRow(usernameLabel, self.usernameInput)

        # First name
        firstNameLabel = BodyLabel("First name:")
        self.firstNameInput = LineEdit()
        self.firstNameInput.setPlaceholderText("First name")
        self.firstNameInput.setClearButtonEnabled(True)
        self.firstNameInput.setMinimumWidth(200)

        formLayout.addRow(firstNameLabel, self.firstNameInput)

        # Last name
        lastNameLabel = BodyLabel("Last name:")
        self.lastNameInput = LineEdit()
        self.lastNameInput.setPlaceholderText("Last name")
        self.lastNameInput.setClearButtonEnabled(True)
        self.lastNameInput.setMinimumWidth(200)

        formLayout.addRow(lastNameLabel, self.lastNameInput)

        # Email
        emailLabel = BodyLabel("Email:")
        self.emailInput = LineEdit()
        self.emailInput.setPlaceholderText("Email address")
        self.emailInput.setClearButtonEnabled(True)
        self.emailInput.setMinimumWidth(200)

        formLayout.addRow(emailLabel, self.emailInput)

        # Role
        roleLabel = BodyLabel("Role:")
        self.roleCombo = ComboBox()
        self.roleCombo.addItems(["Student", "Teacher"])
        self.roleCombo.setCurrentText("Student")
        self.roleCombo.setMinimumWidth(200)

        formLayout.addRow(roleLabel, self.roleCombo)

        # Password
        passwordLabelWidget = QHBoxLayout()
        passwordLabel = BodyLabel("Password:")

        # Password requirements
        self.passwordInfoButton = TransparentToolButton(FluentIcon.INFO)
        self.passwordInfoButton.setFixedSize(20, 20)
        self.passwordInfoButton.clicked.connect(self.showPasswordRequirements)
        self.passwordInfoButton.setToolTip("Click to see password requirements")

        passwordLabelWidget.addWidget(passwordLabel)
        passwordLabelWidget.addWidget(self.passwordInfoButton)
        passwordLabelWidget.addStretch()

        passwordLabelContainer = QHBoxLayout()
        passwordLabelContainer.setContentsMargins(0, 0, 0, 0)
        passwordLabelContainer.addWidget(passwordLabel)
        passwordLabelContainer.addWidget(self.passwordInfoButton)
        passwordLabelContainer.addStretch()

        self.passwordInput = LineEdit()
        self.passwordInput.setPlaceholderText("Password")
        self.passwordInput.setEchoMode(LineEdit.EchoMode.Password)
        self.passwordInput.setClearButtonEnabled(True)
        self.passwordInput.setMinimumWidth(200)

        passwordLabelWidget = QHBoxLayout()
        passwordLabelWidget.setContentsMargins(0, 0, 0, 0)
        passwordLabelWidget.addWidget(passwordLabel)
        passwordLabelWidget.addWidget(self.passwordInfoButton)
        passwordLabelWidget.addStretch()

        passwordLabelContainer = QWidget()
        passwordLabelContainer.setLayout(passwordLabelWidget)

        formLayout.addRow(passwordLabelContainer, self.passwordInput)

        # Confirm Password
        confirmPasswordLabel = BodyLabel("Confirm Password:")
        self.confirmPasswordInput = LineEdit()
        self.confirmPasswordInput.setPlaceholderText("Password")
        self.confirmPasswordInput.setEchoMode(LineEdit.EchoMode.Password)
        self.confirmPasswordInput.setClearButtonEnabled(True)
        self.confirmPasswordInput.setMinimumWidth(200)

        formLayout.addRow(confirmPasswordLabel, self.confirmPasswordInput)

        mainLayout.addLayout(formLayout)
        mainLayout.addSpacing(20)

        # Sign up button
        self.signupButton = PushButton("Sign up")
        self.signupButton.clicked.connect(self.handleSignup)
        mainLayout.addWidget(self.signupButton)

        mainLayout.addSpacing(10)

        # Sign in link
        signinLayout = QHBoxLayout()
        signinLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        signinText = CaptionLabel("Already have an account?")

        signinLink = PushButton("Sign in")
        signinLink.clicked.connect(self.handleSignin)
        signinLink.setStyleSheet("""
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

        signinLayout.addWidget(signinText)
        signinLayout.addWidget(signinLink)

        mainLayout.addLayout(signinLayout)

        self.setLayout(mainLayout)

        self.usernameInput.setFocus()

        self.confirmPasswordInput.returnPressed.connect(self.handleSignup)

    def showPasswordRequirements(self):
        """Show password requirements in a teaching tip for better UX"""
        requirementsContent = """• At least 8 characters long
• Include uppercase letters (A-Z)
• Include lowercase letters (a-z)  
• Include numbers (0-9)
• Include symbols (!@#$%^&*...)"""

        TeachingTip.create(
            target=self.passwordInfoButton,
            icon=FluentIcon.INFO,
            title="Password Requirements",
            content=requirementsContent,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=3000,
            parent=self,
        )

    def isValidEmail(self, email):
        """Check if email format is valid"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def validateForm(self):
        """Validate all form fields"""
        username = self.usernameInput.text().strip()
        firstName = self.firstNameInput.text().strip()
        lastName = self.lastNameInput.text().strip()
        email = self.emailInput.text().strip()
        password = self.passwordInput.text()
        confirmPassword = self.confirmPasswordInput.text()

        if not username:
            self.showError("Please enter a username")
            self.usernameInput.setFocus()
            return False

        if not firstName:
            self.showError("Please enter your first name")
            self.firstNameInput.setFocus()
            return False

        if not lastName:
            self.showError("Please enter your last name")
            self.lastNameInput.setFocus()
            return False

        if not email:
            self.showError("Please enter your email address")
            self.emailInput.setFocus()
            return False

        if not self.isValidEmail(email):
            self.showError("Please enter a valid email address")
            self.emailInput.setFocus()
            return False

        if not password:
            self.showError("Please enter a password")
            self.passwordInput.setFocus()
            return False

        if len(password) < 8:
            self.showError("Password must be at least 8 characters long")
            self.passwordInput.setFocus()
            return False

        if not any(c.isupper() for c in password):
            self.showError("Password must include at least one uppercase letter")
            self.passwordInput.setFocus()
            return False

        if not any(c.islower() for c in password):
            self.showError("Password must include at least one lowercase letter")
            self.passwordInput.setFocus()
            return False

        if not any(c.isdigit() for c in password):
            self.showError("Password must include at least one number")
            self.passwordInput.setFocus()
            return False

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            self.showError("Password must include at least one symbol")
            self.passwordInput.setFocus()
            return False

        if password != confirmPassword:
            self.showError("Passwords do not match")
            self.confirmPasswordInput.setFocus()
            return False

        return True

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

    def handleSignup(self):
        """Handle sign-up button click"""
        if not self.validateForm():
            return

        username = self.usernameInput.text().strip()
        firstName = self.firstNameInput.text().strip()
        lastName = self.lastNameInput.text().strip()
        email = self.emailInput.text().strip()
        role = self.roleCombo.currentText()
        password = self.passwordInput.text()

        self.signupRequested.emit(username, firstName, lastName, email, role, password)

    def handleSignin(self):
        """Handle sign-in link click"""
        self.signinRequested.emit()
