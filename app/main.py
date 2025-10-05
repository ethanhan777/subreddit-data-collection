import os
import praw
import pandas as pd
from datetime import datetime
import json

class RedditDataCollector:
    """
    Flexible Reddit data collection tool for research purposes.
    Easily configurable for different keywords, subreddits, and time ranges.
    """
    
    def __init__(self, client_id, client_secret, user_agent):
        """Initialize Reddit API connection"""
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "reddit-docker-app")
        )
        
    def search_posts(self, subreddits, keywords, start_date=None, end_date=None, 
                     limit=100, sort='relevance', time_filter='all'):
        """
        Search Reddit posts across multiple subreddits and keywords
        
        Parameters:
        -----------
        subreddits : list
            List of subreddit names (without r/)
        keywords : list
            List of search keywords/phrases
        start_date : datetime, optional
            Filter posts after this date
        end_date : datetime, optional
            Filter posts before this date
        limit : int
            Maximum posts per keyword per subreddit
        sort : str
            Sort method: 'relevance', 'hot', 'top', 'new', 'comments'
        time_filter : str
            Time filter: 'all', 'day', 'hour', 'month', 'week', 'year'
        
        Returns:
        --------
        DataFrame with collected posts
        """
        all_results = []
        
        for subreddit_name in subreddits:
            print(f"\nSearching r/{subreddit_name}...")
            
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                for keyword in keywords:
                    print(f"  Keyword: '{keyword}'")
                    
                    # Search subreddit
                    for submission in subreddit.search(
                        keyword, 
                        limit=limit, 
                        sort=sort, 
                        time_filter=time_filter
                    ):
                        post_date = datetime.fromtimestamp(submission.created_utc)
                        
                        # Apply date filters if specified
                        if start_date and post_date < start_date:
                            continue
                        if end_date and post_date > end_date:
                            continue
                        
                        all_results.append({
                            'subreddit': subreddit_name,
                            'search_keyword': keyword,
                            'post_id': submission.id,
                            'title': submission.title,
                            'author': str(submission.author),
                            'created_utc': post_date,
                            'score': submission.score,
                            'upvote_ratio': submission.upvote_ratio,
                            'num_comments': submission.num_comments,
                            'url': submission.url,
                            'selftext': submission.selftext,
                            'link_flair_text': submission.link_flair_text,
                            'is_self': submission.is_self,
                            'permalink': f"https://reddit.com{submission.permalink}"
                        })
                        
            except Exception as e:
                print(f"  Error in r/{subreddit_name}: {e}")
                continue
        
        df = pd.DataFrame(all_results)
        
        # Remove duplicate posts (found with multiple keywords)
        if len(df) > 0:
            df = df.drop_duplicates(subset=['post_id'], keep='first')
            print(f"\nTotal unique posts collected: {len(df)}")
        
        return df
    
    def get_comments(self, post_ids, top_level_only=True, limit=None):
        """
        Retrieve comments from specified posts
        
        Parameters:
        -----------
        post_ids : list
            List of Reddit post IDs
        top_level_only : bool
            If True, only collect top-level comments (no replies)
        limit : int, optional
            Maximum comments per post (None = all)
        
        Returns:
        --------
        DataFrame with collected comments
        """
        all_comments = []
        
        for idx, post_id in enumerate(post_ids):
            print(f"Collecting comments from post {idx+1}/{len(post_ids)}")
            
            try:
                submission = self.reddit.submission(id=post_id)
                submission.comments.replace_more(limit=0)
                
                if top_level_only:
                    comments = submission.comments
                else:
                    comments = submission.comments.list()
                
                for comment in comments:
                    if isinstance(comment, praw.models.Comment):
                        all_comments.append({
                            'post_id': post_id,
                            'comment_id': comment.id,
                            'author': str(comment.author),
                            'body': comment.body,
                            'score': comment.score,
                            'created_utc': datetime.fromtimestamp(comment.created_utc),
                            'is_submitter': comment.is_submitter,
                            'permalink': f"https://reddit.com{comment.permalink}"
                        })
                        
                        if limit and len(all_comments) >= limit:
                            break
                            
            except Exception as e:
                print(f"  Error collecting comments from {post_id}: {e}")
                continue
        
        return pd.DataFrame(all_comments)
    
    def save_data(self, posts_df, comments_df=None, output_prefix='reddit_data'):
        """Save collected data to CSV files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        posts_filename = f"{output_prefix}_posts_{timestamp}.csv"
        posts_df.to_csv(posts_filename, index=False)
        print(f"\nPosts saved to: {posts_filename}")
        
        if comments_df is not None and len(comments_df) > 0:
            comments_filename = f"{output_prefix}_comments_{timestamp}.csv"
            comments_df.to_csv(comments_filename, index=False)
            print(f"Comments saved to: {comments_filename}")
        
        return posts_filename


# ============================================================
# CONFIGURATION SECTION - MODIFY THIS FOR EACH STUDY
# ============================================================

def main():
    """Main execution function - configure parameters here"""
    
    # API Credentials
    CONFIG = {
        'client_id': os.getenv("REDDIT_CLIENT_ID"),
        'client_secret': os.getenv("REDDIT_CLIENT_SECRET"),
        'user_agent': os.getenv("REDDIT_USER_AGENT", "reddit-docker-app")
    }
    
    # Study Parameters - MODIFY THESE FOR EACH PROJECT
    STUDY_CONFIG = {
        # Target subreddits (without r/)
        'subreddits': [
            'Replika',
            'MyBoyfriendIsAI', 
            'CharacterAI',
            'ChatGPT',
            'singularity'
        ],
        
        # Search keywords
        'keywords': [
            'AI boyfriend',
            'AI girlfriend',
            'AI partner',
            'lobotomized',
            'nerfed',
            'personality shift',
            'GPT-5',
            'model update'
        ],
        
        # Date range (set to None for no filtering)
        'start_date': datetime(2025, 8, 1),
        'end_date': datetime(2025, 9, 30),
        
        # Search parameters
        'limit': 100,  # Posts per keyword per subreddit
        'sort': 'relevance',  # 'relevance', 'hot', 'top', 'new', 'comments'
        'time_filter': 'all',  # 'all', 'year', 'month', 'week', 'day', 'hour'
        
        # Comment collection
        'collect_comments': True,
        'top_level_only': True,
        
        # Output
        'output_prefix': 'ai_boyfriend_study'
    }
    
    # Initialize collector
    collector = RedditDataCollector(
        client_id=CONFIG['client_id'],
        client_secret=CONFIG['client_secret'],
        user_agent=CONFIG['user_agent']
    )
    
    # Collect posts
    print("=== Starting Data Collection ===\n")
    posts_df = collector.search_posts(
        subreddits=STUDY_CONFIG['subreddits'],
        keywords=STUDY_CONFIG['keywords'],
        start_date=STUDY_CONFIG['start_date'],
        end_date=STUDY_CONFIG['end_date'],
        limit=STUDY_CONFIG['limit'],
        sort=STUDY_CONFIG['sort'],
        time_filter=STUDY_CONFIG['time_filter']
    )
    
    # Collect comments if requested
    comments_df = None
    if STUDY_CONFIG['collect_comments'] and len(posts_df) > 0:
        print("\n=== Collecting Comments ===\n")
        comments_df = collector.get_comments(
            post_ids=posts_df['post_id'].tolist(),
            top_level_only=STUDY_CONFIG['top_level_only']
        )
    
    # Save data
    print("\n=== Saving Data ===")
    collector.save_data(
        posts_df=posts_df,
        comments_df=comments_df,
        output_prefix=STUDY_CONFIG['output_prefix']
    )
    
    # Display summary
    print(f"\n=== Collection Summary ===")
    print(f"Total posts: {len(posts_df)}")
    if comments_df is not None:
        print(f"Total comments: {len(comments_df)}")
    print("\nCollection complete!")


if __name__ == "__main__":
    main()