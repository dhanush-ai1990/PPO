import random
import numpy as np
import torch

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

def cuda_if(torch_object, cuda):
    return torch_object.cuda() if cuda else torch_object

def gae(rewards, masks, values, gamma, lambd):
    """ Generalized Advantage Estimation

    Args:
        rewards (FloatTensor): rewards shaped [T x N x 1]
        masks (FloatTensor): continuation masks shaped [T x N x 1]
            zero at done timesteps, one otherwise
        values (Variable): value predictions shaped [(T + 1) x N x 1]
        gamma (float): discount factor
        lambd (float): GAE lambda parameter

    Returns:
        advantages (FloatTensor): advantages shaped [T x N x 1]
        returns (FloatTensor): returns shaped [T x N x 1]
    """
    T, N, _ = rewards.size()

    cuda = rewards.is_cuda

    advantages = torch.zeros(T, N, 1)
    advantages = cuda_if(advantages, cuda)
    advantage_t = torch.zeros(N, 1)
    advantage_t = cuda_if(advantage_t, cuda)

    for t in reversed(range(T)):
        delta = rewards[t] + values[t + 1].data * gamma * masks[t] - values[t].data
        advantage_t = delta + advantage_t * gamma * lambd * masks[t]
        advantages[t] = advantage_t

    returns = values[:T].data + advantages

    return advantages, returns
