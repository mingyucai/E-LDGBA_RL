<p align="center">
    <img width="200" src="figures/E-LDGBA_RL.JPG">
</p>

# E-LDGBA-LTL

## Publications
<pre>
@inproceedings{cai2021reinforcement,
  title={Reinforcement learning based temporal logic control with maximum probabilistic satisfaction},
  author={Cai, Mingyu and Xiao, Shaoping and Li, Baoluo and Li, Zhiliang and Kan, Zhen},
  booktitle={2021 IEEE International Conference on Robotics and Automation (ICRA)},
  pages={806--812},
  year={2021},
  organization={IEEE}
}

@article{cai2020learning,
  title={Learning-based probabilistic LTL motion planning with environment and motion uncertainties},
  author={Cai, Mingyu and Peng, Hao and Li, Zhijun and Kan, Zhen},
  journal={IEEE Transactions on Automatic Control},
  volume={66},
  number={5},
  pages={2386--2392},
  year={2020},
  publisher={IEEE}
}
</pre>

<br>


## Results
The agent have been trained on the task: go to goal-1 and then to goal-2 with maximum probability

![trajectory](/figures/tested_policy_SlipperyGrid_layout_1_g1-then-g2.png)


## Installation and Usage
Clone this repository and install the coressponding dependencies:
```
git clone https:https://github.com/mingyucai/E-LDGBA_RL
```
Execute the example:
```
python3 main.py --env 'SlipperyGrid' --layout 'layout_1' --property 'g1-then-g2' 
```


## LTL-to-Automaton:
This benchmark shows an E-LDGBA built from LDGBA. 
As for more samples, the LTL can be converted to LDGBA or LDBA by
excellent tool OWL, which is available at (https://owl.model.in.tum.de/try/).
