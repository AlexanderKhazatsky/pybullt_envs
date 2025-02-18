import roboverse
import numpy as np
import pickle as pkl
from tqdm import tqdm
from rlkit.envs.images import EnvRenderer, InsertImageEnv
import rlkit.torch.pytorch_util as ptu
import os
from PIL import Image
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--num_trajectories", type=int, default=100)
parser.add_argument("--num_timesteps", type=int, default=50)
parser.add_argument("--video_save_frequency", type=int,
                    default=0, help="Set to zero for no video saving")

args = parser.parse_args()
for obj in ['mug', 'long_sofa', 'camera', 'grill_trash_can', 'beer_bottle']:
    print('Collecting Data For: ' + obj)
    data_save_path = "/home/ashvin/data/rail-khazatsky/sasha/presampled_goals/affordances/combined/pnp_{0}_goals.pkl".format(obj)
    env = roboverse.make('SawyerRigMultiobj-v0', test_env=True, object_subset=[obj])

    obs_dim = env.observation_space.spaces['state_achieved_goal'].low.size
    imlength = env.obs_img_dim * env.obs_img_dim * 3

    dataset = {
            'initial_latent_state': np.zeros((args.num_trajectories * args.num_timesteps, 720), dtype=np.float),
            'latent_desired_goal': np.zeros((args.num_trajectories * args.num_timesteps, 720), dtype=np.float),
            'state_desired_goal': np.zeros((args.num_trajectories * args.num_timesteps,
                obs_dim), dtype=np.float),
            'image_desired_goal': np.zeros((args.num_trajectories * args.num_timesteps, imlength), dtype=np.float),
            'initial_image_observation': np.zeros((args.num_trajectories * args.num_timesteps, imlength), dtype=np.float),
            }

    comb_tasks_done = 0
    for i in tqdm(range(args.num_trajectories)):
        env.demo_reset(test_traj=True)
        init_img = np.uint8(env.render_obs()).transpose() / 255.0

        for j in range(25):
            action = env.get_demo_action()
            obs, reward, done, info = env.step(action)
            
        for j in range(args.num_timesteps):
            action = env.get_demo_action()
            obs, reward, done, info = env.step(action)

            img = np.uint8(env.render_obs()).transpose() / 255.0

            dataset['state_desired_goal'][i * args.num_timesteps + j] = obs['state_achieved_goal']
            dataset['image_desired_goal'][i * args.num_timesteps + j] = img.flatten()
            dataset['initial_image_observation'][i * args.num_timesteps + j] = init_img.flatten()
        
        comb_tasks_done += env.done

    print('Success Rate: {}'.format(comb_tasks_done / args.num_trajectories))
    file = open(data_save_path, 'wb')
    pkl.dump(dataset, file)
    file.close()

# dataset = {
#         'initial_latent_state': np.zeros((args.num_trajectories * args.num_timesteps, 720), dtype=np.float),
#         'latent_desired_goal': np.zeros((args.num_trajectories * args.num_timesteps, 720), dtype=np.float),
#         'state_desired_goal': np.zeros((args.num_trajectories * args.num_timesteps,
#             obs_dim), dtype=np.float),
#         'image_desired_goal': np.zeros((args.num_trajectories * args.num_timesteps, imlength), dtype=np.float),
#         'initial_image_observation': np.zeros((args.num_trajectories * args.num_timesteps, imlength), dtype=np.float),
#         }

# comb_tasks_done = 0
# for i in tqdm(range(args.num_trajectories)):
#     env.demo_reset()
#     init_img = np.uint8(env.render_obs()).transpose() / 255.0
    
#     for j in range(args.num_timesteps):
#         action = env.get_demo_action()
#         obs, reward, done, info = env.step(action)

#         img = np.uint8(env.render_obs()).transpose() / 255.0

#         dataset['state_desired_goal'][i * args.num_timesteps + j] = obs['state_achieved_goal']
#         dataset['image_desired_goal'][i * args.num_timesteps + j] = img.flatten()
#         dataset['initial_image_observation'][i * args.num_timesteps + j] = init_img.flatten()
    
#     comb_tasks_done += env.done

# print('Success Rate: {}'.format(comb_tasks_done / args.num_trajectories))
# file = open(data_save_path, 'wb')
# pkl.dump(dataset, file)
# file.close()