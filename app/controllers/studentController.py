from PyQt6.QtCore import QObject, pyqtSignal

from app.controllers.apiWorker import ApiWorker


class StudentController(QObject):
    """Controller for student-related operations"""

    dashboardDataReady = pyqtSignal(dict)
    classDataReady = pyqtSignal(dict)
    questionsReady = pyqtSignal(list)
    questionAnsweringDataReady = pyqtSignal(dict)
    questionReviewDataReady = pyqtSignal(dict)
    assignmentReviewDataReady = pyqtSignal(dict)
    subQuestionFeedbackReady = pyqtSignal(int, dict)  # sub_question_id, feedback
    aiResponseReady = pyqtSignal(str)  # text
    joinClassResult = pyqtSignal(bool, str)  # success, message
    errorOccurred = pyqtSignal(str, str)  # operation, error_message

    navigateToHome = pyqtSignal()
    navigateToClass = pyqtSignal()
    navigateToQuestions = pyqtSignal()

    def __init__(self, apiWorker: ApiWorker):
        super().__init__()
        self.apiWorker = apiWorker
        self.current_student_id = None
        self.current_class_id = None

        self._connectSignals()

    def _connectSignals(self):
        """Connect API worker signals to controller methods"""
        self.apiWorker.dashboardDataLoaded.connect(self._onDashboardDataLoaded)
        self.apiWorker.classDataLoaded.connect(self._onClassDataLoaded)
        self.apiWorker.questionsLoaded.connect(self._onQuestionsLoaded)
        self.apiWorker.questionAnsweringDataLoaded.connect(
            self._onQuestionAnsweringDataLoaded
        )
        self.apiWorker.questionReviewDataLoaded.connect(
            self._onQuestionReviewDataLoaded
        )
        self.apiWorker.assignmentReviewDataLoaded.connect(
            self._onAssignmentReviewDataLoaded
        )
        self.apiWorker.subQuestionFeedbackReceived.connect(
            self._onSubQuestionFeedbackReceived
        )
        self.apiWorker.aiResponseReceived.connect(self._onAIResponseReceived)
        self.apiWorker.joinClassFinished.connect(self._onJoinClassFinished)
        self.apiWorker.operationFailed.connect(self._onOperationFailed)

    def setStudentId(self, student_id: str):
        """Set the current student ID

        Args:
            student_id (str): The ID of the student
        """
        self.current_student_id = student_id

    def setClassId(self, class_id: str):
        """Set the current class ID

        Args:
            class_id (str): The ID of the class
        """
        self.current_class_id = class_id

    def loadDashboardData(self):
        """Load all dashboard data for the home interface"""
        self.apiWorker.setup("load_dashboard_data")
        self.apiWorker.start()

    def loadClassData(self):
        """Load class data for the class interface"""
        self.apiWorker.setup("load_class_data")
        self.apiWorker.start()

    def loadQuestions(self):
        """Load question history for the student

        Args:
            student_id (str, optional): Student ID. Uses current if not provided.
        """
        self.apiWorker.setup("load_questions")
        self.apiWorker.start()

    def loadAssignmentData(self, assignment_id: str):
        """Load specific assignment data for question answering

        Args:
            assignment_id (str): ID of the assignment to load
        """
        if not assignment_id:
            self.errorOccurred.emit("load_assignment_data", "No assignment ID provided")
            return

        self.apiWorker.setup("load_assignment_data", assignment_id=assignment_id)
        self.apiWorker.start()

    def loadAssignmentReviewData(self, assignment_id: str):
        """Load specific assignment data for review (read-only)

        Args:
            assignment_id (str): ID of the assignment to load for review
        """
        if not assignment_id:
            self.errorOccurred.emit(
                "load_assignment_review_data", "No assignment ID provided"
            )
            return

        self.apiWorker.setup("load_assignment_review_data", assignment_id=assignment_id)
        self.apiWorker.start()

    def loadQuestionReviewData(self, question_id: str):
        """Load specific question data for review (read-only)

        Args:
            question_id (str): ID of the question to load for review
        """
        if not question_id:
            self.errorOccurred.emit(
                "load_question_review_data", "No question ID provided"
            )
            return

        self.apiWorker.setup("load_question_review_data", question_id=question_id)
        self.apiWorker.start()

    def sendAIMessage(self, message: str, sub_question_id: int, history: list):
        """Send a message to the AI assistant

        Args:
            message (str): The message to send
            sub_question_id (int): The ID of the sub-question
            history (list): The history of messages
        """
        self.apiWorker.setup(
            "send_ai_message",
            message=message,
            sub_question_id=sub_question_id,
            history=history,
        )
        self.apiWorker.start()

    def submitAnswer(self, question_id: int, answer, question_type: str = "text"):
        """Submit an answer for a question

        Args:
            question_id (int): ID of the question
            answer: The answer (could be text or list of selections)
            question_type (str): Type of question ("text" or "multiple_choice")
        """
        self.apiWorker.setup(
            "submit_answer",
            question_id=question_id,
            answer=answer,
            question_type=question_type,
        )
        self.apiWorker.start()

    def submitSubQuestion(self, assignment_id: int, sub_question_id: int, answer):
        """Submit a sub-question answer for instant feedback

        Args:
            assignment_id (int): ID of the assignment
            sub_question_id (int): ID of the sub-question
            answer: The answer (could be text or list of selections)
        """
        self.apiWorker.setup(
            "submit_sub_question",
            assignment_id=assignment_id,
            sub_question_id=sub_question_id,
            answer=answer,
        )
        self.apiWorker.start()

    def refreshAllData(self):
        """Refresh all data for the current student"""
        if not self.current_student_id:
            self.errorOccurred.emit("refresh_all_data", "No student ID available")
            return

        self.loadDashboardData()

    def goToHome(self):
        """Navigate to home interface"""
        self.navigateToHome.emit()

    def goToClass(self):
        """Navigate to class interface"""
        self.navigateToClass.emit()

    def goToQuestions(self):
        """Navigate to questions interface"""
        self.navigateToQuestions.emit()

    def _onDashboardDataLoaded(self, data: dict):
        """Handle dashboard data loaded from API

        Args:
            data (dict): The data from the API
        """
        self.dashboardDataReady.emit(data)

    def _onClassDataLoaded(self, data: dict):
        """Handle class data loaded from API

        Args:
            data (dict): The data from the API
        """
        self.classDataReady.emit(data)

    def _onQuestionsLoaded(self, questions: list):
        """Handle questions loaded from API

        Args:
            questions (list): The questions from the API
        """
        self.questionsReady.emit(questions)

    def _onQuestionAnsweringDataLoaded(self, data: dict):
        """Handle question answering data loaded from API

        Args:
            data (dict): The data from the API
        """
        self.questionAnsweringDataReady.emit(data)

    def _onQuestionReviewDataLoaded(self, data: dict):
        """Handle question review data loaded from API

        Args:
            data (dict): The data from the API
        """
        self.questionReviewDataReady.emit(data)

    def _onAssignmentReviewDataLoaded(self, data: dict):
        """Handle assignment review data loaded from API

        Args:
            data (dict): The data from the API
        """
        self.assignmentReviewDataReady.emit(data)

    def _onSubQuestionFeedbackReceived(self, sub_question_id: int, feedback: dict):
        """Handle sub-question feedback received from API

        Args:
            sub_question_id (int): The ID of the sub-question
            feedback (dict): The feedback from the API
        """
        self.subQuestionFeedbackReady.emit(sub_question_id, feedback)

    def _onAIResponseReceived(self, response: str):
        """Handle AI response received from API

        Args:
            response (str): The response from the API
        """
        self.aiResponseReady.emit(response)

    def _onJoinClassFinished(self, success: bool, message: str):
        """Handle join class result from API

        Args:
            success (bool): Whether the join class operation was successful
            message (str): The message from the API
        """
        self.joinClassResult.emit(success, message)

    def _onOperationFailed(self, operation: str, error_message: str):
        """Handle operation failure

        Args:
            operation (str): The operation that failed
            error_message (str): The error message
        """
        self.errorOccurred.emit(operation, error_message)

    def joinClass(self, class_name: str, enter_code: str):
        """Join a class with the given name and enter code

        Args:
            class_name (str): Name of the class to join
            enter_code (str): Enter code for the class
        """
        if not class_name or not enter_code:
            self.errorOccurred.emit(
                "join_class", "Class name and enter code are required"
            )
            return

        self.apiWorker.setup(
            "join_class",
            class_name=class_name,
            enter_code=enter_code,
            student_id=self.current_student_id,
        )
        self.apiWorker.start()
