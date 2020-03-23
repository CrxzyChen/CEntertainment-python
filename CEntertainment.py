import os

from ImageCloud import ImageCloud, IMAGE_NOT_CACHED, IMAGE_COVER_DOWNLOADING
from Scrapy import Scrapy
from .Driver.MongoDB import MongoDB


class CEntertainment:
    def __init__(self, username, password, host, port=27017, db_driver="MongoDB"):
        if db_driver is "MongoDB":
            self.client = MongoDB(username, password, host, port)
        self.db = self.client.centertainment
        self.image_cloud = ImageCloud(username, password, host, 27018)
        self.scrapy = Scrapy(username, password, host, port)

    def insert_manga_resource(self, source, source_id, thumb_id, info):
        resource = dict()
        resource["source"] = source
        resource["source_id"] = source_id
        resource["thumb_id"] = thumb_id
        resource["tags"] = info["tags"]
        resource["languages"] = info["languages"]
        resource["artists"] = info["artists"]
        resource["name"] = info["original_name"] if info["original_name"] is not None else info["name"]
        resource["page_count"] = info["page"]
        self.db.manga_resource.save(resource)

    def change_manga_resource_status(self, query, status):
        self.__set_resource_status("manga_resource", query, status)

    def __set_resource_status(self, collection, query, status):
        return self.image_cloud.db.get_collection(collection).find_and_modify(query, {'$set': {'status': status}})
