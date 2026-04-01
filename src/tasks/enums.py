from enum import Enum

class TaskStatus(Enum):
    TODO = "To-Do"
    PROGRESS = "In Progress"
    DONE = "Done"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = 'medium'
    HIGH = "high"