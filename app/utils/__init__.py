import pytz
from typing import Tuple
from datetime import datetime
from PyQt6.QtGui import QColor
from nanoko.models.user import Permission


def getPermissionFromRole(role: str) -> Permission:
    """Get permission from role in GUI

    Args:
        role (str): Role in GUI

    Raises:
        ValueError: Invalid role

    Returns:
        Permission: Permission from role
    """
    match role:
        case "Student":
            return Permission.STUDENT
        case "Teacher":
            return Permission.TEACHER
        case _:
            raise ValueError(f"Invalid role: {role}")


def enumNameToText(name: str) -> str:
    """Convert enum name to text

    Args:
        name (str): Enum name

    Returns:
        str: Text
    """
    return name.replace("_", " ").lower().capitalize()


def textToEnumName(text: str) -> str:
    """Convert text to enum name

    Args:
        text (str): Text

    Returns:
        str: Enum name
    """
    return text.replace(" ", "_").upper()


def getAttribution(source: str) -> str:
    """Get attribution for a source

    Args:
        source (str): The source of the question

    Returns:
        str: Question attribution to display
    """
    match source:
        case "nzqa":
            return "This question is sourced from past NCEA Numeracy papers published by the New Zealand Qualifications Authority (NZQA). Licensed under <a href='https://creativecommons.org/licenses/by/3.0/nz/' style='color: #007ACC;'>Creative Commons Attribution 3.0 New Zealand</a>."
        case _:
            return ""


def levelToColor(level: str) -> Tuple[QColor, QColor]:
    """Get color for a performance level

    Args:
        level (str): Level

    Returns:
        Tuple[QColor, QColor]: Light theme color, Dark theme color
    """

    levelLower = level.lower()

    if levelLower == "not_started":
        return QColor("#A1887F"), QColor("#D7CCC8")
    elif levelLower == "attempted":
        return QColor("#FFAB91"), QColor("#FF8A65")
    elif levelLower == "familiar":
        return QColor("#FF9800"), QColor("#FFB74D")
    elif levelLower == "proficient":
        return QColor("#E53935"), QColor("#EF5350")
    elif levelLower == "mastered":
        return QColor("#8E24AA"), QColor("#AB47BC")
    else:
        return QColor("#000000"), QColor("#000000")


def datetimeToText(datetime: datetime) -> str:
    """Convert datetime to text

    Args:
        datetime (datetime): Datetime

    Returns:
        str: Text
    """
    if datetime.tzinfo is None:
        datetime = datetime.replace(tzinfo=pytz.timezone("Pacific/Auckland"))
    if datetime.year == datetime.now(pytz.timezone("Pacific/Auckland")).year:
        return datetime.strftime("%m/%d %H:%M")
    else:
        return datetime.strftime("%Y/%m/%d %H:%M")
