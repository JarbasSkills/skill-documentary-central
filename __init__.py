from os.path import join, dirname
import random

from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_utils.log import LOG
from ovos_utils.parse import fuzzy_match
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search, ocp_featured_media
from youtube_archivist import YoutubeMonitor


class DocumentaryCentralSkill(OVOSCommonPlaybackSkill):

    def __init__(self):
        super().__init__("DocumentaryCentral")
        self.supported_media = [MediaType.DOCUMENTARY, MediaType.GENERIC]
        self.skill_icon = join(dirname(__file__), "ui", "documentarycentral_icon.jpg")
        self.archive = YoutubeMonitor(db_name="DocumentaryCentral",
                                      min_duration=30 * 60,
                                      logger=LOG,
                                      blacklisted_kwords=["trailer", "teaser", "documentary scene",
                                                          "documentary clip", "behind the scenes",
                                                          "documentary analysis",
                                                          "Documentary Preview", "soundtrack", " OST",
                                                          "opening theme"])

    def initialize(self):
        bootstrap = "https://github.com/JarbasSkills/skill-documentary-central/raw/dev/bootstrap.json"
        self.archive.bootstrap_from_url(bootstrap)
        self.schedule_event(self._sync_db, random.randint(3600, 24 * 3600))

    def _sync_db(self):
        url = "https://www.youtube.com/channel/UCp4wHZCrDhITkiUILOd4gRw"
        self.archive.parse_videos(url)
        self.schedule_event(self._sync_db, random.randint(3600, 24*3600))

    # matching
    def match_skill(self, phrase, media_type):
        score = 0
        if self.voc_match(phrase, "documentary") or media_type == MediaType.DOCUMENTARY:
            score += 15
        if self.voc_match(phrase, "central"):
            score += 10
        return score

    def normalize_title(self, title):
        title = title.lower().strip()
        title = self.remove_voc(title, "documentary")
        title = self.remove_voc(title, "central")
        title = title.replace("|", "").replace('"', "") \
            .replace(':', "").replace('”', "").replace('“', "") \
            .strip()
        return " ".join(
            [w for w in title.split(" ") if w])  # remove extra spaces

    def calc_score(self, phrase, match, base_score=0):
        score = base_score
        score += 100 * fuzzy_match(phrase.lower(), match["title"].lower())
        return min(100, score)

    def get_playlist(self, score=50, num_entries=250):
        pl = self.featured_media()[:num_entries]
        return {
            "match_confidence": score,
            "media_type": MediaType.DOCUMENTARY,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "title": "Documentary Central (Documentary Playlist)",
            "author": "Documentary Central"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = self.match_skill(phrase, media_type)
        if self.voc_match(phrase, "documentarycentral"):
            yield self.get_playlist(base_score)
        if media_type == MediaType.DOCUMENTARY:
            # only search db if user explicitly requested documentarys
            phrase = self.normalize_title(phrase)
            for url, video in self.archive.db.items():
                yield {
                    "title": video["title"],
                    "author": "Documentary Central",
                    "match_confidence": self.calc_score(phrase, video, base_score),
                    "media_type": MediaType.DOCUMENTARY,
                    "uri": "youtube//" + url,
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"]
                }

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "title": video["title"],
            "image": video["thumbnail"],
            "match_confidence": 70,
            "media_type": MediaType.DOCUMENTARY,
            "uri": "youtube//" + video["url"],
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "bg_image": video["thumbnail"],
            "skill_id": self.skill_id
        } for video in self.archive.sorted_entries()]


def create_skill():
    return DocumentaryCentralSkill()
