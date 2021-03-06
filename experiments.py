import argparse
import os
import json
import torch
from utils.network import build_network
from utils.dataset import build_dataset
from utils.train import train
from torch.utils.tensorboard import SummaryWriter
from utils.utils import get_events_data


def get_args():
    """
    Function used for parsing the command line arguments
    Returns: Command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment_id', type=str, help='ID of the experiment that you want to run.')
    arguments = parser.parse_args()

    return arguments


args = get_args()

experiment_path = f"experiment{args.experiment_id}"

# Create configs, logs and checkpoints folder
if not os.path.exists("configs/"):
    os.mkdir("configs/")
if not os.path.exists("logs/"):
    os.mkdir("logs/")
if not os.path.exists("logs/" + experiment_path):
    os.mkdir("logs/" + experiment_path)
if not os.path.exists("checkpoints/"):
    os.mkdir("checkpoints/")
if not os.path.exists("checkpoints/" + experiment_path):
    os.mkdir("checkpoints/" + experiment_path)


config_path = 'configs/' + experiment_path

for config_filename in os.listdir(config_path):
    if config_filename.endswith(".json"): 
        # Get config
        with open(os.path.join(config_path, config_filename)) as json_config:
            config = json.load(json_config)

        config["name"] = config_filename.split('.')[0]

        # Set folder for logging
        log_dir = config["log_dir"] + '/' + experiment_path + '/' + config["name"]
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        # Set folder for checkpoints
        checkpoints_dir = config["checkpoint_dir"] + '/' + experiment_path + '/' + config["name"]
        if not os.path.exists(checkpoints_dir):
            os.mkdir(checkpoints_dir)

        config["checkpoint_dir"] = checkpoints_dir
        config["log_dir"] = log_dir

        # Check for cuda availability
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print('Device state: ', device)

        # Get dataset
        dataset = build_dataset(config, config["data"], train=True)

        # Get network
        net = build_network(config)
        net.to(device=device)

        # Train network
        writer = SummaryWriter(log_dir=config["log_dir"])
        train(dataset, net, config, writer, device=device)

        # Log scores
        cfg_name = config["name"]
        log_path = f"logs/{experiment_path}/{cfg_name}"
        get_events_data(log_path, False, True, log_path, to_watch='_lr')
        get_events_data(log_path + "/Loss_train", False, True, log_path, to_watch='_loss_train')
        get_events_data(log_path + "/Loss_val", False, True, log_path, to_watch='_loss_val')
        get_events_data(log_path + "/Accuracy_train", False, True, log_path, to_watch='_acc_train')
        get_events_data(log_path + "/Accuracy_val", False, True, log_path, to_watch='_acc_val')
