# unofficial_beam_redis
An unofficial apache beam sink for redis

```
#...

from unofficial_beam_redis.io.redisio import WriteToRedis

#...

WriteToRedis('localhost', port=8888, batch_size=100)

```