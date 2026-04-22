import torch
import torch.nn as nn
import os

MODEL_PATH = "models/speaker_model/classifier.pth"

class ECAPAClassifier:
    def __init__(self, num_speakers):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = nn.Linear(192, 51)
        self.model.load_state_dict(torch.load(MODEL_PATH, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def predict(self, embedding):
        embedding = torch.tensor(embedding).float().to(self.device)
        embedding = embedding.unsqueeze(0)

        with torch.no_grad():
            output = self.model(embedding)
            pred = torch.argmax(output, dim=1).item()

        return pred