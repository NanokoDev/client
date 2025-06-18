import pytz
import traceback
from nanoko import Nanoko
from nanoko.models.llm import LLMMessage
from PyQt6.QtCore import QThread, pyqtSignal
from datetime import datetime, timedelta, timezone
from nanoko.models.performance import Performance, ProcessPerformances
from nanoko.models.question import ConceptType, ProcessType, Question, SubQuestion
from nanoko.exceptions import (
    NanokoAPI400BadRequestError,
    NanokoAPI401UnauthorizedError,
    NanokoAPI403ForbiddenError,
    NanokoAPI404NotFoundError,
)

from app.utils import (
    getAttribution,
    datetimeToText,
    textToEnumName,
    enumNameToText,
    getPermissionFromRole,
)


class ApiWorker(QThread):
    """Worker thread for API operations"""

    signInFinished = pyqtSignal(bool, str, object)  # success, message, user
    signUpFinished = pyqtSignal(bool, str)  # success, message

    # Student signals
    dashboardDataLoaded = pyqtSignal(dict)
    classDataLoaded = pyqtSignal(dict)
    questionsLoaded = pyqtSignal(list)
    questionAnsweringDataLoaded = pyqtSignal(dict)
    questionReviewDataLoaded = pyqtSignal(dict)
    assignmentReviewDataLoaded = pyqtSignal(dict)
    subQuestionFeedbackReceived = pyqtSignal(int, dict)  # sub_question_id, feedback
    answerSubmitted = pyqtSignal(dict)
    joinClassFinished = pyqtSignal(bool, str)  # success, message
    aiResponseReceived = pyqtSignal(str)  # text

    # Teacher signals
    teacherDashboardDataLoaded = pyqtSignal(dict)
    teacherClassesDataLoaded = pyqtSignal(list)
    teacherAssignmentsDataLoaded = pyqtSignal(list)
    teacherQuestionsDataLoaded = pyqtSignal(list)
    teacherClassDataLoaded = pyqtSignal(dict)
    teacherStudentStatisticsLoaded = pyqtSignal(dict)
    assignmentCreated = pyqtSignal(bool, str)  # success, message
    classCreated = pyqtSignal(bool, str)  # success, message
    questionCreated = pyqtSignal(bool, str)  # success, message
    classAssignmentReviewLoaded = pyqtSignal(dict)
    studentRemovedFromClass = pyqtSignal(bool, str)  # success, message
    assignmentQuestionsDataLoaded = pyqtSignal(dict)
    assignmentAssignmentResult = pyqtSignal(bool, str)  # success, message
    availableAssignmentsDataLoaded = pyqtSignal(list)
    filteredQuestionsLoaded = pyqtSignal(list)

    operationFailed = pyqtSignal(str, str)  # operation, error_message

    def __init__(self, nanokoClient: Nanoko):
        super().__init__()
        self.nanokoClient = nanokoClient
        self.operation = None
        self.params = None

    def setup(self, operation, **params):
        """Setup the worker with operation and parameters

        Args:
            operation (str): The operation to perform
            **params: Additional parameters for the operation
        """
        if self.isRunning():
            self.wait()

        self.operation = operation
        self.params = params

    def run(self):
        """Execute the operation in a separate thread"""
        if not self.operation:
            return

        print(f"[ApiWorker] Starting operation: {self.operation}")

        try:
            match self.operation:
                case "signin":
                    self._handleSignin()
                case "signup":
                    self._handleSignup()

                # Student operations
                case "load_dashboard_data":
                    self._handleLoadDashboardData()
                case "load_class_data":
                    self._handleLoadClassData()
                case "load_assignment_data":
                    self._handleLoadAssignmentData()
                case "load_assignment_review_data":
                    self._handleLoadAssignmentReviewData()
                case "load_question_review_data":
                    self._handleLoadQuestionReviewData()
                case "load_assignments":
                    self._handleLoadAssignments()
                case "load_questions":
                    self._handleLoadQuestions()
                case "submit_answer":
                    self._handleSubmitAnswer()
                case "submit_sub_question":
                    self._handleSubmitSubQuestion()
                case "send_ai_message":
                    self._handleSendAIMessage()
                case "join_class":
                    self._handleJoinClass()

                # Teacher operations
                case "load_teacher_dashboard_data":
                    self._handleLoadTeacherDashboardData()
                case "load_teacher_assignments_data":
                    self._handleLoadTeacherAssignmentsData()
                case "load_teacher_questions_data":
                    self._handleLoadTeacherQuestionsData()
                case "load_teacher_class_data":
                    self._handleLoadTeacherClassData()
                case "load_teacher_student_statistics":
                    self._handleLoadTeacherStudentStatistics()
                case "load_teacher_class_assignments":
                    self._handleLoadTeacherClassAssignments()
                case "create_assignment":
                    self._handleCreateAssignment()
                case "create_class":
                    self._handleCreateClass()
                case "create_question":
                    self._handleCreateQuestion()
                case "load_class_assignment_review":
                    self._handleLoadClassAssignmentReview()
                case "remove_student_from_class":
                    self._handleRemoveStudentFromClass()
                case "load_assignment_questions":
                    self._handleLoadAssignmentQuestions()
                case "load_class_performance":
                    self._handleLoadClassPerformance()
                case "load_available_assignments":
                    self._handleLoadAvailableAssignments()
                case "assign_assignment_to_class":
                    self._handleAssignAssignmentToClass()
                case "load_filtered_questions":
                    self._handleLoadFilteredQuestions()
                case "load_sub_question_student_performance":
                    self._handleLoadSubQuestionStudentPerformance()
                case _:
                    self.operationFailed.emit(
                        self.operation, f"Unknown operation: {self.operation}"
                    )
        except Exception as e:
            self.operationFailed.emit(self.operation, str(e))

    def _handleSignin(self):
        """Handle user sign in"""
        try:
            self.nanokoClient.user.login(
                self.params["username"], self.params["password"]
            )
            me = self.nanokoClient.user.me()
            self.signInFinished.emit(
                True,
                "Signin successful",
                me,
            )
        except NanokoAPI401UnauthorizedError as e:
            self.signInFinished.emit(False, e.response.json()["detail"], "student")
        except Exception as e:
            self.operationFailed.emit("signin", str(e))

    def _handleSignup(self):
        """Handle user sign up"""
        try:
            self.nanokoClient.user.register(
                username=self.params["username"],
                email=self.params["email"],
                display_name=(self.params["firstName"] + " " + self.params["lastName"]),
                password=self.params["password"],
                permission=getPermissionFromRole(self.params["role"]),
            )
            self.signUpFinished.emit(True, "Signup successful")
        except NanokoAPI400BadRequestError as e:
            self.signUpFinished.emit(False, e.response.json()["detail"])
        except Exception as e:
            self.operationFailed.emit("signup", str(e))

    def _handleLoadDashboardData(self):
        """Load all dashboard data"""
        try:
            overview_data = self.nanokoClient.service.get_overview()

            assignments = [
                (
                    assignment.name,
                    assignment.due_date.astimezone(
                        pytz.timezone("Pacific/Auckland")
                    ).strftime("%Y-%m-%d %H:%M"),
                )
                for assignment in overview_data.assignments
            ]

            performaces = overview_data.performances

            average_score = 0
            best_concept = ""
            best_concept_score = 0
            best_process = ""
            best_process_score = 0

            for concept in ConceptType:
                process_performances: ProcessPerformances = getattr(
                    performaces, concept.name.lower()
                )
                concept_score = (
                    process_performances.apply
                    + process_performances.formulate
                    + process_performances.explain
                ) / 3
                average_score += concept_score
                if concept_score > best_concept_score:
                    best_concept_score = concept_score
                    best_concept = concept.name

            average_score /= 7

            for process in ProcessType:
                for concept in ConceptType:
                    process_performances: ProcessPerformances = getattr(
                        performaces, concept.name.lower()
                    )
                    process_score = getattr(process_performances, process.name.lower())
                    if process_score > best_process_score:
                        best_process_score = process_score
                        best_process = process.name

            grades = {0: "Ⅰ", 1: "Ⅱ", 2: "Ⅲ", 3: "Ⅳ", 4: "Ⅴ"}

            stats = {
                "display_name": overview_data.display_name,
                "stats": {
                    "Total Question Answered": overview_data.total_question_number,
                    "Average Level": [
                        performance
                        for performance in Performance
                        if performance.value == average_score.__ceil__()
                    ][0]
                    .name.replace("_", " ")
                    .lower()
                    .capitalize(),
                    "Best Concept": best_concept.replace("_", " ").lower().capitalize(),
                    "Best Process": best_process.replace("_", " ").lower().capitalize(),
                },
                "level": int(average_score % 1 * 100),
                "grade": grades[average_score.__ceil__()],
            }

            matrix = [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]
            for concept in ConceptType:
                for process in ProcessType:
                    process_performances: ProcessPerformances = getattr(
                        performaces, concept.name.lower()
                    )
                    matrix[concept.value][process.value] = getattr(
                        process_performances, process.name.lower()
                    )

            dashboard_data = {
                "class_name": overview_data.class_name,
                "assignments": assignments,
                "stats": stats,
                "matrix": matrix,
                "display_name": overview_data.display_name,
            }

            self.dashboardDataLoaded.emit(dashboard_data)

        except NanokoAPI404NotFoundError:
            # user is not enrolled in any class
            self.dashboardDataLoaded.emit({"class_name": None})
        except Exception as e:
            self.operationFailed.emit("load_dashboard_data", str(e))

    def _handleLoadClassData(self):
        """Load class data for the class interface"""
        try:
            class_data = self.nanokoClient.user.get_class_data().model_dump()
            self.classDataLoaded.emit(class_data)
        except NanokoAPI404NotFoundError:
            self.classDataLoaded.emit({"class_name": None})
        except Exception as e:
            self.operationFailed.emit("load_class_data", str(e))

    def _handleLoadAssignmentData(self):
        """Load specific assignment data for the question answering interface"""
        try:
            assignment_id = self.params.get("assignment_id")

            assignments = self.nanokoClient.user.get_assignments()
            assignment_result = [
                assignment
                for assignment in assignments
                if assignment.id == assignment_id
            ]
            if len(assignment_result) == 0:
                self.operationFailed.emit(
                    "load_assignment_data", "Assignment not found"
                )
                return

            assignment = assignment_result[0]

            questions = self.nanokoClient.bank.get_questions(
                question_ids=assignment.question_ids
            )

            completed_sub_questions = (
                self.nanokoClient.user.get_completed_sub_questions(
                    assignment_id=assignment.id
                )
            )
            completed_sub_questions_dict = {
                sub_question.id: sub_question
                for sub_question in completed_sub_questions
            }

            assignment_data = {
                "id": assignment.id,
                "title": assignment.name,
                "description": assignment.description,
                "questions": [
                    {
                        "id": question.id,
                        "title": question.name,
                        "attribution": getAttribution(question.source),
                        "sub_questions": [
                            (
                                {
                                    "id": sub_question.id,
                                    "is_submitted": False,
                                    "type": "multiple_choice"
                                    if sub_question.options is not None
                                    else "text",
                                    "text": sub_question.description,
                                    "options": sub_question.options,
                                    "image": (
                                        self.nanokoClient.bank.get_image(
                                            sub_question.image_id
                                        )
                                        if sub_question.image_id
                                        else None
                                    ),
                                    "keywords": sub_question.keywords,
                                }
                            )
                            if sub_question.id not in completed_sub_questions_dict
                            else {
                                "id": sub_question.id,
                                "type": "multiple_choice"
                                if sub_question.options is not None
                                else "text",
                                "text": sub_question.description,
                                "options": sub_question.options,
                                "image": (
                                    self.nanokoClient.bank.get_image(
                                        sub_question.image_id
                                    )
                                    if sub_question.image_id
                                    else None
                                ),
                                "keywords": sub_question.keywords,
                                "is_submitted": True,
                                "user_answer": completed_sub_questions_dict[
                                    sub_question.id
                                ].submitted_answer,
                                "performance": completed_sub_questions_dict[
                                    sub_question.id
                                ]
                                .performance.name.replace("_", " ")
                                .lower()
                                .capitalize(),
                                "feedback": completed_sub_questions_dict[
                                    sub_question.id
                                ].feedback,
                            }
                            for sub_question in question.sub_questions
                        ],
                    }
                    for question in questions
                ],
            }

            self.questionAnsweringDataLoaded.emit(assignment_data)

        except Exception as e:
            self.operationFailed.emit("load_assignment_data", str(e))

    def _handleLoadAssignmentReviewData(self):
        """Load specific assignment data for review"""
        try:
            assignment_id = self.params.get("assignment_id")

            assignments = self.nanokoClient.user.get_assignments()
            assignment_result = [
                assignment
                for assignment in assignments
                if assignment.id == assignment_id
            ]
            if len(assignment_result) == 0:
                self.questionAnsweringDataLoaded.emit({"id": None})
                return

            assignment = assignment_result[0]

            questions = self.nanokoClient.bank.get_questions(
                question_ids=assignment.question_ids
            )

            completed_sub_questions = (
                self.nanokoClient.user.get_completed_sub_questions(
                    assignment_id=assignment.id
                )
            )
            completed_sub_questions_dict = {
                sub_question.id: sub_question
                for sub_question in completed_sub_questions
            }

            assignment_data = {
                "id": assignment.id,
                "title": assignment.name,
                "description": assignment.description,
                "questions": [
                    {
                        "id": question.id,
                        "title": question.name,
                        "attribution": getAttribution(question.source),
                        "sub_questions": [
                            {
                                "id": sub_question.id,
                                "type": "multiple_choice"
                                if sub_question.options is not None
                                else "text",
                                "text": sub_question.description,
                                "options": sub_question.options,
                                "image": (
                                    self.nanokoClient.bank.get_image(
                                        sub_question.image_id
                                    )
                                    if sub_question.image_id
                                    else None
                                ),
                                "keywords": sub_question.keywords,
                                "user_answer": completed_sub_questions_dict[
                                    sub_question.id
                                ].submitted_answer
                                if sub_question.options is None
                                else completed_sub_questions_dict[
                                    sub_question.id
                                ].submitted_answer.split("<OPTION>"),
                                "performance": completed_sub_questions_dict[
                                    sub_question.id
                                ]
                                .performance.name.replace("_", " ")
                                .lower()
                                .capitalize(),
                                "feedback": completed_sub_questions_dict[
                                    sub_question.id
                                ].feedback,
                            }
                            for sub_question in question.sub_questions
                        ],
                    }
                    for question in questions
                ],
            }

            self.assignmentReviewDataLoaded.emit(assignment_data)

        except Exception as e:
            self.operationFailed.emit("load_assignment_review_data", str(e))

    def _handleLoadQuestionReviewData(self):
        """Load specific question data for review"""
        try:
            question_id = self.params.get("question_id")

            question_data = self.nanokoClient.user.get_completed_question(question_id)
            question_json = {
                "id": question_data.id,
                "title": question_data.name,
                "questions": [
                    {
                        "id": question_data.id,
                        "title": question_data.name,
                        "attribution": getAttribution(question_data.source),
                        "sub_questions": [
                            {
                                "id": sub_question.id,
                                "type": "multiple_choice"
                                if sub_question.options is not None
                                else "text",
                                "text": sub_question.description,
                                "options": sub_question.options,
                                "image": (
                                    self.nanokoClient.bank.get_image(
                                        sub_question.image_id
                                    )
                                    if sub_question.image_id
                                    else None
                                ),
                                "keywords": sub_question.keywords,
                                "user_answer": sub_question.submitted_answer
                                if sub_question.options is None
                                else sub_question.submitted_answer.split("<OPTION>"),
                                "performance": sub_question.performance.name.replace(
                                    "_", " "
                                )
                                .lower()
                                .capitalize(),
                                "feedback": sub_question.feedback,
                            }
                            for sub_question in question_data.sub_questions
                        ],
                    }
                ],
            }

            self.questionReviewDataLoaded.emit(question_json)

        except Exception as e:
            self.operationFailed.emit("load_question_review_data", str(e))

    def _handleLoadQuestions(self):
        """Load question history and completed questions"""
        try:
            questions = self.nanokoClient.user.get_completed_questions()
            questions.sort(key=lambda x: x.id)

            questions_json = []
            for question in questions:
                questions_json.append(
                    {
                        "id": question.id,
                        "title": question.name,
                        "footer": getAttribution(question.source),
                        "sub_questions": [
                            {
                                "title": f"Question {chr(65 + idx)}",
                                "text": sub_question.description,
                                "image": (
                                    self.nanokoClient.bank.get_image(
                                        sub_question.image_id
                                    )
                                    if sub_question.image_id
                                    else None
                                ),
                                "tags": [
                                    (
                                        sub_question.concept.name.replace("_", " ")
                                        .lower()
                                        .capitalize(),
                                        "concept",
                                    ),
                                    (
                                        sub_question.process.name.replace("_", " ")
                                        .lower()
                                        .capitalize(),
                                        "process",
                                    ),
                                    (
                                        sub_question.performance.name.replace("_", " ")
                                        .lower()
                                        .capitalize(),
                                        "result",
                                    ),
                                ],
                            }
                            for idx, sub_question in enumerate(question.sub_questions)
                        ],
                    }
                )

            self.questionsLoaded.emit(questions_json)

        except Exception as e:
            self.operationFailed.emit("load_questions", str(e))

    def _handleSubmitSubQuestion(self):
        """Submit sub-question answer for instant feedback"""
        try:
            assignment_id = self.params.get("assignment_id")
            sub_question_id = self.params.get("sub_question_id")
            answer = self.params.get("answer")

            feedback = self.nanokoClient.user.submit(
                assignment_id=assignment_id,
                sub_question_id=sub_question_id,
                answer=answer if isinstance(answer, str) else "<OPTION>".join(answer),
            )

            self.subQuestionFeedbackReceived.emit(
                sub_question_id,
                {
                    "feedback": feedback.comment,
                    "performance": feedback.performance.name.replace("_", " ")
                    .lower()
                    .capitalize(),
                },
            )

        except Exception as e:
            self.operationFailed.emit("submit_sub_question", str(e))

    def _handleSendAIMessage(self):
        """Handle AI message sending and response"""
        try:
            user_message = self.params.get("message", "")
            sub_question_id = self.params.get("sub_question_id", 0)
            history = self.params.get("history", [])

            hint = self.nanokoClient.llm.get_hint(
                sub_question_id,
                user_message,
                [LLMMessage.model_validate(message) for message in history],
            )

            self.aiResponseReceived.emit(hint)

        except Exception as e:
            self.operationFailed.emit("send_ai_message", str(e))

    def _handleJoinClass(self):
        """Handle joining a class"""
        try:
            class_name = self.params.get("class_name", "")
            enter_code = self.params.get("enter_code", "")

            if class_name and enter_code:
                self.nanokoClient.user.join_class(class_name, enter_code)
                self.joinClassFinished.emit(
                    True, f"Successfully joined class '{class_name}'!"
                )
            else:
                self.joinClassFinished.emit(False, "Invalid class name or enter code.")

        except NanokoAPI403ForbiddenError:
            self.operationFailed.emit(
                "join_class", "You are already enrolled in this class."
            )
        except NanokoAPI404NotFoundError:
            self.operationFailed.emit("join_class", "Invalid class name or enter code.")
        except Exception as e:
            self.operationFailed.emit("join_class", str(e))

    # Teacher-specific mock data handlers
    def _handleLoadTeacherDashboardData(self):
        """Load teacher dashboard data"""
        print("[ApiWorker] _handleLoadTeacherDashboardData called")

        def _process_performance_data(performance_data):
            return {
                "dates": [
                    date.astimezone(pytz.timezone("Pacific/Auckland")).strftime("%m/%d")
                    for date in performance_data.dates
                ],
                "scores": [score for score in performance_data.performances],
            }

        try:
            overview = self.nanokoClient.service.get_teacher_overview()
            dashboard_data = {
                "classes": [
                    {
                        "id": class_.class_id,
                        "name": class_.name,
                        "student_count": class_.student_number,
                        "assignments": [
                            (
                                assignment.name,
                                assignment.due_date.astimezone(
                                    pytz.timezone("Pacific/Auckland")
                                ).strftime("%m/%d %H:%M"),
                            )
                            for assignment in class_.assignments
                        ],
                    }
                    for class_ in overview.classes
                ],
                "recent_assignments": [
                    {
                        "id": assignment.id,
                        "name": assignment.name,
                        "description": assignment.description,
                        "image": self.nanokoClient.user.get_assignment_image(
                            assignment.id
                        ),
                    }
                    for assignment in overview.assignments
                ],
                "students": [
                    {
                        "id": student.id,
                        "name": student.display_name,
                        "performance_data": _process_performance_data(
                            self.nanokoClient.service.get_performance_date_data(
                                user_id=student.id,
                                start_time=datetime.now(timezone.utc)
                                - timedelta(days=30),
                            )
                        ),
                    }
                    for student in overview.students
                ],
            }

            self.teacherDashboardDataLoaded.emit(dashboard_data)
            self.teacherClassesDataLoaded.emit(
                [
                    {
                        "id": class_.class_id,
                        "name": class_.name,
                        "student_count": class_.student_number,
                    }
                    for class_ in overview.classes
                ]
            )
        except NanokoAPI403ForbiddenError as e:
            self.operationFailed.emit(
                "load_teacher_dashboard_data",
                e.response.json()["detail"],
            )
        except Exception as e:
            self.operationFailed.emit("load_teacher_dashboard_data", str(e))

    def _handleLoadTeacherAssignmentsData(self):
        """Load teacher assignments data"""
        print("[ApiWorker] _handleLoadTeacherAssignmentsData called")
        try:
            assignments = self.nanokoClient.user.get_assignments()
            assignments_data = [
                {
                    "id": assignment.id,
                    "name": assignment.name,
                    "description": assignment.description,
                    "image": self.nanokoClient.user.get_assignment_image(assignment.id),
                }
                for assignment in assignments
            ]
            self.teacherAssignmentsDataLoaded.emit(assignments_data)
        except (NanokoAPI403ForbiddenError, NanokoAPI404NotFoundError) as e:
            self.operationFailed.emit(
                "load_teacher_assignments_data",
                e.response.json()["detail"],
            )
        except Exception as e:
            self.operationFailed.emit("load_teacher_assignments_data", str(e))

    def _handleLoadTeacherQuestionsData(self):
        """Load teacher questions data"""
        print("[ApiWorker] _handleLoadTeacherQuestionsData called")
        try:
            questions = self.nanokoClient.user.get_questions()
            questions_data = [
                {
                    "id": question.id,
                    "name": question.name,
                    "source": question.source,
                    "is_audited": question.is_audited,
                    "sub_questions_count": len(question.sub_questions),
                }
                for question in questions
            ]
            self.teacherQuestionsDataLoaded.emit(questions_data)
        except Exception as e:
            self.operationFailed.emit("load_teacher_questions_data", str(e))

    def _handleLoadTeacherClassData(self):
        """Load individual teacher class data"""
        try:
            class_id = self.params.get("class_id")

            class_data = self.nanokoClient.user.get_class_data(class_id)
            class_name = class_data.name
            class_code = class_data.enter_code
            students = class_data.students
            assignments = class_data.assignments
            performance_data = class_data.performances

            class_data = {
                "id": class_id,
                "name": class_name,
                "code": class_code,
                "students": [
                    {
                        "id": student.id,
                        "name": student.display_name,
                        "username": student.name,
                    }
                    for student in students
                ],
                "assignments": [
                    {
                        "id": assignment.id,
                        "name": assignment.name,
                        "description": assignment.description,
                        "status": "Assigned"
                        if datetime.now(pytz.timezone("Pacific/Auckland"))
                        < assignment.due_date.astimezone(
                            pytz.timezone("Pacific/Auckland")
                        )
                        else "Closed",
                        "due_date": datetimeToText(
                            assignment.due_date.astimezone(
                                pytz.timezone("Pacific/Auckland")
                            )
                        ),
                    }
                    for assignment in assignments
                ],
                "performance_data": performance_data.model_dump(),
            }

            print(f"[ApiWorker] class_data: {class_data}")
            self.teacherClassDataLoaded.emit(class_data)
        except (NanokoAPI400BadRequestError, NanokoAPI404NotFoundError) as e:
            self.operationFailed.emit(
                "load_teacher_class_data",
                e.response.json()["detail"],
            )
        except Exception as e:
            self.operationFailed.emit("load_teacher_class_data", str(e))

    def _handleLoadTeacherStudentStatistics(self):
        """Load teacher student statistics"""
        print(
            f"[ApiWorker] _handleLoadTeacherStudentStatistics called with params: {self.params}"
        )
        try:
            student_id = self.params.get("student_id")
            student_name = self.params.get("student_name")
            matrix_30_days = self.nanokoClient.service.get_recent_average_performances(
                user_id=student_id,
                start_time=datetime.now(timezone.utc) - timedelta(days=30),
            )
            matrix_all_time = self.nanokoClient.service.get_average_performances(
                user_id=student_id,
            )
            performance_chart_data = (
                self.nanokoClient.service.get_performance_date_data(
                    user_id=student_id,
                    start_time=datetime.now(timezone.utc) - timedelta(days=30),
                )
            )

            student_data = {
                "student_id": student_id,
                "student_name": student_name,
                "matrix_30_days": matrix_30_days.model_dump(),
                "matrix_all_time": matrix_all_time.model_dump(),
                "performance_chart_data": {
                    "dates": [
                        date.astimezone(pytz.timezone("Pacific/Auckland")).strftime(
                            "%m/%d"
                        )
                        for date in performance_chart_data.dates
                    ],
                    "scores": performance_chart_data.performances,
                },
            }
            self.teacherStudentStatisticsLoaded.emit(student_data)
        except Exception as e:
            self.operationFailed.emit("load_teacher_student_statistics", str(e))

    def _handleLoadAvailableAssignments(self):
        """Handle loading available assignments"""
        try:
            assignments = self.nanokoClient.user.get_assignments()
            available_assignments_data = [
                {
                    "id": assignment.id,
                    "name": assignment.name,
                    "description": assignment.description,
                }
                for assignment in assignments
            ]
            self.availableAssignmentsDataLoaded.emit(available_assignments_data)
        except (NanokoAPI403ForbiddenError, NanokoAPI404NotFoundError) as e:
            self.operationFailed.emit(
                "load_available_assignments",
                e.response.json()["detail"],
            )
        except Exception as e:
            self.operationFailed.emit("load_available_assignments", str(e))

    def _handleCreateAssignment(self):
        """Handle creating a new assignment"""
        try:
            name = self.params.get("name", "")
            description = self.params.get("description", "")
            question_ids = self.params.get("question_ids", [])

            if not name or not description:
                self.assignmentCreated.emit(
                    False, "Assignment name and description are required."
                )
                return

            if not question_ids:
                self.assignmentCreated.emit(False, "At least one question is required.")
                return

            assignment = self.nanokoClient.user.create_assignment(
                assignment_name=name,
                description=description,
                question_ids=question_ids,
            )
            self.assignmentCreated.emit(
                True, f"Assignment '{assignment.name}' created successfully!"
            )
        except (NanokoAPI403ForbiddenError, NanokoAPI404NotFoundError) as e:
            self.operationFailed.emit(
                "create_assignment",
                e.response.json()["detail"],
            )
        except Exception as e:
            self.operationFailed.emit("create_assignment", str(e))

    def _handleCreateClass(self):
        """Handle creating a new class"""
        try:
            class_name = self.params.get("class_name", "")
            enter_code = self.params.get("enter_code", "")

            if not class_name:
                self.classCreated.emit(False, "Class name is required.")
                return

            if not enter_code:
                self.classCreated.emit(False, "Enter code is required.")
                return

            class_ = self.nanokoClient.user.create_class(
                class_name=class_name, enter_code=enter_code
            )
            self.classCreated.emit(True, f"Class '{class_.name}' created successfully!")
        except (
            NanokoAPI400BadRequestError,
            NanokoAPI403ForbiddenError,
            NanokoAPI404NotFoundError,
        ) as e:
            self.operationFailed.emit("create_class", e.response.json()["detail"])
        except Exception as e:
            self.operationFailed.emit("create_class", str(e))

    def _handleCreateQuestion(self):
        """Handle creating a new question"""
        try:
            name = self.params.get("name", "")
            source = self.params.get("source", "")
            sub_questions_data = self.params.get("sub_questions_data", [])

            if not name or not sub_questions_data:
                self.questionCreated.emit(
                    False, "Question name and sub-questions are required."
                )
                return

            path_to_id = {}
            for sub_question in sub_questions_data:
                if sub_question["image_path"]:
                    image_hash = self.nanokoClient.bank.upload_image(
                        file=sub_question["image_path"],
                        content_type="image/png"
                        if sub_question["image_path"].endswith(".png")
                        else "image/jpeg",
                    )
                    image_id = self.nanokoClient.bank.add_image(
                        hash=image_hash,
                        description=sub_question["image_description"],
                    )
                    path_to_id[sub_question["image_path"]] = image_id

            question = Question(
                name=name,
                source=source,
                sub_questions=[
                    SubQuestion(
                        description=sub_question["description"],
                        answer=sub_question["answer"],
                        concept=ConceptType[textToEnumName(sub_question["concept"])],
                        process=ProcessType[textToEnumName(sub_question["process"])],
                        keywords=sub_question["keywords"],
                        options=sub_question["options"],
                        image_id=path_to_id[sub_question["image_path"]]
                        if sub_question["image_path"] is not None
                        else None,
                    )
                    for sub_question in sub_questions_data
                ],
            )
            self.nanokoClient.bank.add_question(question)
            self.questionCreated.emit(
                True,
                f"Question '{name}' created successfully with {len(sub_questions_data)} sub-questions!",
            )
        except (
            NanokoAPI403ForbiddenError,
            NanokoAPI404NotFoundError,
        ) as e:
            self.operationFailed.emit(
                "create_question",
                e.response.json()["detail"],
            )
        except Exception as e:
            print(traceback.format_exc())
            self.operationFailed.emit("create_question", str(e))

    def _handleLoadClassAssignmentReview(self):
        """Load class assignment review data for teachers"""
        try:
            assignment_id = self.params.get("assignment_id", 1)
            class_id = self.params.get("class_id")

            review_data = self.nanokoClient.user.get_assignment_review_data(
                class_id=class_id,
                assignment_id=assignment_id,
            )
            total_students = 0
            if (
                len(review_data.questions) > 0
                and len(review_data.questions[0].sub_questions) > 0
            ):
                total_students = len(
                    review_data.questions[0].sub_questions[0].student_performances
                )

            review_data = {
                "title": review_data.title,
                "class_id": class_id,
                "assignment_id": assignment_id,
                "total_students": total_students,
                "questions": [
                    {
                        "title": question.name,
                        "attribution": getAttribution(question.source),
                        "sub_questions": [
                            {
                                "id": sub_question.id,
                                "text": sub_question.description,
                                "answer": sub_question.answer,
                                "type": "multiple_choice"
                                if sub_question.options
                                else "text",
                                "options": sub_question.options,
                                "image": self.nanokoClient.bank.get_image(
                                    sub_question.image_id
                                )
                                if sub_question.image_id is not None
                                else None,
                                "student_performances": [
                                    {
                                        "user": student_performance.user.model_dump(),
                                        "answer": student_performance.answer
                                        if sub_question.options is None
                                        else (
                                            student_performance.answer.replace(
                                                "<OPTION>", ", "
                                            )
                                            if student_performance.answer is not None
                                            else None
                                        ),
                                        "performance": student_performance.performance,
                                        "feedback": student_performance.feedback,
                                        "date": student_performance,
                                    }
                                    for student_performance in sub_question.student_performances
                                ],
                            }
                            for sub_question in question.sub_questions
                        ],
                    }
                    for question in review_data.questions
                ],
            }
            self.classAssignmentReviewLoaded.emit(review_data)
        except (NanokoAPI403ForbiddenError, NanokoAPI404NotFoundError) as e:
            self.operationFailed.emit(
                "load_class_assignment_review",
                e.response.json()["detail"],
            )
        except Exception as e:
            self.operationFailed.emit("load_class_assignment_review", str(e))

    def _handleRemoveStudentFromClass(self):
        """Handle removing a student from a class"""
        print(
            f"[ApiWorker] _handleRemoveStudentFromClass called with params: {self.params}"
        )
        try:
            student_id = self.params.get("student_id", "")

            if not student_id:
                self.studentRemovedFromClass.emit(False, "Student id is required.")
                return

            self.nanokoClient.user.kick_student(student_id)
            self.studentRemovedFromClass.emit(True, "Student removed from class")
        except (
            NanokoAPI404NotFoundError,
            NanokoAPI403ForbiddenError,
        ) as e:
            self.operationFailed.emit(
                "remove_student_from_class", e.response.json()["detail"]
            )
            return
        except Exception as e:
            self.operationFailed.emit("remove_student_from_class", str(e))

    def _handleLoadAssignmentQuestions(self):
        """Handle loading assignment questions"""
        try:
            assignment_id = self.params.get("assignment_id")
            assignments = self.nanokoClient.user.get_assignments()
            assignment_result = [
                assignment
                for assignment in assignments
                if assignment.id == assignment_id
            ]
            if not assignment_result:
                self.operationFailed.emit(
                    "load_assignment_questions", "Assignment not found"
                )
            assignment = assignment_result[0]
            question_ids = assignment.question_ids
            questions = self.nanokoClient.bank.get_questions(question_ids)

            assignment_questions_data = {
                "title": assignment.name,
                "description": assignment.description,
                "questions": [
                    {
                        "id": question.id,
                        "title": question.name,
                        "attribution": getAttribution(question.source),
                        "sub_questions": [
                            {
                                "id": sub_question.id,
                                "type": "multiple_choice"
                                if sub_question.options
                                else "text",
                                "text": sub_question.description,
                                "answer": sub_question.answer,
                                "options": sub_question.options,
                                "image": self.nanokoClient.bank.get_image(
                                    sub_question.image_id
                                )
                                if sub_question.image_id is not None
                                else None,
                            }
                            for sub_question in question.sub_questions
                        ],
                    }
                    for question in questions
                ],
            }
            self.assignmentQuestionsDataLoaded.emit(assignment_questions_data)
        except (NanokoAPI403ForbiddenError, NanokoAPI404NotFoundError) as e:
            self.operationFailed.emit(
                "load_assignment_questions",
                e.response.json()["detail"],
            )
        except Exception as e:
            self.operationFailed.emit("load_assignment_questions", str(e))

    def _handleAssignAssignmentToClass(self):
        """Handle assigning an assignment to a class"""
        try:
            assignment_id = self.params.get("assignment_id")
            class_id = self.params.get("class_id")
            due_date = self.params.get("due_date")

            print(
                f"[ApiWorker] Mock: Assigning assignment {assignment_id} to class {class_id} with due date {due_date}"
            )

            try:
                self.nanokoClient.user.assign_assignment(
                    assignment_id=assignment_id,
                    class_id=class_id,
                    due_date=due_date,
                )
            except (
                NanokoAPI404NotFoundError,
                NanokoAPI403ForbiddenError,
                NanokoAPI400BadRequestError,
            ) as e:
                self.operationFailed.emit(
                    "assign_assignment_to_class",
                    e.response.json()["detail"],
                )
                return
            except Exception as e:
                self.operationFailed.emit("assign_assignment_to_class", str(e))
                return

            self.assignmentAssignmentResult.emit(
                True, "Assignment successfully assigned"
            )
        except Exception as e:
            self.operationFailed.emit("assign_assignment_to_class", str(e))

    def _handleLoadFilteredQuestions(self):
        """Handle loading filtered questions for selection"""
        print("[ApiWorker] _handleLoadFilteredQuestions called")
        try:
            search_text = self.params.get("search_text", "").lower()
            concept_filter = self.params.get("concept_filter", "")
            process_filter = self.params.get("process_filter", "")

            print(
                f"[ApiWorker] Filters - search: '{search_text}', concept: '{concept_filter}', process: '{process_filter}'"
            )

            concept = (
                None
                if concept_filter == "All Concepts"
                else ConceptType[textToEnumName(concept_filter)]
            )
            process = (
                None
                if process_filter == "All Processes"
                else ProcessType[textToEnumName(process_filter)]
            )

            questions = self.nanokoClient.bank.get_questions(
                keyword=search_text, concept=concept, process=process
            )

            questions_data = [
                {
                    "id": question.id,
                    "title": question.name,
                    "sub_questions": [
                        {
                            "id": sub_question.id,
                            "type": "multiple_choice"
                            if sub_question.options
                            else "text",
                            "text": sub_question.description,
                            "answer": sub_question.answer,
                            "options": sub_question.options,
                            "image": self.nanokoClient.bank.get_image(
                                sub_question.image_id
                            )
                            if sub_question.image_id is not None
                            else None,
                            "tags": [
                                (
                                    enumNameToText(sub_question.concept.name),
                                    "concept",
                                ),
                                (
                                    enumNameToText(sub_question.process.name),
                                    "process",
                                ),
                            ],
                        }
                        for sub_question in question.sub_questions
                    ],
                    "attribution": getAttribution(question.source),
                }
                for question in questions
            ]

            self.filteredQuestionsLoaded.emit(questions_data)

        except Exception as e:
            self.operationFailed.emit("load_filtered_questions", str(e))
