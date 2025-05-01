import os
import googleapiclient.discovery
import pandas as pd
import s3fs 
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

def process_comments(response_items):
    comments = []
    for comment in response_items:
        author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
        comment_text = comment['snippet']['topLevelComment']['snippet']['textOriginal']
        publish_time = comment['snippet']['topLevelComment']['snippet']['publishedAt']
        comment_info = {
            'author': author,
            'comment': comment_text,
            'published_at': publish_time
        }
        comments.append(comment_info)
    return comments

def main():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = api_key
    video_id = "F_v_Qj6watw"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)

    comments_list = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id
    )
    response = request.execute()
    comments_list.extend(process_comments(response['items']))

    while response.get('nextPageToken'):
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        comments_list.extend(process_comments(response['items']))

    print(f'Finished processing {len(comments_list)} comments.')
    df=pd.DataFrame(comments_list)
    df.to_csv("s3://non-airflow-youtube/TMD_comment_data.csv")

if __name__ == "__main__":
    main()
