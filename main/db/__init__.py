import json
import os
from datetime import datetime, time, timedelta

from bson.objectid import ObjectId
from mongoengine import DateTimeField, DynamicDocument, Q, connect

from config import config_by_name

config = config_by_name[os.getenv("FLASK_ENV") or "dev"]
connect(host=config["DATABASE_URI"])


class BaseModel(DynamicDocument):
    created_at = DateTimeField(default=datetime.now)

    meta = {"abstract": True}

    def to_json(self, *args, **kwargs) -> dict:
        """
        To convert data into json.
        """
        data = self.to_mongo(*args, **kwargs)
        self._convert_objects_ids_and_date_to_strings(data)
        return json.loads(json.dumps(data))

    def _convert_objects_ids_and_date_to_strings(self, data: dict):
        """
        To convert object ids and date values to string.
        :param data:
        """
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, datetime):
                data[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, dict):
                self._convert_objects_ids_and_date_to_strings(value)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        self._convert_objects_ids_and_date_to_strings(item)
                    if isinstance(item, ObjectId):
                        value[index] = str(item)
                    if isinstance(item, datetime):
                        value[index] = item.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def create(cls, data: dict, to_json=False):
        """
        To create the record.
        :param data: Data to create the record
        :param to_json: Flag to get response in json
        :return: Created document
        """
        record = cls(**data)
        record.save(validate=False)
        if to_json:
            return record.to_json()
        return record

    def update(self, data: dict):
        """
        To update the record.
        :param data: Data to update the record
        """
        for k, v in data.items():
            setattr(self, k, v)
        self.save()

    def replace(self, data: dict):
        """
        To replace the record.
        :param data:
        """
        for field_name in self._fields_ordered:
            if field_name != "id" and field_name not in data:
                delattr(self, field_name)

        for k, v in data.items():
            setattr(self, k, v)

        self.save()

    @classmethod
    def delete(cls, **filters):
        """
        To delete object with id
        :return:
        :rtype:
        """
        cls.objects(**filters).delete()

    @classmethod
    def get_all(cls, to_json=False) -> list:
        """
        To get all records.
        :param to_json:
        :return:
        """
        return [(record.to_json() if to_json else record) for record in cls.objects()]

    @classmethod
    def get_objects_with_filter(cls, only_first=False, to_json=False, **filters) -> list or dict or "BaseModel":
        """
        To get objects with filter
        :param only_first:
        :param to_json:
        :param filters:
        :return:
        """
        filtered_records = cls.objects(**filters)
        if only_first:
            record = filtered_records.first()
            if record:
                return record.to_json() if to_json else record
            return None

        return [(record.to_json() if to_json else record) for record in filtered_records]

    @classmethod
    def get_distinct(cls, field: str) -> list:
        """
        To get distinct of a field.
        :param field:
        :return:
        """
        return cls.objects.distinct(field)

    @classmethod
    def get_distinct_with_filters(cls, field: str, **filters) -> list:
        """
        To get distinct of a with filters.
        :param field:
        :param filters:
        :return:
        """
        return cls.objects(**filters).distinct(field)

    @classmethod
    def get_objects_with_filter_or(cls, only_first=None, to_json=False, **filters) -> list or "BaseModel":
        """
        To get objects with filter using OR operator.
        :param only_first:
        :param to_json:
        :param filters: Multiple filter conditions with OR operator
        :return:
        """
        or_filters = [Q(**{field: value}) for field, value in filters.items()]

        if or_filters:
            combined_filter = or_filters.pop()
            for q in or_filters:
                combined_filter |= q

            filtered_records = cls.objects.filter(combined_filter)
        else:
            filtered_records = cls.objects()

        if only_first:
            record = filtered_records.first()
            return (record.to_json() if to_json and record else record) if record else None
        return [(record.to_json() if to_json else record) for record in filtered_records]

    @classmethod
    def get_objects_with_or_filter_multiple_values(
        cls,
        or_filters: dict,
        only_first=None,
        to_json=False,
        today_records: bool = False,
        order_by: str = None,
        **filters,
    ) -> list or "BaseModel":
        """
        To get the filtered objects on same key with multiple values.
        :param order_by:
        :type order_by:
        :param today_records:
        :type today_records:
        :param only_first:
        :type only_first:
        :param to_json:
        :type to_json:
        :param or_filters:  {key: [val, val2], key2: [val, val2]}
        :type or_filters:
        :return:
        :rtype:
        """
        if or_filters:
            or_filters = [Q(**{field: or_value}) for field, values in or_filters.items() for or_value in values]

        combined_filter = None

        if or_filters:
            combined_filter = or_filters.pop()
            for q in or_filters:
                combined_filter |= q

        if filters:
            additional_filter = Q(**filters)
            if combined_filter:
                combined_filter &= additional_filter
            else:
                combined_filter = additional_filter

        if today_records:
            date_filter = cls.get_time_range_filters(today=True)
            if combined_filter:
                combined_filter &= date_filter
            else:
                combined_filter = date_filter

        if combined_filter:
            filtered_records = cls.objects.filter(combined_filter)
        else:
            filtered_records = cls.objects()

        if order_by:
            filtered_records = filtered_records.order_by(order_by)
        if only_first:
            record = filtered_records.first()
            return (record.to_json() if to_json and record else record) if record else None
        return [(record.to_json() if to_json else record) for record in filtered_records]

    @staticmethod
    def get_time_range_filters(start_datetime: str = "", end_datetime: str = "", today: bool = False):
        """
        To create filters for a time range.
        :param start_datetime:
        :type start_datetime:
        :param end_datetime:
        :type end_datetime:
        :param today:
        :type today:
        :return:
        :rtype:
        """
        if today:
            start_of_day = datetime.combine(datetime.now().date(), time())
            end_of_day = start_of_day + timedelta(days=1)
            return Q(created_at__gte=start_of_day, created_at__lt=end_of_day)
