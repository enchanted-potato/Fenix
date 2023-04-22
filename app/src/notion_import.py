import requests
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin


class NotionClient:
    def __init__(self, notion_key):
        self.notion_key = notion_key
        self.default_headers = {
            "Authorization": f"Bearer {self.notion_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)
        self.NOTION_BASE_URL = "https://api.notion.com/v1/"

    def query_database(
        self, db_id, filter_object=None, sorts=None, start_cursor=None, page_size=None
    ):
        db_url = urljoin(self.NOTION_BASE_URL, f"databases/{db_id}/query")
        params = {}
        if filter_object is not None:
            params["filter"] = filter_object
        if sorts is not None:
            params["sorts"] = sorts
        if start_cursor is not None:
            params["start_cursor"] = start_cursor
        if page_size is not None:
            params["page_size"] = page_size

        return self.session.post(db_url, json=params, headers=self.default_headers)


class PandasConverter:
    text_types = ["rich_text", "title", "text"]

    def response_to_records(self, db_response):
        records = []
        for result in db_response["results"]:
            records.append(self.get_record(result))
        return records

    def get_record(self, result):
        record = {}
        for name in result["properties"]:
            if self.is_supported(result["properties"][name]):
                record[name] = self.get_property_value(result["properties"][name])

        return record

    def is_supported(self, prop):
        if prop.get("type") in [
            "checkbox",
            "date",
            "number",
            "rich_text",
            "title",
            "status",
            "multi_select",
            "people",
        ]:
            return True
        else:
            return False

    def get_property_value(self, prop):
        prop_type = prop.get("type")
        if prop_type in self.text_types:
            return self.get_text(prop)
        elif prop_type == "date":
            return self.get_date(prop)
        elif prop_type == "multi_select":
            return self.get_multi_select(prop)
        elif prop_type == "status":
            return self.get_status(prop)
        elif prop_type == "people":
            return self.get_people(prop)
        else:
            return prop.get(prop_type)

    def get_multi_select(self, text_object):
        text = ""
        ms_type = text_object.get("type")
        for rt in text_object.get(ms_type):
            text += rt.get("name")
        return text

    def get_people(self, text_object):
        people_list = []
        people_type = text_object.get("type")
        for rt in text_object.get(people_type):
            people_list.append(rt.get("id"))
        return people_list

    def get_status(self, text_object):
        status_type = text_object.get("type")
        text = text_object[status_type]["name"]
        return text

    def get_text(self, text_object):
        text = ""
        text_type = text_object.get("type")
        for rt in text_object.get(text_type):
            text += rt.get("plain_text")
        return text

    def get_date(self, date_object):
        date_value = date_object.get("date")
        if date_value is not None:
            if date_value.get("end") is None:
                return date_value.get("start")
            else:
                start = datetime.fromisoformat(date_value.get("start"))
                end = datetime.fromisoformat(date_value.get("end"))
                return end - start
        return None


class PandasLoader:
    def __init__(self, notion_client, pandas_converter):
        self.notion_client = notion_client
        self.converter = pandas_converter

    def load_db(self, db_id):
        page_count = 1
        print(f"Loading page {page_count}")
        db_response = self.notion_client.query_database(db_id)
        records = []
        if db_response.ok:
            db_response_obj = db_response.json()
            records.extend(self.converter.response_to_records(db_response_obj))

            while db_response_obj.get("has_more"):
                page_count += 1
                print(f"Loading page {page_count}")
                start_cursor = db_response_obj.get("next_cursor")
                db_response = self.notion_client.query_database(
                    db_id, start_cursor=start_cursor
                )
                if db_response.ok:
                    db_response_obj = db_response.json()
                    records.extend(self.converter.response_to_records(db_response_obj))
        return pd.DataFrame(records)
