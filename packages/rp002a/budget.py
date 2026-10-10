"""Cooperative elapsed-time limits that also count host suspension."""
import datetime,math,time

class WallBudget:
 def __init__(self,seconds,monotonic=None,wall=None):
  if not math.isfinite(seconds) or seconds<=0:raise ValueError('Positive finite allowance required')
  self.seconds=seconds;self.monotonic=monotonic or time.monotonic;self.wall=wall or time.time
  self.started_monotonic=self.monotonic();self.started_wall=self.wall()
 def elapsed(self):return max(0,self.wall()-self.started_wall)
 def expired(self):return self.elapsed()>=self.seconds or self.monotonic()-self.started_monotonic>=self.seconds
 def timing(self):
  finish=self.wall()
  utc=lambda x:datetime.datetime.fromtimestamp(x,datetime.timezone.utc).isoformat()
  return dict(started_at_utc=utc(self.started_wall),finished_at_utc=utc(finish),elapsed_wall_seconds=max(0,finish-self.started_wall),elapsed_monotonic_seconds=self.monotonic()-self.started_monotonic,allowance_seconds=self.seconds,policy='Expire when either wall or monotonic elapsed time reaches the allowance; forward wall-clock jumps stop conservatively and backward jumps cannot extend monotonic allowance.')
