"""
Expose the public API to manage camunda external tasks.
"""

from bptl.utils.constants import Statuses
from bptl.utils.decorators import save_and_log

from .models import ExternalTask
from .utils import complete_task

__all__ = [
    "TaskNotPerformed",
    "complete",
]


class TaskNotPerformed(Exception):
    pass


@save_and_log(status=Statuses.completed)
def complete(task: ExternalTask):
    """
    Send the result of a fetched task into Camunda.

    :param task: A :class:`ExternalTask` instance, that has been already performed.
    :raises: :class:`TaskNotPerformed` if the task status is not "performed", this exception is
      raised.
    """
    if task.status != Statuses.performed:
        raise TaskNotPerformed(
            f"The task {task} is {task.status}. The task should be performed before sending results"
        )

    complete_task(task, variables=task.result_variables)
