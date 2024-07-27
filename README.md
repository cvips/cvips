# CVIPS: Collaborative Vision for Increased Pedestrian Safety

Implementation of the paper "Impact of Latency and Bandwidth Limitations on the Safety Performance of Collaborative Perception" (2024 IEEE International Conference on Computer Communications and Networks (ICCN)).

## Dataset

The CVIPS dataset is available [here](https://drive.google.com/drive/folders/1gCCrIslzVkupyF0lj_1I9qXTB2_a4tjd?usp=drive_link).

## Installation and Data Preparation

Please check [installation](docs/installation.md) for setup instructions and [data_preparation](docs/data_preparation.md) for preparing the dataset.

## Getting Started

Refer to [getting_started](docs/getting_started.md) for training, evaluation, and visualization of the CVIPS model.

## Dataset Generation Setup

![Dataset Generation](figs/First_video.gif "Dataset Generation Visualization")

Our dataset is generated using the CARLA simulator, providing diverse scenarios for collaborative perception.

## V2XFormer for Pedestrian Detection

![V2XFormer Architecture](figs/V2XFormer.jpg "V2XFormer Architecture")

We utilize a modified V2XFormer architecture for pedestrian detection in collaborative scenarios.

## Results

(You can add a brief summary of your key results here)

## Acknowledgement

This project is based on the following open-source projects: [BEVerse](https://github.com/zhangyp15/BEVerse), [Fiery](https://github.com/wayveai/fiery), [open-mmlab](https://github.com/open-mmlab), and [DeepAccident](https://arxiv.org/pdf/2304.01168).

## Citation

If you find this work helpful for your research, please consider citing:

```bibtex
@inproceedings{shenkut2024impact,
  title={Impact of Latency and Bandwidth Limitations on the Safety Performance of Collaborative Perception},
  author={Shenkut, D. and Kumar, B.V.K.},
  booktitle={2024 IEEE International Conference on Computer Communications and Networks (ICCN)},
  year={2024},
  organization={IEEE}
}
