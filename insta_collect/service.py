from insta_collect.scraper import scrape_hashtag
from insta_collect.saver import save_data
import datetime


class InstaCollectService:

    @staticmethod
    def collect(
        tag: str,
        limit: int = 10,
        profile_dir: str = "ig_profile",
        auto_save: bool = True,
        filename: str | None = None
    ):
        """
        Core orchestration layer
        Tidak tahu siapa pemanggilnya (CLI/API/etc)
        """

        # 1. Scrape
        data = scrape_hashtag(
            hashtag=tag,
            limit=limit,
            profile_dir=profile_dir
        )

        # 2. Optional save
        saved_files = None
        if auto_save and data:
            if not filename:
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"result_{tag}_{ts}"

            save_data(data, filename=filename)

            saved_files = {
                "json": f"{filename}.json",
                "csv": f"{filename}.csv"
            }

        # 3. Response standar
        return {
            "meta": {
                "tag": tag,
                "limit": limit,
                "collected": len(data),
                "timestamp": datetime.datetime.now().isoformat()
            },
            "data": data,
            "files": saved_files
        }



