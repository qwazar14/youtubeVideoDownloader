import asyncio
from pytube import YouTube
from tqdm import tqdm


def grab_links(file_path):
    try:
        with open(file_path, 'r') as file:
            links = [line.strip() for line in file.readlines()]
        return links
    except FileNotFoundError:
        print(f"No such file: '{file_path}'")
        return []
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []


class VideoProcessor:
    def __init__(self, links_file_path, output_directory):
        self.links = grab_links(links_file_path)
        self.output_directory = output_directory

    def on_progress(self, stream, bytes_remaining):
        file_size = stream.filesize
        bytes_downloaded = file_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / file_size * 100
        self.pbar.update(percentage_of_completion - self.pbar.n)

    async def download_video(self, url, video_number, total_videos):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._download_video, url, video_number, total_videos)

    def _download_video(self, url, video_number, total_videos):
        try:
            yt = YouTube(url, on_progress_callback=self.on_progress)
            video_stream = yt.streams.get_highest_resolution()

            if video_stream is None:
                print(f"Cannot download {url}: No suitable stream found")
                return None

            print(f"\nDownloading video {video_number}/{total_videos}")
            print(f"Video Name: {yt.title}")
            print(f"Video URL: {url}")

            self.pbar = tqdm(total=100, unit='%', desc="Progress", ncols=100)
            video_stream.download(output_path=self.output_directory)
            self.pbar.close()
            print(f"Video downloaded to {self.output_directory}")
            return yt.title
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    async def process_videos(self):
        total_videos = len(self.links)
        for i, url in enumerate(self.links, start=1):
            await self.download_video(url, i, total_videos)


video_processor = VideoProcessor(links_file_path='path/to/links_file',
                                 output_directory='path/to/output_dir')

asyncio.run(video_processor.process_videos())
