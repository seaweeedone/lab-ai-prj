import argparse
from typing import Dict, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


def get_data_loaders(batch_size: int) -> Tuple[DataLoader, DataLoader]:
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
    )
    train_dataset = datasets.MNIST(
        './data', train=True, download=True, transform=transform
    )
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False
    )
    return train_loader, test_loader


class MNISTModel(nn.Module):
    def __init__(self) -> None:
        super(MNISTModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3)
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = nn.Conv2d(32, 64, 3)
        self.pool2 = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(64 * 5 * 5, 128)
        self.output = nn.Linear(128, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = self.output(x)
        return x


class MetricsPrint:
    def __init__(self) -> None:
        self.history: Dict[str, list[float]] = {"loss": [], "accuracy": []}

    def on_epoch_end(self, epoch: int, loss: float, accuracy: float) -> None:
        self.history["loss"].append(loss)
        self.history["accuracy"].append(accuracy)
        print('\nepoche {}:'.format(epoch))
        print('loss={}'.format(loss))
        print('accuracy={}'.format(accuracy))


def train(
    model: nn.Module,
    device: torch.device,
    train_loader: DataLoader,
    optimizer: optim.Optimizer,
    criterion: nn.modules.loss._Loss,
    epoch: int,
    callbacks: MetricsPrint,
) -> None:
    model.train()
    running_loss: float = 0.0
    correct: int = 0
    total: int = 0
    for data, target in train_loader:
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * data.size(0)
        preds = output.argmax(dim=1, keepdim=True)
        correct += preds.eq(target.view_as(preds)).sum().item()
        total += data.size(0)

    avg_loss: float = running_loss / total
    accuracy: float = correct / total
    callbacks.on_epoch_end(epoch, avg_loss, accuracy)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--batch-size',
        type=int,
        default=64,
        help='input batch size for training (default: 64)',
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.001,
        help='learning rate (default: 0.001)',
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=5,
        metavar='N',
        help='number of epochs to train (default: 5)',
    )
    args = parser.parse_args(args=[])

    print('Loading MNIST data...')
    train_loader: DataLoader
    train_loader, _ = get_data_loaders(args.batch_size)

    device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model: MNISTModel = MNISTModel().to(device)

    optimizer: optim.Adam = optim.Adam(model.parameters(), lr=args.learning_rate)
    criterion: nn.modules.loss._Loss = nn.CrossEntropyLoss()

    print('Neural Network Model Summary:')
    print(model)

    metrics_callback: MetricsPrint = MetricsPrint()

    for epoch in range(args.epochs):
        train(
            model,
            device,
            train_loader,
            optimizer,
            criterion,
            epoch,
            metrics_callback,
        )


if __name__ == "__main__":
    main()
