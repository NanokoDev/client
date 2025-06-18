from datetime import datetime
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication
from qframelesswindow import FramelessWindow
from PyQt6.QtGui import QColor, QPixmap, QImage, QIcon
from nanoko.models.question import ConceptType, ProcessType
from PyQt6.QtCore import Qt, pyqtSignal, QTime, QSize, QEasingCurve
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QHeaderView,
    QFileDialog,
    QStackedWidget,
    QTableWidgetItem,
)
from qfluentwidgets import (
    Pivot,
    Theme,
    TabBar,
    Flyout,
    Action,
    InfoBar,
    setTheme,
    LineEdit,
    ComboBox,
    CheckBox,
    BodyLabel,
    InfoBadge,
    RoundMenu,
    CardWidget,
    TimePicker,
    PushButton,
    ImageLabel,
    TitleLabel,
    FluentIcon,
    FlowLayout,
    TableWidget,
    InfoBarIcon,
    TeachingTip,
    CaptionLabel,
    SplashScreen,
    FluentWindow,
    SubtitleLabel,
    PlainTextEdit,
    CalendarPicker,
    SearchLineEdit,
    StrongBodyLabel,
    InfoBarPosition,
    SmoothScrollArea,
    SimpleCardWidget,
    PrimaryPushButton,
    FlyoutAnimationType,
    TransparentToolButton,
    TeachingTipTailPosition,
)

from app.controllers.teacherController import TeacherController
from app.utils import enumNameToText, levelToColor, cropImageToSquare
from app.views.studentMainWindow import OptionsQuestionCard, TextQuestionCard


class TeacherClassCard(CardWidget):
    """Teacher class card showing class information and assignments"""

    classClicked = pyqtSignal(int)  # classId

    def __init__(self, classId: int, className: str, assignments: list, parent=None):
        super().__init__(parent)
        self.classId = classId
        self.className = className
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedWidth(280)
        self.setMinimumHeight(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Class name
        title = SubtitleLabel(className)
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 16px;")
        layout.addWidget(title)

        # Assignments
        for assignmentName, dueDate in assignments:
            assignmentLayout = QHBoxLayout()
            assignmentLayout.setContentsMargins(0, 2, 0, 2)

            # Assignment name
            nameLabel = BodyLabel(assignmentName)
            nameLabel.setStyleSheet("color: #333333; font-size: 12px;")

            # Due date
            dueLabel = CaptionLabel(f"Due at {dueDate}")
            dueLabel.setStyleSheet("color: #666666; font-size: 10px;")

            assignmentLayout.addWidget(nameLabel)
            assignmentLayout.addStretch()
            assignmentLayout.addWidget(dueLabel)

            layout.addLayout(assignmentLayout)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.classClicked.emit(self.classId)
        super().mousePressEvent(event)


class TeacherAssignmentCard(CardWidget):
    """Teacher assignment card with image"""

    assignmentClicked = pyqtSignal(int)  # assignmentId

    def __init__(
        self,
        assignmentId: int,
        assignmentName: str,
        description: str,
        image: bytes,
        parent=None,
    ):
        super().__init__(parent)
        self.assignmentId = assignmentId
        self.assignmentName = assignmentName
        self.description = description
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedWidth(300)
        self.setFixedHeight(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        contentLayout = QVBoxLayout()
        contentLayout.setSpacing(5)

        # Assignment name
        nameLabel = StrongBodyLabel(assignmentName)
        nameLabel.setStyleSheet("color: #333333; font-weight: 600; font-size: 14px;")
        contentLayout.addWidget(nameLabel)

        # Description
        descLabel = CaptionLabel(
            description[:80] + "..." if len(description) > 80 else description
        )
        descLabel.setStyleSheet("color: #666666; font-size: 11px;")
        descLabel.setWordWrap(True)
        contentLayout.addWidget(descLabel)

        layout.addLayout(contentLayout, 1)

        # Image
        if image is not None:
            scaled_pixmap = cropImageToSquare(image)
            imageWidget = ImageLabel(scaled_pixmap)
            imageWidget.setFixedSize(60, 60)
            layout.addWidget(imageWidget)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.assignmentClicked.emit(self.assignmentId)
        super().mousePressEvent(event)


class SelectableQuestionCard(CardWidget):
    """Individual question card displaying question information, with a selectable checkbox"""

    selectionChanged = pyqtSignal(bool, int)  # selected, questionId

    def __init__(
        self,
        questionId: int,
        questionTitle: str,
        questions: list,
        footerText: str = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedWidth(760)
        self.questionId = questionId
        self.questionTitle = questionTitle
        self.questions = questions

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(10)

        # Question title
        questionTitle = SubtitleLabel(questionTitle)
        headerLayout.addWidget(questionTitle)

        headerLayout.addStretch()

        self.selectCheckbox = CheckBox("Select")
        self.selectCheckbox.stateChanged.connect(self.handleSelect)
        headerLayout.addWidget(self.selectCheckbox)

        headerWidget = QWidget()
        headerWidget.setLayout(headerLayout)
        layout.addWidget(headerWidget)

        # Questions
        for i, questionData in enumerate(questions):
            questionLayout = self.createQuestionItem(questionData, i)
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

    def createQuestionItem(self, questionData, index):
        """Create a single question item layout"""
        questionLayout = QHBoxLayout()
        questionLayout.setSpacing(20)

        # Content area
        contentLayout = QVBoxLayout()
        contentLayout.setSpacing(8)

        # Question title
        questionTitle = StrongBodyLabel(f"Sub-question {chr(65 + index)}")
        contentLayout.addWidget(questionTitle)

        # Question text
        questionText = BodyLabel(questionData["text"])
        questionText.setAlignment(Qt.AlignmentFlag.AlignTop)
        questionText.setWordWrap(True)
        contentLayout.addWidget(questionText)

        # Tags
        tagsLayout = QHBoxLayout()
        tagsLayout.setSpacing(8)
        tagsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for tagText, tagType in questionData["tags"]:
            tag = self.createTag(tagText, tagType)
            tagsLayout.addWidget(tag)

        tagsLayout.addStretch()
        contentLayout.addLayout(tagsLayout)

        questionLayout.addLayout(contentLayout, 1)

        # Right section
        rightLayout = QVBoxLayout()
        rightLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        rightLayout.setSpacing(10)

        # Image area
        imageData = questionData.get("image", None)
        if imageData:
            imageWidget = ImageLabel(cropImageToSquare(imageData, 80))
            rightLayout.addWidget(imageWidget)

        questionLayout.addLayout(rightLayout)

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
        }

        tag = colorMap.get(
            tagType.lower(),
            lambda text: InfoBadge.info(text),
        )(text)

        return tag

    def handleSelect(self, state):
        """Handle select the checkbox"""
        isChecked = state == Qt.CheckState.Checked.value
        self.selectionChanged.emit(isChecked, self.questionId)

    def setChecked(self, checked: bool):
        """Set the checked state of the checkbox"""
        self.selectCheckbox.setChecked(checked)


class SelectQuestionsWindow(FramelessWindow):
    """Window for selecting questions to add to assignments"""

    questionsSelected = pyqtSignal(list)

    def __init__(
        self,
        controller: TeacherController = None,
        selectedQuestions: list = None,
        questionsData: list = None,
        parent=None,
    ):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Select Questions")
        self.resize(900, 700)
        self.selectedQuestions = {
            questionId: True for questionId in selectedQuestions or []
        }
        self.selectedQuestionsData = []
        self.questionsData = questionsData or []
        self.questionCards = []
        self.setupUi()

        if self.controller:
            self.controller.filteredQuestionsDataReady.connect(self.onQuestionsLoaded)

        if parent:
            parentGeometry = parent.geometry()
            x = parentGeometry.x() + (parentGeometry.width() - self.width()) // 2
            y = parentGeometry.y() + (parentGeometry.height() - self.height()) // 2
            self.move(x, y)

        if not self.questionsData:
            self.loadQuestions()

    def setupUi(self):
        self.setStyleSheet("background-color: #f5f5f5;")

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 35, 30, 30)
        mainLayout.setSpacing(20)

        # Header
        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(15)

        # Title
        title = TitleLabel("Select Questions")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 24px;")
        headerLayout.addWidget(title)

        headerLayout.addStretch()

        # Search bar
        self.searchInput = SearchLineEdit()
        self.searchInput.setPlaceholderText("Search")
        self.searchInput.setFixedWidth(200)
        self.searchInput.textChanged.connect(self.handleSearch)
        headerLayout.addWidget(self.searchInput)

        # Filters
        self.conceptFilter = ComboBox()
        self.conceptFilter.addItems(
            ["All Concepts"] + [enumNameToText(concept.name) for concept in ConceptType]
        )
        self.conceptFilter.setFixedWidth(130)
        self.conceptFilter.currentTextChanged.connect(self.handleFilterChange)
        headerLayout.addWidget(self.conceptFilter)

        self.processFilter = ComboBox()
        self.processFilter.addItems(
            ["All Processes"]
            + [enumNameToText(process.name) for process in ProcessType]
        )
        self.processFilter.setFixedWidth(130)
        self.processFilter.currentTextChanged.connect(self.handleFilterChange)
        headerLayout.addWidget(self.processFilter)

        mainLayout.addLayout(headerLayout)

        # Questions
        scrollArea = SmoothScrollArea()
        scrollArea.setScrollAnimation(
            Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint
        )
        scrollArea.setScrollAnimation(
            Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint
        )

        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("background-color: #f5f5f5; border: none;")

        scrollContainer = QWidget()
        scrollArea.setWidget(scrollContainer)

        self.questionsLayout = QVBoxLayout(scrollContainer)
        self.questionsLayout.setContentsMargins(0, 20, 0, 20)
        self.questionsLayout.setSpacing(20)

        if self.questionsData:
            self.createQuestionCards()

        self.questionsLayout.addStretch()
        mainLayout.addWidget(scrollArea)

        # Bottom buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 10, 0, 0)

        # Cancel button
        cancelBtn = PushButton("Cancel")
        cancelBtn.setFixedHeight(35)
        cancelBtn.setFixedWidth(80)
        cancelBtn.clicked.connect(self.handleCancel)
        buttonLayout.addWidget(cancelBtn)

        buttonLayout.addStretch()

        # Next button
        self.nextBtn = PrimaryPushButton("Next")
        self.nextBtn.setFixedHeight(35)
        self.nextBtn.setFixedWidth(100)
        self.nextBtn.setEnabled(len(self.selectedQuestions) > 0)
        self.nextBtn.clicked.connect(self.handleNext)
        buttonLayout.addWidget(self.nextBtn)

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def loadQuestions(self):
        """Load questions with current filters"""
        if not self.controller:
            return

        searchText = self.searchInput.text()
        conceptFilter = self.conceptFilter.currentText()
        processFilter = self.processFilter.currentText()

        self.controller.loadFilteredQuestions(searchText, conceptFilter, processFilter)

    def onQuestionsLoaded(self, questionsData: list):
        """Handle when questions data is loaded from the API"""
        print(f"[SelectQuestionsWindow] Loaded {len(questionsData)} questions")
        self.questionsData = questionsData
        self.createQuestionCards()

    def createQuestionCards(self):
        """Create question cards from loaded data"""
        self.clearQuestionCards()

        for questionData in self.questionsData:
            questionCard = SelectableQuestionCard(
                questionData["id"],
                questionData["title"],
                questionData["sub_questions"],
                questionData.get("attribution", ""),
                self,
            )
            questionCard.setChecked(
                self.selectedQuestions.get(questionData["id"], False)
            )

            questionCard.selectionChanged.connect(self.handleQuestionSelectionChanged)

            stretchIndex = self.questionsLayout.count() - 1
            if stretchIndex >= 0:
                self.questionsLayout.insertWidget(stretchIndex, questionCard)
            else:
                self.questionsLayout.addWidget(questionCard)

            self.questionCards.append(questionCard)

    def clearQuestionCards(self):
        """Clear all existing question cards"""
        for questionCard in self.questionCards:
            self.questionsLayout.removeWidget(questionCard)
            questionCard.setParent(None)
            questionCard.deleteLater()
        self.questionCards.clear()

    def handleSearch(self, text):
        """Handle search input"""
        self.loadQuestions()

    def handleFilterChange(self, text):
        """Handle filter dropdown changes"""
        self.loadQuestions()

    def handleQuestionSelectionChanged(self, selected, questionId):
        """Handle when a question selection changes"""
        if selected:
            self.selectedQuestions[questionId] = True
        else:
            self.selectedQuestions.pop(questionId, None)

        self.nextBtn.setEnabled(len(self.selectedQuestions) > 0)

    def handleCancel(self):
        """Handle cancel button click"""
        self.close()

    def handleNext(self):
        """Handle next button click"""
        self.questionsSelected.emit(list(self.selectedQuestions.keys()))

        self.close()


class TeacherAssignmentsInterface(QWidget):
    """Teacher assignments interface matching the design image"""

    def __init__(self, controller: TeacherController = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("teacherAssignmentsInterface")
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
        mainLayout.setSpacing(25)

        # Header
        headerLayout = QHBoxLayout()
        headerLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Title
        title = TitleLabel("Assignments")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 28px;")
        headerLayout.addWidget(title)

        headerLayout.addStretch()

        # Create assignment
        createBtn = PrimaryPushButton("Create")
        createBtn.setIcon(FluentIcon.ADD)
        createBtn.clicked.connect(self.handleCreateAssignment)
        headerLayout.addWidget(createBtn)

        mainLayout.addLayout(headerLayout)

        # Assignments
        self.assignmentsFlow = FlowLayout()
        self.assignmentsFlow.setContentsMargins(0, 20, 0, 20)
        self.assignmentsFlow.setVerticalSpacing(20)
        self.assignmentsFlow.setHorizontalSpacing(20)

        mainLayout.addLayout(self.assignmentsFlow)
        mainLayout.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

    def handleCreateAssignment(self):
        """Handle create assignment button click"""
        self.createDialog = CreateAssignmentDialog(self.controller, self)

        self.createDialog.assignmentCreated.connect(self.onAssignmentCreated)

        self.createDialog.show()
        self.createDialog.raise_()
        self.createDialog.activateWindow()

    def onAssignmentCreated(self, name: str, description: str, questionIds: list):
        """Handle when a new assignment is created"""
        self.controller.createAssignment(name, description, questionIds)

    def addAssignment(self, assignmentName: str, description: str, image: bytes):
        """Add a new assignment card to the interface"""
        assignmentCard = TeacherAssignmentCard(
            assignmentName, description, image=image, parent=self
        )
        assignmentCard.assignmentClicked.connect(self.handleAssignmentClick)
        self.assignmentsFlow.addWidget(assignmentCard)

    def updateContent(self, assignmentsData: list):
        """Update the assignments display with new data"""
        while self.assignmentsFlow.count():
            item = self.assignmentsFlow.takeAt(0)
            if item:
                if hasattr(item, "widget"):
                    widget = item.widget()
                else:
                    widget = item
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

        for assignmentData in assignmentsData:
            assignmentId = assignmentData.get("id", None)
            assignmentName = assignmentData.get("name", "Unknown Assignment")
            description = assignmentData.get("description", "")
            image = assignmentData.get("image", None)

            assignmentCard = TeacherAssignmentCard(
                assignmentId, assignmentName, description, image=image, parent=self
            )
            assignmentCard.assignmentClicked.connect(self.handleAssignmentClick)
            self.assignmentsFlow.addWidget(assignmentCard)

    def handleAssignmentClick(self, assignmentId: int):
        """Handle assignment card click"""
        if self.controller:
            self.controller.showAssignmentReview(assignmentId)


class PerformanceChartWidget(QWidget):
    """Student performance chart widget"""

    def __init__(self, studentName: str, performanceData: dict, parent=None):
        super().__init__(parent)
        self.studentName = studentName
        self.performanceData = performanceData
        self.setFixedSize(400, 250)
        self.setupChart()

    def setupChart(self):
        self.figure = Figure(figsize=(5, 3), dpi=80, facecolor="white")
        self.canvas = FigureCanvas(self.figure)

        dates = self.performanceData.get("dates", [])
        scores = self.performanceData.get("scores", [])

        ax = self.figure.add_subplot(111)

        if dates and scores and len(dates) == len(scores):
            ax.plot(dates, scores, "o-", color="#0078d4", linewidth=2, markersize=6)
        else:
            ax.text(
                0.5,
                0.5,
                "No performance data available",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=12,
            )

        ax.set_ylim(0, 4)
        ax.set_ylabel("Score")
        ax.set_title(
            f"{self.studentName}'s Recent Average Performance",
            fontsize=12,
            fontweight="bold",
        )
        ax.grid(True, alpha=0.3)
        ax.set_facecolor("#f8f9fa")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#ccc")
        ax.spines["bottom"].set_color("#ccc")

        self.figure.tight_layout()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def updateChart(self, studentName: str, performanceData: dict):
        """Update the chart with new data"""
        self.studentName = studentName
        self.performanceData = performanceData

        self.figure.clear()

        dates = self.performanceData.get("dates", [])
        scores = self.performanceData.get("scores", [])

        ax = self.figure.add_subplot(111)

        if dates and scores and len(dates) == len(scores):
            ax.plot(dates, scores, "o-", color="#0078d4", linewidth=2, markersize=6)
        else:
            ax.text(
                0.5,
                0.5,
                "No performance data available",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=12,
            )

        ax.set_ylim(0, 4)
        ax.set_ylabel("Score")
        ax.set_title(
            f"{self.studentName}'s Recent Average Performance",
            fontsize=12,
            fontweight="bold",
        )
        ax.grid(True, alpha=0.3)
        ax.set_facecolor("#f8f9fa")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#ccc")
        ax.spines["bottom"].set_color("#ccc")

        self.figure.tight_layout()
        self.canvas.draw()


class StudentPerformanceCard(CardWidget):
    """Student performance card with chart"""

    def __init__(self, studentName: str, performanceData: dict = None, parent=None):
        super().__init__(parent)
        self.studentName = studentName
        self.performanceData = performanceData
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedWidth(450)
        self.setFixedHeight(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.chartWidget = PerformanceChartWidget(
            self.studentName, self.performanceData
        )
        layout.addWidget(self.chartWidget)

    def updateData(self, studentName: str, performanceData: dict):
        """Update the card with new student data"""
        self.studentName = studentName
        self.performanceData = performanceData
        self.chartWidget.updateChart(studentName, performanceData)


class StudentTableWidget(TableWidget):
    """Custom table widget for displaying students"""

    studentStatisticsClicked = pyqtSignal(int, str)  # studentId, studentName
    studentRemovalRequested = pyqtSignal(int, str)  # studentId, studentName

    def __init__(self, controller: TeacherController = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.students = []
        self.className = ""
        self.setupTable()
        self.setupContextMenu()

    def setupTable(self):
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Name", "Username"])

        self.setRowCount(0)

        self.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)
        self.setSelectRightClickedRow(True)
        self.doubleClicked.connect(self.handleDoubleClick)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def handleDoubleClick(self, item):
        """Handle double-click on student item to view statistics"""
        if item is None:
            return
        row = item.row()
        studentId = self.students[row].get("id")
        studentName = self.students[row].get("name")
        print(f"Student ID: {studentId}, Student Name: {studentName}")
        print(f"Students: {self.students}")
        self.studentStatisticsClicked.emit(studentId, studentName)

    def setupContextMenu(self):
        """Setup context menu for right-click actions"""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, position):
        """Show context menu on right-click"""
        item = self.itemAt(position)
        if item is None:
            return

        row = item.row()
        studentId = self.students[row].get("id")
        studentName = self.students[row].get("name")

        menu = RoundMenu(parent=self)

        statsAction = Action(FluentIcon.PIE_SINGLE, "View Statistics")
        statsAction.triggered.connect(
            lambda: self.handleStatisticsClick(studentId, studentName)
        )
        menu.addAction(statsAction)

        menu.addSeparator()

        removeAction = Action(FluentIcon.DELETE, "Remove Student")
        removeAction.triggered.connect(
            lambda: self.handleRemoveStudent(studentId, studentName)
        )
        menu.addAction(removeAction)

        menu.exec(self.mapToGlobal(position))

    def handleStatisticsClick(self, studentId: int, studentName: str):
        """Handle statistics button click"""
        self.studentStatisticsClicked.emit(studentId, studentName)

    def handleRemoveStudent(self, studentId: int, studentName: str):
        """Handle remove student request"""
        self.studentRemovalRequested.emit(studentId, studentName)

    def setClassName(self, className: str):
        """Set the class name for this table"""
        self.className = className

    def updateStudents(self, studentsData: list):
        """Update the students table with new data"""
        self.setRowCount(len(studentsData))
        self.students = studentsData

        for row, studentData in enumerate(studentsData):
            name = studentData.get("name", "Unknown")
            username = studentData.get("username", "unknown")

            # Name column
            nameItem = QTableWidgetItem(name)
            nameItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.setItem(row, 0, nameItem)

            # Username column
            usernameItem = QTableWidgetItem(username)
            usernameItem.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            self.setItem(row, 1, usernameItem)


class AssignmentsTableWidget(TableWidget):
    """Custom table widget for displaying assignments"""

    def __init__(self, controller: TeacherController = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.classId = None
        self.setupTable()
        self.setupContextMenu()

    def setupTable(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(
            ["Assignment Name", "Description", "Status", "Due Date"]
        )

        self.assignments = []
        self.setRowCount(0)

        self.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)
        self.setSelectRightClickedRow(True)

        self.itemDoubleClicked.connect(self.handleItemDoubleClick)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        self.setColumnWidth(0, 200)  # Assignment Name
        self.setColumnWidth(2, 100)  # Status
        self.setColumnWidth(3, 120)  # Due Date

    def setupContextMenu(self):
        """Setup context menu for right-click actions"""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def handleItemDoubleClick(self, item):
        """Handle double-click on assignment item to review"""
        if item is None:
            return

        row = item.row()
        if row < len(self.assignments):
            assignmentId = self.assignments[row][4]
            self.handleReviewClick(assignmentId)

    def showContextMenu(self, position):
        """Show context menu on right-click"""
        item = self.itemAt(position)
        if item is None:
            return

        row = item.row()
        assignmentId = self.assignments[row][4] if row < len(self.assignments) else 1

        menu = RoundMenu(parent=self)

        reviewAction = Action(FluentIcon.LINK, "Review Assignment")
        reviewAction.triggered.connect(lambda: self.handleReviewClick(assignmentId))
        menu.addAction(reviewAction)

        menu.exec(self.mapToGlobal(position))

    def setClassId(self, classId: int):
        """Set the class name for this table"""
        self.classId = classId

    def handleReviewClick(self, assignmentId: int):
        """Handle review button click"""
        if self.controller and self.classId:
            self.controller.loadClassAssignmentReview(assignmentId, self.classId)

    def updateAssignments(self, assignmentsData: list):
        """Update the assignments table with new data"""
        self.assignments = []
        self.setRowCount(len(assignmentsData))

        for row, assignmentData in enumerate(assignmentsData):
            name = assignmentData.get("name", "Unknown Assignment")
            description = assignmentData.get("description", "")
            status = assignmentData.get("status", "Unknown")
            due_date = assignmentData.get("due_date", "")
            assignment_id = assignmentData.get("id")

            self.assignments.append(
                (name, description, status, due_date, assignment_id)
            )

            # Name column
            nameItem = QTableWidgetItem(name)
            nameItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.setItem(row, 0, nameItem)

            # Description column
            descItem = QTableWidgetItem(description)
            descItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.setItem(row, 1, descItem)

            # Status column
            statusItem = QTableWidgetItem(status)
            statusItem.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )

            if status == "Assigned":
                statusItem.setForeground(QColor("#4CAF50"))
            elif status == "Closed":
                statusItem.setForeground(QColor("#9E9E9E"))

            self.setItem(row, 2, statusItem)

            # Due date column
            dueItem = QTableWidgetItem(due_date)
            dueItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.setItem(row, 3, dueItem)

            # Set row height
            self.setRowHeight(row, 50)


class ClassPerformanceTableWidget(CardWidget):
    """Class performance statistics table widget"""

    def __init__(
        self,
        className: str,
        controller=None,
        parent=None,
    ):
        super().__init__(parent)
        self.className = className
        self.controller = controller
        self.performanceData = {}
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedWidth(780)
        self.setMinimumHeight(400)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(15)

        self.setupHeader()
        self.setupDataRows()

    def setupHeader(self):
        """Setup the header section"""
        # Title
        self.titleLabel = SubtitleLabel(
            f"{self.className}'s Average Performance (30 Days)"
        )
        self.titleLabel.setStyleSheet(
            "color: #333333; font-weight: 600; font-size: 18px;"
        )
        self.mainLayout.addWidget(self.titleLabel)

        # Table header
        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(0)
        headerLayout.setContentsMargins(0, 10, 0, 10)

        emptyHeader = QLabel("")
        emptyHeader.setFixedWidth(250)
        headerLayout.addWidget(emptyHeader)

        formulateHeader = BodyLabel("Formulate")
        formulateHeader.setStyleSheet(
            "font-weight: 600; color: #333333; text-align: center;"
        )
        formulateHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formulateHeader.setFixedWidth(120)

        applyHeader = BodyLabel("Apply")
        applyHeader.setStyleSheet(
            "font-weight: 600; color: #333333; text-align: center;"
        )
        applyHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        applyHeader.setFixedWidth(120)

        explainHeader = BodyLabel("Explain")
        explainHeader.setStyleSheet(
            "font-weight: 600; color: #333333; text-align: center;"
        )
        explainHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        explainHeader.setFixedWidth(120)

        headerLayout.addWidget(formulateHeader)
        headerLayout.addWidget(applyHeader)
        headerLayout.addWidget(explainHeader)
        headerLayout.addStretch()

        self.mainLayout.addLayout(headerLayout)

    def setupDataRows(self):
        """Setup data rows from performance data"""
        for i in reversed(range(2, self.mainLayout.count())):
            item = self.mainLayout.takeAt(i)
            if item:
                if hasattr(item, "widget") and item.widget():
                    item.widget().deleteLater()
                elif hasattr(item, "layout") and item.layout():
                    self.clearLayout(item.layout())

        if not self.performanceData:
            placeholderLabel = BodyLabel("Loading performance data...")
            placeholderLabel.setStyleSheet(
                "color: #999999; font-style: italic; text-align: center;"
            )
            placeholderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.mainLayout.addWidget(placeholderLabel)
            self.mainLayout.addStretch()
            return

        for i, (concept, data) in enumerate(self.performanceData.items()):
            formulate = str(data.get("formulate", 0.0))
            apply = str(data.get("apply", 0.0))
            explain = str(data.get("explain", 0.0))

            rowLayout = QHBoxLayout()
            rowLayout.setSpacing(0)
            rowLayout.setContentsMargins(0, 5, 0, 5)

            # Concept
            conceptLabel = BodyLabel(concept.replace("_", " ").capitalize())
            conceptLabel.setStyleSheet("color: #333333; font-size: 14px;")
            conceptLabel.setFixedWidth(250)
            conceptLabel.setWordWrap(True)
            rowLayout.addWidget(conceptLabel)

            # Performance scores
            for score in [formulate, apply, explain]:
                scoreLabel = BodyLabel(str(score))
                scoreLabel.setStyleSheet(
                    "color: #333333; font-size: 14px; text-align: center;"
                )
                scoreLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                scoreLabel.setFixedWidth(120)
                rowLayout.addWidget(scoreLabel)

            rowLayout.addStretch()
            self.mainLayout.addLayout(rowLayout)

            if i < len(self.performanceData) - 1:
                separator = QLabel()
                separator.setFixedHeight(1)
                separator.setStyleSheet("background-color: #e0e0e0; margin: 2px 0px;")
                self.mainLayout.addWidget(separator)

        self.mainLayout.addStretch()

    def updatePerformanceData(self, performanceData: dict):
        """Update performance data"""
        self.performanceData = performanceData
        self.setupDataRows()

    def clearLayout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())

    def updateClassName(self, className: str):
        """Update the class name in the performance table title"""
        self.className = className
        if hasattr(self, "titleLabel"):
            self.titleLabel.setText(f"{self.className}'s Average Performance (30 Days)")

        if self.controller:
            self.controller.loadClassPerformance(className)


class ClassCardWidget(CardWidget):
    """Individual class card widget for the classes overview"""

    classClicked = pyqtSignal(int)  # classId
    classStudentsClicked = pyqtSignal(int)  # classId
    classAssignmentsClicked = pyqtSignal(int)  # classId
    classStatisticsClicked = pyqtSignal(int)  # classId

    def __init__(self, classId: int, className: str, studentCount: int, parent=None):
        super().__init__(parent)
        self.classId = classId
        self.className = className
        self.studentCount = studentCount
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedSize(280, 180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Class name
        title = SubtitleLabel(className)
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 18px;")
        layout.addWidget(title)

        # Student count
        studentLabel = CaptionLabel(f"{studentCount} students")
        studentLabel.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(studentLabel)

        layout.addStretch()

        buttonsLayout = QHBoxLayout()
        buttonsLayout.setAlignment(Qt.AlignmentFlag.AlignRight)
        buttonsLayout.setContentsMargins(0, 0, 0, 0)
        buttonsLayout.setSpacing(10)

        studentsBtn = TransparentToolButton(FluentIcon.PEOPLE)
        assignmentsBtn = TransparentToolButton(FluentIcon.DOCUMENT)
        statsBtn = TransparentToolButton(FluentIcon.PIE_SINGLE)

        studentsBtn.clicked.connect(
            lambda: self.classStudentsClicked.emit(self.classId)
        )
        assignmentsBtn.clicked.connect(
            lambda: self.classAssignmentsClicked.emit(self.classId)
        )
        statsBtn.clicked.connect(lambda: self.classStatisticsClicked.emit(self.classId))

        buttonsLayout.addWidget(studentsBtn)
        buttonsLayout.addWidget(assignmentsBtn)
        buttonsLayout.addWidget(statsBtn)
        buttonsLayout.addStretch()

        layout.addLayout(buttonsLayout)

    def mousePressEvent(self, event):
        """Handle click to navigate to individual class"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.classClicked.emit(self.classId)
        super().mousePressEvent(event)


class ClassesOverview(QWidget):
    """Classes overview page showing all class cards"""

    def __init__(self, controller: TeacherController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("classesOverview")
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
        mainLayout.setSpacing(25)

        # Header
        headerLayout = QHBoxLayout()

        title = TitleLabel("Classes")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 28px;")
        headerLayout.addWidget(title)

        headerLayout.addStretch()

        # Create button
        createBtn = PrimaryPushButton("Create")
        createBtn.setIcon(FluentIcon.ADD)
        createBtn.setFixedHeight(35)
        createBtn.clicked.connect(self.handleCreateClass)
        headerLayout.addWidget(createBtn)

        mainLayout.addLayout(headerLayout)

        # Classes
        self.classesFlow = FlowLayout()
        self.classesFlow.setContentsMargins(0, 20, 0, 20)
        self.classesFlow.setVerticalSpacing(20)
        self.classesFlow.setHorizontalSpacing(20)

        mainLayout.addLayout(self.classesFlow)
        mainLayout.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

    def handleCreateClass(self):
        """Handle create class button click"""
        self.createDialog = CreateClassDialog(self)
        self.createDialog.classCreated.connect(self.onClassCreated)
        self.createDialog.show()
        self.createDialog.raise_()
        self.createDialog.activateWindow()

    def onClassCreated(self, className: str, enterCode: str):
        """Handle when a new class is created"""
        self.controller.createClass(className, enterCode)

    def updateContent(self, classesData: list):
        """Update the classes display with new data"""
        while self.classesFlow.count():
            item = self.classesFlow.takeAt(0)
            if item:
                if hasattr(item, "widget"):
                    widget = item.widget()
                else:
                    widget = item
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

        for classData in classesData:
            classId = classData.get("id", "Unknown Class")
            className = classData.get("name", "Unknown Class")
            studentCount = classData.get("student_count", 0)

            classCard = ClassCardWidget(classId, className, studentCount, self)
            classCard.classClicked.connect(
                lambda classId: self.controller.showIndividualClass(classId, "students")
            )
            classCard.classStudentsClicked.connect(
                lambda classId: self.controller.showIndividualClass(classId, "students")
            )
            classCard.classAssignmentsClicked.connect(
                lambda classId: self.controller.showIndividualClass(
                    classId, "assignments"
                )
            )
            classCard.classStatisticsClicked.connect(
                lambda classId: self.controller.showIndividualClass(
                    classId, "statistics"
                )
            )
            self.classesFlow.addWidget(classCard)


class IndividualClassInterface(QWidget):
    """Individual class management interface"""

    def __init__(
        self,
        controller: TeacherController,
        classId: int,
        className: str,
        classCode: str,
        parent=None,
    ):
        super().__init__(parent)
        self.controller = controller
        self.classId = classId
        self.className = className
        self.classCode = classCode
        self.setObjectName("individualClassInterface")
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

        # Header
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(10)

        # Class title
        self.titleLabel = TitleLabel(self.className)
        self.titleLabel.setStyleSheet(
            "color: #333333; font-weight: 600; font-size: 28px;"
        )
        headerLayout.addWidget(self.titleLabel)

        # Class code
        self.codeLabel = BodyLabel(f"Enter code: {self.classCode}")
        self.codeLabel.setStyleSheet("color: #666666; font-size: 14px;")
        headerLayout.addWidget(self.codeLabel)

        mainLayout.addLayout(headerLayout)

        self.stackedWidget = QStackedWidget(self)

        self.studentsWidget = self.createStudentsTab()
        self.assignmentsWidget = self.createAssignmentsTab()
        self.statisticsWidget = self.createStatisticsTab()

        self.stackedWidget.addWidget(self.studentsWidget)
        self.stackedWidget.addWidget(self.assignmentsWidget)
        self.stackedWidget.addWidget(self.statisticsWidget)

        self.pivot = Pivot(self)
        self.pivot.addItem(routeKey="students", text="Students")
        self.pivot.addItem(routeKey="assignments", text="Assignments")
        self.pivot.addItem(routeKey="statistics", text="Statistics")

        self.pivot.currentItemChanged.connect(self.handleTabChanged)

        self.pivot.setCurrentItem("students")
        self.stackedWidget.setCurrentWidget(self.studentsWidget)

        mainLayout.addWidget(self.pivot)
        mainLayout.addWidget(self.stackedWidget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

    def createStudentsTab(self):
        """Create the students tab content"""
        studentsWidget = QWidget()
        studentsWidget.setObjectName("studentsTab")
        layout = QVBoxLayout(studentsWidget)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 20, 0, 0)

        # Student table
        self.studentTable = StudentTableWidget(self.controller)
        self.studentTable.setClassName(self.className)
        self.studentTable.studentStatisticsClicked.connect(
            lambda studentId, studentName: self.controller.showStudentStatistics(
                studentId, studentName
            )
        )
        self.studentTable.studentRemovalRequested.connect(
            self.handleRemoveStudentRequest
        )
        layout.addWidget(self.studentTable)

        return studentsWidget

    def createAssignmentsTab(self):
        """Create the assignments tab content"""
        assignmentsWidget = QWidget()
        assignmentsWidget.setObjectName("assignmentsTab")
        layout = QVBoxLayout(assignmentsWidget)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 20, 0, 0)

        # Assignments table
        self.assignmentsTable = AssignmentsTableWidget(self.controller)
        self.assignmentsTable.setClassId(self.classId)
        layout.addWidget(self.assignmentsTable)

        layout.addStretch()

        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 10, 0, 0)

        buttonLayout.addStretch()

        assignBtn = PrimaryPushButton("Assign")
        assignBtn.setIcon(FluentIcon.ADD)
        assignBtn.setFixedHeight(35)
        assignBtn.setFixedWidth(100)
        assignBtn.clicked.connect(self.handleAssignAssignment)
        buttonLayout.addWidget(assignBtn)

        layout.addLayout(buttonLayout)

        return assignmentsWidget

    def createStatisticsTab(self):
        """Create the statistics tab content"""
        statisticsWidget = QWidget()
        statisticsWidget.setObjectName("statisticsTab")
        layout = QVBoxLayout(statisticsWidget)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 20, 0, 0)

        # Performance table
        self.performanceTable = ClassPerformanceTableWidget(
            self.className, self.controller
        )
        layout.addWidget(self.performanceTable)
        layout.addStretch()

        return statisticsWidget

    def handleTabChanged(self, routeKey):
        """Handle tab changes from the Pivot"""
        if routeKey == "students":
            self.stackedWidget.setCurrentWidget(self.studentsWidget)
        elif routeKey == "assignments":
            self.stackedWidget.setCurrentWidget(self.assignmentsWidget)
        elif routeKey == "statistics":
            self.stackedWidget.setCurrentWidget(self.statisticsWidget)

    def updateClassInfo(self, className: str, classCode: str):
        """Update the class information"""
        self.className = className
        self.classCode = classCode
        self.titleLabel.setText(className)
        self.codeLabel.setText(f"Enter code: {classCode}")

    def updateContent(self, classData: dict):
        """Update the class interface with new data"""
        self.classId = classData.get("id")
        className = classData.get("name", "Unknown Class")
        classCode = classData.get("code", "Unknown")
        self.updateClassInfo(className, classCode)
        self.updateStudentsData(classData.get("students", []))
        self.updateAssignmentsData(classData.get("assignments", []))
        self.updatePerformanceData(classData.get("performance_data", {}))

    def updateStudentsData(self, studentsData: list):
        """Update students table with data from API"""
        if hasattr(self, "studentTable"):
            self.studentTable.updateStudents(studentsData)
            self.studentTable.setClassName(self.className)

    def updateAssignmentsData(self, assignmentsData: list):
        """Update assignments table with data from API"""
        if hasattr(self, "assignmentsTable"):
            self.assignmentsTable.updateAssignments(assignmentsData)
            self.assignmentsTable.setClassId(self.classId)

    def updatePerformanceData(self, performanceData: dict):
        """Update performance table with data from API"""
        if hasattr(self, "performanceTable"):
            self.performanceTable.updatePerformanceData(performanceData)

    def handleRemoveStudentRequest(self, studentId: int, studentName: str):
        """Handle student removal request - show confirmation dialog"""

        self.removeDialog = RemoveStudentDialog(studentId, studentName, self)
        self.removeDialog.studentRemoved.connect(self.onStudentRemovalConfirmed)
        self.removeDialog.show()
        self.removeDialog.raise_()
        self.removeDialog.activateWindow()

    def onStudentRemovalConfirmed(self, studentId: int):
        """Handle confirmed student removal"""
        if self.controller:
            self.controller.removeStudentFromClass(studentId)

    def handleAssignAssignment(self):
        """Handle assign assignment button click"""
        self.assignDialog = AssignAssignmentDialog(
            self.classId, self.className, self.controller, self
        )
        self.assignDialog.show()
        self.assignDialog.raise_()
        self.assignDialog.activateWindow()


class StudentNumeracyMatrixWidget(CardWidget):
    """Individual student numeracy matrix widget"""

    def __init__(
        self,
        studentName: str,
        period: str = "30 Days",
        matrixData: dict = None,
        parent=None,
    ):
        super().__init__(parent)
        self.studentName = studentName
        self.period = period
        self.matrixData = matrixData or {}
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedWidth(780)
        self.setMinimumHeight(300)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(15)

        self.setupHeader()
        self.createMatrixRows()

    def setupHeader(self):
        """Setup the header section with title and column headers"""
        # Title
        titleText = f"{self.studentName}'s Numeracy Matrix ({self.period})"
        self.titleLabel = SubtitleLabel(titleText)
        self.titleLabel.setStyleSheet(
            "color: #333333; font-weight: 600; font-size: 18px;"
        )
        self.mainLayout.addWidget(self.titleLabel)

        # Table header
        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(0)
        headerLayout.setContentsMargins(0, 10, 0, 10)

        emptyHeader = QLabel("")
        emptyHeader.setFixedWidth(250)
        headerLayout.addWidget(emptyHeader)

        # Column headers
        formulateHeader = BodyLabel("Formulate")
        formulateHeader.setStyleSheet(
            "font-weight: 600; color: #333333; text-align: center;"
        )
        formulateHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formulateHeader.setFixedWidth(120)

        applyHeader = BodyLabel("Apply")
        applyHeader.setStyleSheet(
            "font-weight: 600; color: #333333; text-align: center;"
        )
        applyHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        applyHeader.setFixedWidth(120)

        explainHeader = BodyLabel("Explain")
        explainHeader.setStyleSheet(
            "font-weight: 600; color: #333333; text-align: center;"
        )
        explainHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        explainHeader.setFixedWidth(120)

        headerLayout.addWidget(formulateHeader)
        headerLayout.addWidget(applyHeader)
        headerLayout.addWidget(explainHeader)
        headerLayout.addStretch()

        self.mainLayout.addLayout(headerLayout)

    def createMatrixRows(self):
        """Create matrix rows from data"""
        for i in reversed(range(2, self.mainLayout.count())):
            item = self.mainLayout.takeAt(i)
            if item:
                if hasattr(item, "widget") and item.widget():
                    item.widget().deleteLater()
                elif hasattr(item, "layout") and item.layout():
                    self.clearLayout(item.layout())

        if not self.matrixData:
            placeholderLabel = BodyLabel("No matrix data available")
            placeholderLabel.setStyleSheet(
                "color: #999999; font-style: italic; text-align: center;"
            )
            placeholderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.mainLayout.addWidget(placeholderLabel)
            self.mainLayout.addStretch()
            return

        for i, (concept, data) in enumerate(self.matrixData.items()):
            formulate = data.get("formulate", "0.0")
            apply = data.get("apply", "0.0")
            explain = data.get("explain", "0.0")

            rowLayout = QHBoxLayout()
            rowLayout.setSpacing(0)
            rowLayout.setContentsMargins(0, 5, 0, 5)

            # Concept
            conceptLabel = BodyLabel(concept.replace("_", " ").capitalize())
            conceptLabel.setStyleSheet("color: #333333; font-size: 14px;")
            conceptLabel.setFixedWidth(250)
            conceptLabel.setWordWrap(True)
            rowLayout.addWidget(conceptLabel)

            # Performance scores
            for score in [formulate, apply, explain]:
                scoreLabel = BodyLabel(str(score))
                scoreLabel.setStyleSheet(
                    "color: #333333; font-size: 14px; text-align: center;"
                )
                scoreLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                scoreLabel.setFixedWidth(120)
                rowLayout.addWidget(scoreLabel)

            rowLayout.addStretch()
            self.mainLayout.addLayout(rowLayout)

            if i < len(self.matrixData) - 1:
                separator = QLabel()
                separator.setFixedHeight(1)
                separator.setStyleSheet("background-color: #e0e0e0; margin: 2px 0px;")
                self.mainLayout.addWidget(separator)

        self.mainLayout.addStretch()

    def clearLayout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())

    def updateStudentName(self, studentName: str):
        """Update the student name in the matrix title"""
        self.studentName = studentName
        self.titleLabel.setText(f"{self.studentName}'s Numeracy Matrix ({self.period})")

    def updateMatrixData(self, matrixData: dict):
        """Update the matrix with new data"""
        print(
            f"[StudentNumeracyMatrixWidget] Updating {self.period} matrix with data: {len(matrixData)} concepts"
        )
        self.matrixData = matrixData
        self.createMatrixRows()


class StudentStatisticsInterface(QWidget):
    """Individual student statistics interface with detailed performance data"""

    def __init__(
        self,
        controller: TeacherController,
        studentId: int,
        studentName: str,
        classId: int,
        parent=None,
    ):
        super().__init__(parent)
        self.controller = controller
        self.studentId = studentId
        self.studentName = studentName
        self.classId = classId
        self.setObjectName("studentStatisticsInterface")
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

        # Header
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(10)

        # Student name
        self.titleLabel = TitleLabel(self.studentName)
        self.titleLabel.setStyleSheet(
            "color: #333333; font-weight: 600; font-size: 28px;"
        )
        headerLayout.addWidget(self.titleLabel)

        mainLayout.addLayout(headerLayout)

        contentLayout = QVBoxLayout()
        contentLayout.setSpacing(25)

        # 30 Days Matrix
        self.matrix_30Days = StudentNumeracyMatrixWidget(self.studentName, "30 Days")
        contentLayout.addWidget(self.matrix_30Days)

        # All Time Matrix
        self.matrixAllTime = StudentNumeracyMatrixWidget(self.studentName, "All")
        contentLayout.addWidget(self.matrixAllTime)

        # Performance Chart
        chartCard = CardWidget()
        chartCard.setStyleSheet("background-color: white; border-radius: 8px;")
        chartCard.setFixedWidth(780)
        chartCard.setFixedHeight(320)

        chartLayout = QVBoxLayout(chartCard)
        chartLayout.setContentsMargins(20, 20, 20, 20)
        chartLayout.setSpacing(15)

        # Chart title
        chartTitle = SubtitleLabel(f"{self.studentName}'s Recent Average Performance")
        chartTitle.setStyleSheet("color: #333333; font-weight: 600; font-size: 18px;")
        chartLayout.addWidget(chartTitle)

        # Performance chart
        self.performanceChart = PerformanceChartWidget(
            self.studentName, {"dates": [], "scores": []}
        )
        chartLayout.addWidget(self.performanceChart)

        contentLayout.addWidget(chartCard)

        mainLayout.addLayout(contentLayout)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

    def updateStudentInfo(self, studentName: str, classId: int):
        """Update the student and class information"""
        self.studentName = studentName
        self.classId = classId

        self.titleLabel.setText(studentName)

        self.matrix_30Days.updateStudentName(studentName)
        self.matrixAllTime.updateStudentName(studentName)

        chartCard = self.performanceChart.parent()
        if chartCard:
            chartLayout = chartCard.layout()
            if chartLayout and chartLayout.count() > 0:
                chartTitle = chartLayout.itemAt(0).widget()
                if hasattr(chartTitle, "setText"):
                    chartTitle.setText(f"{studentName}'s Recent Average Performance")

    def updateContent(self, studentData: dict):
        """Update the student statistics interface with new data"""
        print(
            f"[StudentStatisticsInterface] updateContent called with data keys: {list(studentData.keys())}"
        )
        studentName = studentData.get("student_name", "Unknown Student")
        classId = studentData.get("class_id", "Unknown Class")
        print(f"[StudentStatisticsInterface] Student: {studentName}, Class: {classId}")

        self.updateStudentInfo(studentName, classId)

        performanceData = studentData.get("performance_chart_data")

        if hasattr(self, "performanceChart"):
            print(
                f"[StudentStatisticsInterface] Updating chart with data: {performanceData}"
            )
            self.performanceChart.updateChart(studentName, performanceData)

            chartCard = self.performanceChart.parent()
            if chartCard:
                chartLayout = chartCard.layout()
                if chartLayout and chartLayout.count() > 0:
                    chartTitle = chartLayout.itemAt(0).widget()
                    if hasattr(chartTitle, "setText"):
                        chartTitle.setText(
                            f"{studentName}'s Recent Average Performance"
                        )

        matrix30DaysData = studentData.get("matrix_30_days", [])
        matrixAllTimeData = studentData.get("matrix_all_time", [])

        if hasattr(self, "matrix_30Days"):
            self.matrix_30Days.updateMatrixData(matrix30DaysData)

        if hasattr(self, "matrixAllTime"):
            self.matrixAllTime.updateMatrixData(matrixAllTimeData)


class AssignAssignmentDialog(CardWidget):
    """Assign assignment to class dialog"""

    def __init__(
        self,
        classId: int,
        className: str,
        controller: TeacherController = None,
        parent=None,
    ):
        super().__init__(parent)
        self.classId = classId
        self.className = className
        self.controller = controller
        self.availableAssignments = []
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedSize(500, 320)
        self.setupUi()

        if parent:
            parentRect = parent.geometry()
            x = parentRect.x() + (parentRect.width() - self.width()) // 2
            y = parentRect.y() + (parentRect.height() - self.height()) // 2
            self.move(x, y)

        if self.controller:
            self.controller.loadAvailableAssignments()
            self.controller.availableAssignmentsDataReady.connect(
                self.onAvailableAssignmentsLoaded
            )

    def setupUi(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(20)

        # Title
        title = SubtitleLabel(f"Assign Assignment to {self.className}")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 20px;")
        mainLayout.addWidget(title)

        # Assignment
        assignmentLayout = QVBoxLayout()
        assignmentLayout.setSpacing(8)

        assignmentLabel = BodyLabel("Assignment")
        assignmentLabel.setStyleSheet(
            "color: #333333; font-weight: 500; font-size: 14px;"
        )
        assignmentLayout.addWidget(assignmentLabel)

        self.assignmentCombo = ComboBox()
        self.assignmentCombo.setPlaceholderText("Select an assignment...")
        assignmentLayout.addWidget(self.assignmentCombo)

        mainLayout.addLayout(assignmentLayout)

        # Due Date
        dueDateLayout = QVBoxLayout()
        dueDateLayout.setSpacing(8)

        dueDateLabel = BodyLabel("Due Date")
        dueDateLabel.setStyleSheet("color: #333333; font-weight: 500; font-size: 14px;")
        dueDateLayout.addWidget(dueDateLabel)

        # Date & Time
        dateTimeLayout = QHBoxLayout()
        dateTimeLayout.setSpacing(15)

        # Calendar picker
        self.calendarPicker = CalendarPicker()
        dateTimeLayout.addWidget(self.calendarPicker)

        # Time picker
        self.timePicker = TimePicker()
        self.timePicker.setTime(QTime(19, 0))
        dateTimeLayout.addWidget(self.timePicker)

        dueDateLayout.addLayout(dateTimeLayout)
        mainLayout.addLayout(dueDateLayout)

        mainLayout.addStretch()

        # Buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 10, 0, 0)

        cancelBtn = PushButton("Cancel")
        cancelBtn.clicked.connect(self.handleCancel)
        buttonLayout.addWidget(cancelBtn)

        buttonLayout.addStretch()

        self.assignBtn = PrimaryPushButton("Assign")
        self.assignBtn.clicked.connect(self.handleAssign)
        self.assignBtn.setEnabled(False)
        buttonLayout.addWidget(self.assignBtn)

        mainLayout.addLayout(buttonLayout)

        self.assignmentCombo.currentTextChanged.connect(
            self.onAssignmentSelectionChanged
        )

    def onAvailableAssignmentsLoaded(self, assignments: list):
        """Handle when available assignments are loaded"""
        self.availableAssignments = assignments
        self.assignmentCombo.clear()

        for assignment in assignments:
            assignmentName = assignment.get("name", "Unknown Assignment")
            self.assignmentCombo.addItem(assignmentName, userData=assignment["id"])

    def onAssignmentSelectionChanged(self, text: str):
        """Handle assignment selection change"""
        self.assignBtn.setEnabled(bool(text and text != "Select an assignment..."))

    def handleCancel(self):
        """Handle cancel button click"""
        self.close()

    def handleAssign(self):
        """Handle assign button click"""
        if self.assignmentCombo.currentIndex() < 0:
            self.showError("Please select an assignment.")
            return

        assignmentId = self.assignmentCombo.currentData()
        if not assignmentId:
            self.showError("Invalid assignment selection.")
            return

        selectedDate = self.calendarPicker.getDate()
        selectedTime = self.timePicker.getTime()

        dueDate = (
            f"{selectedDate.toString('yyyy-MM-dd')} {selectedTime.toString('HH:mm')}"
        )
        try:
            dueDate = datetime.strptime(dueDate, "%Y-%m-%d %H:%M")
        except ValueError:
            self.showError("Invalid date or time format.")
            return

        if self.controller:
            self.controller.assignAssignmentToClass(assignmentId, self.classId, dueDate)

        self.close()

    def showError(self, message: str):
        """Show error message to user"""
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title="Error",
            content=message,
            target=self,
            parent=self,
            aniType=FlyoutAnimationType.PULL_UP,
        )


class TeacherHomeInterface(QWidget):
    """Teacher home dashboard interface"""

    def __init__(self, controller: TeacherController = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("teacherHome")
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
        mainLayout.setSpacing(25)

        # Page title
        title = TitleLabel("Home")
        title.setStyleSheet(
            "background-color: transparent; color: #333333; font-weight: 600;"
        )
        mainLayout.addWidget(title)

        # Classes
        classesLayout = QVBoxLayout()
        classesLayout.setSpacing(15)

        classesTitle = SubtitleLabel("Classes")
        classesLayout.addWidget(classesTitle)

        self.classesGrid = QHBoxLayout()
        self.classesGrid.setSpacing(20)
        self.classesGrid.addStretch()
        classesLayout.addLayout(self.classesGrid)
        mainLayout.addLayout(classesLayout)

        # Assignments
        assignmentsLayout = QVBoxLayout()
        assignmentsLayout.setSpacing(15)

        assignmentsTitle = SubtitleLabel("Assignments")
        assignmentsLayout.addWidget(assignmentsTitle)

        self.assignmentsGrid = QHBoxLayout()
        self.assignmentsGrid.setSpacing(20)
        self.assignmentsGrid.addStretch()
        assignmentsLayout.addLayout(self.assignmentsGrid)
        mainLayout.addLayout(assignmentsLayout)

        # Students
        studentsLayout = QVBoxLayout()
        studentsLayout.setSpacing(15)

        studentsTitle = SubtitleLabel("Students")
        studentsLayout.addWidget(studentsTitle)

        self.studentsGrid = QHBoxLayout()
        self.studentsGrid.setSpacing(20)
        self.studentsGrid.addStretch()
        studentsLayout.addLayout(self.studentsGrid)

        mainLayout.addLayout(studentsLayout)
        mainLayout.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

    def updateContent(self, dashboardData: dict):
        """Update the home interface with new data"""
        while self.classesGrid.count() > 1:
            item = self.classesGrid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        while self.assignmentsGrid.count() > 1:
            item = self.assignmentsGrid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        while self.studentsGrid.count() > 1:
            item = self.studentsGrid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        classes = dashboardData.get("classes", [])
        for classData in classes:
            classId = classData.get("id")
            className = classData.get("name", "Unknown Class")
            assignments = classData.get("assignments", [])
            classCard = TeacherClassCard(classId, className, assignments)
            classCard.classClicked.connect(
                lambda classId: self.controller.showIndividualClass(classId, "students")
            )
            self.classesGrid.insertWidget(self.classesGrid.count() - 1, classCard)

        assignments = dashboardData.get("recent_assignments", [])
        for assignmentData in assignments:
            assignmentId = assignmentData.get("id", None)
            assignmentName = assignmentData.get("name", "Unknown Assignment")
            description = assignmentData.get("description", "")
            image = assignmentData.get("image", None)
            assignmentCard = TeacherAssignmentCard(
                assignmentId, assignmentName, description, image=image
            )
            assignmentCard.assignmentClicked.connect(
                lambda assignmentId: self.controller.showAssignmentReview(assignmentId)
            )
            self.assignmentsGrid.insertWidget(
                self.assignmentsGrid.count() - 1, assignmentCard
            )

        students = dashboardData.get("students", [])
        for studentData in students:
            studentName = studentData.get("name", "Unknown Student")
            performanceData = studentData.get(
                "performance_data", {"dates": [], "scores": []}
            )
            studentCard = StudentPerformanceCard(studentName, performanceData)
            self.studentsGrid.insertWidget(self.studentsGrid.count() - 1, studentCard)


class RemoveStudentDialog(CardWidget):
    """Student removal confirmation dialog"""

    studentRemoved = pyqtSignal(int)

    def __init__(
        self,
        studentId: int,
        studentName: str,
        parent=None,
    ):
        super().__init__(parent)
        self.studentId = studentId
        self.studentName = studentName
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedSize(400, 250)
        self.setupUi()

        if parent:
            parentRect = parent.geometry()
            x = parentRect.x() + (parentRect.width() - self.width()) // 2
            y = parentRect.y() + (parentRect.height() - self.height()) // 2
            self.move(x, y)

    def setupUi(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(20)

        # Title
        title = SubtitleLabel("Remove Student")
        title.setStyleSheet("color: #d32f2f; font-weight: 600; font-size: 20px;")
        mainLayout.addWidget(title)

        # Warning message
        warningText = (
            f"Are you sure you want to remove {self.studentName} from the class?"
        )
        warningLabel = BodyLabel(warningText)
        warningLabel.setWordWrap(True)
        warningLabel.setStyleSheet("color: #333333; font-size: 14px; line-height: 1.4;")
        mainLayout.addWidget(warningLabel)

        # Info message
        infoLabel = CaptionLabel(
            "This action cannot be undone. The student will lose access to class assignments and materials."
        )
        infoLabel.setWordWrap(True)
        infoLabel.setStyleSheet("color: #666666; font-size: 12px; font-style: italic;")
        mainLayout.addWidget(infoLabel)

        mainLayout.addStretch()

        # Buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 10, 0, 0)

        cancelBtn = PushButton("Cancel")
        cancelBtn.clicked.connect(self.handleCancel)
        buttonLayout.addWidget(cancelBtn)

        buttonLayout.addStretch()

        removeBtn = PrimaryPushButton("Remove")
        removeBtn.clicked.connect(self.handleRemove)
        buttonLayout.addWidget(removeBtn)

        mainLayout.addLayout(buttonLayout)

    def handleCancel(self):
        """Handle cancel button click"""
        self.close()

    def handleRemove(self):
        """Handle remove button click"""
        self.studentRemoved.emit(self.studentId)
        self.close()


class CreateClassDialog(CardWidget):
    """Class creation dialog interface"""

    classCreated = pyqtSignal(str, str)  # className, enterCode

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedSize(400, 300)
        self.setupUi()

        if parent:
            parentRect = parent.geometry()
            x = parentRect.x() + (parentRect.width() - self.width()) // 2
            y = parentRect.y() + (parentRect.height() - self.height()) // 2
            self.move(x, y)

    def setupUi(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(20)

        # Title
        title = SubtitleLabel("Create Class")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 20px;")
        mainLayout.addWidget(title)

        # Class Name
        nameLayout = QVBoxLayout()
        nameLayout.setSpacing(8)

        nameLabel = BodyLabel("Class Name")
        nameLabel.setStyleSheet("color: #333333; font-weight: 500; font-size: 14px;")
        nameLayout.addWidget(nameLabel)

        self.nameInput = LineEdit()
        self.nameInput.setPlaceholderText("Enter class name")
        nameLayout.addWidget(self.nameInput)

        # Enter Code
        enterCodeVLayout = QVBoxLayout()
        enterCodeVLayout.setSpacing(8)
        enterCodeLayout = QHBoxLayout()
        enterCodeLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        enterCodeLayout.setSpacing(8)

        enterCodeLabel = BodyLabel("Enter Code")
        enterCodeLabel.setStyleSheet(
            "color: #333333; font-weight: 500; font-size: 14px;"
        )
        enterCodeLayout.addWidget(enterCodeLabel)

        self.enterCodeInfoButton = TransparentToolButton(FluentIcon.INFO)
        self.enterCodeInfoButton.setFixedSize(20, 20)
        self.enterCodeInfoButton.clicked.connect(self.showEnterCodeInfo)
        self.enterCodeInfoButton.setToolTip("Click to see class code info")
        enterCodeLayout.addWidget(self.enterCodeInfoButton)

        self.enterCodeInput = LineEdit()
        self.enterCodeInput.setPlaceholderText("Enter class code")

        enterCodeVLayout.addLayout(enterCodeLayout)
        enterCodeVLayout.addWidget(self.enterCodeInput)

        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(enterCodeVLayout)

        mainLayout.addStretch()

        # Buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 10, 0, 0)

        cancelBtn = PushButton("Cancel")
        cancelBtn.clicked.connect(self.handleCancel)
        buttonLayout.addWidget(cancelBtn)

        buttonLayout.addStretch()

        createBtn = PrimaryPushButton("Create")
        createBtn.clicked.connect(self.handleCreate)
        buttonLayout.addWidget(createBtn)

        mainLayout.addLayout(buttonLayout)

    def handleCancel(self):
        """Handle cancel button click"""
        self.close()

    def handleCreate(self):
        """Handle create button click"""
        className = self.nameInput.text().strip()
        enterCode = self.enterCodeInput.text().strip()

        if not className:
            self.showError("Please enter a class name.")
            return

        if not enterCode:
            self.showError("Please enter a class code.")
            return

        self.classCreated.emit(className, enterCode)

        self.close()

    def showEnterCodeInfo(self):
        """Show enter code info in a teaching tip for better UX"""
        infoContent = """• The enter code is a code that is used for students to join the class.
• Make sure it is secure and not easy to guess."""

        TeachingTip.create(
            target=self.enterCodeInfoButton,
            icon=FluentIcon.INFO,
            title="Enter Code Info",
            content=infoContent,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=3000,
            parent=self,
        )

    def showError(self, message: str):
        """Show error message to user"""
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title="Error",
            content=message,
            target=self,
            parent=self,
            aniType=FlyoutAnimationType.PULL_UP,
        )


class CreateAssignmentDialog(CardWidget):
    """Assignment creation dialog/sheet interface"""

    assignmentCreated = pyqtSignal(str, str, list)  # name, description, questionIds

    def __init__(self, controller: TeacherController = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedSize(600, 450)
        self.selectedQuestionIds = []
        self.setupUi()
        self.questionsWindow = None

        if parent:
            parentRect = parent.geometry()
            x = parentRect.x() + (parentRect.width() - self.width()) // 2
            y = parentRect.y() + (parentRect.height() - self.height()) // 2
            self.move(x, y)

    def setupUi(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(20)

        # Title
        title = SubtitleLabel("Create Assignment")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 20px;")
        mainLayout.addWidget(title)

        # Assignment Name
        nameLayout = QVBoxLayout()
        nameLayout.setSpacing(8)

        nameLabel = BodyLabel("Assignment Name")
        nameLabel.setStyleSheet("color: #333333; font-weight: 500; font-size: 14px;")
        nameLayout.addWidget(nameLabel)

        self.nameInput = LineEdit()
        self.nameInput.setPlaceholderText("Assignment Name")
        nameLayout.addWidget(self.nameInput)

        mainLayout.addLayout(nameLayout)

        # Description
        descLayout = QVBoxLayout()
        descLayout.setSpacing(8)

        descLabel = BodyLabel("Description")
        descLabel.setStyleSheet("color: #333333; font-weight: 500; font-size: 14px;")
        descLayout.addWidget(descLabel)

        self.descriptionInput = PlainTextEdit()
        self.descriptionInput.setPlaceholderText("Assignment Description")
        descLayout.addWidget(self.descriptionInput)

        mainLayout.addLayout(descLayout)

        # Questions
        questionsLayout = QVBoxLayout()
        questionsLayout.setSpacing(8)

        questionsLabel = BodyLabel("Questions")
        questionsLabel.setStyleSheet(
            "color: #333333; font-weight: 500; font-size: 14px;"
        )
        questionsLayout.addWidget(questionsLabel)

        self.addQuestionsBtn = PushButton("Add")
        self.addQuestionsBtn.clicked.connect(self.handleAddQuestions)
        questionsLayout.addWidget(self.addQuestionsBtn)

        mainLayout.addLayout(questionsLayout)

        mainLayout.addStretch()

        # Buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 10, 0, 0)

        cancelBtn = PushButton("Cancel")
        cancelBtn.clicked.connect(self.handleCancel)
        buttonLayout.addWidget(cancelBtn)

        buttonLayout.addStretch()

        submitBtn = PrimaryPushButton("Submit")
        submitBtn.clicked.connect(self.handleSubmit)
        buttonLayout.addWidget(submitBtn)

        mainLayout.addLayout(buttonLayout)

    def handleAddQuestions(self):
        """Handle add questions button click"""
        if self.questionsWindow is not None:
            self.questionsWindow.close()
            self.questionsWindow.deleteLater()
            self.questionsWindow = None

        if self.controller:
            self.controller.filteredQuestionsDataReady.connect(
                self.onQuestionsLoadedForSelection
            )
            self.controller.loadFilteredQuestions("", "All Concepts", "All Processes")
        else:
            self.createSelectQuestionsWindow([])

    def onQuestionsLoadedForSelection(self, questionsData: list):
        """Handle questions loaded for selection window"""
        if self.controller:
            self.controller.filteredQuestionsDataReady.disconnect(
                self.onQuestionsLoadedForSelection
            )

        self.createSelectQuestionsWindow(questionsData)

    def createSelectQuestionsWindow(self, questionsData: list):
        """Create the select questions window with questions data"""
        self.questionsWindow = SelectQuestionsWindow(
            self.controller, self.selectedQuestionIds, questionsData, self
        )

        self.questionsWindow.questionsSelected.connect(self.onQuestionsSelected)

        self.questionsWindow.show()
        self.questionsWindow.raise_()
        self.questionsWindow.activateWindow()

    def onQuestionsSelected(self, selectedQuestionIds):
        """Handle when questions are selected from the SelectQuestionsWindow"""
        self.selectedQuestionIds = selectedQuestionIds
        print(f"[CreateAssignmentDialog]: Selected {selectedQuestionIds}")

        if len(selectedQuestionIds) == 1:
            self.addQuestionsBtn.setText(f"Add ({len(selectedQuestionIds)} Question)")
        elif len(selectedQuestionIds) > 1:
            self.addQuestionsBtn.setText(f"Add ({len(selectedQuestionIds)} Questions)")
        else:
            self.addQuestionsBtn.setText("Add")
            self.addQuestionsBtn.setIcon(FluentIcon.ADD)

    def handleCancel(self):
        """Handle cancel button click"""
        self.close()

    def handleSubmit(self):
        """Handle submit button click"""
        assignmentName = self.nameInput.text().strip()
        description = self.descriptionInput.toPlainText().strip()

        if not assignmentName:
            self.showError("Please enter an assignment name.")
            return

        if not description:
            self.showError("Please enter a description.")
            return

        if not self.selectedQuestionIds:
            self.showError("Please select at least one question.")
            return

        self.assignmentCreated.emit(
            assignmentName, description, self.selectedQuestionIds
        )

        self.close()

    def showError(self, message: str):
        """Show error message to user"""
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title="Error",
            content=message,
            target=self,
            parent=self,
            aniType=FlyoutAnimationType.PULL_UP,
        )


class QuestionsTableWidget(TableWidget):
    """Custom table widget for displaying questions"""

    def __init__(self, controller: TeacherController = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setupTable()

    def setupTable(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Name", "Source", "Status", "Sub-Questions"])

        self.setRowCount(0)

        self.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 120)  # Source
        self.setColumnWidth(2, 120)  # Status
        self.setColumnWidth(3, 100)  # Sub-questions

    def updateQuestions(self, questionsData: list):
        """Update the questions table with new data"""
        self.setRowCount(len(questionsData))

        for row, questionData in enumerate(questionsData):
            name = questionData.get("name", "Unknown")
            source = questionData.get("source", "Unknown")
            is_audited = questionData.get("is_audited", False)
            subQuestions = str(questionData.get("sub_questions_count", "0"))

            # Name
            nameItem = QTableWidgetItem(name)
            nameItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.setItem(row, 0, nameItem)

            # Source
            sourceItem = QTableWidgetItem(source)
            sourceItem.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            self.setItem(row, 1, sourceItem)

            # Status
            statusItem = QTableWidgetItem("Approved" if is_audited else "Auditing")
            statusItem.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )

            if is_audited:
                statusItem.setForeground(QColor("#4CAF50"))
            else:
                statusItem.setForeground(QColor("#FF9800"))

            self.setItem(row, 2, statusItem)

            # Sub-questions
            subQuestionsItem = QTableWidgetItem(subQuestions)
            subQuestionsItem.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            self.setItem(row, 3, subQuestionsItem)

            self.setRowHeight(row, 50)


class UploadQuestionDialog(CardWidget):
    """Upload question dialog matching the design image"""

    def __init__(self, controller: TeacherController = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        self.setFixedSize(500, 350)
        self.setupUi()

        if parent:
            parentRect = parent.geometry()
            x = parentRect.x() + (parentRect.width() - self.width()) // 2
            y = parentRect.y() + (parentRect.height() - self.height()) // 2
            self.move(x, y)

    def setupUi(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(25)

        # Title & description
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(8)

        title = SubtitleLabel("Create Your Question")
        headerLayout.addWidget(title)

        subtitle = BodyLabel("Upload your question to share with the community")
        subtitle.setTextColor(QColor("#666666"))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)
        headerLayout.addWidget(subtitle)

        mainLayout.addLayout(headerLayout)

        formLayout = QVBoxLayout()
        formLayout.setSpacing(20)

        # Name
        nameLayout = QVBoxLayout()
        nameLayout.setSpacing(8)

        nameLabel = BodyLabel("Name")
        nameLabel.setStyleSheet("color: #333333; font-weight: 500; font-size: 14px;")
        nameLayout.addWidget(nameLabel)

        self.nameInput = LineEdit()
        self.nameInput.setPlaceholderText("Question Name")
        nameLayout.addWidget(self.nameInput)

        formLayout.addLayout(nameLayout)

        # Source
        sourceLayout = QVBoxLayout()
        sourceLayout.setSpacing(8)

        sourceLabel = BodyLabel("Source")
        sourceLabel.setStyleSheet("color: #333333; font-weight: 500; font-size: 14px;")
        sourceLayout.addWidget(sourceLabel)

        self.sourceCombo = ComboBox()
        self.sourceCombo.addItems(
            [
                "NCEA",
                "Original",
                "Textbook",
                "Worksheet",
                "Online",
                "AI Generated",
                "Other",
            ]
        )
        self.sourceCombo.setCurrentText("NCEA")
        sourceLayout.addWidget(self.sourceCombo)

        formLayout.addLayout(sourceLayout)

        mainLayout.addLayout(formLayout)

        mainLayout.addStretch()

        buttonFooter = QHBoxLayout()
        buttonFooter.setContentsMargins(0, 10, 0, 0)

        cancelBtn = PushButton("Cancel")
        cancelBtn.clicked.connect(self.close)
        buttonFooter.addWidget(cancelBtn)

        createBtn = PrimaryPushButton("Create")
        createBtn.clicked.connect(self.handleCreate)
        buttonFooter.addWidget(createBtn)

        mainLayout.addLayout(buttonFooter)

    def handleCreate(self):
        """Handle create button click"""
        questionName = self.nameInput.text().strip()
        source = self.sourceCombo.currentText()

        if not questionName:
            self.showError("Please enter a question name.")
            return

        self.close()

        self.questionEditor = QuestionEditorWindow(questionName, source, self.parent())
        self.questionEditor.questionSaved.connect(self.controller.createQuestion)

        self.questionEditor.show()
        self.questionEditor.raise_()
        self.questionEditor.activateWindow()

    def showError(self, message: str):
        """Show error message to user"""
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title="Error",
            content=message,
            target=self,
            parent=self,
            aniType=FlyoutAnimationType.PULL_UP,
        )


class TeacherQuestionsInterface(QWidget):
    """Teacher questions interface with question table and upload functionality"""

    def __init__(self, controller: TeacherController = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("teacherQuestionsInterface")
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
        mainLayout.setSpacing(25)

        # Header
        headerLayout = QHBoxLayout()
        headerLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Title
        title = TitleLabel("Questions")
        title.setStyleSheet("color: #333333; font-weight: 600; font-size: 28px;")
        headerLayout.addWidget(title)

        headerLayout.addStretch()

        # Upload button
        uploadBtn = PrimaryPushButton("Upload")
        uploadBtn.setIcon(FluentIcon.CLOUD)
        uploadBtn.clicked.connect(self.handleUploadQuestion)
        headerLayout.addWidget(uploadBtn)

        mainLayout.addLayout(headerLayout)

        # Questions table
        self.questionsTable = QuestionsTableWidget(self.controller)
        mainLayout.addWidget(self.questionsTable)

        mainLayout.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

    def handleUploadQuestion(self):
        """Handle upload question button click"""
        self.uploadDialog = UploadQuestionDialog(self.controller, self)

        self.uploadDialog.show()
        self.uploadDialog.raise_()
        self.uploadDialog.activateWindow()

    def onQuestionSaved(self, name: str, source: str, subQuestionsData: list):
        """Handle when a new question is saved from the editor"""
        subQuestionCount = len(subQuestionsData)
        self.addQuestionToTable(name, source, str(subQuestionCount))

    def addQuestionToTable(self, name: str, source: str, subQuestionCount: str):
        """Add a new question to the questions table"""
        table = self.questionsTable
        rowCount = table.rowCount()
        table.setRowCount(rowCount + 1)

        nameItem = QTableWidgetItem(name)
        nameItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        table.setItem(rowCount, 0, nameItem)

        statusItem = QTableWidgetItem("Auditing")
        statusItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        statusItem.setForeground(QColor("#FF9800"))
        table.setItem(rowCount, 1, statusItem)

        sourceItem = QTableWidgetItem(source)
        sourceItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        table.setItem(rowCount, 2, sourceItem)

        subQuestionsItem = QTableWidgetItem(subQuestionCount)
        subQuestionsItem.setFlags(
            Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        )
        table.setItem(rowCount, 3, subQuestionsItem)

        table.setRowHeight(rowCount, 50)

    def updateContent(self, questionsData: list):
        """Update the questions display with new data"""
        self.questionsTable.updateQuestions(questionsData)


class SubQuestionWidget(SimpleCardWidget):
    """Widget for editing a single sub-question with all its fields"""

    def __init__(self, subQuestionNumber: int, parent=None):
        super().__init__(parent)
        self.subQuestionNumber = subQuestionNumber
        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Title
        title = StrongBodyLabel(f"Sub-Question {chr(64 + self.subQuestionNumber)}")
        title.setStyleSheet("background-color: transparent; color: #000000;")
        layout.addWidget(title)

        mainContent = QHBoxLayout()
        mainContent.setSpacing(30)

        # Text fields
        leftColumn = QVBoxLayout()
        leftColumn.setAlignment(Qt.AlignmentFlag.AlignTop)
        leftColumn.setSpacing(20)

        # Description
        descSection = self.createFieldSection(
            "Description", PlainTextEdit(), "Enter the question description..."
        )
        self.descriptionInput = descSection[1]
        leftColumn.addLayout(descSection[0])

        # Answer
        answerSection = self.createFieldSection(
            "Answer / Marking Criteria",
            PlainTextEdit(),
            "Enter the answer or marking criteria...",
        )
        self.answerInput = answerSection[1]
        leftColumn.addLayout(answerSection[0])

        # Options
        optionsSection = self.createFieldSection(
            "Options", PlainTextEdit(), "Enter options (one per line)..."
        )
        self.optionsInput = optionsSection[1]
        leftColumn.addLayout(optionsSection[0])

        mainContent.addLayout(leftColumn, 2)

        # Image+
        rightColumn = QVBoxLayout()
        rightColumn.setAlignment(Qt.AlignmentFlag.AlignTop)
        rightColumn.setSpacing(20)

        # Image
        imageSection = QVBoxLayout()
        imageSection.setSpacing(10)

        imageLabel = BodyLabel("Image (Optional)")
        imageLabel.setStyleSheet("background-color: transparent; color: #000000;")
        imageSection.addWidget(imageLabel)

        self.imageLabel = ImageLabel()
        self.imageLabel.scaledToWidth(300)
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageLabel.setText("No image selected")
        self.imagePath = None
        imageSection.addWidget(self.imageLabel)

        # Image upload button
        self.uploadBtn = PushButton("Upload Image")
        self.uploadBtn.setIcon(FluentIcon.PHOTO)
        self.uploadBtn.clicked.connect(self.uploadImage)
        imageSection.addWidget(self.uploadBtn)

        # Remove image button
        self.removeImageBtn = PushButton("Remove Image")
        self.removeImageBtn.setIcon(FluentIcon.DELETE)
        self.removeImageBtn.clicked.connect(self.removeImage)
        self.removeImageBtn.setVisible(False)
        imageSection.addWidget(self.removeImageBtn)

        # Image description
        imageDescriptionSection = self.createFieldSection(
            "Image Description", LineEdit(), "Enter image description..."
        )
        self.imageDescriptionInput = imageDescriptionSection[1]
        imageSection.addLayout(imageDescriptionSection[0])

        rightColumn.addLayout(imageSection)

        # Keywords
        keywordsSection = self.createFieldSection(
            "Keywords", LineEdit(), "Enter keywords (comma-separated)..."
        )
        self.keywordsInput = keywordsSection[1]
        rightColumn.addLayout(keywordsSection[0])

        # Concept
        conceptSection = QVBoxLayout()
        conceptSection.setSpacing(8)
        conceptLabel = BodyLabel("Concept")
        conceptLabel.setStyleSheet("background-color: transparent; color: #000000;")
        conceptSection.addWidget(conceptLabel)

        self.conceptCombo = ComboBox()
        self.conceptCombo.addItems(
            [enumNameToText(concept.name) for concept in ConceptType]
        )
        conceptSection.addWidget(self.conceptCombo)
        rightColumn.addLayout(conceptSection)

        # Process
        processSection = QVBoxLayout()
        processSection.setSpacing(8)
        processLabel = BodyLabel("Process")
        processLabel.setStyleSheet("background-color: transparent; color: #000000;")
        processSection.addWidget(processLabel)

        self.processCombo = ComboBox()
        self.processCombo.addItems(
            [enumNameToText(process.name) for process in ProcessType]
        )
        processSection.addWidget(self.processCombo)
        rightColumn.addLayout(processSection)

        rightColumn.addStretch()
        mainContent.addLayout(rightColumn, 1)

        layout.addLayout(mainContent)

    def createFieldSection(self, labelText, widget, placeholder):
        """Create a labeled input field section"""
        sectionLayout = QVBoxLayout()
        sectionLayout.setSpacing(8)

        label = BodyLabel(labelText)
        label.setStyleSheet("background-color: transparent; color: #000000;")
        sectionLayout.addWidget(label)

        widget.setPlaceholderText(placeholder)
        if isinstance(widget, PlainTextEdit):
            widget.setFixedHeight(80)
        sectionLayout.addWidget(widget)

        return sectionLayout, widget

    def uploadImage(self):
        """Handle image upload"""
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg);;All Files (*)",
        )

        if filePath:
            self.imagePath = filePath
            self.onImageSelected(filePath)

    def onImageSelected(self, filePath):
        """Handle selected image file"""
        try:
            pixmap = QPixmap(filePath)
            if not pixmap.isNull():
                self.imageLabel.setPixmap(pixmap)
                self.imageLabel.scaledToWidth(300)
                self.imageLabel.setText("")
                self.removeImageBtn.setVisible(True)
                self.uploadBtn.setText("Change Image")
        except Exception as e:
            print(f"Error loading image: {e}")

    def removeImage(self):
        """Remove the selected image"""
        self.imageLabel.clear()
        self.imageLabel.setPixmap(QPixmap())
        self.imageLabel.scaledToWidth(300)
        self.imageLabel.setText("No image selected")
        self.removeImageBtn.setVisible(False)
        self.uploadBtn.setText("Upload Image")
        self.imagePath = None

    def getData(self):
        """Get all data from this sub-question"""
        return {
            "description": self.descriptionInput.toPlainText().strip(),
            "answer": self.answerInput.toPlainText().strip(),
            "concept": self.conceptCombo.currentText(),
            "process": self.processCombo.currentText(),
            "keywords": self.keywordsInput.text().strip().split(","),
            "options": self.optionsInput.toPlainText().strip().split("\n"),
            "image_path": self.imagePath,
            "image_description": self.imageDescriptionInput.text().strip(),
        }


class QuestionEditorWindow(FramelessWindow):
    """Question editor with TabBar interface for sub-questions"""

    questionSaved = pyqtSignal(str, str, list)  # name, source, subQuestionsData

    def __init__(self, questionName: str, source: str, parent=None):
        super().__init__()
        self.questionName = questionName
        self.source = source
        self.subQuestionCount = 1
        self.subQuestionWidgets = []
        self.routeKeyCounter = 1

        self.setWindowTitle("Edit Question")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #f5f5f5;")

        self.setupUi()

        if parent:
            parentGeometry = parent.geometry()
            x = parentGeometry.x() + (parentGeometry.width() - self.width()) // 2
            y = parentGeometry.y() + (parentGeometry.height() - self.height()) // 2
            self.move(x, y)

    def setupUi(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 35, 30, 30)
        mainLayout.setSpacing(25)

        # Header
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(10)

        # Question title
        title = TitleLabel(self.questionName)
        headerLayout.addWidget(title)

        # Source info
        sourceInfo = BodyLabel(
            f"Source: {self.source} • {self.subQuestionCount} Sub-Questions"
        )
        headerLayout.addWidget(sourceInfo)

        mainLayout.addLayout(headerLayout)

        # TabBar
        self.tabBar = TabBar(self)
        self.tabBar.setMovable(False)
        self.tabBar.setTabMaximumWidth(200)
        self.tabBar.setTabShadowEnabled(True)
        self.tabBar.tabAddRequested.connect(self.addSubQuestion)
        self.tabBar.tabCloseRequested.connect(self.removeSubQuestion)

        # Stacked widget
        self.stackedWidget = QStackedWidget()

        # Sub-question widgets
        subQuestionWidget = SubQuestionWidget(1)
        self.subQuestionWidgets.append(subQuestionWidget)

        # Scroll area
        scrollArea = SmoothScrollArea()
        scrollArea.setScrollAnimation(
            Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint
        )
        scrollArea.setScrollAnimation(
            Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint
        )
        scrollArea.setWidget(subQuestionWidget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("border: none;")

        self.stackedWidget.addWidget(scrollArea)

        tabName = "Sub-Question A"
        routeKey = f"subQuestion_{self.routeKeyCounter}"
        self.routeKeyCounter += 1
        self.tabBar.addTab(routeKey, tabName, FluentIcon.EDIT)

        self.tabBar.currentChanged.connect(self.onTabChanged)

        if self.subQuestionCount > 0:
            self.tabBar.setCurrentIndex(0)
            self.stackedWidget.setCurrentIndex(0)

        mainLayout.addWidget(self.tabBar)
        mainLayout.addWidget(self.stackedWidget)

        # Buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 15, 0, 0)
        buttonLayout.setSpacing(10)

        # Cancel button
        cancelBtn = PushButton("Cancel")
        cancelBtn.setFixedHeight(40)
        cancelBtn.clicked.connect(self.close)
        buttonLayout.addWidget(cancelBtn)

        buttonLayout.addStretch()

        # Save button
        saveBtn = PrimaryPushButton("Save Question")
        saveBtn.setIcon(FluentIcon.SAVE)
        saveBtn.setFixedHeight(40)
        saveBtn.clicked.connect(self.saveQuestion)
        buttonLayout.addWidget(saveBtn)

        mainLayout.addLayout(buttonLayout)

    def onTabChanged(self, index: int):
        """Handle tab changes from the TabBar"""
        if 0 <= index < self.stackedWidget.count():
            self.stackedWidget.setCurrentIndex(index)

    def addSubQuestion(self):
        """Add a new sub-question"""
        self.subQuestionCount += 1

        subQuestionWidget = SubQuestionWidget(self.subQuestionCount)
        self.subQuestionWidgets.append(subQuestionWidget)

        scrollArea = SmoothScrollArea()
        scrollArea.setScrollAnimation(
            Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint
        )
        scrollArea.setScrollAnimation(
            Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint
        )
        scrollArea.setWidget(subQuestionWidget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("border: none;")

        self.stackedWidget.addWidget(scrollArea)

        tabName = f"Sub-Question {chr(64 + self.subQuestionCount)}"
        routeKey = f"subQuestion_{self.routeKeyCounter}"
        self.routeKeyCounter += 1
        self.tabBar.addTab(routeKey, tabName, FluentIcon.EDIT)

        self.tabBar.setCurrentIndex(self.subQuestionCount - 1)
        self.stackedWidget.setCurrentIndex(self.subQuestionCount - 1)

    def removeSubQuestion(self, index: int):
        """Remove a sub-question"""
        if self.subQuestionCount == 1:
            Flyout.create(
                icon=InfoBarIcon.WARNING,
                title="Validation Error",
                content="Please add at least one sub-question with a description.",
                target=self,
                parent=self,
                aniType=FlyoutAnimationType.PULL_UP,
            )
            return

        if 0 <= index < self.stackedWidget.count():
            scrollAreaToRemove = self.stackedWidget.widget(index)
            self.stackedWidget.removeWidget(scrollAreaToRemove)
            scrollAreaToRemove.deleteLater()

            del self.subQuestionWidgets[index]

            self.tabBar.removeTab(index)

            for i in range(index, self.tabBar.count()):
                tabName = f"Sub-Question {chr(65 + i)}"
                self.tabBar.setTabText(i, tabName)

                if i < len(self.subQuestionWidgets):
                    self.subQuestionWidgets[i].subQuestionNumber = i + 1
                    titleWidget = self.subQuestionWidgets[i].layout().itemAt(0).widget()
                    if hasattr(titleWidget, "setText"):
                        titleWidget.setText(f"Sub-Question {chr(65 + i)}")

            self.subQuestionCount -= 1

    def saveQuestion(self):
        """Save the question and emit signal"""
        validSubQuestions = []
        for widget in self.subQuestionWidgets:
            data = widget.getData()
            if data["description"].strip():
                validSubQuestions.append(data)

        if not validSubQuestions:
            Flyout.create(
                icon=InfoBarIcon.WARNING,
                title="Validation Error",
                content="Please add at least one sub-question with a description.",
                target=self,
                parent=self,
                aniType=FlyoutAnimationType.PULL_UP,
            )
            return

        self.questionSaved.emit(
            self.questionName,
            self.source,
            validSubQuestions,
        )

        self.close()


class StudentPerformanceWindow(FramelessWindow):
    """Window showing detailed student performance for an assignment"""

    def __init__(
        self,
        data: dict,
        parent=None,
    ):
        super().__init__()
        self.data = data

        self.setWindowTitle("Student Performance")
        self.resize(1200, 700)
        self.setStyleSheet("background-color: #f5f5f5;")
        self.setupUi()

        if parent:
            parentGeometry = parent.geometry()
            x = parentGeometry.x() + (parentGeometry.width() - self.width()) // 2
            y = parentGeometry.y() + (parentGeometry.height() - self.height()) // 2
            self.move(x, y)

    def setupUi(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 35, 30, 10)
        mainLayout.setSpacing(20)

        # Header
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(8)

        title = TitleLabel(f"{self.data.get('title', 'Assignment')}")
        headerLayout.addWidget(title)

        # Sub-question
        question_title = self.data.get("question_title", "")
        sub_question_text = self.data.get("sub_question_text", "")
        attribution = self.data.get("attribution", "")

        if question_title:
            questionLabel = SubtitleLabel(question_title)
            questionLabel.setStyleSheet("color: #666666; font-weight: 500;")
            headerLayout.addWidget(questionLabel)

        if sub_question_text:
            subQuestionLabel = BodyLabel(f"Sub-question: {sub_question_text}")
            subQuestionLabel.setStyleSheet("color: #666666; font-style: italic;")
            subQuestionLabel.setWordWrap(True)
            headerLayout.addWidget(subQuestionLabel)

        mainLayout.addLayout(headerLayout)

        self.createStudentTable()
        self.studentTable.setSizePolicy(
            self.studentTable.sizePolicy().horizontalPolicy(),
            self.studentTable.sizePolicy().Policy.Expanding,
        )
        self.studentTable.setMinimumHeight(400)
        mainLayout.addWidget(self.studentTable, 1)

        if attribution:
            attributionLabel = CaptionLabel(attribution)
            attributionLabel.setWordWrap(True)
            attributionLabel.setStyleSheet("color: #666666; margin-top: 10px;")
            mainLayout.addWidget(attributionLabel)

    def createStudentTable(self):
        """Create a single table showing all students"""
        self.studentTable = TableWidget()
        self.studentTable.setColumnCount(4)
        self.studentTable.setHorizontalHeaderLabels(
            ["Student", "Answer", "Performance", "Feedback"]
        )

        all_students = self.data.get("student_performances")

        self.studentTable.setRowCount(len(all_students))

        for row, student in enumerate(all_students):
            # Student name
            nameItem = QTableWidgetItem(student["user"]["display_name"])
            self.studentTable.setItem(row, 0, nameItem)

            # Answer
            answer = student["answer"] or "No answer provided"
            answerItem = QTableWidgetItem(answer)
            answerItem.setToolTip(answer)

            if answer == "No answer provided":
                answerItem.setForeground(QColor("#999999"))

            self.studentTable.setItem(row, 1, answerItem)

            # Performance
            performance = (
                student["performance"].name.lower()
                if student["performance"]
                else "Not Submitted"
            )
            color, _ = levelToColor(performance)
            performanceItem = QTableWidgetItem(enumNameToText(performance))
            performanceItem.setForeground(color)
            self.studentTable.setItem(row, 2, performanceItem)

            # Feedback
            feedback = student["feedback"] or "No feedback provided"
            feedbackItem = QTableWidgetItem(feedback)
            feedbackItem.setToolTip(feedback)

            self.studentTable.setItem(row, 3, feedbackItem)

        self.studentTable.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.studentTable.verticalHeader().setVisible(False)
        self.studentTable.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)

        header = self.studentTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)


class StandardAnswerCard(CardWidget):
    """Standard answer card displaying correct answers"""

    def __init__(self, standardAnswer: str, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        # Title
        title = StrongBodyLabel("Standard Answer")
        title.setStyleSheet(
            "color: #2e7d32; font-weight: 600; background-color: transparent;"
        )
        layout.addWidget(title)

        # Answer content
        answerLabel = BodyLabel(standardAnswer)
        answerLabel.setWordWrap(True)
        answerLabel.setStyleSheet(
            "color: #333333; line-height: 1.4; background-color: transparent;"
        )
        layout.addWidget(answerLabel)


class TeacherAssignmentQuestionInterface(QWidget):
    """Teacher assignment question review interface showing standard answers"""

    def __init__(
        self,
        assignmentData: dict = None,
        teacherController=None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("teacherAssignmentQuestionInterface")
        self.teacherController = teacherController

        self.assignmentData = assignmentData or {}
        self.assignment_title = self.assignmentData.get("title", "Assignment")
        self.questions = self.assignmentData.get("questions", [])

        self.currentQuestionIndex = 0
        self.totalQuestions = len(self.questions)

        self.current_question_title = self.questions[0].get("title", "Question")

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
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mainLayout.setContentsMargins(35, 25, 35, 25)
        self.mainLayout.setSpacing(20)

        # Header
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(8)

        # Assignment title
        self.titleLabel = TitleLabel(self.assignment_title)
        headerLayout.addWidget(self.titleLabel)

        # Current question title
        self.questionTitleLabel = SubtitleLabel(self.current_question_title)
        self.questionTitleLabel.setStyleSheet("color: #666666; font-weight: 500;")
        headerLayout.addWidget(self.questionTitleLabel)

        # Attribution
        self.attributionLabel = BodyLabel("")
        self.attributionLabel.hide()
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

        self.mainLayout.addStretch()
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
        self.questionTitleLabel.setText(question_title)

        if attribution:
            self.attributionLabel.setText(attribution)
            self.attributionLabel.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextBrowserInteraction
            )
            self.attributionLabel.setOpenExternalLinks(True)
            self.attributionLabel.setWordWrap(True)
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
        for sub_question_data in sub_questions:
            sub_question_card = self._createReadOnlySubQuestionCard(sub_question_data)
            if sub_question_card:
                self.currentSubQuestionCards.append(sub_question_card)
                self.questionLayout.addWidget(sub_question_card)

    def _clearQuestionContainer(self):
        """Clear all widgets from the question container"""
        while self.questionLayout.count():
            item = self.questionLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _createReadOnlySubQuestionCard(self, subQuestionData: dict):
        """Create a read-only sub-question card with standard answer"""
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

            for checkbox in questionCard.checkboxes:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)

        elif question_type == "text" or question_type == "text_input":
            questionCard = TextQuestionCard(question_text, parent=self)

            image_data = subQuestionData.get("image", None)
            if image_data:
                questionCard.setImage(image_data)
            else:
                questionCard.hideImage()

            if hasattr(questionCard, "answerInput"):
                questionCard.answerInput.hide()

        else:
            questionCard = TextQuestionCard(question_text, parent=self)

            image_data = subQuestionData.get("image", None)
            if image_data:
                questionCard.setImage(image_data)
            else:
                questionCard.hideImage()
            if hasattr(questionCard, "answerInput"):
                questionCard.answerInput.hide()

        if hasattr(questionCard, "submitBtn"):
            questionCard.submitBtn.hide()
        if hasattr(questionCard, "showKeywordsBtn"):
            questionCard.showKeywordsBtn.hide()
        if hasattr(questionCard, "dontKnowBtn"):
            questionCard.dontKnowBtn.hide()

        if hasattr(questionCard, "actionLayout"):
            questionCard.actionLayout.setContentsMargins(0, 0, 0, 0)

        standard_answer = subQuestionData.get("answer", "No standard answer provided")
        standardAnswerCard = StandardAnswerCard(standard_answer)
        questionCard.addExtraWidget(standardAnswerCard)

        return questionCard

    def _onBackClicked(self):
        """Handle back button click"""
        if self.currentQuestionIndex > 0:
            self.currentQuestionIndex -= 1
            self._loadCurrentQuestion()
        else:
            if self.teacherController:
                self.teacherController.goToAssignments()

    def _onNextClicked(self):
        """Handle next button click"""
        if self.currentQuestionIndex < self.totalQuestions - 1:
            self.currentQuestionIndex += 1
            self._loadCurrentQuestion()
        else:
            if self.teacherController:
                self.teacherController.goToAssignments()


class TeacherAssignmentReviewInterface(QWidget):
    """Class-level assignment review interface showing overall statistics"""

    def __init__(
        self,
        controller: TeacherController,
        reviewData: dict = None,
        parent=None,
    ):
        super().__init__(parent)
        self.controller = controller
        self.reviewData = reviewData or {}
        self.setObjectName("teacherAssignmentReviewInterface")

        self.assignmentTitle = self.reviewData.get("title", "Assignment Review")
        self.classId = self.reviewData.get("class_id", "Class")
        self.totalStudents = self.reviewData.get("total_students", 0)
        self.questions = self.reviewData.get("questions", [])

        self.currentQuestionIndex = 0
        self.totalQuestions = len(self.questions)

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
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollArea.setStyleSheet("background-color: #f5f5f5; border: none;")

        container = QWidget()
        scrollArea.setWidget(container)

        mainLayout = QVBoxLayout(container)
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainLayout.setContentsMargins(35, 25, 35, 25)
        mainLayout.setSpacing(20)

        # Header
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(8)

        # Assignment title
        self.titleLabel = TitleLabel(self.assignmentTitle)
        headerLayout.addWidget(self.titleLabel)

        mainLayout.addLayout(headerLayout)

        # Progress
        progressLayout = QHBoxLayout()
        self.progressLabel = BodyLabel(
            f"Question {self.currentQuestionIndex + 1} of {self.totalQuestions}"
        )
        self.progressLabel.setStyleSheet("color: #666666; font-weight: 500;")
        progressLayout.addWidget(self.progressLabel)
        progressLayout.addStretch()
        mainLayout.addLayout(progressLayout)

        # Question container
        self.questionContainer = QWidget()
        self.questionLayout = QVBoxLayout(self.questionContainer)
        self.questionLayout.setContentsMargins(0, 0, 0, 0)
        self.questionLayout.setSpacing(15)
        mainLayout.addWidget(self.questionContainer)

        # Footer navigation
        footerLayout = QHBoxLayout()
        footerLayout.setContentsMargins(0, 15, 0, 0)

        # Back button
        self.backButton = PushButton("Back")
        self.backButton.clicked.connect(self.handleBack)

        # Next button
        self.nextButton = PrimaryPushButton("Next")
        self.nextButton.clicked.connect(self.handleNext)

        footerLayout.addWidget(self.backButton)
        footerLayout.addStretch()
        footerLayout.addWidget(self.nextButton)

        mainLayout.addStretch()
        mainLayout.addLayout(footerLayout)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

        self.loadCurrentQuestion()

    def loadCurrentQuestion(self):
        """Load the current question and its sub-questions"""
        if not self.questions or self.currentQuestionIndex >= len(self.questions):
            return

        self.clearQuestionContainer()

        current_question = self.questions[self.currentQuestionIndex]
        question_title = current_question.get(
            "title", f"Question {self.currentQuestionIndex + 1}"
        )
        attribution = current_question.get("attribution", "")
        sub_questions = current_question.get("sub_questions", [])

        self.progressLabel.setText(
            f"Question {self.currentQuestionIndex + 1} of {self.totalQuestions}"
        )

        if self.currentQuestionIndex == self.totalQuestions - 1:
            self.nextButton.setText("Finish Review")
        else:
            self.nextButton.setText("Next")

        self.backButton.setEnabled(self.currentQuestionIndex > 0)

        # Question title
        if question_title:
            titleWidget = SubtitleLabel(question_title)
            titleWidget.setStyleSheet(
                "color: #333333; font-weight: 600; font-size: 18px;"
            )
            self.questionLayout.addWidget(titleWidget)

        # Attribution
        if attribution:
            attributionWidget = CaptionLabel(attribution)
            attributionWidget.setOpenExternalLinks(True)
            attributionWidget.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextBrowserInteraction
            )
            attributionWidget.setWordWrap(True)
            self.questionLayout.addWidget(attributionWidget)

        for sub_question_data in sub_questions:
            sub_question_card = self.createStatisticsSubQuestionCard(
                sub_question_data, sub_question_data["id"]
            )
            if sub_question_card:
                self.questionLayout.addWidget(sub_question_card)

    def createStatisticsSubQuestionCard(
        self, subQuestionData: dict, subQuestionId: int
    ):
        """Create a statistics card showing class performance on a sub-question"""
        question_text = subQuestionData.get("text", "")
        question_type = subQuestionData.get("type", "text")
        image_data = subQuestionData.get("image", None)
        student_performances = subQuestionData.get("student_performances", [])

        students_answered = sum(
            student_performance["performance"] is not None
            for student_performance in student_performances
        )
        average_score = (
            sum(
                student_performance["performance"].value
                for student_performance in student_performances
                if student_performance["performance"] is not None
            )
            / students_answered
            if students_answered > 0
            else 0
        )
        total_students = len(student_performances)

        # Main card
        card = CardWidget()
        card.setStyleSheet("border-radius: 8px;")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Main content
        contentLayout = QHBoxLayout()
        contentLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        contentLayout.setSpacing(20)

        # Question text & options
        textLayout = QVBoxLayout()
        textLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        textLayout.setSpacing(10)

        # Question text
        questionLabel = BodyLabel(question_text)
        questionLabel.setStyleSheet("background-color: transparent; color: #000000;")
        questionLabel.setWordWrap(True)
        textLayout.addWidget(questionLabel)

        if question_type == "multiple_choice":
            options = subQuestionData.get("options", [])
            if options:
                optionsLayout = QVBoxLayout()
                optionsLayout.setSpacing(5)
                for i, option in enumerate(options):
                    optionLabel = BodyLabel(f"{chr(65 + i)}. {option}")
                    optionLabel.setStyleSheet(
                        "color: #666666; font-size: 12px; background-color: transparent;"
                    )
                    optionsLayout.addWidget(optionLabel)
                textLayout.addLayout(optionsLayout)

        contentLayout.addLayout(textLayout, 1)

        # Image
        if image_data:
            imageWidget = ImageLabel(QImage.fromData(image_data))
            imageWidget.scaledToWidth(800)
            contentLayout.addWidget(imageWidget)

        layout.addLayout(contentLayout)

        # Standard answer
        standard_answer = subQuestionData.get("answer", "No standard answer provided")
        standardAnswerCard = StandardAnswerCard(standard_answer)
        layout.addWidget(standardAnswerCard)

        # Statistics
        statsLayout = QHBoxLayout()
        statsLayout.setSpacing(30)

        # Average score
        scoreSection = QVBoxLayout()
        scoreSection.setSpacing(5)

        scoreTitle = BodyLabel("Average Score")
        scoreTitle.setStyleSheet(
            "color: #333333; font-weight: 600; background-color: transparent;"
        )
        scoreSection.addWidget(scoreTitle)

        scoreValue = SubtitleLabel(f"{average_score:.1f}/4.0")
        if average_score >= 3.0:
            scoreValue.setStyleSheet(
                "color: #4CAF50; font-weight: 600; background-color: transparent;"
            )
        elif average_score >= 2.0:
            scoreValue.setStyleSheet(
                "color: #8BC34A; font-weight: 600; background-color: transparent;"
            )
        elif average_score >= 1.0:
            scoreValue.setStyleSheet(
                "color: #FF9800; font-weight: 600; background-color: transparent;"
            )
        else:
            scoreValue.setStyleSheet(
                "color: #F44336; font-weight: 600; background-color: transparent;"
            )
        scoreSection.addWidget(scoreValue)

        statsLayout.addLayout(scoreSection)

        # Response rate
        responseSection = QVBoxLayout()
        responseSection.setSpacing(5)

        responseTitle = BodyLabel("Response Rate")
        responseTitle.setStyleSheet(
            "color: #333333; font-weight: 600; background-color: transparent;"
        )
        responseSection.addWidget(responseTitle)

        responseValue = SubtitleLabel(f"{students_answered}/{total_students}")
        response_rate = students_answered / total_students if total_students > 0 else 0
        if response_rate >= 0.9:
            responseValue.setStyleSheet(
                "color: #4CAF50; font-weight: 600; background-color: transparent;"
            )
        elif response_rate >= 0.7:
            responseValue.setStyleSheet(
                "color: #FF9800; font-weight: 600; background-color: transparent;"
            )
        else:
            responseValue.setStyleSheet(
                "color: #F44336; font-weight: 600; background-color: transparent;"
            )
        responseSection.addWidget(responseValue)

        statsLayout.addLayout(responseSection)

        viewPerformanceBtn = PushButton("View Student Performance")
        viewPerformanceBtn.setIcon(FluentIcon.PEOPLE)
        viewPerformanceBtn.clicked.connect(
            lambda: self.showStudentPerformance(
                subQuestionId, question_text, student_performances
            )
        )

        statsLayout.addStretch()
        statsLayout.addWidget(viewPerformanceBtn, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(statsLayout)

        return card

    def clearQuestionContainer(self):
        """Clear all widgets from the question container"""
        while self.questionLayout.count():
            item = self.questionLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def handleBack(self):
        """Handle back button click"""
        if self.currentQuestionIndex > 0:
            self.currentQuestionIndex -= 1
            self.loadCurrentQuestion()

    def handleNext(self):
        """Handle next button click"""
        if self.currentQuestionIndex < self.totalQuestions - 1:
            self.currentQuestionIndex += 1
            self.loadCurrentQuestion()
        else:
            self.controller.showIndividualClass(self.classId)

    def showStudentPerformance(
        self, subQuestionId: int, subQuestionText: str, student_performances: list
    ):
        """Show student performance window for a specific sub-question"""
        assignmentId = self.reviewData.get("assignment_id")
        className = self.reviewData.get("class_name")

        if self.controller:
            self.controller.loadSubQuestionStudentPerformance(
                {
                    "assignment_title": self.reviewData.get("title"),
                    "question_title": self.reviewData["questions"][
                        self.currentQuestionIndex
                    ].get("title"),
                    "attribution": self.reviewData["questions"][
                        self.currentQuestionIndex
                    ].get("attribution"),
                    "sub_question_text": subQuestionText,
                    "assignment_id": assignmentId,
                    "sub_question_id": subQuestionId,
                    "class_name": className,
                    "student_performances": student_performances,
                }
            )

    def updateReviewData(self, reviewData: dict):
        """Update the review data and reload"""
        self.reviewData = reviewData
        self.assignmentTitle = reviewData.get("title")
        self.classId = reviewData.get("class_id")
        self.totalStudents = reviewData.get("total_students", 0)
        self.questions = reviewData.get("questions", [])
        self.totalQuestions = len(self.questions)
        self.currentQuestionIndex = 0

        self.titleLabel.setText(self.assignmentTitle)

        self.loadCurrentQuestion()


class TeacherMainWindow(FluentWindow):
    """Main teacher application window"""

    def __init__(self, teacherController: TeacherController):
        super().__init__()
        self.teacherController = teacherController

        self.setupInterfaces()
        self.initWindow()
        self.connectControllerSignals()

        self.loadData()

    def setupInterfaces(self):
        """Initialize interface placeholders"""
        self.setWindowIcon(QIcon("resources:icon.png"))

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))
        self.splashScreen.show()

        self.homeInterface = None
        self.classesInterface = None
        self.assignmentsInterface = None
        self.questionsInterface = None

        self.individualClassInterface = None
        self.studentStatisticsInterface = None
        self.assignmentReviewInterface = None
        self.assignmentQuestionInterface = None

    def loadData(self):
        """Load data from the controller"""
        self.splashScreen.show()
        print("[TeacherMainWindow] loadData called - starting initial data load")
        self._loadStatus = {
            "dashboard": False,
            "classes": False,
            "assignments": False,
            "questions": False,
        }
        self.teacherController.loadDashboardData()
        self.teacherController.loadAssignmentsData()
        self.teacherController.loadQuestionsData()

    def refreshBackgroundData(self):
        """Refresh background data"""
        self._isBackgroundRefresh = True
        self._backgroundRefreshCount = 0

        self.teacherController.loadDashboardData()
        self.teacherController.loadAssignmentsData()
        self.teacherController.loadQuestionsData()

    def _checkBackgroundRefreshComplete(self):
        """Check if background refresh is complete and reset flag"""
        self._backgroundRefreshCount = getattr(self, "_backgroundRefreshCount", 0) + 1

        if self._backgroundRefreshCount >= 4:  # 4 data sources for teacher
            self._isBackgroundRefresh = False
            self._backgroundRefreshCount = 0

    def connectControllerSignals(self):
        """Connect controller signals"""
        if not self.teacherController:
            return

        self.teacherController.navigateToClassOverview.connect(
            self.handleShowClassesOverview
        )
        self.teacherController.navigateToIndividualClass.connect(
            self.handleShowIndividualClass
        )
        self.teacherController.navigateToStudentStatistics.connect(
            self.handleShowStudentStatistics
        )
        self.teacherController.navigateToAssignmentReview.connect(
            self.handleShowAssignmentReview
        )
        self.teacherController.navigateToAssignmentQuestions.connect(
            self.handleShowAssignmentQuestions
        )
        self.teacherController.navigateToAssignments.connect(self.handleGoToAssignments)

        self.teacherController.dashboardDataReady.connect(self.onDashboardDataReady)
        self.teacherController.classesDataReady.connect(self.onClassesDataReady)
        self.teacherController.assignmentsDataReady.connect(self.onAssignmentsDataReady)
        self.teacherController.questionsDataReady.connect(self.onQuestionsDataReady)
        self.teacherController.classDataReady.connect(self.onClassDataReady)
        self.teacherController.studentStatisticsReady.connect(
            self.onStudentStatisticsReady
        )
        self.teacherController.assignmentCreationResult.connect(
            self.onAssignmentCreated
        )
        self.teacherController.classCreationResult.connect(self.onClassCreated)
        self.teacherController.questionCreationResult.connect(self.onQuestionCreated)
        self.teacherController.classAssignmentReviewReady.connect(
            self.onClassAssignmentReviewReady
        )
        self.teacherController.studentRemovalResult.connect(self.onStudentRemovalResult)
        self.teacherController.assignmentQuestionsDataReady.connect(
            self.onAssignmentQuestionsDataReady
        )
        self.teacherController.assignmentAssignmentResult.connect(
            self.onAssignmentAssignmentResult
        )
        self.teacherController.operationError.connect(self.onOperationError)
        self.teacherController.subQuestionStudentPerformanceReady.connect(
            self.onSubQuestionStudentPerformanceReady
        )

    def initNavigation(self):
        """Initialize navigation items"""
        if self.homeInterface:
            self.addSubInterface(self.homeInterface, FluentIcon.HOME, "Home")
        if self.classesInterface:
            self.addSubInterface(
                self.classesInterface, FluentIcon.BOOK_SHELF, "Classes"
            )
        if self.assignmentsInterface:
            self.addSubInterface(
                self.assignmentsInterface, FluentIcon.DOCUMENT, "Assignments"
            )
        if self.questionsInterface:
            self.addSubInterface(
                self.questionsInterface, FluentIcon.QUESTION, "Questions"
            )

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

    def handleShowIndividualClass(self, classId: int, tab: str = "students"):
        """Handle navigation to individual class interface"""
        self._classTab = tab
        self.teacherController.loadClassData(classId)

    def handleShowClassesOverview(self):
        """Handle navigation back to classes overview"""
        self.switchTo(self.classesInterface)

    def handleShowStudentStatistics(self, studentId: int, studentName: str):
        """Handle navigation to student statistics interface"""
        self.teacherController.loadStudentStatistics(studentId, studentName)

    def handleShowAssignmentReview(self, reviewData: dict):
        """Handle navigation to assignment review interface"""
        if not self.assignmentReviewInterface:
            self.assignmentReviewInterface = TeacherAssignmentReviewInterface(
                self.teacherController, reviewData, self
            )
            self.stackedWidget.addWidget(self.assignmentReviewInterface)

        self.assignmentReviewInterface.updateReviewData(reviewData)
        self.stackedWidget.setCurrentWidget(self.assignmentReviewInterface)
        self.navigationInterface.setCurrentItem("classesOverview")

    def handleShowAssignmentQuestions(self, assignmentId: int):
        """Handle showing assignment questions interface with standard answers"""
        self.teacherController.loadAssignmentQuestions(assignmentId)

    def handleGoToAssignments(self):
        """Handle navigation back to assignments interface"""
        self.switchTo(self.assignmentsInterface)

    def _finishLoading(self):
        """Finish loading data"""
        if (
            self._loadStatus["dashboard"]
            and self._loadStatus["classes"]
            and self._loadStatus["assignments"]
            and self._loadStatus["questions"]
        ):
            self.initNavigation()
            if self.homeInterface:
                self.switchTo(self.homeInterface)
            self.splashScreen.hide()

    def _updateHomeInterfaceContent(self, dashboardData: dict):
        """Update home interface content"""
        if self.homeInterface:
            self.homeInterface.updateContent(dashboardData)

    def _updateClassesInterfaceContent(self, classesData: list):
        """Update classes interface content"""
        if self.classesInterface:
            self.classesInterface.updateContent(classesData)

    def _updateAssignmentsInterfaceContent(self, assignmentsData: list):
        """Update assignments interface content"""
        if self.assignmentsInterface:
            self.assignmentsInterface.updateContent(assignmentsData)

    def _updateQuestionsInterfaceContent(self, questionsData: list):
        """Update questions interface content"""
        if self.questionsInterface:
            self.questionsInterface.updateContent(questionsData)

    def onDashboardDataReady(self, data: dict):
        """Handle dashboard data ready"""
        if getattr(self, "_isBackgroundRefresh", False):
            self._updateHomeInterfaceContent(data)
            self._checkBackgroundRefreshComplete()
        else:
            self._loadStatus["dashboard"] = True
            if self.homeInterface:
                self._updateHomeInterfaceContent(data)
            else:
                self.homeInterface = TeacherHomeInterface(self.teacherController)
                self.homeInterface.updateContent(data)
            self._finishLoading()

    def onClassesDataReady(self, data: list):
        """Handle classes data ready"""
        if getattr(self, "_isBackgroundRefresh", False):
            self._updateClassesInterfaceContent(data)
            self._checkBackgroundRefreshComplete()
        else:
            self._loadStatus["classes"] = True
            if self.classesInterface:
                self._updateClassesInterfaceContent(data)
            else:
                self.classesInterface = ClassesOverview(self.teacherController, self)
                self.classesInterface.updateContent(data)
            self._finishLoading()

    def onAssignmentsDataReady(self, data: list):
        """Handle assignments data ready"""
        if getattr(self, "_isBackgroundRefresh", False):
            self._updateAssignmentsInterfaceContent(data)
            self._checkBackgroundRefreshComplete()
        else:
            self._loadStatus["assignments"] = True
            if self.assignmentsInterface:
                self._updateAssignmentsInterfaceContent(data)
            else:
                self.assignmentsInterface = TeacherAssignmentsInterface(
                    self.teacherController, self
                )
                self.assignmentsInterface.updateContent(data)
            self._finishLoading()

    def onQuestionsDataReady(self, data: list):
        """Handle questions data ready"""
        if getattr(self, "_isBackgroundRefresh", False):
            self._updateQuestionsInterfaceContent(data)
            self._checkBackgroundRefreshComplete()
        else:
            self._loadStatus["questions"] = True
            if self.questionsInterface:
                self._updateQuestionsInterfaceContent(data)
            else:
                self.questionsInterface = TeacherQuestionsInterface(
                    self.teacherController, self
                )
                self.questionsInterface.updateContent(data)
            self._finishLoading()

    def onClassDataReady(self, data: dict):
        """Handle individual class data ready"""
        if not self.individualClassInterface:
            self.individualClassInterface = IndividualClassInterface(
                self.teacherController,
                classId=data.get("id"),
                className=data.get("name"),
                classCode=data.get("code"),
                parent=self,
            )
            self.stackedWidget.addWidget(self.individualClassInterface)

        self.stackedWidget.setCurrentWidget(self.individualClassInterface)
        self.navigationInterface.setCurrentItem("classesOverview")
        self.individualClassInterface.pivot.setCurrentItem(
            self._classTab if hasattr(self, "_classTab") else "students"
        )
        self.individualClassInterface.updateContent(data)

    def onStudentStatisticsReady(self, data: dict):
        """Handle student statistics data ready"""
        print(
            f"[TeacherMainWindow] onStudentStatisticsReady called with data keys: {list(data.keys())}"
        )

        if not self.studentStatisticsInterface:
            self.studentStatisticsInterface = StudentStatisticsInterface(
                self.teacherController,
                studentId=data.get("student_id"),
                studentName=data.get("student_name"),
                classId=data.get("class_id"),
                parent=self,
            )
            self.stackedWidget.addWidget(self.studentStatisticsInterface)

        self.stackedWidget.setCurrentWidget(self.studentStatisticsInterface)
        self.navigationInterface.setCurrentItem("classesOverview")
        self.studentStatisticsInterface.updateContent(data)

    def onAssignmentCreated(self, success: bool, message: str):
        """Handle assignment creation result"""
        if success:
            InfoBar.success(
                title="Assignment Created",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            self.loadData()

    def onClassCreated(self, success: bool, message: str):
        """Handle class creation result"""
        if success:
            InfoBar.success(
                title="Class Created",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            self.loadData()

    def onQuestionCreated(self, success: bool, message: str):
        """Handle question creation result"""
        if success:
            InfoBar.success(
                title="Question Created",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            self.loadData()

    def onClassAssignmentReviewReady(self, data: dict):
        """Handle class assignment review data ready"""
        self.handleShowAssignmentReview(data)

    def onClassStudentsDataReady(self, data: list):
        """Handle class students data ready"""
        if self.individualClassInterface:
            self.individualClassInterface.updateStudentsData(data)

    def onClassAssignmentsDataReady(self, data: list):
        """Handle class assignments data ready"""
        if self.individualClassInterface:
            self.individualClassInterface.updateAssignmentsData(data)

    def onStudentRemovalResult(self, success: bool, message: str):
        """Handle student removal result"""
        if success:
            print(f"[TeacherMainWindow] Student removal successful: {message}")
            self.loadData()

            InfoBar.success(
                title="Student Removed",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
        else:
            print(f"[TeacherMainWindow] Student removal failed: {message}")
            InfoBar.error(
                title="Removal Failed",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self,
            )

    def onAssignmentQuestionsDataReady(self, data: dict):
        """Handle assignment questions data ready"""
        if not self.assignmentQuestionInterface:
            self.assignmentQuestionInterface = TeacherAssignmentQuestionInterface(
                data, self.teacherController, self
            )
            self.stackedWidget.addWidget(self.assignmentQuestionInterface)

        self.assignmentQuestionInterface.assignmentData = data
        self.assignmentQuestionInterface.questions = data.get("questions", [])
        self.assignmentQuestionInterface.totalQuestions = len(data.get("questions", []))
        self.assignmentQuestionInterface.currentQuestionIndex = 0
        self.assignmentQuestionInterface._loadCurrentQuestion()

        self.stackedWidget.setCurrentWidget(self.assignmentQuestionInterface)
        self.navigationInterface.setCurrentItem("teacherAssignmentsInterface")

    def onAssignmentAssignmentResult(self, success: bool, message: str):
        """Handle assignment assignment result"""
        if success:
            InfoBar.success(
                title="Assignment Assigned",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            self.loadData()

    def onOperationError(self, operation: str, error: str):
        """Handle operation errors"""
        print(f"[TeacherMainWindow] Error in {operation}: {error}")
        InfoBar.error(
            title="Error",
            content=error,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )

    def onSubQuestionStudentPerformanceReady(
        self,
        data: dict,
    ):
        """Handle sub-question student performance data ready"""
        print("[TeacherMainWindow] Sub-question student performance data ready")
        self.performanceWindow = StudentPerformanceWindow(data, self)
        self.performanceWindow.show()
        self.performanceWindow.raise_()
        self.performanceWindow.activateWindow()
