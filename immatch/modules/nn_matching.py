import torch
import numpy as np

def mutual_nn_matching_torch(desc1, desc2, threshold=None):
    device = desc1.device
    desc1 = desc1 / desc1.norm(dim=1, keepdim=True)
    desc2 = desc2 / desc2.norm(dim=1, keepdim=True)
    #similarity = desc1 @ desc2.t()
    similarity = torch.einsum('id, jd->ij', desc1, desc2)

    
    nn12 = similarity.max(dim=1)[1]
    nn21 = similarity.max(dim=0)[1]
    ids1 = torch.arange(0, similarity.shape[0], device=device)
    mask = (ids1 == nn21[nn12])
    matches = torch.stack([ids1[mask], nn12[mask]]).t()
    scores = similarity.max(dim=1)[0][mask]    
    if threshold:
        mask = scores > threshold
        matches = matches[mask]    
        scores = scores[mask]
    return matches, scores

def mutual_nn_matching(desc1, desc2, threshold=None):
    if isinstance(desc1, np.ndarray):
        desc1 = torch.from_numpy(desc1)
        desc2 = torch.from_numpy(desc2)
    matches, scores = mutual_nn_matching_torch(desc1, desc2, threshold=threshold)
    return matches.cpu().numpy(), scores.cpu().numpy()
