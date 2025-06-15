from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

from app.controllers.apiWorker import ApiWorker


class TeacherController(QObject):
    """Controller for teacher-related navigation and operations"""

    # Navigation signals
    navigateToClassOverview = pyqtSignal()
    navigateToIndividualClass = pyqtSignal(int, str)  # classId, tab
    navigateToStudentStatistics = pyqtSignal(int, str)  # studentId, studentName
    navigateToAssignmentReview = pyqtSignal(dict)  # assignmentData
    navigateToAssignmentQuestions = pyqtSignal(int)  # assignmentId
    navigateToAssignments = pyqtSignal()

    # Data signals
    dashboardDataReady = pyqtSignal(dict)
    classesDataReady = pyqtSignal(list)
    assignmentsDataReady = pyqtSignal(list)
    questionsDataReady = pyqtSignal(list)
    classDataReady = pyqtSignal(dict)
    studentStatisticsReady = pyqtSignal(dict)
    assignmentCreationResult = pyqtSignal(bool, str)  # success, message
    classCreationResult = pyqtSignal(bool, str)  # success, message
    questionCreationResult = pyqtSignal(bool, str)  # success, message
    classAssignmentReviewReady = pyqtSignal(dict)
    studentRemovalResult = pyqtSignal(bool, str)  # success, message
    assignmentQuestionsDataReady = pyqtSignal(dict)
    assignmentAssignmentResult = pyqtSignal(bool, str)  # success, message
    availableAssignmentsDataReady = pyqtSignal(list)
    filteredQuestionsDataReady = pyqtSignal(list)
    subQuestionStudentPerformanceReady = pyqtSignal(dict)

    operationError = pyqtSignal(str, str)  # operation, error_message

    def __init__(self, apiWorker: ApiWorker):
        super().__init__()
        self.apiWorker = apiWorker
        self._connectApiWorkerSignals()

    def _connectApiWorkerSignals(self):
        """Connect API worker signals to controller signals"""
        self.apiWorker.teacherDashboardDataLoaded.connect(self.dashboardDataReady.emit)
        self.apiWorker.teacherClassesDataLoaded.connect(self.classesDataReady.emit)
        self.apiWorker.teacherAssignmentsDataLoaded.connect(
            self.assignmentsDataReady.emit
        )
        self.apiWorker.teacherQuestionsDataLoaded.connect(self.questionsDataReady.emit)
        self.apiWorker.teacherClassDataLoaded.connect(self.classDataReady.emit)
        self.apiWorker.teacherStudentStatisticsLoaded.connect(
            self.studentStatisticsReady.emit
        )
        self.apiWorker.assignmentCreated.connect(self.assignmentCreationResult.emit)
        self.apiWorker.classCreated.connect(self.classCreationResult.emit)
        self.apiWorker.questionCreated.connect(self.questionCreationResult.emit)
        self.apiWorker.classAssignmentReviewLoaded.connect(
            self.classAssignmentReviewReady.emit
        )
        self.apiWorker.studentRemovedFromClass.connect(self.studentRemovalResult.emit)
        self.apiWorker.assignmentQuestionsDataLoaded.connect(
            self.assignmentQuestionsDataReady.emit
        )
        self.apiWorker.assignmentAssignmentResult.connect(
            self.assignmentAssignmentResult.emit
        )
        self.apiWorker.availableAssignmentsDataLoaded.connect(
            self.availableAssignmentsDataReady.emit
        )
        self.apiWorker.filteredQuestionsLoaded.connect(
            self.filteredQuestionsDataReady.emit
        )

        self.apiWorker.operationFailed.connect(self.operationError.emit)

    # Navigation methods
    def showClassesOverview(self):
        """Navigate to classes overview"""
        self.navigateToClassOverview.emit()

    def showIndividualClass(self, classId: int, tab: str = "students"):
        """Navigate to individual class interface"""
        self.navigateToIndividualClass.emit(classId, tab)

    def showStudentStatistics(self, studentId: int, studentName: str):
        """Navigate to individual student statistics interface"""
        self.navigateToStudentStatistics.emit(studentId, studentName)

    def showAssignmentReview(self, assignmentId: int):
        """Navigate to assignment questions interface with standard answers"""
        self.navigateToAssignmentQuestions.emit(assignmentId)

    def showClassAssignmentReview(self, assignmentData: dict):
        """Navigate to class assignment review interface"""
        self.navigateToAssignmentReview.emit(assignmentData)

    def goToAssignments(self):
        """Navigate back to assignments interface"""
        self.navigateToAssignments.emit()

    # Data loading methods
    def loadDashboardData(self):
        """Load teacher dashboard data"""
        print("[TeacherController] loadDashboardData called")
        self.apiWorker.setup("load_teacher_dashboard_data")
        self.apiWorker.start()

    def loadAssignmentsData(self):
        """Load teacher assignments data"""
        self.apiWorker.setup("load_teacher_assignments_data")
        self.apiWorker.start()

    def loadQuestionsData(self):
        """Load teacher questions data"""
        self.apiWorker.setup("load_teacher_questions_data")
        self.apiWorker.start()

    def loadClassData(self, classId: int):
        """Load individual class data"""
        self.apiWorker.setup("load_teacher_class_data", class_id=classId)
        self.apiWorker.start()

    def loadStudentStatistics(self, studentId: int, studentName: str):
        """Load student statistics data"""
        print(
            f"[TeacherController] loadStudentStatistics called for {studentId} {studentName}"
        )
        self.apiWorker.setup(
            "load_teacher_student_statistics",
            student_id=studentId,
            student_name=studentName,
        )
        self.apiWorker.start()

    def loadClassAssignmentReview(self, assignmentId: int, classId: int):
        """Load class assignment review data"""
        self.apiWorker.setup(
            "load_class_assignment_review",
            assignment_id=assignmentId,
            class_id=classId,
        )
        self.apiWorker.start()

    # Creation methods
    def createAssignment(self, name: str, description: str, questionIds: list):
        """Create a new assignment"""
        self.apiWorker.setup(
            "create_assignment",
            name=name,
            description=description,
            question_ids=questionIds,
        )
        self.apiWorker.start()

    def createClass(self, className: str, enterCode: str):
        """Create a new class"""
        self.apiWorker.setup("create_class", class_name=className, enter_code=enterCode)
        self.apiWorker.start()

    def createQuestion(self, name: str, source: str, subQuestionsData: list):
        """Create a new question"""
        self.apiWorker.setup(
            "create_question",
            name=name,
            source=source,
            sub_questions_data=subQuestionsData,
        )
        self.apiWorker.start()

    def removeStudentFromClass(self, studentId: int):
        """Remove a student from a class"""
        print(f"[TeacherController] removeStudentFromClass called for {studentId}")
        self.apiWorker.setup(
            "remove_student_from_class",
            student_id=studentId,
        )
        self.apiWorker.start()

    def loadAssignmentQuestions(self, assignmentId: int):
        """Load assignment questions data"""
        print(f"[TeacherController] loadAssignmentQuestions called for {assignmentId}")
        self.apiWorker.setup("load_assignment_questions", assignment_id=assignmentId)
        self.apiWorker.start()

    def loadAvailableAssignments(self):
        """Load available assignments for assignment"""
        print("[TeacherController] loadAvailableAssignments called")
        self.apiWorker.setup("load_available_assignments")
        self.apiWorker.start()

    def assignAssignmentToClass(
        self, assignmentId: int, classId: int, dueDate: datetime
    ):
        """Assign an assignment to a class"""
        print(
            f"[TeacherController] assignAssignmentToClass called: {assignmentId} to {classId}"
        )
        self.apiWorker.setup(
            "assign_assignment_to_class",
            assignment_id=assignmentId,
            class_id=classId,
            due_date=dueDate,
        )
        self.apiWorker.start()

    def loadFilteredQuestions(
        self, searchText: str = "", conceptFilter: str = "", processFilter: str = ""
    ):
        """Load filtered questions for selection"""
        print(
            f"[TeacherController] loadFilteredQuestions called with search: '{searchText}', concept: '{conceptFilter}', process: '{processFilter}'"
        )
        self.apiWorker.setup(
            "load_filtered_questions",
            search_text=searchText,
            concept_filter=conceptFilter,
            process_filter=processFilter,
        )
        self.apiWorker.start()

    def loadSubQuestionStudentPerformance(
        self,
        data: dict,
    ):
        """Load student performance data for a specific sub-question"""
        print(
            f"[TeacherController] loadSubQuestionStudentPerformance called for {data}"
        )
        self.subQuestionStudentPerformanceReady.emit(data)
