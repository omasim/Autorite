"""RP002A fixtures/models. No execution or scientific status changes on import."""
import hashlib,itertools,time
from pathlib import Path
import numpy as np
import torch
from torch import nn


def seed(version,world,replicate,split,purpose):
 text=f'rp002a/{version}/{world}/{replicate}/{split}/{purpose}'
 return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],'big')


def observations(values):
 a=np.asarray(values)
 if a.ndim!=2 or min(a.shape)<1 or not np.issubdtype(a.dtype,np.integer) or not np.isin(a,[0,1,2]).all():raise ValueError('Expected episode x time categorical observations 0/1/2')
 return a


def generate(p,q,episodes,length,data_seed):
 if not (0<=p<=1 and 0<=q<=1 and type(episodes) is int and type(length) is int and episodes>0 and length>=2):raise ValueError('Invalid generator configuration')
 rng=np.random.default_rng(data_seed)
 latent=rng.integers(0,2,size=episodes)
 obs=np.empty((episodes,length),dtype=np.int64)
 for t in range(length):
  if t:latent=np.bitwise_xor(latent,rng.random(episodes)<p)
  obs[:,t]=np.where(rng.random(episodes)<q,2,latent)
 return obs  # Deliberately expose no realized hidden-state array.


def oracle(history,p,q):
 a=observations(history)
 if not (0<=p<=1 and 0<=q<=1):raise ValueError('Invalid generator law')
 prior=np.full(a.shape[0],0.5);out=np.empty((*a.shape,3),dtype=np.float64)
 for t in range(a.shape[1]):
  o=a[:,t]
  evidence=np.where(o==2,q,np.where(o==1,prior,1-prior)*(1-q))
  if np.any(evidence<=0):raise ValueError('History has zero probability under generator')
  posterior=np.where(o==2,prior,o)
  prior=p+(1-2*p)*posterior
  out[:,t,:]=np.stack(((1-q)*(1-prior),(1-q)*prior,np.full(len(prior),q)),axis=1)
 return out


def enumerated_next(history,p,q):
 """Independent brute-force reference for short-history acceptance tests."""
 h=list(history)
 if not h or any(o not in [0,1,2] for o in h):raise ValueError('Invalid short history')
 weights=np.zeros(2)
 for states in itertools.product([0,1],repeat=len(h)):
  mass=0.5
  for t,(s,o) in enumerate(zip(states,h)):
   if t:mass*=p if s!=states[t-1] else 1-p
   mass*=q if o==2 else (1-q if o==s else 0)
  weights[states[-1]]+=mass
 if weights.sum()==0:raise ValueError('Impossible history')
 posterior=weights[1]/weights.sum();next_one=p+(1-2*p)*posterior
 return np.array([(1-q)*(1-next_one),(1-q)*next_one,q])


def fit_b0(train,alpha=1.0):
 a=observations(train)
 if a.shape[1]<2 or alpha<=0:raise ValueError('Insufficient data or nonpositive smoothing')
 counts=np.full((3,3),float(alpha))
 np.add.at(counts,(a[:,:-1].ravel(),a[:,1:].ravel()),1)
 return counts/counts.sum(axis=1,keepdims=True)


def features(history,window):
 """Causal finite windows, oldest-to-newest; episode-local zero padding."""
 a=observations(history)
 if type(window) is not int or window<1:raise ValueError('Invalid window')
 n,t=a.shape;onehot=np.eye(3,dtype=np.float32)[a]
 x=np.zeros((n,t,window,3),dtype=np.float32);valid=np.zeros((n,t,window),dtype=np.float32)
 for k in range(window):
  lag=window-1-k
  if lag<t:x[:,lag:,k,:]=onehot[:,:t-lag,:];valid[:,lag:,k]=1
 return np.concatenate((x.reshape(n,t,window*3),valid),axis=-1)


class FiniteHistory(nn.Module):
 def __init__(self,window=8,hidden=16):
  super().__init__();self.window=window;self.net=nn.Sequential(nn.Linear(window*4,hidden),nn.ReLU(),nn.Linear(hidden,3))
 def forward(self,obs):
  x=features(obs.detach().cpu().numpy(),self.window)
  return self.net(torch.from_numpy(x).to(obs.device))


class RecursiveState(nn.Module):
 def __init__(self,hidden=12):
  super().__init__();self.gru=nn.GRU(3,hidden,batch_first=True);self.head=nn.Linear(hidden,3)
 def forward(self,obs):
  x=nn.functional.one_hot(obs,num_classes=3).float()
  state,_=self.gru(x)  # No hidden state supplied: zero reset for each batch/episode.
  return self.head(state)


def losses(probabilities,targets,clip=1e-8):
 p=np.asarray(probabilities,dtype=float);a=observations(targets)
 if p.shape!=(*a.shape,3) or not np.isfinite(p).all() or (p<0).any() or not np.allclose(p.sum(-1),1,atol=1e-6):raise ValueError('Invalid categorical probabilities')
 if not 0<clip<1:raise ValueError('Invalid clipping probability')
 true=np.take_along_axis(p,a[...,None],axis=-1)[...,0]
 return -np.log(np.maximum(true,clip))


def train_model(model,train,validation,optimizer_config,batch_seed,deadline):
 """Training primitive; caller must enforce authorization/freeze and artifact policy."""
 train=observations(train);validation=observations(validation)
 if min(train.shape[1],validation.shape[1])<2:raise ValueError('Insufficient prediction pairs')
 optimizer=torch.optim.Adam(model.parameters(),lr=optimizer_config['learning_rate'])
 order=np.random.default_rng(batch_seed);best=float('inf');saved=None;stale=0;trace=[]
 for epoch in range(optimizer_config['max_epochs']):
  model.train()
  indices=order.permutation(len(train))
  for offset in range(0,len(indices),optimizer_config['batch_episodes']):
   if time.monotonic()>=deadline:raise TimeoutError('Declared training wall-time budget exhausted')
   b=torch.as_tensor(train[indices[offset:offset+optimizer_config['batch_episodes']]],dtype=torch.long)
   optimizer.zero_grad();logits=model(b[:,:-1]);loss=nn.functional.cross_entropy(logits.reshape(-1,3),b[:,1:].reshape(-1))
   if not torch.isfinite(loss):raise FloatingPointError('Nonfinite training loss')
   loss.backward();nn.utils.clip_grad_norm_(model.parameters(),optimizer_config['gradient_norm_clip']);optimizer.step()
  model.eval()
  with torch.no_grad():
   b=torch.as_tensor(validation,dtype=torch.long);value=float(nn.functional.cross_entropy(model(b[:,:-1]).reshape(-1,3),b[:,1:].reshape(-1)))
  if time.monotonic()>=deadline:raise TimeoutError('Declared training wall-time budget exhausted')
  if not np.isfinite(value):raise FloatingPointError('Nonfinite validation loss')
  trace.append({'epoch':epoch+1,'validation_log_loss':value})
  if value<best:
   best=value;saved={k:v.detach().clone() for k,v in model.state_dict().items()};stale=0
  else:stale+=1
  if stale>=optimizer_config['early_stopping_patience']:break
 if saved is None:raise ValueError('No model checkpoint selected')
 model.load_state_dict(saved);model.eval()
 return trace


def probabilities(model,history):
 model.eval()
 with torch.no_grad():return torch.softmax(model(torch.as_tensor(observations(history),dtype=torch.long)),dim=-1).cpu().numpy()


def paired_interval(alternative,reference,resamples,alpha,bootstrap_seed):
 """Hierarchical paired interval from replicate x episode mean losses."""
 a=np.asarray(alternative,dtype=float);b=np.asarray(reference,dtype=float)
 if a.shape!=b.shape or a.ndim!=2 or min(a.shape)<2 or not np.isfinite(a-b).all() or resamples<1 or not 0<alpha<1:raise ValueError('Invalid paired bootstrap input')
 diff=a-b;rng=np.random.default_rng(bootstrap_seed);estimates=[]
 for _ in range(resamples):
  rs=rng.integers(0,len(diff),size=len(diff));means=[]
  for r in rs:means.append(diff[r,rng.integers(0,diff.shape[1],size=diff.shape[1])].mean())
  estimates.append(np.mean(means))
 return {'mean_difference':float(diff.mean()),'interval':np.quantile(estimates,[alpha/2,1-alpha/2]).tolist()}
