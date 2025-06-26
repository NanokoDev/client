from datetime import datetime
from PyQt6.QtGui import QColor
from typing import Optional, List
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QEasingCurve
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)
from qfluentwidgets import (
    Theme,
    InfoBar,
    LineEdit,
    setTheme,
    CheckBox,
    BodyLabel,
    InfoBadge,
    CardWidget,
    TitleLabel,
    FlowLayout,
    PushButton,
    FluentIcon,
    ImageLabel,
    CaptionLabel,
    SplashScreen,
    FluentWindow,
    ProgressRing,
    PlainTextEdit,
    SubtitleLabel,
    StrongBodyLabel,
    InfoBarPosition,
    SmoothScrollArea,
    PrimaryPushButton,
    TransparentToolButton,
)

from app.utils import levelToColor, cropImageToSquare
from app.controllers.studentController import StudentController


class ClassCard(CardWidget):
    """Unified class card containing all assignments"""

    def __init__(self, className: str, assignments: list, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self.setFixedSize(QSize(380, 200))

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Class name
        self.title = SubtitleLabel(className)
        self.title.setStyleSheet("color: #333333; font-weight: 600; font-size: 18px;")
        layout.addWidget(self.title)

        # Assignments
        self.assignments = assignments

        for assignmentName, dueDate in self.assignments:
            assignmentLayout = QHBoxLayout()
            assignmentLayout.setContentsMargins(0, 5, 0, 5)

            bullet = BodyLabel("•")
            bullet.setStyleSheet("color: #333333; font-weight: bold; font-size: 16px;")
            bullet.setFixedWidth(5)

            nameLabel = BodyLabel(assignmentName)
            nameLabel.setStyleSheet("color: #333333; font-weight: 500;")

            dueLabel = BodyLabel(f"Due at {dueDate}")
            dueLabel.setStyleSheet("color: #666666;")

            assignmentLayout.addWidget(bullet)
            assignmentLayout.addWidget(nameLabel)
            assignmentLayout.addStretch()
            assignmentLayout.addWidget(dueLabel)

            layout.addLayout(assignmentLayout)

    def setClassName(self, className: str):
        """Set the class name and reload the card"""
        self.title.setText(className)
        self._reloadCard()

    def setAssignments(self, assignments: list):
        """Set the assignments and reload the card"""
        self.assignments = assignments
        self._reloadCard()

    def _reloadCard(self):
        """Reload the card by clearing and rebuilding the layout"""
        layout = self.layout()

        while layout.count() > 1:
            item = layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clearLayout(item.layout())

        for assignmentName, dueDate in self.assignments:
            assignmentLayout = QHBoxLayout()
            assignmentLayout.setContentsMargins(0, 5, 0, 5)

            bullet = BodyLabel("•")
            bullet.setStyleSheet("color: #333333; font-weight: bold; font-size: 16px;")
            bullet.setFixedWidth(15)

            nameLabel = BodyLabel(assignmentName)
            nameLabel.setStyleSheet("color: #333333; font-weight: 500;")

            dueLabel = BodyLabel(f"Due at {dueDate}")
            dueLabel.setStyleSheet("color: #666666;")

            assignmentLayout.addWidget(bullet)
            assignmentLayout.addWidget(nameLabel)
            assignmentLayout.addStretch()
            assignmentLayout.addWidget(dueLabel)

            layout.addLayout(assignmentLayout)

    def _clearLayout(self, layout):
        """Clear the layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clearLayout(item.layout())


class StatsCard(CardWidget):
    """Statistics display card"""

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data
        self.setStyleSheet("background-color: transparent;")
        self.setFixedSize(380, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = SubtitleLabel(f"{self.data['display_name']}'s Numeracy Stats")
        title.setStyleSheet("color: #009a9c; font-weight: 600;")
        layout.addWidget(title)

        contentLayout = QHBoxLayout()

        statsLayout = QVBoxLayout()
        statsLayout.setSpacing(8)

        for label, value in data["stats"].items():
            statLayout = QHBoxLayout()
            statLayout.setContentsMargins(0, 0, 0, 0)

            labelWidget = StrongBodyLabel(label)
            valueWidget = StrongBodyLabel(str(value))

            statLayout.addWidget(labelWidget)
            statLayout.addWidget(valueWidget)
            statLayout.addStretch()

            statsLayout.addLayout(statLayout)

        gradeLayout = QVBoxLayout()
        gradeLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progressRing = ProgressRing()
        progressRing.setFixedSize(80, 80)
        progressRing.setValue(data["level"])
        progressRing.setTextVisible(False)

        gradeLabel = TitleLabel(data["grade"])
        gradeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gradeLabel.setStyleSheet("font-weight: bold; font-size: 24px; color: #000000;")

        gradeLayout.addWidget(progressRing)
        gradeLabel.setParent(progressRing)
        gradeLabel.setGeometry(20, 25, 40, 30)

        contentLayout.addLayout(statsLayout, 2)
        contentLayout.addLayout(gradeLayout, 1)

        layout.addLayout(contentLayout)

    def setStats(self, stats: dict):
        """Update the stats data and reload the card"""
        self.data = stats
        self._reloadCard()

    def _reloadCard(self):
        """Reload the card by clearing and rebuilding the layout"""
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clearLayout(item.layout())

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = SubtitleLabel(f"{self.data['display_name']}'s Numeracy Stats")
        title.setStyleSheet("color: #009a9c; font-weight: 600;")
        layout.addWidget(title)

        # Stats content
        contentLayout = QHBoxLayout()

        statsLayout = QVBoxLayout()
        statsLayout.setSpacing(8)

        for label, value in self.data["stats"].items():
            statLayout = QHBoxLayout()
            statLayout.setContentsMargins(0, 0, 0, 0)

            labelWidget = StrongBodyLabel(label)
            valueWidget = StrongBodyLabel(value)

            statLayout.addWidget(labelWidget)
            statLayout.addWidget(valueWidget)
            statLayout.addStretch()

            statsLayout.addLayout(statLayout)

        gradeLayout = QVBoxLayout()
        gradeLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progressRing = ProgressRing()
        progressRing.setFixedSize(80, 80)
        progressRing.setValue(self.data["level"])
        progressRing.setTextVisible(False)

        gradeLabel = TitleLabel(self.data["grade"])
        gradeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gradeLabel.setStyleSheet("font-weight: bold; font-size: 24px; color: #000000;")

        gradeLayout.addWidget(progressRing)
        gradeLabel.setParent(progressRing)
        gradeLabel.setGeometry(20, 25, 40, 30)

        contentLayout.addLayout(statsLayout, 2)
        contentLayout.addLayout(gradeLayout, 1)

        layout.addLayout(contentLayout)

    def _clearLayout(self, layout):
        """Clear the layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clearLayout(item.layout())


class NumeracyMatrixCard(CardWidget):
    """Numeracy matrix table card"""

    EMOJI_MAP = {
        0: "🥉",
        1: "🥈",
        2: "🥇",
        3: "🏅",
        4: "🏆",
    }

    def __init__(self, matrix: list[list[float]], display_name: str, parent=None):
        # 0 <= matrix[:][:] <= 4
        super().__init__(parent)
        self.display_name = display_name
        self.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = SubtitleLabel(f"{self.display_name}'s Numeracy Matrix")
        title.setStyleSheet("color: #333333; font-weight: 600;")
        layout.addWidget(title)

        # Matrix
        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(20)

        conceptHeader = StrongBodyLabel("Concept & Process")
        conceptHeader.setFixedWidth(200)

        formulateHeader = StrongBodyLabel("Formulate")
        formulateHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formulateHeader.setFixedWidth(80)

        applyHeader = StrongBodyLabel("Apply")
        applyHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        applyHeader.setFixedWidth(80)

        explainHeader = StrongBodyLabel("Explain")
        explainHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        explainHeader.setFixedWidth(80)

        headerLayout.addWidget(conceptHeader)
        headerLayout.addWidget(formulateHeader)
        headerLayout.addWidget(applyHeader)
        headerLayout.addWidget(explainHeader)
        headerLayout.addStretch()

        layout.addLayout(headerLayout)

        concepts = [
            "Operations on numbers",
            "Mathematical relationships",
            "Spatial properties and representations",
            "Location and navigation",
            "Measurement",
            "Statistics and data",
            "Elements of chance",
        ]

        for j, concept in enumerate(concepts):
            rowLayout = QHBoxLayout()
            rowLayout.setSpacing(20)

            conceptLabel = StrongBodyLabel(concept)
            conceptLabel.setFixedWidth(200)
            conceptLabel.setWordWrap(True)

            rowLayout.addWidget(conceptLabel)
            for i in range(3):
                statusLabel = BodyLabel(self.EMOJI_MAP[(matrix[j][i]).__ceil__()])
                statusLabel.setStyleSheet("font-size: 16px;")
                statusLabel.setFixedWidth(20)
                statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                rowLayout.addWidget(statusLabel)
                if i < 2:
                    rowLayout.addSpacing(60)

            rowLayout.addStretch()

            layout.addLayout(rowLayout)

    def setAttributes(self, matrix: list[list[float]], display_name: str):
        """Set the matrix and reload the card"""
        self.matrix = matrix
        self.display_name = display_name
        self._reloadCard()

    def _reloadCard(self):
        """Reload the card by clearing and rebuilding the layout"""
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clearLayout(item.layout())

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = SubtitleLabel(f"{self.display_name}'s Numeracy Matrix")
        title.setStyleSheet("color: #333333; font-weight: 600;")
        layout.addWidget(title)

        # Matrix
        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(20)

        conceptHeader = StrongBodyLabel("Concept & Process")
        conceptHeader.setFixedWidth(200)

        formulateHeader = StrongBodyLabel("Formulate")
        formulateHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formulateHeader.setFixedWidth(80)

        applyHeader = StrongBodyLabel("Apply")
        applyHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        applyHeader.setFixedWidth(80)

        explainHeader = StrongBodyLabel("Explain")
        explainHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        explainHeader.setFixedWidth(80)

        headerLayout.addWidget(conceptHeader)
        headerLayout.addWidget(formulateHeader)
        headerLayout.addWidget(applyHeader)
        headerLayout.addWidget(explainHeader)
        headerLayout.addStretch()

        layout.addLayout(headerLayout)

        concepts = [
            "Operations on numbers",
            "Mathematical relationships",
            "Spatial properties and representations",
            "Location and navigation",
            "Measurement",
            "Statistics and data",
            "Elements of chance",
        ]

        for j, concept in enumerate(concepts):
            rowLayout = QHBoxLayout()
            rowLayout.setSpacing(20)

            conceptLabel = StrongBodyLabel(concept)
            conceptLabel.setFixedWidth(200)
            conceptLabel.setWordWrap(True)

            rowLayout.addWidget(conceptLabel)
            for i in range(3):
                statusLabel = BodyLabel(self.EMOJI_MAP[(self.matrix[j][i]).__ceil__()])
                statusLabel.setStyleSheet("font-size: 16px;")
                statusLabel.setFixedWidth(20)
                statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                rowLayout.addWidget(statusLabel)
                if i < 2:
                    rowLayout.addSpacing(60)

            rowLayout.addStretch()

            layout.addLayout(rowLayout)

    def _clearLayout(self, layout):
        """Clear the layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clearLayout(item.layout())


class AssignmentCard(CardWidget):
    """Individual assignment card for the class page"""

    assignmentClicked = pyqtSignal(int)  # assignmentId

    def __init__(
        self,
        assignmentId: str,
        assignmentName: str,
        dueDate: datetime,
        description: str,
        imagePath: str = None,
        parent=None,
    ):
        super().__init__(parent)
        self.assignmentId = assignmentId
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedHeight(120)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        contentLayout = QVBoxLayout()
        contentLayout.setSpacing(5)

        # Assignment
        nameLabel = SubtitleLabel(assignmentName)
        nameLabel.setStyleSheet("color: #333333; font-weight: 600; font-size: 16px;")
        contentLayout.addWidget(nameLabel)

        # Description
        descLabel = BodyLabel(description)
        descLabel.setStyleSheet("color: #666666; font-size: 12px;")
        descLabel.setWordWrap(True)
        contentLayout.addWidget(descLabel)

        # Due date
        dueLabel = CaptionLabel(
            f"Due at {dueDate.strftime('%m-%d %H:%M') if dueDate.year == datetime.now().year else dueDate.strftime('%Y-%m-%d %H:%M')}"
        )
        dueLabel.setStyleSheet("color: #999999; font-size: 10px;")
        contentLayout.addWidget(dueLabel)

        layout.addLayout(contentLayout, 1)

        # Image
        if imagePath:
            imageWidget = QWidget()
            imageWidget.setFixedSize(60, 60)
            imageWidget.setStyleSheet("background-color: #e3f2fd; border-radius: 4px;")
            layout.addWidget(imageWidget)

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.assignmentClicked.emit(self.assignmentId)
        super().mousePressEvent(event)


class FeedbackCard(CardWidget):
    """Feedback card displaying question results"""

    def __init__(self, feedbackText: str, performanceLevel: str, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        # Feedback
        title = StrongBodyLabel("Feedback")
        layout.addWidget(title)

        message = BodyLabel(feedbackText)
        message.setWordWrap(True)
        layout.addWidget(message)

        # Performance
        badgeLayout = QHBoxLayout()
        badgeLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        performanceBadge = self.CreatePerformanceBadge(performanceLevel)
        badgeLayout.addWidget(performanceBadge)
        badgeLayout.addStretch()

        layout.addLayout(badgeLayout)

    def CreatePerformanceBadge(self, level: str):
        """Create a performance badge based on level"""
        return InfoBadge.custom(level, *levelToColor(level))


class BaseQuestionCard(CardWidget):
    """Base class for question cards"""

    def __init__(self, questionText: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(25, 20, 25, 20)
        self.mainLayout.setSpacing(18)

        # Question
        self.questionLabel = BodyLabel(questionText)
        self.questionLabel.setWordWrap(True)
        self.mainLayout.addWidget(self.questionLabel)

        self.contentWidget = None

        # Feedback
        self.extraWidgetLayout = QVBoxLayout()
        self.extraWidgetLayout.setSpacing(15)

        self.actionLayout = QHBoxLayout()
        self.actionLayout.setContentsMargins(0, 25, 0, 0)

        self.leftButtonsLayout = QHBoxLayout()
        self.leftButtonsLayout.setSpacing(10)

        self.showKeywordsBtn = PushButton("Show Keywords")
        self.dontKnowBtn = PushButton("I Don't Know")

        self.leftButtonsLayout.addWidget(self.showKeywordsBtn)
        self.leftButtonsLayout.addWidget(self.dontKnowBtn)

        self.submitBtn = PrimaryPushButton("Submit")

        self.actionLayout.addLayout(self.leftButtonsLayout)
        self.actionLayout.addStretch()
        self.actionLayout.addWidget(self.submitBtn)

    def finalizeLayout(self):
        """Call this after adding content to finalize the layout"""
        if self.contentWidget:
            self.mainLayout.addWidget(self.contentWidget)

        self.mainLayout.addLayout(self.extraWidgetLayout)
        self.mainLayout.addLayout(self.actionLayout)

    def addExtraWidget(self, widget: QWidget):
        """Add a widget between content and action buttons"""
        self.extraWidgetLayout.addWidget(widget)

    def removeExtraWidget(self, widget: QWidget):
        """Remove a widget from the extra area"""
        self.extraWidgetLayout.removeWidget(widget)
        widget.setParent(None)

    def showKeywords(self, keywords: Optional[List[str]]):
        """Bold the keywords"""
        if keywords is None:
            return

        for keyword in keywords:
            self.questionLabel.setText(
                self.questionLabel.text().replace(keyword, f"<b>{keyword}</b>")
            )


class OptionsQuestionCard(BaseQuestionCard):
    """Question card with checkbox options"""

    def __init__(self, questionText: str, options: list, parent=None):
        super().__init__(questionText, parent)

        self.contentWidget = QWidget()
        contentLayout = QVBoxLayout(self.contentWidget)
        contentLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        contentLayout.setSpacing(15)

        # Image
        self.imageContainer = QWidget()
        self.imageContainer.hide()

        imageLayout = QVBoxLayout(self.imageContainer)
        imageLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.imageLabel = ImageLabel()
        self.imageLabel.scaledToWidth(800)
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        imageLayout.addWidget(self.imageLabel)

        contentLayout.addWidget(self.imageContainer)

        # Options
        self.optionsLayout = QHBoxLayout()
        self.optionsLayout.setContentsMargins(0, 0, 0, 0)
        self.optionsLayout.setSpacing(8)
        self.optionsLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.checkboxes = []
        for option in options:
            checkbox = CheckBox(option, self)
            self.checkboxes.append(checkbox)
            self.optionsLayout.addWidget(checkbox)

        contentLayout.addLayout(self.optionsLayout)

        self.finalizeLayout()

    def setImage(self, image: bytes):
        """Set the image"""
        self.imageLabel.setPixmap(QPixmap.fromImage(QImage.fromData(image)))
        self.imageLabel.scaledToWidth(800)
        self.imageContainer.show()

    def hideImage(self):
        """Hide the image container"""
        self.imageContainer.hide()

    def getSelectedOptions(self):
        """Get list of selected options"""
        selected = []
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                selected.append(checkbox.text())
        return selected


class TextQuestionCard(BaseQuestionCard):
    """Question card with text input"""

    def __init__(
        self,
        questionText: str,
        parent=None,
    ):
        super().__init__(questionText, parent)

        self.contentWidget = QWidget()
        contentLayout = QVBoxLayout(self.contentWidget)
        contentLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        contentLayout.setSpacing(20)

        # Image
        self.imageContainer = QWidget()
        self.imageContainer.hide()

        imageLayout = QVBoxLayout(self.imageContainer)
        imageLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.imageLabel = ImageLabel()
        self.imageLabel.scaledToWidth(800)
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        imageLayout.addWidget(self.imageLabel)

        contentLayout.addWidget(self.imageContainer)

        # Answer
        inputContainer = QWidget()
        inputContainer.setFixedWidth(820)

        inputLayout = QVBoxLayout(inputContainer)
        inputLayout.setContentsMargins(20, 0, 20, 0)

        self.answerInput = PlainTextEdit()
        self.answerInput.setPlaceholderText("Please enter your answer here")
        self.answerInput.setFixedWidth(820)

        inputLayout.addWidget(self.answerInput)

        inputContainerLayout = QHBoxLayout()
        inputContainerLayout.addStretch()
        inputContainerLayout.addWidget(inputContainer)
        inputContainerLayout.addStretch()

        contentLayout.addLayout(inputContainerLayout)

        self.finalizeLayout()

    def setImage(self, image: bytes):
        """Set the image"""
        self.imageLabel.setPixmap(QPixmap.fromImage(QImage.fromData(image)))
        self.imageLabel.scaledToWidth(800)
        self.imageContainer.show()

    def hideImage(self):
        """Hide the image container"""
        self.imageContainer.hide()

    def getAnswerText(self):
        """Get the text from the answer input"""
        return self.answerInput.toPlainText()

    def setAnswerText(self, text: str):
        """Set the text in the answer input"""
        self.answerInput.setPlainText(text)


class AskAIPanel(CardWidget):
    """AI assistant panel that appears when user clicks 'I don't know'"""

    sendMessage = pyqtSignal(str, list)  # message, history
    closePanel = pyqtSignal()  # Emits when panel should be closed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedWidth(350)
        self.setMinimumHeight(400)

        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(15)

        # Header
        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(0, 0, 0, 0)

        # Title
        self.titleLabel = SubtitleLabel("Ask AI")
        self.titleLabel.setStyleSheet(
            "color: #333333; font-weight: 600; font-size: 18px;"
        )
        headerLayout.addWidget(self.titleLabel)

        headerLayout.addStretch()

        # Close
        self.closeButton = TransparentToolButton(FluentIcon.CLOSE, self)
        self.closeButton.setFixedSize(32, 32)
        self.closeButton.clicked.connect(self.closePanel.emit)
        headerLayout.addWidget(self.closeButton)

        layout.addLayout(headerLayout)

        # Chat
        self.chatArea = SmoothScrollArea(self)
        self.chatArea.setScrollAnimation(
            Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint
        )
        self.chatArea.setScrollAnimation(
            Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint
        )
        self.chatArea.setWidgetResizable(True)
        self.chatArea.setStyleSheet(
            "background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px;"
        )
        self.chatArea.setMinimumHeight(250)

        # Chat content
        self.chatWidget = QWidget()
        self.chatWidget.setStyleSheet("border: 0px;")
        self.chatLayout = QVBoxLayout(self.chatWidget)
        self.chatLayout.setContentsMargins(15, 15, 15, 15)
        self.chatLayout.setSpacing(10)
        self.chatLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.chatHistory = []

        self.addAIMessage(
            "Hi! I'm here to help you with this question. What would you like to know?"
        )

        self.chatArea.setWidget(self.chatWidget)
        layout.addWidget(self.chatArea)

        inputLayout = QVBoxLayout()
        inputLayout.setSpacing(10)

        self.messageInput = PlainTextEdit()
        self.messageInput.setPlaceholderText("Type your question here...")
        self.messageInput.setFixedHeight(80)
        self.messageInput.setStyleSheet(
            "border: 1px solid #ddd; border-radius: 4px; padding: 8px; background-color: transparent; color: #000000;"
        )
        inputLayout.addWidget(self.messageInput)

        # Send
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()

        self.sendButton = PrimaryPushButton("Send")
        self.sendButton.setFixedWidth(80)
        self.sendButton.clicked.connect(self._onSendClicked)
        buttonLayout.addWidget(self.sendButton)

        inputLayout.addLayout(buttonLayout)
        layout.addLayout(inputLayout)

        self.messageInput.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle Enter key press in message input"""
        if (
            hasattr(self, "messageInput")
            and obj == self.messageInput
            and event.type() == event.Type.KeyPress
        ):
            if (
                event.key() == Qt.Key.Key_Return
                and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            ):
                self._onSendClicked()
                return True
        return super().eventFilter(obj, event)

    def _onSendClicked(self):
        """Handle send button click"""
        message = self.messageInput.toPlainText().strip()
        if message:
            self.addUserMessage(message)
            self.messageInput.clear()
            self.sendMessage.emit(message, self.chatHistory)

    def addUserMessage(self, message: str):
        """Add a user message to the chat"""
        messageWidget = self._createMessageWidget(message, isUser=True)
        self.chatLayout.addWidget(messageWidget)
        self.chatHistory.append({"role": "user", "content": message})
        self._scrollToBottom()

    def addAIMessage(self, message: str):
        """Add an AI message to the chat"""
        messageWidget = self._createMessageWidget(message, isUser=False)
        self.chatLayout.addWidget(messageWidget)
        self.chatHistory.append({"role": "assistant", "content": message})
        self._scrollToBottom()

    def _createMessageWidget(self, message: str, isUser: bool):
        """Create a message widget"""
        messageContainer = QWidget()
        containerLayout = QHBoxLayout(messageContainer)
        containerLayout.setContentsMargins(0, 0, 0, 0)

        messageLabel = BodyLabel(message)
        messageLabel.setWordWrap(True)
        messageLabel.setStyleSheet(
            f"background-color: {'#007acc' if isUser else '#e9ecef'}; "
            f"color: {'white' if isUser else '#333333'}; "
            f"padding: 8px 12px; border-radius: 12px; max-width: 250px;"
        )

        if isUser:
            containerLayout.addStretch()
            containerLayout.addWidget(messageLabel)
        else:
            containerLayout.addWidget(messageLabel)
            containerLayout.addStretch()

        return messageContainer

    def _scrollToBottom(self):
        """Scroll chat area to bottom"""
        scrollBar = self.chatArea.verticalScrollBar()
        scrollBar.setValue(scrollBar.maximum())

    def setSubQuestionContext(self, subQuestionId: int):
        """Set the context for the current question"""
        self.currentSubQuestionId = subQuestionId

        self._clearChat()

    def _clearChat(self):
        """Clear the chat area"""
        while self.chatLayout.count() > 1:
            item = self.chatLayout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()


class ClassInterface(QWidget):
    """Class interface with split To do/Done layout"""

    assignmentClicked = pyqtSignal(int)  # assignmentId
    doneAssignmentClicked = pyqtSignal(int)  # assignmentId
    joinClassRequested = pyqtSignal(str, str)  # className, enterCode

    def __init__(self, classData: dict = None, parent=None):
        super().__init__(parent)
        self.setObjectName("classInterface")

        self.classData = classData or {}
        self.className = self.classData.get("class_name", "No Class Available")
        self.teacherName = self.classData.get("teacher_name", "Not Available")
        self.todoAssignments = self.classData.get("to_do_assignments", [])
        self.doneAssignments = self.classData.get("done_assignments", [])

        self.setupUi()

    def setupUi(self):
        self.setStyleSheet("background-color: #f5f5f5;")

        mainScroll = SmoothScrollArea(self)
        mainScroll.setScrollAnimation(
            Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint
        )
        mainScroll.setScrollAnimation(
            Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint
        )
        mainScroll.setWidgetResizable(True)
        mainScroll.setStyleSheet("background-color: #f5f5f5; border: none;")

        container = QWidget()
        mainScroll.setWidget(container)

        self.mainLayout = QVBoxLayout(container)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mainLayout.setContentsMargins(30, 30, 30, 30)
        self.mainLayout.setSpacing(20)

        if self.className is None:
            self._setupJoinClassInterface(self.mainLayout)
        else:
            self._setupRegularClassInterface(self.mainLayout)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(mainScroll)

    def _setupJoinClassInterface(self, mainLayout):
        """Setup the join class interface when user is not enrolled"""
        title = TitleLabel("Class")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 28px;")
        mainLayout.addWidget(title)

        centerLayout = QVBoxLayout()
        centerLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        centerLayout.setSpacing(30)

        illustrationLayout = QVBoxLayout()
        illustrationLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        illustrationLayout.setSpacing(20)

        iconLabel = BodyLabel("📚")
        iconLabel.setStyleSheet("font-size: 80px;")
        iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        illustrationLayout.addWidget(iconLabel)

        mainMessage = SubtitleLabel("You're not enrolled in any class yet")
        mainMessage.setStyleSheet("color: #333333; font-weight: 600; font-size: 24px;")
        mainMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        illustrationLayout.addWidget(mainMessage)

        subMessage = BodyLabel("Join a class to access assignments and start learning!")
        subMessage.setStyleSheet("color: #666666; font-size: 16px;")
        subMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        illustrationLayout.addWidget(subMessage)

        centerLayout.addLayout(illustrationLayout)

        buttonLayout = QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        joinButton = PrimaryPushButton("Join a Class")
        joinButton.setFixedSize(200, 40)
        joinButton.clicked.connect(self._onJoinClassClicked)
        buttonLayout.addWidget(joinButton)

        centerLayout.addLayout(buttonLayout)

        mainLayout.addStretch(1)
        mainLayout.addLayout(centerLayout)
        mainLayout.addStretch(1)

    def _setupRegularClassInterface(self, mainLayout):
        """Setup the regular class interface when user is enrolled"""
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(5)

        # Class name
        self.classTitle = TitleLabel(self.className)
        self.classTitle.setStyleSheet("color: #333333; font-weight: 600;")
        headerLayout.addWidget(self.classTitle)

        # Created by
        self.createdLabel = BodyLabel(f"Created by {self.teacherName}")
        self.createdLabel.setStyleSheet("color: #666666;")
        headerLayout.addWidget(self.createdLabel)

        mainLayout.addLayout(headerLayout)

        contentLayout = QHBoxLayout()
        contentLayout.setSpacing(30)
        contentLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # To do
        todoLayout = QVBoxLayout()
        todoLayout.setObjectName("todoLayout")
        todoLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        todoLayout.setSpacing(15)

        todoTitle = SubtitleLabel("To do")
        todoTitle.setStyleSheet("color: #333333; font-weight: 600;")
        todoLayout.addWidget(todoTitle)

        for assignment in self.todoAssignments:
            card = AssignmentCard(
                assignment["id"],
                assignment["name"],
                assignment["due_date"],
                assignment["description"],
                assignment.get("image", None),
            )
            todoLayout.addWidget(card)

        # Done
        doneLayout = QVBoxLayout()
        doneLayout.setObjectName("doneLayout")
        doneLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        doneLayout.setSpacing(15)

        doneTitle = SubtitleLabel("Done")
        doneTitle.setStyleSheet("color: #333333; font-weight: 600;")
        doneLayout.addWidget(doneTitle)

        for assignment in self.doneAssignments:
            card = AssignmentCard(
                assignment["id"],
                assignment["name"],
                assignment["due_date"],
                assignment["description"],
                assignment.get("image", None),
            )
            doneLayout.addWidget(card)

        contentLayout.addLayout(todoLayout, 1)
        contentLayout.addLayout(doneLayout, 1)

        mainLayout.addLayout(contentLayout)

        self._connectAssignmentSignals()

    def _onJoinClassClicked(self):
        """Handle join class button click"""
        dialog = JoinClassDialog(self)
        dialog.joinClass.connect(self.joinClassRequested.emit)
        dialog.show()

    def updateContent(self, classData: dict):
        """Update the interface content with new data"""
        self.classData = classData
        self.className = classData.get("class_name", "No Class Available")
        self.teacherName = classData.get("teacher_name", "Not Available")
        self.todoAssignments = classData.get("to_do_assignments", [])
        self.doneAssignments = classData.get("done_assignments", [])

        if self.className is not None and hasattr(self, "classTitle"):
            self.classTitle.setText(self.className)
        if hasattr(self, "createdLabel"):
            self.createdLabel.setText(f"Created by {self.teacherName}")

        if (
            hasattr(self, "mainLayout")
            and self.mainLayout is not None
            and self.findChild(QVBoxLayout, "todoLayout") is not None
        ):
            self._updateAssignmentSections()

    def _connectAssignmentSignals(self):
        """Connect signals for assignment cards after creating the interface"""
        todoLayout = self.findChild(QVBoxLayout, "todoLayout")
        doneLayout = self.findChild(QVBoxLayout, "doneLayout")

        if todoLayout is not None:
            self._connectAssignmentCardsInLayout(todoLayout, True)
        if doneLayout is not None:
            self._connectAssignmentCardsInLayout(doneLayout, False)

    def _updateAssignmentSections(self):
        """Update assignment cards in todo and done sections"""
        todoLayout = self.findChild(QVBoxLayout, "todoLayout")
        doneLayout = self.findChild(QVBoxLayout, "doneLayout")

        if todoLayout is not None:
            self._clearAndAddAssignments(todoLayout, self.todoAssignments, True)
        if doneLayout is not None:
            self._clearAndAddAssignments(doneLayout, self.doneAssignments, False)

    def _connectAssignmentCardsInLayout(self, layout, isTodo):
        """Connect signals for assignment cards in a specific layout"""
        if layout is None:
            return

        for i in range(1, layout.count()):
            item = layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), AssignmentCard):
                card = item.widget()
                try:
                    card.assignmentClicked.disconnect()
                except Exception:
                    pass

                if isTodo:
                    card.assignmentClicked.connect(self.assignmentClicked.emit)
                else:
                    card.assignmentClicked.connect(self.doneAssignmentClicked.emit)

    def _clearAndAddAssignments(self, layout, assignments, isTodo):
        """Clear existing assignment cards and add new ones"""
        if layout is None:
            return

        while layout.count() > 1:
            item = layout.takeAt(1)
            if item and item.widget():
                item.widget().deleteLater()
                item.widget().setParent(None)

        for assignment in assignments:
            card = AssignmentCard(
                assignment["id"],
                assignment["name"],
                assignment["due_date"],
                assignment["description"],
                assignment.get("image", None),
            )
            layout.addWidget(card)

        self._connectAssignmentCardsInLayout(layout, isTodo)


class HomeInterface(QWidget):
    """Home dashboard interface"""

    classClicked = pyqtSignal()
    joinClassRequested = pyqtSignal(str, str)  # className, enterCode

    def __init__(self, dashboardData: dict = None, parent=None):
        super().__init__(parent)
        self.setObjectName("homeInterface")

        self.dashboardData = dashboardData or {}
        self.className = self.dashboardData.get("class_name", "Loading...")
        self.assignments = self.dashboardData.get("assignments", [])
        self.stats = self.dashboardData.get(
            "stats",
            {
                "stats": {
                    "Total Question Answered": "0",
                    "Average Level": "Loading...",
                    "Best Concept": "Loading...",
                    "Best Process": "Loading...",
                },
                "level": 100,
                "grade": "Ⅰ",
                "display_name": "Loading...",
            },
        )
        self.matrix = self.dashboardData.get("matrix", [[0] * 3 for _ in range(7)])
        self.displayName = self.dashboardData.get("display_name", "Loading...")

        self.setupUi()

    def setupUi(self):
        scrollArea = SmoothScrollArea(self)
        scrollArea.setScrollAnimation(
            Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint
        )
        scrollArea.setScrollAnimation(
            Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint
        )
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("background-color: #f5f5f5; border: none;")

        container = QWidget()
        scrollArea.setWidget(container)

        mainLayout = QVBoxLayout(container)
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(20)

        title = TitleLabel("Home")
        title.setStyleSheet("background-color: transparent; color: #333333;")
        mainLayout.addWidget(title)

        # Cards
        flowLayout = FlowLayout()

        flowLayout.setContentsMargins(30, 30, 30, 30)
        flowLayout.setVerticalSpacing(20)
        flowLayout.setHorizontalSpacing(10)

        # Class card
        if self.className is None:
            joinClassCard = JoinClassCard()
            joinClassCard.joinClassClicked.connect(self._onJoinClassClicked)
            flowLayout.addWidget(joinClassCard)
        else:
            classCard = ClassCard(self.className, self.assignments)
            classCard.clicked.connect(self.classClicked.emit)
            flowLayout.addWidget(classCard)

        # Stats card
        if self.className is not None:
            statsCard = StatsCard(self.stats)
            flowLayout.addWidget(statsCard)

            # Numeracy matrix card
            matrixCard = NumeracyMatrixCard(self.matrix, self.displayName)
            flowLayout.addWidget(matrixCard)

        mainLayout.addLayout(flowLayout)
        mainLayout.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

    def _onJoinClassClicked(self):
        """Handle join class card click"""
        dialog = JoinClassDialog(self)
        dialog.joinClass.connect(self.joinClassRequested.emit)
        dialog.show()

    def updateContent(self, dashboardData: dict):
        """Update the interface content with new data"""
        self.dashboardData = dashboardData
        self.className = dashboardData.get("class_name", "Loading...")
        self.assignments = dashboardData.get("assignments", [])
        self.stats = dashboardData.get("stats", {})
        self.matrix = dashboardData.get("matrix", [[0] * 3 for _ in range(7)])
        self.displayName = dashboardData.get("display_name", "Loading...")

        for child in self.findChildren(FlowLayout):
            flowLayout = child

            while flowLayout.count() > 0:
                item = flowLayout.takeAt(0)
                if item:
                    if hasattr(item, "widget"):
                        widget = item.widget()
                    else:
                        widget = item
                    if widget:
                        widget.setParent(None)
                        widget.deleteLater()

            if self.className is None:
                joinClassCard = JoinClassCard()
                joinClassCard.joinClassClicked.connect(self._onJoinClassClicked)
                flowLayout.addWidget(joinClassCard)
            else:
                classCard = ClassCard(self.className, self.assignments)
                classCard.clicked.connect(self.classClicked.emit)
                flowLayout.addWidget(classCard)

                statsCard = StatsCard(self.stats)
                flowLayout.addWidget(statsCard)

                matrixCard = NumeracyMatrixCard(self.matrix, self.displayName)
                flowLayout.addWidget(matrixCard)
            break


class QuestionCard(CardWidget):
    """Individual question card displaying question information"""

    questionClicked = pyqtSignal(int)  # questionId

    def __init__(
        self,
        questionId: int,
        question: str,
        subQuestions: list,
        footerText: str = None,
        parent=None,
    ):
        super().__init__(parent)
        self.questionId = questionId
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedWidth(760)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        questionTitle = SubtitleLabel(question)
        questionTitle.setStyleSheet(
            "color: #333333; font-weight: 600; font-size: 20px; padding-bottom: 10px; border-bottom: 1px solid #eee;"
        )
        layout.addWidget(questionTitle)

        # Sub-questions
        for subQuestion in subQuestions:
            questionLayout = self.createSubQuestionItem(subQuestion)
            layout.addLayout(questionLayout)

        # Footer
        if footerText:
            footerLabel = CaptionLabel(footerText)
            footerLabel.setStyleSheet(
                "color: #6c757d; font-size: 11px; padding-top: 15px; "
                "border-top: 1px solid #f0f0f0; margin-top: 20px;"
            )
            footerLabel.setWordWrap(True)
            layout.addWidget(footerLabel)

    def createSubQuestionItem(self, subQuestion):
        """Create a single sub-question item layout"""
        questionLayout = QHBoxLayout()
        questionLayout.setSpacing(20)

        # Content
        contentLayout = QVBoxLayout()
        contentLayout.setSpacing(8)

        # Title
        questionTitle = StrongBodyLabel(subQuestion["title"])
        contentLayout.addWidget(questionTitle)

        # Description
        questionText = BodyLabel(subQuestion["text"])
        questionText.setAlignment(Qt.AlignmentFlag.AlignTop)
        questionText.setWordWrap(True)
        contentLayout.addWidget(questionText)

        # Tags
        tagsLayout = QHBoxLayout()
        tagsLayout.setSpacing(8)
        tagsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for tagText, tagType in subQuestion["tags"]:
            tag = self.createTag(tagText, tagType)
            tagsLayout.addWidget(tag)

        tagsLayout.addStretch()
        contentLayout.addLayout(tagsLayout)

        questionLayout.addLayout(contentLayout, 1)

        # Image
        if subQuestion.get("image", None):
            imageWidget = ImageLabel(cropImageToSquare(subQuestion["image"], 80))
            imageWidget.setFixedSize(80, 80)
            questionLayout.addWidget(imageWidget)

        return questionLayout

    def createTag(self, text: str, tagType: str):
        """Create a colored tag widget"""
        colorMap = {
            "concept": lambda text: InfoBadge.custom(
                text, QColor("#0f7b0f"), QColor("#7ED321")
            ),
            "process": lambda text: InfoBadge.custom(
                text, QColor("#005fb7"), QColor("#4A90E2")
            ),
            "result": lambda text: InfoBadge.custom(text, *levelToColor(text)),
        }

        tag = colorMap.get(
            tagType.lower(),
            lambda text: InfoBadge.info(text),
        )(text)

        return tag

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.questionClicked.emit(self.questionId)
        super().mousePressEvent(event)


class QuestionsInterface(QWidget):
    """Questions interface displaying completed questions"""

    questionClicked = pyqtSignal(int)  # questionId

    def __init__(self, questionsData: list = None, parent=None):
        super().__init__(parent)
        self.setObjectName("questionsInterface")

        self.questionsData = questionsData or []

        self.setupUi()

    def setupUi(self):
        self.setStyleSheet("background-color: #f5f5f5;")

        scrollArea = SmoothScrollArea(self)
        scrollArea.setScrollAnimation(
            Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint
        )
        scrollArea.setScrollAnimation(
            Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint
        )
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("background-color: #f5f5f5; border: none;")

        container = QWidget()
        scrollArea.setWidget(container)

        mainLayout = QVBoxLayout(container)
        mainLayout.setContentsMargins(25, 25, 25, 25)
        mainLayout.setSpacing(20)

        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(5)

        title = TitleLabel("Questions")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 26px;")
        headerLayout.addWidget(title)

        subtitle = BodyLabel(
            "Questions you have done is listed here, old results are replaced with new ones"
        )
        subtitle.setStyleSheet("color: #6c757d; font-size: 14px;")
        headerLayout.addWidget(subtitle)

        mainLayout.addLayout(headerLayout)

        questionsLayout = QVBoxLayout()
        questionsLayout.setObjectName("questionsLayout")
        questionsLayout.setSpacing(20)

        for questionGroup in self.questionsData:
            questionCard = QuestionCard(
                questionGroup.get("id", ""),
                questionGroup["title"],
                questionGroup["sub_questions"],
                questionGroup.get("footer", None),
            )
            questionCard.questionClicked.connect(self.questionClicked.emit)
            questionsLayout.addWidget(questionCard)

        mainLayout.addLayout(questionsLayout)
        mainLayout.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

    def updateContent(self, questionsData: list):
        """Update the interface content with new data"""
        self.questionsData = questionsData

        for layout in self.findChildren(QVBoxLayout):
            if layout.objectName() != "questionsLayout":
                continue

            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                if item and item.widget() and isinstance(item.widget(), QuestionCard):
                    widget = item.widget()
                    layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()

            for questionGroup in self.questionsData:
                questionCard = QuestionCard(
                    questionGroup.get("id", ""),
                    questionGroup["title"],
                    questionGroup["sub_questions"],
                    questionGroup.get("footer", None),
                )
                questionCard.questionClicked.connect(self.questionClicked.emit)
                layout.addWidget(questionCard)
            break


class QuestionAnsweringInterface(QWidget):
    """Question answering interface for interactive questions"""

    submitSubQuestion = pyqtSignal(
        int, int, object
    )  # assignmentId, subQuestionId, answer
    submitAssignment = pyqtSignal(dict)  # allAnswers

    def __init__(self, questionData: dict = None, studentController=None, parent=None):
        super().__init__(parent)
        self.setObjectName("questionAnsweringInterface")
        self.studentController = studentController

        self.questionData = questionData or {}
        self.assignmentId = self.questionData.get("id", None)
        self.assignment_title = self.questionData.get("title", "Assignment")
        self.questions = self.questionData.get("questions", [])

        self.currentQuestionIndex = 0
        self.totalQuestions = len(self.questions)
        self.allAnswers = {}

        self.current_question_title = "Question"

        self.setupUi()

    def setupUi(self):
        mainHorizontalLayout = QHBoxLayout(self)
        mainHorizontalLayout.setContentsMargins(0, 0, 0, 0)
        mainHorizontalLayout.setSpacing(0)

        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setScrollAnimation(
            Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint
        )
        self.scrollArea.setScrollAnimation(
            Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint
        )
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollArea.setStyleSheet("background-color: #f5f5f5; border: none;")

        self.container = QWidget()
        self.scrollArea.setWidget(self.container)

        self.mainLayout = QVBoxLayout(self.container)
        self.mainLayout.setContentsMargins(35, 25, 35, 25)
        self.mainLayout.setSpacing(20)

        # Header
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(8)

        # Question name
        self.titleLabel = TitleLabel(self.current_question_title)
        headerLayout.addWidget(self.titleLabel)

        # Attribution
        self.attributionLabel = BodyLabel("")
        self.attributionLabel.hide()
        if self.questions[self.currentQuestionIndex].get("attribution", None):
            self.attributionLabel = BodyLabel(
                self.questions[self.currentQuestionIndex].get("attribution", "")
            )
            self.attributionLabel.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextBrowserInteraction
            )
            self.attributionLabel.setOpenExternalLinks(True)
            self.attributionLabel.setWordWrap(True)
            self.attributionLabel.show()
            headerLayout.addWidget(self.attributionLabel)

        self.mainLayout.addLayout(headerLayout)

        # Progress
        self.progressLayout = QHBoxLayout()
        self.progressLabel = BodyLabel(
            f"Question {self.currentQuestionIndex + 1} of {self.totalQuestions}"
        )
        self.progressLabel.setStyleSheet("color: #666666; font-weight: 500;")
        self.progressLayout.addWidget(self.progressLabel)
        self.progressLayout.addStretch()
        self.mainLayout.addLayout(self.progressLayout)

        # Question
        self.questionContainer = QWidget()
        self.questionLayout = QVBoxLayout(self.questionContainer)
        self.questionLayout.setContentsMargins(0, 0, 0, 0)
        self.questionLayout.setSpacing(15)
        self.mainLayout.addWidget(self.questionContainer)

        # Footer
        footerLayout = QHBoxLayout()
        footerLayout.setContentsMargins(0, 15, 0, 0)

        # Back
        self.backButton = PushButton("Back")
        self.backButton.clicked.connect(self._onBackClicked)

        # Next/Submit
        self.nextButton = PrimaryPushButton("Next")
        self.nextButton.clicked.connect(self._onNextClicked)

        footerLayout.addWidget(self.backButton)
        footerLayout.addStretch()
        footerLayout.addWidget(self.nextButton)

        self.mainLayout.addLayout(footerLayout)

        mainHorizontalLayout.addWidget(self.scrollArea)

        # I don't know
        self.aiPanel = AskAIPanel(self)
        self.aiPanel.hide()
        self.aiPanel.closePanel.connect(self._onAIPanelClose)

        aiPanelContainer = QWidget()
        aiPanelContainer.setFixedWidth(370)
        aiPanelLayout = QVBoxLayout(aiPanelContainer)
        aiPanelLayout.setContentsMargins(20, 25, 20, 25)
        aiPanelLayout.addWidget(self.aiPanel)

        mainHorizontalLayout.addWidget(aiPanelContainer)
        aiPanelContainer.hide()
        self.aiPanelContainer = aiPanelContainer

        self._loadCurrentQuestion()

    def _loadCurrentQuestion(self):
        """Load the current question and its sub-questions"""
        if not self.questions or self.currentQuestionIndex >= len(self.questions):
            return

        self._clearQuestionContainer()

        current_question = self.questions[self.currentQuestionIndex]
        question_title = current_question.get(
            "title", f"Question {self.currentQuestionIndex + 1}"
        )
        attribution = current_question.get("attribution", None)
        sub_questions = current_question.get("sub_questions", [])

        self.current_question_title = question_title
        self.titleLabel.setText(question_title)

        if attribution:
            self.attributionLabel.setText(attribution)
            self.attributionLabel.show()
        else:
            self.attributionLabel.hide()

        self.progressLabel.setText(
            f"Question {self.currentQuestionIndex + 1} of {self.totalQuestions}"
        )

        if self.currentQuestionIndex == self.totalQuestions - 1:
            self.nextButton.setText("Submit")
        else:
            self.nextButton.setText("Next")

        self.backButton.setEnabled(self.currentQuestionIndex > 0)

        self.currentSubQuestionCards = []
        for i, sub_question_data in enumerate(sub_questions):
            sub_question_card = self._createSubQuestionCard(sub_question_data, i)
            if sub_question_card:
                self.currentSubQuestionCards.append(sub_question_card)
                self.questionLayout.addWidget(sub_question_card)

    def _clearQuestionContainer(self):
        """Clear all widgets from the question container"""
        if hasattr(self, "currentSubQuestionCards"):
            for card in self.currentSubQuestionCards:
                if hasattr(card, "extraWidgetLayout"):
                    while card.extraWidgetLayout.count():
                        item = card.extraWidgetLayout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()

        while self.questionLayout.count():
            item = self.questionLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _createSubQuestionCard(self, subQuestionData: dict, subQuestionIndex: int):
        """Create a sub-question card based on the sub-question data"""
        question_type = subQuestionData.get("type", "text")
        question_text = subQuestionData.get("text", "")
        is_submitted = subQuestionData.get("is_submitted", False)

        if question_type == "multiple_choice" or question_type == "options":
            options = subQuestionData.get("options", [])
            questionCard = OptionsQuestionCard(question_text, options, parent=self)

            image_data = subQuestionData.get("image", None)
            if image_data:
                questionCard.setImage(image_data)
            elif not subQuestionData.get("show_image", True):
                questionCard.hideImage()

        elif question_type == "text" or question_type == "text_input":
            questionCard = TextQuestionCard(question_text, parent=self)

            image_data = subQuestionData.get("image", None)
            if image_data:
                questionCard.setImage(image_data)
            elif not subQuestionData.get("show_image", True):
                questionCard.hideImage()

        else:
            questionCard = TextQuestionCard(question_text, parent=self)

        if hasattr(questionCard, "submitBtn"):
            questionCard.submitBtn.clicked.connect(
                lambda checked, idx=subQuestionIndex: self._onSubQuestionSubmit(idx)
            )
        if hasattr(questionCard, "showKeywordsBtn"):
            questionCard.showKeywordsBtn.clicked.connect(
                lambda checked, idx=subQuestionIndex: self._onShowKeywords(idx)
            )
        if hasattr(questionCard, "dontKnowBtn"):
            questionCard.dontKnowBtn.clicked.connect(
                lambda checked, idx=subQuestionIndex: self._onDontKnow(idx)
            )

        if is_submitted:
            if isinstance(questionCard, TextQuestionCard):
                questionCard.setAnswerText(subQuestionData.get("user_answer", ""))
                questionCard.answerInput.setReadOnly(True)
            elif isinstance(questionCard, OptionsQuestionCard):
                for checkbox in questionCard.checkboxes:
                    checkbox.setChecked(
                        subQuestionData.get("user_answer", []).count(checkbox.text())
                        > 0
                    )
                    checkbox.setEnabled(False)

            questionCard.addExtraWidget(
                FeedbackCard(
                    subQuestionData.get("feedback", ""),
                    subQuestionData.get("performance", ""),
                )
            )
            questionCard.submitBtn.hide()
            questionCard.showKeywordsBtn.hide()
            questionCard.dontKnowBtn.hide()

        return questionCard

    def _onSubQuestionSubmit(self, subQuestionIndex: int):
        """Handle sub-question submission"""
        if subQuestionIndex < len(self.currentSubQuestionCards):
            questionCard = self.currentSubQuestionCards[subQuestionIndex]

            if isinstance(questionCard, OptionsQuestionCard):
                answer = questionCard.getSelectedOptions()
            elif isinstance(questionCard, TextQuestionCard):
                answer = questionCard.getAnswerText()
            else:
                answer = None

            current_question = self.questions[self.currentQuestionIndex]
            sub_question_id = current_question["sub_questions"][subQuestionIndex]["id"]

            self.submitSubQuestion.emit(self.assignmentId, sub_question_id, answer)

    def _onShowKeywords(self, subQuestionIndex: int):
        """Handle show keywords button click"""
        if self.currentQuestionIndex < len(self.questions) and subQuestionIndex < len(
            self.questions[self.currentQuestionIndex].get("sub_questions", [])
        ):
            currentQuestion = self.questions[self.currentQuestionIndex]
            subQuestions = currentQuestion.get("sub_questions", [])
            keywords = subQuestions[subQuestionIndex].get("keywords", [])
            questionCard = self.currentSubQuestionCards[subQuestionIndex]
            questionCard.showKeywords(keywords)

    def _onDontKnow(self, subQuestionIndex: int):
        """Handle don't know button click"""
        if self.currentQuestionIndex < len(self.questions) and subQuestionIndex < len(
            self.questions[self.currentQuestionIndex].get("sub_questions", [])
        ):
            currentQuestion = self.questions[self.currentQuestionIndex]
            subQuestions = currentQuestion.get("sub_questions", [])
            subQuestionId = subQuestions[subQuestionIndex].get("id", 0)
            self.aiPanel.setSubQuestionContext(subQuestionId)
            self.aiPanelContainer.show()
            self.aiPanel.show()

    def _onBackClicked(self):
        """Handle back button click"""
        if self.currentQuestionIndex > 0:
            self._saveCurrentAnswers()
            self.currentQuestionIndex -= 1
            self._loadCurrentQuestion()
            self._restoreAnswers()
        else:
            if self.studentController:
                self.studentController.goToClass()

    def _onNextClicked(self):
        """Handle next button click"""
        self._saveCurrentAnswers()

        if self.currentQuestionIndex < self.totalQuestions - 1:
            self.currentQuestionIndex += 1
            self._loadCurrentQuestion()
            self._restoreAnswers()
        else:
            self.submitAssignment.emit(self.allAnswers)

    def _saveCurrentAnswers(self):
        """Save answers from current question cards"""
        if (
            not hasattr(self, "currentSubQuestionCards")
            or not self.currentSubQuestionCards
        ):
            return

        current_question = self.questions[self.currentQuestionIndex]
        question_id = current_question["id"]

        if question_id not in self.allAnswers:
            self.allAnswers[question_id] = {}

        for i, questionCard in enumerate(self.currentSubQuestionCards):
            sub_question_id = current_question["sub_questions"][i]["id"]

            if isinstance(questionCard, OptionsQuestionCard):
                answer = questionCard.getSelectedOptions()
            elif isinstance(questionCard, TextQuestionCard):
                answer = questionCard.getAnswerText()
            else:
                answer = None

            self.allAnswers[question_id][sub_question_id] = answer

    def _restoreAnswers(self):
        """Restore answers to current question cards"""
        if (
            not hasattr(self, "currentSubQuestionCards")
            or not self.currentSubQuestionCards
        ):
            return

        current_question = self.questions[self.currentQuestionIndex]
        question_id = current_question["id"]

        if question_id not in self.allAnswers:
            return

        for i, questionCard in enumerate(self.currentSubQuestionCards):
            sub_question_id = current_question["sub_questions"][i]["id"]

            if sub_question_id in self.allAnswers[question_id]:
                answer = self.allAnswers[question_id][sub_question_id]

                if isinstance(questionCard, OptionsQuestionCard) and isinstance(
                    answer, list
                ):
                    for j, checkbox in enumerate(questionCard.checkboxes):
                        checkbox.setChecked((j + 1) in answer)
                elif isinstance(questionCard, TextQuestionCard) and isinstance(
                    answer, str
                ):
                    questionCard.setAnswerText(answer)

    def _onAIPanelClose(self):
        """Handle AI panel close button click"""
        self.aiPanelContainer.hide()
        self.aiPanel.hide()


class QuestionReviewInterface(QWidget):
    """Question review interface for viewing past completed questions"""

    def __init__(
        self,
        questionData: dict = None,
        studentController=None,
        previousInterface="class",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("questionReviewInterface")
        self.studentController = studentController
        self.previousInterface = previousInterface

        self.questionData = questionData or {}
        self.assignment_title = self.questionData.get("title", "Assignment Review")
        self.questions = self.questionData.get("questions", [])

        self.currentQuestionIndex = 0
        self.totalQuestions = len(self.questions)

        self.current_question_title = "Question Review"

        self.setupUi()

    def setupUi(self):
        self.setStyleSheet("background-color: #f5f5f5;")

        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setScrollAnimation(
            Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint
        )
        self.scrollArea.setScrollAnimation(
            Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint
        )
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollArea.setStyleSheet("background-color: #f5f5f5; border: none;")

        self.container = QWidget()
        self.scrollArea.setWidget(self.container)

        self.mainLayout = QVBoxLayout(self.container)
        self.mainLayout.setContentsMargins(35, 25, 35, 25)
        self.mainLayout.setSpacing(20)

        # Header
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(8)

        # Question name
        self.titleLabel = TitleLabel(self.current_question_title)
        headerLayout.addWidget(self.titleLabel)

        # Attribution
        self.attributionLabel = BodyLabel("")
        self.attributionLabel.hide()
        if self.questions[self.currentQuestionIndex].get("attribution", None):
            self.attributionLabel = BodyLabel(
                self.questions[self.currentQuestionIndex].get("attribution", "")
            )
            self.attributionLabel.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextBrowserInteraction
            )
            self.attributionLabel.setOpenExternalLinks(True)
            self.attributionLabel.setWordWrap(True)
            self.attributionLabel.show()
            headerLayout.addWidget(self.attributionLabel)

        self.mainLayout.addLayout(headerLayout)

        # Progress
        self.progressLayout = QHBoxLayout()
        self.progressLabel = BodyLabel(
            f"Question {self.currentQuestionIndex + 1} of {self.totalQuestions}"
        )
        self.progressLabel.setStyleSheet("color: #666666; font-weight: 500;")
        self.progressLayout.addWidget(self.progressLabel)
        self.progressLayout.addStretch()
        self.mainLayout.addLayout(self.progressLayout)

        # Question
        self.questionContainer = QWidget()
        self.questionLayout = QVBoxLayout(self.questionContainer)
        self.questionLayout.setContentsMargins(0, 0, 0, 0)
        self.questionLayout.setSpacing(15)
        self.mainLayout.addWidget(self.questionContainer)

        # Footer
        footerLayout = QHBoxLayout()
        footerLayout.setContentsMargins(0, 15, 0, 0)

        # Back
        self.backButton = PushButton("Back")
        self.backButton.clicked.connect(self._onBackClicked)

        # Next
        self.nextButton = PrimaryPushButton("Next")
        self.nextButton.clicked.connect(self._onNextClicked)

        footerLayout.addWidget(self.backButton)
        footerLayout.addStretch()
        footerLayout.addWidget(self.nextButton)

        self.mainLayout.addLayout(footerLayout)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scrollArea)

        self._loadCurrentQuestion()

    def _loadCurrentQuestion(self):
        """Load the current question and its sub-questions"""
        if not self.questions or self.currentQuestionIndex >= len(self.questions):
            return

        self._clearQuestionContainer()

        current_question = self.questions[self.currentQuestionIndex]
        attribution = current_question.get("attribution", "")
        question_title = current_question.get(
            "title", f"Question {self.currentQuestionIndex + 1}"
        )
        sub_questions = current_question.get("sub_questions", [])

        self.current_question_title = question_title
        self.titleLabel.setText(question_title)

        if attribution:
            self.attributionLabel.setText(attribution)
            self.attributionLabel.show()
        else:
            self.attributionLabel.hide()

        self.progressLabel.setText(
            f"Question {self.currentQuestionIndex + 1} of {self.totalQuestions}"
        )

        if self.currentQuestionIndex == self.totalQuestions - 1:
            self.nextButton.setText("Finish Review")
        else:
            self.nextButton.setText("Next")

        self.backButton.setEnabled(self.currentQuestionIndex > 0)

        self.currentSubQuestionCards = []
        for i, sub_question_data in enumerate(sub_questions):
            sub_question_card = self._createReadOnlySubQuestionCard(
                sub_question_data, i
            )
            if sub_question_card:
                self.currentSubQuestionCards.append(sub_question_card)
                self.questionLayout.addWidget(sub_question_card)

    def _clearQuestionContainer(self):
        """Clear all widgets from the question container"""
        while self.questionLayout.count():
            item = self.questionLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _createReadOnlySubQuestionCard(
        self, subQuestionData: dict, subQuestionIndex: int
    ):
        """Create a read-only sub-question card based on the sub-question data"""
        question_type = subQuestionData.get("type", "text")
        question_text = subQuestionData.get("text", "")

        if question_type == "multiple_choice" or question_type == "options":
            options = subQuestionData.get("options", [])
            questionCard = OptionsQuestionCard(question_text, options, parent=self)

            image_data = subQuestionData.get("image", None)
            if image_data:
                questionCard.setImage(image_data)
            else:
                questionCard.hideImage()

            user_answer = subQuestionData.get("user_answer", [])
            for checkbox in questionCard.checkboxes:
                checkbox.setChecked(user_answer.count(checkbox.text()) > 0)
                checkbox.setEnabled(False)

        elif question_type == "text" or question_type == "text_input":
            questionCard = TextQuestionCard(question_text, parent=self)

            image_data = subQuestionData.get("image", None)
            if image_data:
                questionCard.setImage(image_data)
            else:
                questionCard.hideImage()

            user_answer = subQuestionData.get("user_answer", "")
            questionCard.answerInput.setReadOnly(True)
            questionCard.answerInput.setPlainText(user_answer)

        else:
            questionCard = TextQuestionCard(question_text, parent=self)
            questionCard.answerInput.setReadOnly(True)

        if hasattr(questionCard, "submitBtn"):
            questionCard.submitBtn.hide()
        if hasattr(questionCard, "showKeywordsBtn"):
            questionCard.showKeywordsBtn.hide()
        if hasattr(questionCard, "dontKnowBtn"):
            questionCard.dontKnowBtn.hide()

        if hasattr(questionCard, "actionLayout"):
            questionCard.actionLayout.setContentsMargins(0, 0, 0, 0)

        feedbackCard = FeedbackCard(
            subQuestionData.get("feedback", "No feedback available"),
            subQuestionData.get("performance", "Unknown"),
        )
        questionCard.addExtraWidget(feedbackCard)

        return questionCard

    def _onBackClicked(self):
        """Handle back button click"""
        if self.currentQuestionIndex > 0:
            self.currentQuestionIndex -= 1
            self._loadCurrentQuestion()
        else:
            if self.studentController:
                if self.previousInterface == "class":
                    self.studentController.goToClass()
                elif self.previousInterface == "questions":
                    self.studentController.goToQuestions()
                elif self.previousInterface == "home":
                    self.studentController.goToHome()

    def _onNextClicked(self):
        """Handle next button click"""
        if self.currentQuestionIndex < self.totalQuestions - 1:
            self.currentQuestionIndex += 1
            self._loadCurrentQuestion()
        else:
            if self.studentController:
                if self.previousInterface == "class":
                    self.studentController.goToClass()
                elif self.previousInterface == "questions":
                    self.studentController.goToQuestions()
                elif self.previousInterface == "home":
                    self.studentController.goToHome()


class JoinClassCard(CardWidget):
    """Join class card for users not enrolled in any class"""

    joinClassClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self.setFixedSize(QSize(380, 200))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        iconLabel = BodyLabel("📚")
        iconLabel.setStyleSheet("font-size: 48px;")
        iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(iconLabel)

        # Title
        title = SubtitleLabel("Join a Class")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 18px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Description
        description = BodyLabel(
            "You're not enrolled in any class yet.\nClick here to join a class."
        )
        description.setStyleSheet("color: #666666; text-align: center;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)

    def mousePressEvent(self, event):
        """Handle mouse click to emit join class signal"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.joinClassClicked.emit()
        super().mousePressEvent(event)


class JoinClassDialog(CardWidget):
    """Dialog for joining a class"""

    joinClass = pyqtSignal(str, str)  # className, enterCode
    dialogClosed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Join a Class")
        self.setFixedSize(380, 300)
        self.setStyleSheet("background-color: white; border-radius: 8px;")

        if parent:
            parent_rect = parent.geometry()
            self.move(
                parent_rect.x() + (parent_rect.width() - self.width()) // 2,
                parent_rect.y() + (parent_rect.height() - self.height()) // 2,
            )

        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        # Header
        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(0, 0, 0, 0)

        title = SubtitleLabel("Join a Class")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 20px;")
        headerLayout.addWidget(title)

        headerLayout.addStretch()

        # Close
        closeButton = TransparentToolButton(FluentIcon.CLOSE, self)
        closeButton.setFixedSize(24, 24)
        closeButton.clicked.connect(self.close)
        headerLayout.addWidget(closeButton)

        layout.addLayout(headerLayout)

        # Fields
        formLayout = QVBoxLayout()
        formLayout.setSpacing(15)

        # Class name
        classNameLabel = BodyLabel("Class Name:")
        classNameLabel.setStyleSheet("color: #333333; font-weight: 500;")
        formLayout.addWidget(classNameLabel)

        self.classNameInput = LineEdit()
        self.classNameInput.setPlaceholderText("Enter the class name")
        self.classNameInput.setFixedHeight(35)
        formLayout.addWidget(self.classNameInput)

        # Enter code
        enterCodeLabel = BodyLabel("Enter Code:")
        enterCodeLabel.setStyleSheet("color: #333333; font-weight: 500;")
        formLayout.addWidget(enterCodeLabel)

        self.enterCodeInput = LineEdit()
        self.enterCodeInput.setPlaceholderText("Enter the class code")
        self.enterCodeInput.setFixedHeight(35)
        formLayout.addWidget(self.enterCodeInput)

        layout.addLayout(formLayout)

        # Buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 10, 0, 0)

        cancelButton = PushButton("Cancel")
        cancelButton.clicked.connect(self.close)
        buttonLayout.addWidget(cancelButton)

        buttonLayout.addStretch()

        joinButton = PrimaryPushButton("Join Class")
        joinButton.clicked.connect(self._onJoinClicked)
        buttonLayout.addWidget(joinButton)

        layout.addLayout(buttonLayout)

    def _onJoinClicked(self):
        """Handle join button click"""
        class_name = self.classNameInput.text().strip()
        enter_code = self.enterCodeInput.text().strip()

        if not class_name or not enter_code:
            self.showError("Please fill in both class name and enter code.")
            return

        self.joinClass.emit(class_name, enter_code)
        self.close()

    def closeEvent(self, event):
        """Handle dialog close event"""
        self.dialogClosed.emit()
        super().closeEvent(event)

    def showError(self, message: str):
        """Show error message"""
        InfoBar.error(
            title="Error",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self.parent(),
        )


class StudentMainWindow(FluentWindow):
    """Main student application window"""

    requestNewWindow = pyqtSignal()

    def __init__(self, studentController: StudentController = None):
        super().__init__()
        self.studentController = studentController

        self.setWindowIcon(QIcon("resources:icon.png"))

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))
        self.splashScreen.raise_()

        self.setupInterfaces()
        self.initWindow()
        self.connectControllerSignals()

        self._loadStatus = {
            "dashboard": False,
            "class": False,
            "questions": False,
        }
        self.loadData()

    def loadData(self):
        """Load data from the controller"""
        self.studentController.loadDashboardData()
        self.studentController.loadClassData()
        self.studentController.loadQuestions()

    def refreshBackgroundData(self):
        """Refresh background data"""
        self._isBackgroundRefresh = True
        self._backgroundRefreshCount = 0

        self.studentController.loadDashboardData()
        self.studentController.loadClassData()
        self.studentController.loadQuestions()

    def _checkBackgroundRefreshComplete(self):
        """Check if background refresh is complete and reset flag"""
        self._backgroundRefreshCount = getattr(self, "_backgroundRefreshCount", 0) + 1

        if self._backgroundRefreshCount >= 3:
            self._isBackgroundRefresh = False
            self._backgroundRefreshCount = 0

    def _updateHomeInterfaceContent(self, dashboardData: dict):
        """Update home interface content"""
        if not self.homeInterface:
            return

        self.homeInterface.updateContent(dashboardData)

    def _updateClassInterfaceContent(self, classData: dict):
        """Update class interface content"""
        if not self.classInterface:
            return

        self.classInterface.updateContent(classData)

    def _updateQuestionsInterfaceContent(self, questionsData: list):
        """Update questions interface content"""
        if not self.questionsInterface:
            return

        self.questionsInterface.updateContent(questionsData)

    def initWindow(self):
        """Initialize window properties"""
        self.setWindowTitle("Nanoko")
        self.resize(1200, 800)

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        setTheme(Theme.LIGHT)

        self.navigationInterface.setAcrylicEnabled(True)
        self.navigationInterface.setExpandWidth(250)

    def onAssignmentClicked(self, assignmentId: str):
        """Handle assignment click"""
        self.studentController.loadAssignmentData(assignmentId)

    def onDoneAssignmentClicked(self, assignmentId: str):
        """Handle done assignment click"""
        self.studentController.loadAssignmentReviewData(assignmentId)

    def onQuestionClicked(self, questionId: str):
        """Handle question card click"""
        self.studentController.loadQuestionReviewData(questionId)

    def onQuestionAnsweringDataReady(self, questionData: dict):
        """Handle question answering data ready"""
        questionAnsweringInterface = QuestionAnsweringInterface(
            questionData, self.studentController, self
        )

        questionAnsweringInterface.aiPanel.sendMessage.connect(self._onAIMessageSent)
        questionAnsweringInterface.submitSubQuestion.connect(self._onSubQuestionSubmit)
        questionAnsweringInterface.submitAssignment.connect(self._onAssignmentSubmit)

        if questionAnsweringInterface not in [
            self.stackedWidget.widget(i) for i in range(self.stackedWidget.count())
        ]:
            self.stackedWidget.addWidget(questionAnsweringInterface)

        self.stackedWidget.setCurrentWidget(questionAnsweringInterface)

        self.currentQuestionAnsweringInterface = questionAnsweringInterface

    def onQuestionReviewDataReady(self, questionData: dict):
        """Handle question review data ready"""
        questionReviewInterface = QuestionReviewInterface(
            questionData, self.studentController, "questions", self
        )

        if questionReviewInterface not in [
            self.stackedWidget.widget(i) for i in range(self.stackedWidget.count())
        ]:
            self.stackedWidget.addWidget(questionReviewInterface)

        self.stackedWidget.setCurrentWidget(questionReviewInterface)

    def onAssignmentReviewDataReady(self, assignmentData: dict):
        """Handle assignment review data ready"""
        questionReviewInterface = QuestionReviewInterface(
            assignmentData, self.studentController, "class", self
        )

        if questionReviewInterface not in [
            self.stackedWidget.widget(i) for i in range(self.stackedWidget.count())
        ]:
            self.stackedWidget.addWidget(questionReviewInterface)

        self.stackedWidget.setCurrentWidget(questionReviewInterface)

    def handleError(self, operation: str, error_message: str):
        """Handle errors from the controller"""
        print(f"Error: {operation} - {error_message}")
        InfoBar.error(
            title="Error",
            content=error_message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def switchTo(self, interface):
        """Switch to the specified interface"""
        self.stackedWidget.setCurrentWidget(interface)

    def onSubQuestionFeedbackReady(self, sub_question_id: int, feedback: dict):
        """Handle sub-question feedback ready from controller"""
        if (
            hasattr(self, "currentQuestionAnsweringInterface")
            and self.currentQuestionAnsweringInterface
        ):
            feedbackCard = FeedbackCard(
                feedback.get("feedback", "No feedback available"),
                feedback.get("performance", "Unknown"),
            )

            interface = self.currentQuestionAnsweringInterface
            if (
                hasattr(interface, "currentSubQuestionCards")
                and interface.currentSubQuestionCards
                and hasattr(interface, "questions")
                and interface.currentQuestionIndex < len(interface.questions)
            ):
                current_question = interface.questions[interface.currentQuestionIndex]
                sub_questions = current_question.get("sub_questions", [])

                target_card_index = None
                for i, sub_question in enumerate(sub_questions):
                    if sub_question.get("id") == sub_question_id:
                        target_card_index = i
                        break

                if target_card_index is not None and target_card_index < len(
                    interface.currentSubQuestionCards
                ):
                    targetCard = interface.currentSubQuestionCards[target_card_index]
                    targetCard.addExtraWidget(feedbackCard)

                    if hasattr(targetCard, "submitBtn"):
                        targetCard.submitBtn.hide()
                    if hasattr(targetCard, "showKeywordsBtn"):
                        targetCard.showKeywordsBtn.hide()
                    if hasattr(targetCard, "dontKnowBtn"):
                        targetCard.dontKnowBtn.hide()

                    if hasattr(targetCard, "checkboxes"):
                        for i, checkbox in enumerate(targetCard.checkboxes):
                            checkbox.setEnabled(False)
                    if hasattr(targetCard, "answerInput"):
                        targetCard.answerInput.setReadOnly(True)

            self.refreshBackgroundData()

    def onAIResponseReady(self, response: str):
        """Handle AI response ready from controller"""
        if (
            hasattr(self, "currentQuestionAnsweringInterface")
            and self.currentQuestionAnsweringInterface
        ):
            self.currentQuestionAnsweringInterface.aiPanel.addAIMessage(response)

    def _onAIMessageSent(self, message: str, history: list):
        """Handle AI message sent from the panel"""
        if (
            hasattr(self, "currentQuestionAnsweringInterface")
            and self.currentQuestionAnsweringInterface
        ):
            aiPanel = self.currentQuestionAnsweringInterface.aiPanel
            subQuestionId = getattr(aiPanel, "currentSubQuestionId", 0)

            self.studentController.sendAIMessage(message, subQuestionId, history)

    def _onSubQuestionSubmit(self, assignment_id: int, sub_question_id: int, answer):
        """Handle sub-question submission for instant feedback"""
        if self.studentController:
            self.studentController.submitSubQuestion(
                assignment_id, sub_question_id, answer
            )

    def _onAssignmentSubmit(self, allAnswers: dict):
        """Handle assignment submission"""
        if self.studentController:
            self.studentController.goToClass()

    def onJoinClassRequested(self, class_name: str, enter_code: str):
        """Handle join class request from home interface"""
        if self.studentController:
            self.studentController.joinClass(class_name, enter_code)

    def onJoinClassResult(self, success: bool, message: str):
        """Handle join class result"""
        if success:
            self.requestNewWindow.emit()
        else:
            InfoBar.error(
                title="Error",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )

    def setupInterfaces(self):
        """Create interfaces"""
        self.homeInterface = None
        self.classInterface = None
        self.questionsInterface = None

    def initNavigation(self):
        """Initialize navigation"""
        self.addSubInterface(self.homeInterface, FluentIcon.HOME, "Home")
        self.addSubInterface(self.classInterface, FluentIcon.BOOK_SHELF, "Class")
        self.addSubInterface(self.questionsInterface, FluentIcon.QUESTION, "Questions")

    def connectControllerSignals(self):
        """Connect controller signals"""
        if self.studentController:
            self.studentController.dashboardDataReady.connect(self.onDashboardDataReady)
            self.studentController.classDataReady.connect(self.onClassDataReady)
            self.studentController.questionsReady.connect(self.onQuestionsDataReady)
            self.studentController.questionAnsweringDataReady.connect(
                self.onQuestionAnsweringDataReady
            )
            self.studentController.questionReviewDataReady.connect(
                self.onQuestionReviewDataReady
            )
            self.studentController.assignmentReviewDataReady.connect(
                self.onAssignmentReviewDataReady
            )
            self.studentController.subQuestionFeedbackReady.connect(
                self.onSubQuestionFeedbackReady
            )
            self.studentController.aiResponseReady.connect(self.onAIResponseReady)
            self.studentController.joinClassResult.connect(self.onJoinClassResult)
            self.studentController.errorOccurred.connect(self.handleError)

            self.studentController.navigateToHome.connect(
                lambda: self.switchTo(self.homeInterface)
            )
            self.studentController.navigateToClass.connect(
                lambda: self.switchTo(self.classInterface)
            )
            self.studentController.navigateToQuestions.connect(
                lambda: self.switchTo(self.questionsInterface)
            )

    def connectInterfaceSignals(self):
        """Connect interface signals"""
        if self.classInterface:
            self.classInterface.assignmentClicked.connect(self.onAssignmentClicked)
            self.classInterface.doneAssignmentClicked.connect(
                self.onDoneAssignmentClicked
            )
            self.classInterface.joinClassRequested.connect(self.onJoinClassRequested)
        if self.homeInterface:
            self.homeInterface.classClicked.connect(
                lambda: self.switchTo(self.classInterface)
            )
            self.homeInterface.joinClassRequested.connect(self.onJoinClassRequested)
        if self.questionsInterface:
            self.questionsInterface.questionClicked.connect(self.onQuestionClicked)

    def onDashboardDataReady(self, dashboardData: dict):
        """Handle dashboard data ready"""
        if getattr(self, "_isBackgroundRefresh", False):
            if self.homeInterface:
                self._updateHomeInterfaceContent(dashboardData)

            self._checkBackgroundRefreshComplete()
        else:
            self._loadStatus["dashboard"] = True
            if self.homeInterface:
                self._updateHomeInterfaceContent(dashboardData)
            else:
                self.homeInterface = HomeInterface(dashboardData, self)
            self._finishLoading()

    def onClassDataReady(self, classData: dict):
        """Handle class data ready"""
        if getattr(self, "_isBackgroundRefresh", False):
            if self.classInterface:
                self._updateClassInterfaceContent(classData)

            self._checkBackgroundRefreshComplete()
        else:
            self._loadStatus["class"] = True
            if self.classInterface:
                self._updateClassInterfaceContent(classData)
            else:
                self.classInterface = ClassInterface(classData, self)
            self._finishLoading()

    def onQuestionsDataReady(self, questionsData: list):
        """Handle questions data ready"""
        if getattr(self, "_isBackgroundRefresh", False):
            if self.questionsInterface:
                self._updateQuestionsInterfaceContent(questionsData)

            self._checkBackgroundRefreshComplete()
        else:
            self._loadStatus["questions"] = True
            if self.questionsInterface:
                self._updateQuestionsInterfaceContent(questionsData)
            else:
                self.questionsInterface = QuestionsInterface(questionsData, self)
            self._finishLoading()

    def _finishLoading(self):
        """Finish loading data"""
        if (
            self._loadStatus["dashboard"]
            and self._loadStatus["class"]
            and self._loadStatus["questions"]
        ):
            self.initNavigation()
            self.connectInterfaceSignals()
            self.switchTo(self.homeInterface)
            self.splashScreen.finish()
