"""
Expectation for all OutlineProcessors are:

* something to do a one-time load of data for an entire course
* a method to call to emit a list of usage_keys to hide
* a method to call to add any data that is relevant to this system.

# Processors that we need:

Attributes that apply to both Sections and Sequences
* start
* .hide_from_toc

Might make sense to put this whole thing as a "private" module in an api package,
with the understanding that it's not part of the external contract yet.


"""
import logging
from collections import defaultdict
from datetime import datetime

from django.contrib.auth import get_user_model
from edx_when.api import get_dates_for_course
from opaque_keys.edx.keys import CourseKey, UsageKey

from .data import ScheduleData, ScheduleItemData


User = get_user_model()
log = logging.getLogger(__name__)


class OutlineProcessor:
    """

    """
    def __init__(self, course_key: CourseKey, user: User, at_time: datetime):
        """
        Basic initialization.

        Extend to set your own data attributes, but don't do any real work (e.g.
        database access, expensive computation) here.
        """
        self.course_key = course_key
        self.user = user
        self.at_time = at_time

    def load_data(self):
        """
        Fetch whatever data you need about the course and user here.

        DO NOT USE MODULESTORE OR BLOCKSTRUCTURES HERE, as the up-front
        performance penalties of those modules are the entire reason this app
        exists.
        """
        raise NotImplementedError()

    def usage_keys_to_hide(self, full_course_outline):
        """
        Return a set/frozenset of UsageKeys to hide.
        """
        raise NotImplementedError()

    def data_to_add(self, updated_course_outline):
        """
        Return the data we want to add to this CourseOutlineData.

        Unlike `usage_keys_to_hide`, this method gets a CourseOutlineData
        that only has those LearningSequences that a user has permission to
        access. We can use this to make sure that we're not returning data about
        LearningSequences that the user can't see because it was hidden by a
        different OutlineProcessor.
        """
        raise NotImplementedError


class ScheduleOutlineProcessor(OutlineProcessor):

    def __init__(self, course_key: CourseKey, user: User, at_time: datetime):
        super().__init__(course_key, user, at_time)
        self.dates = None
        self.keys_to_schedule_fields = defaultdict(dict)

    def load_data(self):
        # (usage_key, 'due'): datetime.datetime(2019, 12, 11, 15, 0, tzinfo=<UTC>)
        self.dates = get_dates_for_course(self.course_key, self.user)
        for (usage_key, field_name), date in self.dates.items():
            self.keys_to_schedule_fields[usage_key][field_name] = date

    def usage_keys_to_hide(self, full_course_outline):
        """
        Each
        """
        # Return a set/frozenset of usage keys to hide
        pass

    def data_to_add(self, updated_course_outline):
        return ScheduleData(sequences={
            usage_key: ScheduleItemData(
                usage_key=usage_key,
                start=fields.get('start'),
                due=fields.get('due'),
            )
            for usage_key, fields in self.keys_to_schedule_fields.items()
            if usage_key in updated_course_outline.sequences
        })

    #def disable_set(self, course_outline):
    #    # ???
    #   pass


class VisiblityOutlineProcessor:
    pass



def process():
    # These are processors that alter which sequences are visible to students.
    # For instance, certain sequences that are intentionally hidden or not yet
    # released. These do not need to be run for staff users.
    visibility_processors = [

        ScheduleOutlineProcessor(),
    ]

    # Phase 1:
    sequence_keys_to_hide = set()
    for processor in processors:
        sequence_keys_to_hide.update(processor.sequence_keys_to_hide())

    # What is the desired behavior if you have a Chapter with no sequences?
    # I guess we keep it?
    outline_with_hidden_stuff = hide_sequences

    for processor in processors:
        pass