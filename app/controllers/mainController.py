from nanoko import Nanoko
from PyQt6.QtCore import Qt
from nanoko.models.user import User
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import InfoBar, InfoBarPosition

from app.controllers.apiWorker import ApiWorker
from app.views.signinDialog import SignInDialog
from app.views.signupDialog import SignUpDialog
from app.views.studentMainWindow import StudentMainWindow
from app.views.teacherMainWindow import TeacherMainWindow
from app.controllers.studentController import StudentController
from app.controllers.teacherController import TeacherController


class MainController:
    """Main controller for the application"""

    def __init__(self):
        self.nanokoClient = Nanoko()

        self.signinDialog = None
        self.signupDialog = None
        self.mainWindow = None
        self.apiWorker = ApiWorker(self.nanokoClient)
        self.studentController = StudentController(self.apiWorker)
        self.teacherController = TeacherController(self.apiWorker)

        self.apiWorker.signInFinished.connect(self.handleSigninFinished)
        self.apiWorker.signUpFinished.connect(self.handleSignupFinished)

    def start(self):
        """Start the application by showing the sign-in dialog"""
        self.showSigninDialog()

    def showSigninDialog(self):
        """Show the sign-in dialog"""
        if self.signupDialog:
            self.signupDialog.close()
            self.signupDialog = None

        self.signinDialog = SignInDialog()
        self.signinDialog.show()

        self.signinDialog.signinRequested.connect(self.handleSignin)
        self.signinDialog.signupRequested.connect(self.showSignupDialog)

    def showSignupDialog(self):
        """Show the sign-up dialog"""
        if self.signinDialog:
            self.signinDialog.close()
            self.signinDialog = None

        self.signupDialog = SignUpDialog()
        self.signupDialog.show()

        self.signupDialog.signupRequested.connect(self.handleSignup)
        self.signupDialog.signinRequested.connect(self.showSigninDialog)

    def showMainWindow(self, user: User):
        """Show the main student dashboard window"""
        if self.signinDialog:
            self.signinDialog.close()
            self.signinDialog = None
        if self.signupDialog:
            self.signupDialog.close()
            self.signupDialog = None

        role = user.permission.name.lower().replace("admin", "student")
        if role == "student":
            self.mainWindow = StudentMainWindow(self.studentController)
            self.mainWindow.requestNewWindow.connect(self._createNewStudentWindow)
        elif role == "teacher":
            self.mainWindow = TeacherMainWindow(self.teacherController)

        self.mainWindow.show()

    def _createNewStudentWindow(self):
        """Create a new student window and close the current one"""
        if not self.mainWindow or not isinstance(self.mainWindow, StudentMainWindow):
            return

        current_geometry = self.mainWindow.geometry()
        old_window = self.mainWindow

        QApplication.setQuitOnLastWindowClosed(False)

        try:
            old_window.requestNewWindow.disconnect()
        except Exception:
            pass

        self.mainWindow = StudentMainWindow(self.studentController)
        self.mainWindow.requestNewWindow.connect(self._createNewStudentWindow)
        self.mainWindow.setGeometry(current_geometry)
        self.mainWindow.show()

        old_window.close()
        old_window.deleteLater()

        QApplication.setQuitOnLastWindowClosed(True)

    def showSuccessMessage(self, message, parentDialog):
        """Show success message using InfoBar"""
        if parentDialog:
            InfoBar.success(
                title="Success",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=parentDialog,
            )

    def showErrorMessage(self, message, parentDialog):
        """Show error message using InfoBar"""
        if parentDialog:
            InfoBar.error(
                title="Error",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=parentDialog,
            )

    def handleSignin(self, username, password, remember):
        """Handle sign-in request"""

        self.apiWorker.setup(
            operation="signin",
            username=username,
            password=password,
        )
        self.apiWorker.run()

    def handleSigninFinished(self, success, message, user):
        """Handle sign-in finished"""
        if success:
            self.showMainWindow(user)
        else:
            self.showErrorMessage(message, self.signinDialog)

    def handleSignup(self, username, firstName, lastName, email, role, password):
        """Handle sign-up request"""

        self.apiWorker.setup(
            operation="signup",
            username=username,
            firstName=firstName,
            lastName=lastName,
            email=email,
            role=role,
            password=password,
        )
        self.apiWorker.run()

    def handleSignupFinished(self, success, message):
        """Handle sign-up finished"""
        if success:
            self.showSuccessMessage(
                "Account created successfully! Please sign in.", self.signupDialog
            )

            if self.signupDialog:
                self.signupDialog.close()
                self.showSigninDialog()
        else:
            self.showErrorMessage(message, self.signupDialog)
