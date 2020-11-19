# unofficial_beam_redis

An unofficial apache beam sink to write data into Redis.

This is an unofficial redis sink for apache beam. Only host,
port and batch_size as parameters are supported. Thi applies to the method, 
only `set` is supported as well for now.

# How to use

```
from unofficial_beam_redis.io.redisio import WriteToRedis

  pipeline | WriteToRedis(host='localhost',
                          port=6379,
                          batch_size=100)

```

The ptransform works by getting the first and second elements from the input,
this means that inputs like `[k,v]` or `(k,v)` are valid.

The `batch_size` is to specify how many elements should be written at once to
redis, this is to decrease the round-trip per redis write, `100` is the default.

# License

Check the LICENSE.txt for fair usage. 

# Packages

I'll be publishing updated versions to be
available through pypi https://pypi.org/project/unofficial-beam-redis/.

# Others

Bugs, new features, etc, please follow the github git workflow 
(fork and pull-request). Hopefully when this package is stable and complete
(with all its crucial features).

# Roadmap

- Add options to support all different parameters for and to-connect to redis
- Add validations for its parameters
- Add enumeration for methods
- Add a read class
- Improve logging
- PR to apache-beam repository if already doesn't exist by that time