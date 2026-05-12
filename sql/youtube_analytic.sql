-- Total channel-level performance
with base as (
	select *,
	CURRENT_DATE - channel_created_date as channel_age_days
	from channels
),
kpis as (
	select
	channel_name,
	country,
	subscriber_count,
	total_views,
	video_count,
	channel_age_days,
	ROUND(total_views/NULLIF(subscriber_count,0),2)as views_per_subscriber,
	ROUND(total_views/NULLIF(video_count,0),0)as avg_views_per_video,
	ROUND(total_views/NULLIF(channel_age_days,0),0)as avg_channel_age_days
	from base
)
select *,
	RANK()OVER ( ORDER BY total_views desc)as view_rank,
	RANK()OVER ( ORDER BY subscriber_count desc)as subscriber_rank,
	RANK()OVER ( ORDER BY avg_views_per_video desc)as quality_rank
from kpis
order by total_views desc;

--- TOP 10 videos by views
select
	channel_name,
	title,
	published_date,
	view_count,
	like_count,
	comment_count,
	engagement_rate
from videos
order by view_count desc
limit 10;

--- TOP 10 videos by engagement rate
select
	channel_name,
	title,
	published_date,
	view_count,
	like_count,
	comment_count,
	engagement_rate
from videos
where view_count >= 10000
order by engagement_rate desc
limit 10;

--- monthly publishing and views trend
select 
	published_month,
	count(video_id)as videos_published,
	sum(view_count)as total_views,
	round(Avg(view_count),0)as avg_views_per_video,
	round(avg(engagement_rate),2)as avg_engagement_rate
from videos
group by published_month
order by published_month;

--- Upload day performance
select 
	published_day_name,
	count(video_id)as videos_published,
	sum(view_count)as total_views,
	round(Avg(view_count),0)as avg_views_per_video,
	round(avg(engagement_rate),2)as avg_engagement_rate
from videos
group by published_day_name
order by avg_views_per_video desc;

--- High views but low engagement
with base as (
	select *,
	CURRENT_DATE - channel_Created_date as channel_Age_Days
	from channels
),
kpis as (
	select
		channel_name,
		subscriber_count,
		total_views,
		video_count,
		channel_age_days,
		ROUND(total_views::numeric/ NULLIF(subscriber_count,0),2)as views_per_subscribers,
		ROUND(total_views::numeric/ NULLIF(video_count,0),0)as avg_views_per_video,
		ROUND(total_views::numeric / NULLIF(channel_age_days,0),0)as avg_daily_views
	from base
),
ranked as (
	select *,
		RANK()OVER(ORDER BY total_views desc)as views_rank,
		RANK()OVER(ORDER BY views_per_Subscribers desc)as engagement_rank
	from kpis
)
select * from ranked
where views_rank <=2
and engagement_Rank >=2
order by views_rank;