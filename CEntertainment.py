import os

from ImageCloud import ImageCloud
from Scrapy import Scrapy
from .Driver.MongoDB import MongoDB

MANGA_NOT_CACHED = 0
MANGA_COVER_DOWNLOADING = 1
MANGA_COVER_DOWNLOADED = 2


class CEntertainment:
    def __init__(self, username, password, host, port=27017, db_driver="MongoDB"):
        if db_driver is "MongoDB":
            self.client = MongoDB(username, password, host, port)
        self.db = self.client.centertainment
        self.image_cloud = ImageCloud(username, password, host, port)
        self.scrapy = Scrapy(username, password, host, port)

    def add_manga_resource(self, source, source_id, resource_info=None):
        if resource_info is None:
            resource_info = dict()
        resource = dict()
        resource["source"] = source
        resource["source_id"] = source_id
        resource.update(resource_info)

        self.__add_resource("manga_resource", resource)

    def download_manga_cover(self, success):
        for item in self.__get_null_cover("manga_resource"):
            self.__set_resource_status("manga_resource", {"_id": item['_id']}, MANGA_COVER_DOWNLOADING)
            nhentai_item = list(self.scrapy.find("nhentai", {"_id": item["source_id"]}))[0]
            self.image_cloud.add_task(nhentai_item['thumb_urls'][:3], item['thumb_id'], "Manga" + os.path.sep + "18R")
        self.image_cloud.start(success)

    def change_manga_resource_status(self, query, status):
        self.__set_resource_status("manga_resource", query, status)

    def __add_resource(self, collection, resource):
        self.db.get_collection(collection).save(resource)

    def __get_null_cover(self, collection):
        return self.db.get_collection(collection).find({"status": MANGA_NOT_CACHED})

    def __set_resource_status(self, collection, query, status):
        return self.db.get_collection(collection).find_and_modify(query, {'$set': {'status': status}})
