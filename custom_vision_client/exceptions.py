from typing import Dict
from typing import Text
import pdb


class TrainingError(Exception):

    def __init__(self, status: Text, message: Text):
        self.Status = status
        self.message = message

    def __str__(self):
        return ' '.join(_ for _ in (self.status, self.message) if _)

    @classmethod
    def from_response(cls, response: Dict):
        if response['Code'] == 'BadRequestTrainingNotNeeded':
            status =  response['Code'] or response['statusCode']
            message = "Duplicate Image(s) uploaded. Training is not needed."
        return TrainingError(status=status, message=message)
