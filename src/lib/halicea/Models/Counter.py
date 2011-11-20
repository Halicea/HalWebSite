from google.appengine.ext import db
import random

SHARDS_PER_COUNTER = 20

class CounterShard(db.Model):
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(default=0)

def GetCount(nameOfCounter):
    result = 0
    for shard in CounterShard.gql('WHERE name=:1', nameOfCounter):
        result += shard.count
    return result

def ChangeCount(nameOfCounter, delta):
    shard_id = '/%s/%s' % (
         nameOfCounter, random.randint(1, SHARDS_PER_COUNTER))
    def update():
        shard = CounterShard.get_by_key_name(shard_id)
        if shard:
            shard.count += delta
        else:
            shard = CounterShard(
                 key_name=shard_id, name=nameOfCounter, count=delta)
        shard.put()
    db.run_in_transaction(update)