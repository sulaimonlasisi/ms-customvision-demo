import pdb
import os
from werkzeug.utils import secure_filename
from app import app
from collections import namedtuple
from functools import lru_cache
from typing import Text
from typing import Iterable
import json

from custom_vision_client.client import BaseClient
from custom_vision_client.exceptions import TrainingError
from custom_vision_client.models import AddImageResponse, Tag, Project, TrainingResponse, Iteration

TrainingConfig = namedtuple('TrainingConfig', [
    'region',
    'project_name',
    'training_key',
])

class TagDict(dict):
    def __missing__(self, key):
        return Tag(Description = '', Id = '', ImageCount = 0, Name = '')

class RespDict(dict):
    def __missing__(self, key):
        return TrainingResponse(Id = '', Name = '', Status = '', Created = '', LastModified = '', IsDefault = '', ProjectId = '')

class TrainingClient(BaseClient):
    _auth_keyname = 'Training-Key'

    def __init__(self, config: TrainingConfig):
        super().__init__(config.region, config.training_key)
        self._project_name = config.project_name

    #@lru_cache(maxsize=1)
    def _fetch_project_id(self) -> Text:
        for project in self._fetch_projects():
            if project.Name == self._project_name:                
                return project.Id
        return ''

    def _format_projects_endpoint(self) -> Text:
        return '{base}/customvision/v1.0/Training/projects'.format(
            base=self._format_api_base())

    def _format_project_endpoint(self) -> Text:
        return '{base}/{project_id}'.format(
            base=self._format_projects_endpoint(),
            project_id=self._fetch_project_id())

    def _format_tags_endpoint(self) -> Text:
        return '{base}/tags'.format(base=self._format_project_endpoint())

    def _format_tag_endpoint(self, tag_name: Text) -> Text:
        return '{base}?name={tag_name}'.format(
            base=self._format_tags_endpoint(),
            tag_name=tag_name)

    def _format_training_endpoint(self) -> Text:
        return '{base}/train'.format(base=self._format_project_endpoint())

    def _format_iterations_endpoint(self) -> Text:
        return '{base}/iterations'.format(base=self._format_project_endpoint())

    def _format_iteration_endpoint(self, Id) -> Text:
        return '{base}/{iteration_id}'.format(base=self._format_iterations_endpoint(),
            iteration_id = Id)

    def _format_image_url(self, tags: Iterable[Tag]) -> Text:
        return '{base}/images/image?tagIds={tagIds}'.format(
            base=self._format_project_endpoint(),
            tagIds='&tagIds='.join(tag.Id for tag in tags))

    def _fetch_projects(self) -> Iterable[Project]:
        url = self._format_projects_endpoint()
        response = self._get_json(url)
        return [Project(**_) for _ in response]

    def _fetch_iterations(self) -> Iterable[Iteration]:
        url = self._format_iterations_endpoint()
        response = self._get_json(url)
        iteration_array = []
        for _ in range(0,(len(response))):
            if response[_]['Status']!='New':
                iteration_array.append(Iteration(**response[_]))
        return iteration_array

    def _fetch_iteration_id(self) -> TrainingResponse:
        all_iteration = self._fetch_iterations()
        return all_iteration[len(all_iteration)-1].Id

    def _fetch_project_tags(self) -> Iterable[Tag]:
        url = self._format_tags_endpoint()
        response = self._get_json(url)
        return [Tag(**_) for _ in response['Tags']]

    def _fetch_tags_for_names(self, names: Iterable[Text]) -> Iterable[Tag]:
        all_tags = TagDict((tag.Name, tag) for tag in self._fetch_project_tags())
        return [all_tags[name] for name in names]
    
    def _fetch_tags_for_list_of_names(self, names: Iterable[Text]) -> Iterable[Tag]:
        all_tags = TagDict((tag.Name, tag) for tag in self._fetch_project_tags())
        return [all_tags[name[0]] for name in names]

    def _check_then_create_tags(self, input_tag_list):
        matching_tags = self._fetch_tags_for_names(input_tag_list)
        for tag in input_tag_list:
            if any(t.Name != tag for t in matching_tags):
                self._create_tag(tag)
        return self._fetch_project_tags()

    def _create_tag(self, tag_name: Text) -> Tag:
        url = self._format_tag_endpoint(tag_name)
        response = self._post_json(url)
        return Tag(**response)

    def _create_project(self, project_name: Text) -> Project:
        self._project_name = project_name
        url = '{base}/?name={project_name}'.format(
            base=self._format_projects_endpoint(),
            project_name=self._project_name)
        response = self._post_json(url)
        return Project(**response)

    def trigger_training(self) -> TrainingResponse:
        url = self._format_training_endpoint()
        response = self._post_json(url, headers=[('Content-Length', '0')])
        try:
            return TrainingResponse(**response)
        except TypeError:
            return TrainingError.from_response(response)

    def _add_training_image(self, image_path: Text, *tag_names: Text):
        url = self._format_image_url(self._fetch_tags_for_list_of_names(tag_names))
        image_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'].split("/")[1], image_path)
        with open( image_path, 'rb') as fobj:
            response = self._post_json(url, files=self._format_file(fobj))
        return AddImageResponse(**response)

    def update_iteration (self, iteration_object):
        url = self._format_iteration_endpoint(iteration_object['Id'])
        response = self._patch_json(url, iteration_object, headers=[('Content-Length', '0')])
        try:
            return TrainingResponse(**response)
        except TypeError:
            raise TrainingError.from_response(response)
