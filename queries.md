# Some useful query for the db 

###Count the number of New users per batch

When TEK are published as incremental batches, like in Italian Immuni app,
the number of new users can be deduced with the following query.

```sql
SELECT sum(numkeys), dt FROM
    (SELECT numkeys, batchid, max(start_timestamp) AS dt  FROM
        (SELECT count(key) as numkeys, b.batchid as batchid, start_timestamp
            from keys
                left outer join batches b on
                    keys.batch = b.id and keys.country = b.country
            group by batch,start_timestamp
            order by start_timestamp DESC)
        group by batchid)
group by dt;
```

The assumption is that all the users TEK "chains" have the same starting day. If this is not
correct, as in some other app like in German one, a different approach must be used

### Count the number of keys in a batch

Simple count for keys in a batch. Prints also the batch id.

```sql
SELECT batchid,batches.from_timestamp,batches.to_timestamp, count(key) FROM batches
    left join keys k on batches.id = k.batch and batches.country = k.country
    GROUP BY batchid;
```

### Find duplicate keys

```sql
SELECT rkey, k.batch, k.start_timestamp, k.end_timestamp, k.report_type, k.days from (
    SELECT count(key) AS num,key as rkey from keys group by key)
    left join keys k on k.key = rkey
where num > 1;  
```

