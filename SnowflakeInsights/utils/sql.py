QUERIES_QUERY = """
select *
from snowflake.account_usage.query_history
where START_TIME >= convert_timezone('UTC', 'UTC', ('{date_from}T00:00:00Z')::timestamp_ltz)
and START_TIME < convert_timezone('UTC', 'UTC', ('{date_to}T00:00:00Z')::timestamp_ltz) order by START_TIME DESC limit 1000;
"""

QUERIES_COUNT_QUERY = """
select QUERY_TEXT,
       count(*) as number_of_queries,
       sum(TOTAL_ELAPSED_TIME)/1000 as execution_seconds,
       sum(TOTAL_ELAPSED_TIME)/(1000*60) as execution_minutes,
       sum(TOTAL_ELAPSED_TIME)/(1000*60*60) as execution_hours
from SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY Q
where 1=1
  and Q.START_TIME >= convert_timezone('UTC', 'UTC', ('{date_from}T00:00:00Z')::timestamp_ltz)
  and Q.START_TIME <= convert_timezone('UTC', 'UTC', ('{date_to}T00:00:00Z')::timestamp_ltz)
  and TOTAL_ELAPSED_TIME > 0 --only get queries that actually used compute
  and WAREHOUSE_NAME = '{warehouse_name}'

group by 1
having count(*) >= {num_min} --configurable/minimal threshold

order by 2 desc
limit {limit}; --configurable upper bound threshold
"""

CONSUMPTION_PER_SERVICE_TYPE_QUERY = """
select date_trunc('hour', convert_timezone('UTC', start_time)) as start_time,
       name,
       service_type,
       round(sum(credits_used), 1) as credits_used,
       round(sum(credits_used_compute), 1) as credits_compute,
       round(sum(credits_used_cloud_services), 1) as credits_cloud
from snowflake.account_usage.metering_history
where start_time >= convert_timezone('UTC', 'UTC', ('{date_from}T00:00:00Z')::timestamp_ltz)
and start_time < convert_timezone('UTC', 'UTC', ('{date_to}T00:00:00Z')::timestamp_ltz)
group by 1, 2, 3;
"""

WAREHOUSE_USAGE_HOURLY = """
// Credits used by [hour, warehouse] (past 7 days)
select START_TIME ,
       WAREHOUSE_NAME ,
       CREDITS_USED_COMPUTE
from SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
where START_TIME >= convert_timezone('UTC', 'UTC', ('{date_from}T00:00:00Z')::timestamp_ltz)
  and start_time < convert_timezone('UTC', 'UTC', ('{date_to}T00:00:00Z')::timestamp_ltz)
  and WAREHOUSE_ID > 0 // Skip pseudo-VWs such as "CLOUD_SERVICES_ONLY"
order by 1 desc,
         2
"""

STORAGE_QUERY = """
select convert_timezone('UTC', usage_date) as usage_date,
       database_name as object_name,
       'database' as object_type,
       max(AVERAGE_DATABASE_BYTES) as database_bytes,
       max(AVERAGE_DATABASE_BYTES)/1000 as database_kilobytes,
       max(AVERAGE_FAILSAFE_BYTES) as failsafe_bytes,
       0 as stage_bytes
from snowflake.account_usage.database_storage_usage_history
where usage_date >= date_trunc('day', ('{date_from}T00:00:00Z')::timestamp_ntz)
and usage_date < date_trunc('day', ('{date_to}T00:00:00Z')::timestamp_ntz)
group by 1, 2, 3
union all
select convert_timezone('UTC', usage_date) as usage_date,
       'Stages' as object_name,
       'stage' as object_type,
       0 as database_bytes,
       0 as database_kilobytes,
       0 as failsafe_bytes,
       max(AVERAGE_STAGE_BYTES) as stage_bytes
from snowflake.account_usage.stage_storage_usage_history
where usage_date >= date_trunc('day', ('{date_from}T00:00:00Z')::timestamp_ntz)
and usage_date < date_trunc('day', ('{date_to}T00:00:00Z')::timestamp_ntz)
group by 1, 2, 3;
"""

DATA_TRANSFER_QUERY = """
select date_trunc('hour', convert_timezone('UTC', start_time)) as start_time,
       target_cloud,
       target_region,
       transfer_type,
       sum(bytes_transferred) as bytes_transferred
from snowflake.account_usage.data_transfer_history
where start_time >= convert_timezone('UTC', 'UTC', ('{date_from}T00:00:00Z')::timestamp_ltz)
and start_time < convert_timezone('UTC', 'UTC', ('{date_to}T00:00:00Z')::timestamp_ltz)
group by 1, 2, 3, 4;
"""

USERS_QUERY = """
with USER_HOUR_EXECUTION_CTE as
  (select USER_NAME ,
          WAREHOUSE_NAME ,
          DATE_TRUNC('hour', START_TIME) as START_TIME_HOUR ,
          SUM(EXECUTION_TIME) as USER_HOUR_EXECUTION_TIME
   from "SNOWFLAKE"."ACCOUNT_USAGE"."QUERY_HISTORY"
   where WAREHOUSE_NAME is not null
     and EXECUTION_TIME > 0
     and START_TIME > convert_timezone('UTC', 'UTC', ('{date_from}T00:00:00Z')::timestamp_ltz)
     and START_TIME <= convert_timezone('UTC', 'UTC', ('{date_to}T00:00:00Z')::timestamp_ltz)
   group by 1,
            2,
            3),
     HOUR_EXECUTION_CTE as
  (select START_TIME_HOUR ,
          WAREHOUSE_NAME ,
          SUM(USER_HOUR_EXECUTION_TIME) as HOUR_EXECUTION_TIME
   from USER_HOUR_EXECUTION_CTE
   group by 1,
            2),
     APPROXIMATE_CREDITS as
  (select A.USER_NAME ,
          C.WAREHOUSE_NAME ,
          (A.USER_HOUR_EXECUTION_TIME/B.HOUR_EXECUTION_TIME)*C.CREDITS_USED as APPROXIMATE_CREDITS_USED
   from USER_HOUR_EXECUTION_CTE A
   join HOUR_EXECUTION_CTE B on A.START_TIME_HOUR = B.START_TIME_HOUR
   and B.WAREHOUSE_NAME = A.WAREHOUSE_NAME
   join "SNOWFLAKE"."ACCOUNT_USAGE"."WAREHOUSE_METERING_HISTORY" C on C.WAREHOUSE_NAME = A.WAREHOUSE_NAME
   and C.START_TIME = A.START_TIME_HOUR)
select USER_NAME,
       WAREHOUSE_NAME,
       SUM(APPROXIMATE_CREDITS_USED) as APPROXIMATE_CREDITS_USED
from APPROXIMATE_CREDITS
group by 1,
         2
order by 3 desc;
"""

TABLE_CATALOG="""SELECT
    t.TABLE_ID,
    t.TABLE_CATALOG,
    t.CREATED,
    t.TABLE_NAME,
    t.TABLE_SCHEMA,
    t.TABLE_OWNER,
    t.TABLE_TYPE,
    t.IS_TRANSIENT,
    t.CLUSTERING_KEY,
    t.ROW_COUNT,
    t.BYTES,
    t.RETENTION_TIME,
    t.LAST_ALTERED,
    t.AUTO_CLUSTERING_ON,
    t.COMMENT,
    c.column_count
from
    SNOWFLAKE.ACCOUNT_USAGE.TABLES t
    left join (
        select
            table_id,
            count(distinct column_id) column_count
        from
            SNOWFLAKE.ACCOUNT_USAGE.COLUMNS
        group by
            table_id
    ) c on c.table_id = t.table_id
    where t.table_schema not like '%ANON_HOL%' and deleted is null  order by t.table_id limit 2000"""
    
WAREHOUSE="SHOW WAREHOUSES"
ROLE="SHOW GRANTS"
USE_WAREHOUSE="USE WAREHOUSE {wh}"
USE_ROLE="USE ROLE {role}"

AVERAGE_QUERY_VOLUME="""SELECT DATE_TRUNC('HOUR', START_TIME) AS QUERY_START_HOUR,
WAREHOUSE_NAME,COUNT(*) AS NUM_QUERIES
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
AND WAREHOUSE_NAME IS NOT NULL
GROUP BY 1, 2 ORDER BY 1 DESC, 2"""

WAREHOUSE_WO_AUTO_RESUME="""SELECT "name" AS WAREHOUSE_NAME
      ,"size" AS WAREHOUSE_SIZE
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
 WHERE "auto_resume" = 'false'"""

WAREHOUSE_WO_AUTO_SUSPEND="""SELECT "name" AS WAREHOUSE_NAME
      ,"size" AS WAREHOUSE_SIZE
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
 WHERE IFNULL("auto_suspend",0) = 0"""

WAREHOUSE_WI_LONG_SUSPENSION="""SELECT "name" AS WAREHOUSE_NAME
      ,"size" AS WAREHOUSE_SIZE
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
 WHERE "auto_suspend" >= 3600"""

WAREHOUSE_WO_RESOURCE_MONITOR="""SELECT "name" AS WAREHOUSE_NAME
      ,"size" AS WAREHOUSE_SIZE
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
 WHERE "resource_monitor" = 'null' """

IDLE_USERS="""SELECT USER_ID,NAME,CREATED_ON,DELETED_ON,LOGIN_NAME,DISPLAY_NAME,FIRST_NAME,LAST_NAME,
COMMENT,DISABLED,DEFAULT_WAREHOUSE,DEFAULT_ROLE,LAST_SUCCESS_LOGIN,EXPIRES_AT,
LOCKED_UNTIL_TIME,OWNER FROM SNOWFLAKE.ACCOUNT_USAGE.USERS 
WHERE LAST_SUCCESS_LOGIN < '{date_from}' 
AND DELETED_ON IS NULL"""

USERS_NEVER_LOGGED_IN="""SELECT USER_ID,NAME,CREATED_ON,DELETED_ON,LOGIN_NAME,DISPLAY_NAME,FIRST_NAME,LAST_NAME,
COMMENT,DISABLED,DEFAULT_WAREHOUSE,DEFAULT_ROLE,LAST_SUCCESS_LOGIN,EXPIRES_AT,
LOCKED_UNTIL_TIME,OWNER FROM SNOWFLAKE.ACCOUNT_USAGE.USERS 
WHERE LAST_SUCCESS_LOGIN IS NULL"""
 
IDLE_ROLES="""SELECT R.* FROM SNOWFLAKE.ACCOUNT_USAGE.ROLES R
LEFT JOIN (
    SELECT DISTINCT 
        ROLE_NAME 
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
    WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
    AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
        ) Q 
                ON Q.ROLE_NAME = R.NAME
WHERE Q.ROLE_NAME IS NULL
and DELETED_ON IS NULL"""

IDLE_WAREHOUSES="""select distinct WAREHOUSE_NAME from SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)"""

MOST_EXPENSIVE_QUERY="""
WITH WAREHOUSE_SIZE AS
(
     SELECT WAREHOUSE_SIZE, NODES
       FROM (
              SELECT 'XSMALL' AS WAREHOUSE_SIZE, 1 AS NODES
              UNION ALL
              SELECT 'SMALL' AS WAREHOUSE_SIZE, 2 AS NODES
              UNION ALL
              SELECT 'MEDIUM' AS WAREHOUSE_SIZE, 4 AS NODES
              UNION ALL
              SELECT 'LARGE' AS WAREHOUSE_SIZE, 8 AS NODES
              UNION ALL
              SELECT 'XLARGE' AS WAREHOUSE_SIZE, 16 AS NODES
              UNION ALL
              SELECT '2XLARGE' AS WAREHOUSE_SIZE, 32 AS NODES
              UNION ALL
              SELECT '3XLARGE' AS WAREHOUSE_SIZE, 64 AS NODES
              UNION ALL
              SELECT '4XLARGE' AS WAREHOUSE_SIZE, 128 AS NODES
            )
),
QUERY_HISTORY AS
(
     SELECT QH.QUERY_ID
           ,QH.QUERY_TEXT
           ,QH.USER_NAME
           ,QH.ROLE_NAME
           ,QH.EXECUTION_TIME
           ,QH.WAREHOUSE_SIZE
      FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY QH
     WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
     AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
)

SELECT QH.QUERY_ID
      ,QH.QUERY_TEXT
      ,QH.USER_NAME
      ,QH.ROLE_NAME
      ,QH.EXECUTION_TIME as EXECUTION_TIME_MILLISECONDS
      ,(QH.EXECUTION_TIME/(1000)) as EXECUTION_TIME_SECONDS
      ,(QH.EXECUTION_TIME/(1000*60)) AS EXECUTION_TIME_MINUTES
      ,(QH.EXECUTION_TIME/(1000*60*60)) AS EXECUTION_TIME_HOURS
      ,WS.WAREHOUSE_SIZE
      ,WS.NODES
      ,(QH.EXECUTION_TIME/(1000*60*60))*WS.NODES as RELATIVE_PERFORMANCE_COST

FROM QUERY_HISTORY QH
JOIN WAREHOUSE_SIZE WS ON WS.WAREHOUSE_SIZE = upper(QH.WAREHOUSE_SIZE)
ORDER BY RELATIVE_PERFORMANCE_COST DESC
LIMIT 200"""

AVERAGE_COST_PER_QUERY="""SELECT
    COALESCE(WC.WAREHOUSE_NAME,QC.WAREHOUSE_NAME) AS WAREHOUSE_NAME
    ,QC.QUERY_COUNT_LAST_MONTH
    ,WC.CREDITS_USED_LAST_MONTH
    ,WC.CREDIT_COST_LAST_MONTH
    ,CAST((WC.CREDIT_COST_LAST_MONTH / QC.QUERY_COUNT_LAST_MONTH) AS decimal(10,2) ) AS COST_PER_QUERY

FROM (
    SELECT
       WAREHOUSE_NAME
      ,COUNT(QUERY_ID) as QUERY_COUNT_LAST_MONTH
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
    AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
    GROUP BY WAREHOUSE_NAME
      ) QC
JOIN (

    SELECT
        WAREHOUSE_NAME
        ,SUM(CREDITS_USED) as CREDITS_USED_LAST_MONTH
        ,SUM(CREDITS_USED)*($CREDIT_PRICE) as CREDIT_COST_LAST_MONTH
    FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
    WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
    AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
    GROUP BY WAREHOUSE_NAME
  ) WC
    ON WC.WAREHOUSE_NAME = QC.WAREHOUSE_NAME

ORDER BY COST_PER_QUERY DESC"""

AUTOCLUSTERING_COST_HISTORY="""SELECT TO_DATE(START_TIME) as DATE
,DATABASE_NAME,SCHEMA_NAME,TABLE_NAME,SUM(CREDITS_USED) as CREDITS_USED
FROM "SNOWFLAKE"."ACCOUNT_USAGE"."AUTOMATIC_CLUSTERING_HISTORY"
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ) 
GROUP BY 1,2,3,4
ORDER BY 5 DESC 
"""
MATERIALIZED_VIEWS_COST_HISTORY="""SELECT TO_DATE(START_TIME) as DATE
,DATABASE_NAME,SCHEMA_NAME,TABLE_NAME,SUM(CREDITS_USED) as CREDITS_USED
FROM "SNOWFLAKE"."ACCOUNT_USAGE"."MATERIALIZED_VIEW_REFRESH_HISTORY"
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
GROUP BY 1,2,3,4
ORDER BY 5 DESC 
"""
SEARCH_OPTIMIZATION_COST_HISTORY="""SELECT TO_DATE(START_TIME) as DATE
,DATABASE_NAME,SCHEMA_NAME,TABLE_NAME,SUM(CREDITS_USED) as CREDITS_USED
FROM "SNOWFLAKE"."ACCOUNT_USAGE"."SEARCH_OPTIMIZATION_HISTORY"
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
GROUP BY 1,2,3,4
ORDER BY 5 DESC """

SNOWPIPE_COST_HISTORY="""SELECT TO_DATE(START_TIME) as DATE
,PIPE_NAME,SUM(CREDITS_USED) as CREDITS_USED
FROM "SNOWFLAKE"."ACCOUNT_USAGE"."PIPE_USAGE_HISTORY"
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ) 
GROUP BY 1,2
ORDER BY 3 DESC
"""

REPLICATION_COST_HISTORY="""SELECT TO_DATE(START_TIME) as DATE
,DATABASE_NAME,SUM(CREDITS_USED) as CREDITS_USED
FROM "SNOWFLAKE"."ACCOUNT_USAGE"."REPLICATION_USAGE_HISTORY"
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
GROUP BY 1,2
ORDER BY 3 DESC 
"""

DATA_INGEST_WI_SNOWPIPE="""SELECT 
  TO_DATE(LAST_LOAD_TIME) as LOAD_DATE
  ,STATUS
  ,TABLE_CATALOG_NAME as DATABASE_NAME
  ,TABLE_SCHEMA_NAME as SCHEMA_NAME
  ,TABLE_NAME
  ,CASE WHEN PIPE_NAME IS NULL THEN 'COPY' ELSE 'SNOWPIPE' END AS INGEST_METHOD
  ,SUM(ROW_COUNT) as ROW_COUNT
  ,SUM(ROW_PARSED) as ROWS_PARSED
  ,AVG(FILE_SIZE) as AVG_FILE_SIZE_BYTES
  ,SUM(FILE_SIZE) as TOTAL_FILE_SIZE_BYTES
  ,SUM(FILE_SIZE)/POWER(1000,1) as TOTAL_FILE_SIZE_KB
  ,SUM(FILE_SIZE)/POWER(1000,2) as TOTAL_FILE_SIZE_MB
  ,SUM(FILE_SIZE)/POWER(1000,3) as TOTAL_FILE_SIZE_GB
  ,SUM(FILE_SIZE)/POWER(1000,4) as TOTAL_FILE_SIZE_TB
FROM "SNOWFLAKE"."ACCOUNT_USAGE"."COPY_HISTORY"
GROUP BY 1,2,3,4,5,6
ORDER BY 3,4,5,1,2
"""

WAREHOUSE_CACHE_USAGE="""SELECT WAREHOUSE_NAME
,COUNT(*) AS QUERY_COUNT
,ROUND(SUM(BYTES_SCANNED)/1000/1000,2) AS MB_SCANNED
,ROUND(SUM(BYTES_SCANNED*PERCENTAGE_SCANNED_FROM_CACHE)/1000/1000,2) AS MB_SCANNED_FROM_CACHE
,ROUND(SUM(BYTES_SCANNED*PERCENTAGE_SCANNED_FROM_CACHE) / SUM(BYTES_SCANNED),2) AS PERCENT_SCANNED_FROM_CACHE
FROM "SNOWFLAKE"."ACCOUNT_USAGE"."QUERY_HISTORY"
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
AND BYTES_SCANNED > 0
GROUP BY 1
ORDER BY 5"""

HEAVY_SCANNERS="""select * from (select User_name,warehouse_name
,round(avg(case when partitions_total > 0 then partitions_scanned / partitions_total else 0 end),4) avg_pct_scanned
from snowflake.account_usage.query_history
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
group by 1, 2
order by 3 desc) where avg_pct_scanned >0"""

FULL_TABLE_SCANS="""SELECT USER_NAME
,COUNT(*) as COUNT_OF_QUERIES
FROM "SNOWFLAKE"."ACCOUNT_USAGE"."QUERY_HISTORY"
WHERE START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
AND PARTITIONS_SCANNED > (PARTITIONS_TOTAL*0.95)
AND QUERY_TYPE NOT LIKE 'CREATE%'
group by 1
order by 2 desc"""

TOP_10_SPILLERS_REMOTE="""select query_id, substr(query_text, 1, 50) partial_query_text, user_name, warehouse_name, warehouse_size, 
       BYTES_SPILLED_TO_REMOTE_STORAGE, start_time, end_time, total_elapsed_time/1000 total_elapsed_time
from   snowflake.account_usage.query_history
where  BYTES_SPILLED_TO_REMOTE_STORAGE > 0
AND START_TIME >= CONVERT_TIMEZONE('UTC', 'UTC', ('{date_from}T00:00:00Z')::TIMESTAMP_LTZ)
AND START_TIME < CONVERT_TIMEZONE('UTC', 'UTC', ('{date_to}T00:00:00Z')::TIMESTAMP_LTZ)
order  by BYTES_SPILLED_TO_REMOTE_STORAGE desc
limit 10"""

WAREHOUSE_CREDIT_USAGE="""SELECT WAREHOUSE_NAME, DATE(START_TIME) AS DATE, 
SUM(CREDITS_USED) AS CREDITS_USED,
AVG(SUM(CREDITS_USED)) OVER (PARTITION BY WAREHOUSE_NAME ORDER BY DATE ROWS 7 PRECEDING) AS CREDITS_USED_7_DAY_AVG,
(TO_NUMERIC(SUM(CREDITS_USED)/CREDITS_USED_7_DAY_AVG*100,10,2)-100)::STRING || '%' AS VARIANCE_TO_7_DAY_AVERAGE
FROM "SNOWFLAKE"."ACCOUNT_USAGE"."WAREHOUSE_METERING_HISTORY"
GROUP BY DATE, WAREHOUSE_NAME
ORDER BY DATE DESC"""


YTD_CREDIT_CONSUMPTION="""select to_decimal(sum(credits_used),15,2) as credits
from "SNOWFLAKE"."ACCOUNT_USAGE"."WAREHOUSE_METERING_HISTORY" wmh
where start_time >= DATE_TRUNC('year', current_date())"""

YTD_TOTAL_QUERIES="""select count(1) as count
from "SNOWFLAKE"."ACCOUNT_USAGE"."QUERY_HISTORY"
where start_time >= DATE_TRUNC('year', current_date())
and warehouse_name is not null"""

YTD_AVG_EXEC_TIME="""select to_decimal(avg(total_elapsed_time)/1000,10,3) as avg_time
from snowflake.account_usage.query_history
where start_time >= DATE_TRUNC('year', current_date())
and warehouse_name is not null"""

MTD_CREDIT_CONSUMPTION="""select to_decimal(sum(credits_used),15,2) as credit
from snowflake.account_usage.warehouse_metering_history wmh
where start_time >= DATE_TRUNC('month',current_date())"""

MTD_TOTAL_QUERIES="""select count(1) as count
from snowflake.account_usage.query_history
where start_time >= DATE_TRUNC('month', current_date())
and warehouse_name is not null"""

MTD_AVG_EXEC_TIME="""select to_decimal(avg(total_elapsed_time)/1000,10,3) as avg_time
from snowflake.account_usage.query_history
where start_time >= DATE_TRUNC('month', current_date()) 
and warehouse_name is not null"""

TOTAL_DBS="""select count(1) as db_count from snowflake.account_usage.databases where deleted is null"""

TOTAL_TABLES="""select count(1) as table_count from snowflake.account_usage.tables where deleted is null"""

FAILED_LOGIN_ATTEMPTS="""select sum(case when IS_SUCCESS = 'NO' then 1 else 0 end ) / count(1) *100 as failed 
from snowflake.account_usage.login_history
where EVENT_TIMESTAMP >= DATE_TRUNC('year', current_date())"""

YTD_AVG_STORAGE="""select avg(storage_bytes)/1000/1000 as storage
,avg(stage_bytes)/1000/1000 as stage
,avg(failsafe_bytes)/1000/1000 as failsafe from snowflake.account_usage.storage_usage
where USAGE_DATE >= DATE_TRUNC('year', current_date())"""

MTD_AVG_STORAGE="""select avg(storage_bytes)/1000/1000 as storage
,avg(stage_bytes)/1000/1000 as stage
,avg(failsafe_bytes)/1000/1000 as failsafe from snowflake.account_usage.storage_usage
where USAGE_DATE >= DATE_TRUNC('month', current_date())"""

STORAGE_OVER_TIME="""select usage_date
,round(storage_bytes/1000/1000,2) as storage
,round(stage_bytes/1000/1000,2) as stage
,round(failsafe_bytes/1000/1000,2) as failsafe
from snowflake.account_usage.storage_usage
where usage_date >= date_trunc('day', ('{date_from}T00:00:00Z')::timestamp_ntz)
and usage_date < date_trunc('day', ('{date_to}T00:00:00Z')::timestamp_ntz)"""

DAILY_CREDITS_BY_TYPE="""select usage_date, 
round(sum(decode(service_type,'WAREHOUSE_METERING', credits_billed)),2) as warehouse_credits,
round(sum(decode(service_type,'PIPE', credits_billed)),2) as pipe_credits,
round(sum(decode(service_type,'MATERIALIZED_VIEW', credits_billed)),2) as mview_credits,
round(sum(decode(service_type,'AUTO_CLUSTERING', credits_billed)),2) as clustering_credits,
round(sum(decode(service_type,'WAREHOUSE_METERING_READER', credits_billed)),2) as reader_credits,
round(sum(credits_billed),2) as total
from snowflake.account_usage.metering_daily_history wmh
where usage_date >= '{date_from}'
and usage_date < '{date_to}'
group by usage_date order by usage_date desc"""

if __name__ == "__main__":
    pass
